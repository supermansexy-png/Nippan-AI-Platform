"""Tests for the web-chat channel adapter (card T-079a).

Contract under test: ``docs/product/INTEGRATIONS.md`` — the 4 adapter duties
(authenticity, identity mapping, normalize, dedup) plus usage/monitor
reporting, normalized in/out shapes, and the never-guess-a-tenant rule.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from app.web_chat.adapter import (
    DuplicateMessageError,
    UnmappedChannelError,
    WebChatChannelAdapter,
)
from app.web_chat.models import ChannelMappingRecord, OutboundMessage, ContentPart
from app.web_chat.monitor import MonitorSink
from app.web_chat.store import InMemoryDedupeStore


TENANT = uuid.UUID("11111111-1111-1111-1111-111111111111")
BOT = uuid.UUID("22222222-2222-2222-2222-222222222222")
CHANNEL = uuid.UUID("33333333-3333-3333-3333-333333333333")

AUTH_KEY = "test-channel-auth-key"
DIGEST = WebChatChannelAdapter.key_digest(AUTH_KEY)


def make_adapter(**kwargs) -> WebChatChannelAdapter:
    defaults = dict(
        mappings={
            "shop-a": ChannelMappingRecord(
                tenant_id=TENANT,
                bot_id=BOT,
                channel_id=CHANNEL,
                auth_key_plate_digest=DIGEST,
            )
        },
    )
    defaults.update(kwargs)
    return WebChatChannelAdapter(**defaults)  # type: ignore[arg-type]


def ingest_kwargs(message_id: str = "m-1") -> dict:
    return dict(
        auth_key=AUTH_KEY,
        end_customer_ref="visitor-42",
        message_id=message_id,
        content=[{"type": "text", "text": "สวัสดีครับ"}],
    )


class RecordingUsageSink:
    def __init__(self) -> None:
        self.events: list[dict[str, str]] = []

    def record(self, **kw) -> None:
        self.events.append(kw)


# ── authenticity + identity mapping ─────────────────────

@pytest.mark.anyio
async def test_bad_auth_key_is_rejected_not_guessed() -> None:
    adapter = make_adapter()
    with pytest.raises(UnmappedChannelError):
        adapter.ingest(**{**ingest_kwargs(), "auth_key": "wrong-key"})


@pytest.mark.anyio
async def test_missing_auth_key_is_rejected() -> None:
    adapter = make_adapter()
    with pytest.raises(UnmappedChannelError):
        adapter.ingest(**{**ingest_kwargs(), "auth_key": ""})


@pytest.mark.anyio
async def test_mapped_key_carries_full_identity() -> None:
    adapter = make_adapter()
    msg = adapter.ingest(**ingest_kwargs())
    assert msg.tenant_id == TENANT
    assert msg.bot_id == BOT
    assert msg.channel_id == CHANNEL


# ── normalization ────────────────────────────────────────

@pytest.mark.anyio
async def test_normalized_shape_has_no_platform_fields() -> None:
    adapter = make_adapter()
    msg = adapter.ingest(**ingest_kwargs())
    payload = msg.to_dict()
    assert set(payload) == {
        "tenant_id",
        "bot_id",
        "channel_id",
        "end_customer_ref",
        "message_id",
        "received_at",
        "content",
        "reply_handle",
    }
    assert payload["content"] == [{"type": "text", "text": "สวัสดีครับ"}]


@pytest.mark.anyio
async def test_non_text_part_is_rejected_fail_closed() -> None:
    adapter = make_adapter()
    with pytest.raises(ValueError):
        adapter.ingest(
            **{
                **ingest_kwargs(),
                "content": [{"type": "sticker", "id": "x"}],
            }
        )


@pytest.mark.anyio
async def test_empty_content_rejected() -> None:
    adapter = make_adapter()
    with pytest.raises(ValueError):
        adapter.ingest(**{**ingest_kwargs(), "content": []})


@pytest.mark.anyio
async def test_blank_customer_ref_rejected() -> None:
    adapter = make_adapter()
    with pytest.raises(ValueError):
        adapter.ingest(**{**ingest_kwargs(), "end_customer_ref": "  "})


# ── de-duplication ───────────────────────────────────────

@pytest.mark.anyio
async def test_duplicate_message_id_is_dropped() -> None:
    adapter = make_adapter()
    adapter.ingest(**ingest_kwargs("m-1"))
    with pytest.raises(DuplicateMessageError):
        adapter.ingest(**ingest_kwargs("m-1"))


@pytest.mark.anyio
async def test_different_message_id_passes() -> None:
    adapter = make_adapter()
    adapter.ingest(**ingest_kwargs("m-1"))
    msg = adapter.ingest(**ingest_kwargs("m-2"))
    assert msg.message_id == "m-2"


@pytest.mark.anyio
async def test_dedupe_is_scoped_per_tenant_and_channel() -> None:
    second = uuid.UUID("44444444-4444-4444-4444-444444444444")
    adapter = WebChatChannelAdapter(
        mappings={
            "a": ChannelMappingRecord(
                tenant_id=TENANT,
                bot_id=BOT,
                channel_id=CHANNEL,
                auth_key_plate_digest=DIGEST,
            ),
            "b": ChannelMappingRecord(
                tenant_id=TENANT,
                bot_id=BOT,
                channel_id=second,
                auth_key_plate_digest=WebChatChannelAdapter.key_digest(
                    "key-b"
                ),
            ),
        }
    )
    adapter.ingest(
        auth_key=AUTH_KEY,
        end_customer_ref="v",
        message_id="m-1",
        content=[{"type": "text", "text": "hi"}],
    )
    msg = adapter.ingest(
        auth_key="key-b",
        end_customer_ref="v",
        message_id="m-1",
        content=[{"type": "text", "text": "hi"}],
    )
    assert msg.channel_id == second


# ── outbound / reply shaping ────────────────────────────

@pytest.mark.anyio
async def test_outbound_reply_degrades_to_text() -> None:
    adapter = make_adapter()
    out = OutboundMessage(
        tenant_id=TENANT,
        bot_id=BOT,
        channel_id=CHANNEL,
        end_customer_ref="visitor-42",
        kind="reply",
        content=(
            ContentPart(type="text", text="เปิด 9:00-18:00 ครับ"),
            ContentPart(type="text", text="ยินดีต้อนรับ"),
        ),
        reply_handle="visitor-42",
    )
    text = adapter.send(message=out)
    assert text == "เปิด 9:00-18:00 ครับ\nยินดีต้อนรับ"


@pytest.mark.anyio
async def test_outbound_empty_content_rejected() -> None:
    adapter = make_adapter()
    out = OutboundMessage(
        tenant_id=TENANT,
        bot_id=BOT,
        channel_id=CHANNEL,
        end_customer_ref="v",
        kind="reply",
        content=(),
    )
    with pytest.raises(ValueError):
        adapter.send(message=out)


@pytest.mark.anyio
async def test_outbound_unknown_kind_rejected() -> None:
    adapter = make_adapter()
    out = OutboundMessage(
        tenant_id=TENANT,
        bot_id=BOT,
        channel_id=CHANNEL,
        end_customer_ref="v",
        kind="broadcast",  # type: ignore[arg-type]
        content=(ContentPart(type="text", text="x"),),
    )
    with pytest.raises(ValueError):
        adapter.send(message=out)


# ── observability duty 6 ────────────────────────────────

@pytest.mark.anyio
async def test_usage_and_monitor_reported(tmp_path: Path) -> None:
    usage = RecordingUsageSink()
    log_path = tmp_path / "monitor.jsonl"
    adapter = make_adapter(
        usage_sink=usage,
        monitor=MonitorSink(log_path),
    )
    adapter.ingest(**ingest_kwargs())
    assert any(e["kind"] == "inbound" for e in usage.events)

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    event = json.loads(lines[-1])
    assert event["event_type"] == "web_chat_inbound"
    assert event["tenant_id"] == str(TENANT)
    assert event["bot_id"] == str(BOT)
    assert event["channel_id"] == str(CHANNEL)


@pytest.mark.anyio
async def test_monitor_written_for_duplicate(tmp_path: Path) -> None:
    log_path = tmp_path / "monitor.jsonl"
    adapter = make_adapter(monitor=MonitorSink(log_path))
    adapter.ingest(**ingest_kwargs("m-dup"))
    with pytest.raises(DuplicateMessageError):
        adapter.ingest(**ingest_kwargs("m-dup"))
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    types = [json.loads(line)["event_type"] for line in lines]
    assert "web_chat_duplicate" in types
