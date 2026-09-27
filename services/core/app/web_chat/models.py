"""Normalized message formats for the web-chat channel adapter.

Contract: ``docs/product/INTEGRATIONS.md`` — the adapter is the ONLY place
that knows about ``web_chat`` as a platform; the core sees only these
channel-neutral shapes:

- inbound:  ``tenant_id, bot_id, channel_id, end_customer_ref, message_id,
  received_at, content[], reply_handle``
- outbound: ``tenant_id, bot_id, channel_id, end_customer_ref, kind
  (reply|proactive), content[], reply_handle``

No web-platform field name (widget key, session id, browser fingerprint…)
leaks past this module's mapping boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ContentPart:
    """One normalized content part. Phase A web chat supports ``text``."""

    type: Literal["text"]
    text: str

    def to_dict(self) -> dict[str, str]:
        return {"type": self.type, "text": self.text}

    @classmethod
    def from_dict(cls, raw: object) -> "ContentPart":
        if not isinstance(raw, dict):
            raise ValueError("content part must be an object")
        kind = raw.get("type")
        if kind != "text":
            raise ValueError(f"unsupported content part type: {kind!r}")
        text = raw.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text content part requires non-empty text")
        return cls(type=kind, text=text)


@dataclass(frozen=True, slots=True)
class InboundMessage:
    """Normalized inbound message (channel → core)."""

    tenant_id: UUID
    bot_id: UUID
    channel_id: UUID
    end_customer_ref: str
    message_id: str
    received_at: datetime
    content: tuple[ContentPart, ...]
    reply_handle: str

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": str(self.tenant_id),
            "bot_id": str(self.bot_id),
            "channel_id": str(self.channel_id),
            "end_customer_ref": self.end_customer_ref,
            "message_id": self.message_id,
            "received_at": self.received_at.isoformat(),
            "content": [part.to_dict() for part in self.content],
            "reply_handle": self.reply_handle,
        }


@dataclass(frozen=True, slots=True)
class OutboundMessage:
    """Normalized outbound message (core → channel)."""

    tenant_id: UUID
    bot_id: UUID
    channel_id: UUID
    end_customer_ref: str
    kind: Literal["reply", "proactive"]
    content: tuple[ContentPart, ...]
    reply_handle: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": str(self.tenant_id),
            "bot_id": str(self.bot_id),
            "channel_id": str(self.channel_id),
            "end_customer_ref": self.end_customer_ref,
            "kind": self.kind,
            "content": [part.to_dict() for part in self.content],
            "reply_handle": self.reply_handle,
        }


@dataclass(slots=True)
class ChannelMappingRecord:
    """One mapped ``web_chat`` channel row: identity + auth key digest."""

    tenant_id: UUID
    bot_id: UUID
    channel_id: UUID
    credential_ref: str | None = None
    auth_key_plate_digest: str = ""


def merge_text(parts: tuple[ContentPart, ...]) -> str:
    """Degrade normalized multi-part content to plain text for simple channels."""
    return "\n".join(part.text for part in parts if part.type == "text")
