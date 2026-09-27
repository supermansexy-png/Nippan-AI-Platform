"""Web-chat channel adapter.

Contract: ``docs/product/INTEGRATIONS.md`` — one adapter per platform; the
core never learns which platform it is talking to. Adapter duties enforced
here:

1. **Verify authenticity** — per-channel auth key, compared constant-time as
   SHA-256 digests (no secret is ever accepted in cleartext into the core).
2. **Map identity** — the request's channel key must map to exactly one
   ``(tenant_id, bot_id, channel_id)`` row; unmapped → rejected, never guessed
   (duty 2, and MESSAGE_FLOW_V1.md §14 stop rule 2).
3. **Normalize** — platform payload → ``InboundMessage`` /
   ``OutboundMessage`` normalized shapes in ``models.py``.
4. **Drop duplicates** — de-dup on ``(tenant, channel, message_id)`` via the
   injectable ``DedupeStore`` (ND-1).
5. **Report usage/errors** — to the injectable ``usage-tracker`` and
   ``monitor-log`` sinks (duty 6).

Web chat has NO platform-side signature scheme like LINE's HMAC; authenticity
comes from the per-channel shared auth key bound to the tenant's channel row.
The key digest is stored in ``lite_channels.credential_ref`` — the cleartext
key never enters this module, mirroring duty 7 (credentials out of the
database).

Runnable proof of all 5 duties together (T-079a e2e script) — run from the
repo root; the script bootstraps ``services/core`` onto ``sys.path`` itself,
so no ``PYTHONPATH`` export is needed:

    python services/core/scripts/run_web_chat_e2e.py

It prints a ``PASS``/``FAIL`` transcript and writes
``services/core/scripts/web_chat_e2e_transcript.json`` (besides a JSONL
``web_chat_e2e_monitor.jsonl`` monitor log).
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime
from uuid import UUID

from .models import (
    ChannelMappingRecord,
    ContentPart,
    InboundMessage,
    OutboundMessage,
)
from .monitor import NullUsageSink
from .store import DedupeStore, InMemoryDedupeStore

__all__ = [
    "WebChatAdapterError",
    "UnmappedChannelError",
    "DuplicateMessageError",
    "WebChatChannelAdapter",
]


class WebChatAdapterError(RuntimeError):
    """Base class for adapter failures."""


class UnmappedChannelError(WebChatAdapterError):
    """The request cannot be mapped to a tenant/bot/channel — a REJECT."""


class DuplicateMessageError(WebChatAdapterError):
    """The message id was already processed for this channel."""


class WebChatChannelAdapter:
    """Accepts a web visitor message, normalizes it, and hands back the reply.

    The adapter does NOT do model inference — that is the core's job
    (``chat-bot-core``, MESSAGE_FLOW_V1.md §5). The adapter's scope is ingress
    (+ egress shaping), exactly as ``docs/product/adapters/line-oa.md`` does
    for LINE.
    """

    def __init__(
        self,
        *,
        mappings: dict[str, ChannelMappingRecord],
        dedupe: DedupeStore | None = None,
        usage_sink=None,
        monitor=None,
    ) -> None:
        if not mappings:
            raise ValueError("at least one channel mapping is required")
        self._mappings = mappings
        self._dedupe: DedupeStore = dedupe or InMemoryDedupeStore()
        self._usage = usage_sink or NullUsageSink()
        self._monitor = monitor

    # ── duty 1: authenticity ─────────────────────────────
    @staticmethod
    def key_digest(auth_key: str) -> str:
        return hashlib.sha256(auth_key.encode("utf-8")).hexdigest()

    def _map_channel(self, *, auth_key: str) -> ChannelMappingRecord:
        """Map a presented auth key to its channel row.

        Compares digest with ``hmac.compare_digest`` so timing cannot leak
        which of the registered keys matched.
        """
        if not auth_key or not auth_key.strip():
            raise UnmappedChannelError("channel auth key is missing")
        candidate = self.key_digest(auth_key.strip())
        for record in self._mappings.values():
            if hmac.compare_digest(
                candidate,
                record.auth_key_plate_digest,
            ):
                return record
        raise UnmappedChannelError("channel auth key is not registered")

    # ── duties 1–4: the inbound path ─────────────────────
    def ingest(
        self,
        *,
        auth_key: str,
        end_customer_ref: str,
        message_id: str,
        content: list[dict[str, object]],
    ) -> InboundMessage:
        """Turn one raw web request into a normalized InboundMessage.

        Raises:
        - ``UnmappedChannelError``: bad/unknown auth key (duty 2 reject).
        - ``DuplicateMessageError``: already-seen message_id (duty 4 drop).
        - ``ValueError``: malformed content parts (rejected, fail-closed).
        """
        record = self._map_channel(auth_key=auth_key)

        if (
            not isinstance(end_customer_ref, str)
            or not end_customer_ref.strip()
        ):
            raise ValueError("end_customer_ref is required")
        if not isinstance(message_id, str) or not message_id.strip():
            raise ValueError("message_id is required")

        if not isinstance(content, list) or not content:
            raise ValueError("content must be a non-empty list of parts")

        try:
            parts = tuple(ContentPart.from_dict(item) for item in content)
        except (ValueError, TypeError) as exc:
            self._log_monitor(
                level="warn",
                event_type="web_chat_reject",
                message=f"content rejected: {exc}",
                tenant_id=str(record.tenant_id),
                bot_id=str(record.bot_id),
                channel_id=str(record.channel_id),
            )
            raise

        if self._dedupe.seen_before(
            tenant_id=str(record.tenant_id),
            channel_id=str(record.channel_id),
            message_id=message_id.strip(),
        ):
            self._log_monitor(
                level="info",
                event_type="web_chat_duplicate",
                message=f"dropped duplicate message_id={message_id}",
                tenant_id=str(record.tenant_id),
                bot_id=str(record.bot_id),
                channel_id=str(record.channel_id),
            )
            raise DuplicateMessageError(
                f"message_id={message_id} already processed"
            )

        message = InboundMessage(
            tenant_id=record.tenant_id,
            bot_id=record.bot_id,
            channel_id=record.channel_id,
            end_customer_ref=end_customer_ref.strip(),
            message_id=message_id.strip(),
            received_at=datetime.now(UTC),
            content=parts,
            # Web chat reply handle = the visitor ref: the browser replies in
            # the same open request; there is no LINE-style expiry token.
            reply_handle=end_customer_ref.strip(),
        )
        self._usage_sink.record(
            tenant_id=str(record.tenant_id),
            bot_id=str(record.bot_id),
            channel_id=str(record.channel_id),
            message_id=message.message_id,
            kind="inbound",
        )
        self._log_monitor(
            level="info",
            event_type="web_chat_inbound",
            message=f"accepted message_id={message.message_id}",
            tenant_id=str(record.tenant_id),
            bot_id=str(record.bot_id),
            channel_id=str(record.channel_id),
        )
        return message

    # ── egress: the core's reply back to the visitor ─────
    def send(
        self,
        *,
        message: OutboundMessage,
    ) -> str:
        """Degrade normalized outbound content to plain text for the browser.

        Web chat can render text only in Phase A; other parts (buttons etc.)
        degrade to text per INTEGRATIONS.md — the core never learns this.
        """
        from .models import merge_text

        if message.kind not in ("reply", "proactive"):
            raise ValueError(f"unsupported outbound kind: {message.kind!r}")
        if not message.content:
            self._log_monitor(
                level="warn",
                event_type="web_chat_send_reject",
                message="outbound message must carry at least one part",
                tenant_id=str(message.tenant_id),
                bot_id=str(message.bot_id),
                channel_id=str(message.channel_id),
            )
            raise ValueError("content must not be empty")
        text = merge_text(message.content)
        self._usage_sink.record(
            tenant_id=str(message.tenant_id),
            bot_id=str(message.bot_id),
            channel_id=str(message.channel_id),
            message_id="-",
            kind=message.kind,
        )
        return text

    def _log_monitor(
        self,
        *,
        level: str,
        event_type: str,
        message: str,
        tenant_id: str | None,
        bot_id: str | None,
        channel_id: str | None,
    ) -> None:
        if self._monitor is None:
            return
        self._monitor.log(
            level=level,
            event_type=event_type,
            message=message,
            tenant_id=tenant_id,
            bot_id=bot_id,
            channel_id=channel_id,
        )

    @property
    def _usage_sink(self):
        return self._usage
