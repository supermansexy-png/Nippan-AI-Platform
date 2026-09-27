"""T-079a runnable end-to-end proof.

Post a message as a web visitor → the adapter normalizes it into the
normalized inbound format → a simulated core reply comes back and is
shaped for the web page. Transcript is saved beside this script.

Run (from the repo root):
    python services/core/scripts/run_web_chat_e2e.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from uuid import UUID

# Self-bootstrap: make ``services/core`` importable no matter
# which working directory the script is launched from.
_SERVICES_CORE = Path(__file__).resolve().parent.parent
if str(_SERVICES_CORE) not in sys.path:
    sys.path.insert(0, str(_SERVICES_CORE))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app.web_chat.adapter import WebChatChannelAdapter
from app.web_chat.models import (
    ChannelMappingRecord,
    ContentPart,
    OutboundMessage,
)
from app.web_chat.monitor import MonitorSink
from app.web_chat.store import InMemoryDedupeStore

AUTH_KEY = "demo-web-chat-key"


def main() -> int:
    channel_key = "5a2c1e10-0000-4000-8000-000000000001"
    tenant_key = "11111111-1111-1111-1111-111111111111"
    bot_key = "22222222-2222-2222-2222-222222222222"

    channel_id = UUID(channel_key)
    tenant_id = UUID(tenant_key)
    bot_id = UUID(bot_key)

    adapter = WebChatChannelAdapter(
        mappings={
            channel_id: ChannelMappingRecord(
                tenant_id=tenant_id,
                bot_id=bot_id,
                channel_id=channel_id,
                auth_key_plate_digest=WebChatChannelAdapter.key_digest(AUTH_KEY),
            )
        },
        dedupe=InMemoryDedupeStore(),
        monitor=MonitorSink(Path(__file__).with_name("web_chat_e2e_monitor.jsonl")),
    )

    # 1. A web visitor posts a message (what the widget would POST).
    visitor_payload = {
        "channel_key": AUTH_KEY,
        "end_customer_ref": "visitor-web-001",
        "message_id": "web-msg-20260927-001",
        "content": [{"type": "text", "text": "ร้านเปิดกี่โมงครับ"}],
    }

    # 2. The adapter authenticates + maps + normalizes + de-dups.
    inbound = adapter.ingest(
        auth_key=visitor_payload["channel_key"],
        end_customer_ref=visitor_payload["end_customer_ref"],
        message_id=visitor_payload["message_id"],
        content=visitor_payload["content"],
    )
    normalized = inbound.to_dict()

    # 3. The core answers (simulated core reply — inference is the core's job,
    #    not the adapter's). Reply uses the normalized outbound shape.
    core_reply = OutboundMessage(
        tenant_id=inbound.tenant_id,
        bot_id=inbound.bot_id,
        channel_id=inbound.channel_id,
        end_customer_ref=inbound.end_customer_ref,
        kind="reply",
        content=(ContentPart(type="text", text="ร้านเปิด 9:00-18:00 ทุกวันครับ"),),
        reply_handle=inbound.reply_handle,
    )
    page_render_text = adapter.send(message=core_reply)

    # 4. Replay the same message_id — must be dropped (de-dup duty).
    replayed = False
    try:
        adapter.ingest(
            auth_key=visitor_payload["channel_key"],
            end_customer_ref=visitor_payload["end_customer_ref"],
            message_id=visitor_payload["message_id"],
            content=visitor_payload["content"],
        )
        replayed = True
    except Exception:
        replayed = False

    # 5. An unmapped key — must be rejected, never guessed.
    unmapped_rejected = False
    try:
        adapter.ingest(
            auth_key="not-a-registered-key",
            end_customer_ref="visitor-web-002",
            message_id="web-msg-20260927-002",
            content=[{"type": "text", "text": "hi"}],
        )
        unmapped_rejected = True
    except Exception:
        unmapped_rejected = False

    failed = replayed or unmapped_rejected
    transcript = {
        "visitor_message": visitor_payload,
        "normalized_inbound": normalized,
        "core_reply_rendered_for_web": page_render_text,
        "replay_was_rejected": not replayed,
        "unmapped_key_was_rejected": not unmapped_rejected,
        "result": "FAIL" if failed else "PASS",
    }
    out_path = Path(__file__).with_name("web_chat_e2e_transcript.json")
    out_path.write_text(
        json.dumps(transcript, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(transcript, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
