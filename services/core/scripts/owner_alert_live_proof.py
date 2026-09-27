"""T-071 live firing proof for the owner alert channel.

Fires one synthetic TURN_FAILED room event through the REAL alerting
pipeline — AlertingEventSink -> SmtpEmailAlertTransport -> SMTP wire —
against a local debug SMTP sink (no network egress, no credentials).
The captured message is written to the given output path as evidence
that a red alert addressed to the Owner's endpoint renders and
dispatches correctly.

Usage:
    python scripts/owner_alert_live_proof.py <output.evidence.txt>

This is the card's allowed "simulated with evidence" proof. Real Gmail
delivery additionally requires Owner SMTP credentials in the deployment
environment (NIPPAN_ALERT_EMAIL_* settings) — never committed to git.
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

# Make `app` importable when run from services/core.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.war_room.alert import (  # noqa: E402
    AlertingEventSink,
    EventAlertRenderer,
    SmtpEmailAlertTransport,
)
from app.war_room.contracts import HaltReason, MessageType, RoomState  # noqa: E402
from app.war_room.interfaces import (  # noqa: E402
    CorrelationContext,
    OrderedRoomEvent,
    RoomEventDraft,
    RoomEventType,
    TurnFailureKind,
)

OWNER_ENDPOINT = "supermanexy@gmail.com"
FROM_ADDR = "alerts@nippan.local"
SMTP_PORT = 8825


class DebugSmtpSink:
    """Minimal asyncio SMTP receiver: EHLO -> MAIL -> RCPT -> DATA -> QUIT.

    All connections share one instance, so `captured` accumulates every
    received message until the server is closed.
    """

    def __init__(self, port: int) -> None:
        self.port = port
        self.captured: list[tuple[str, bytes]] = []
        self._server: asyncio.Server | None = None

    async def handle(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        def reply(line: str) -> None:
            writer.write((line + "\r\n").encode())

        reply("220 nippan-alert-proof ESMTP debug sink")
        envelope: list[str] = []
        in_data: list[bytes] = []
        try:
            while True:
                line = await reader.readline()
                if not line:
                    break
                cmd = line.decode(errors="replace").strip()
                upper = cmd.upper()
                if upper.startswith(("EHLO", "HELO")):
                    reply("250-nippan-alert-proof")
                    reply("250 OK")
                elif upper.startswith("MAIL FROM"):
                    envelope.append(cmd)
                    reply("250 OK")
                elif upper.startswith("RCPT TO"):
                    envelope.append(cmd)
                    reply("250 OK")
                elif upper == "DATA":
                    reply("354 end with <CRLF>.<CRLF>")
                    while True:
                        data_line = await reader.readline()
                        if data_line in (b".\r\n", b".\n", b""):
                            break
                        if data_line.startswith(b"."):
                            data_line = data_line[1:]
                        in_data.append(data_line)
                    self.captured.append(
                        ("\n".join(envelope), b"".join(in_data))
                    )
                    envelope.clear()
                    in_data.clear()
                    reply("250 OK queued")
                elif upper == "QUIT":
                    reply("221 bye")
                    break
                else:
                    reply("250 OK")
                await writer.drain()
        finally:
            writer.close()

    async def __aenter__(self) -> "DebugSmtpSink":
        self._server = await asyncio.start_server(
            self.handle, "127.0.0.1", self.port
        )
        return self

    async def __aexit__(self, *exc) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()


async def main(output_path: str) -> None:
    evidence_sink = DebugSmtpSink(SMTP_PORT)
    async with evidence_sink:
        transport = SmtpEmailAlertTransport(
            host="127.0.0.1",
            port=SMTP_PORT,
            timeout=10.0,
        )
        renderer = EventAlertRenderer(
            to_addr=OWNER_ENDPOINT,
            from_addr=FROM_ADDR,
        )

        class ProofInnerSink:
            """Simulates one successful durable append (no DB needed)."""

            async def append(
                self,
                event: RoomEventDraft,
                *,
                expected_state=None,
                new_state=None,
            ) -> OrderedRoomEvent:
                return OrderedRoomEvent(
                    event_id=uuid4(),
                    sequence=1,
                    event_type=event.event_type,
                    correlation=event.correlation,
                    occurred_at=event.occurred_at,
                    room_state=event.room_state,
                    participant_id=event.participant_id,
                    message_type=event.message_type,
                    halt_reason=event.halt_reason,
                    payload=event.payload,
                )

        sink = AlertingEventSink(ProofInnerSink(), transport, renderer)

        correlation = CorrelationContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            room_id=UUID(int=3),
            agenda_item_id=UUID(int=4),
            request_id=uuid4(),
            trace_id=(uuid4().hex + uuid4().hex)[:32],
        )
        draft = RoomEventDraft(
            event_type=RoomEventType.TURN_FAILED,
            correlation=correlation,
            occurred_at=datetime.now(UTC),
            room_state=RoomState.NEEDS_OWNER_DECISION,
            participant_id="synthetic-participant",
            message_type=MessageType.ERROR,
            halt_reason=HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED,
            payload={
                "failure_kind": TurnFailureKind.PROVIDER_UNAVAILABLE.value
            },
        )

        await sink.append(draft)
        await sink.await_pending()
        assert sink._bg_tasks == set(), "no delivery task was recorded"
        # Let the server connection handler finish reading QUIT.
        await asyncio.sleep(0.3)

    assert evidence_sink.captured, "SMTP sink captured no message"
    envelope, data = evidence_sink.captured[-1]
    text = data.decode("utf-8", errors="replace")
    subject_line = next(
        (line for line in text.splitlines() if line.startswith("Subject:")),
        None,
    )
    assert f"To: {OWNER_ENDPOINT}" in text, "alert not addressed to Owner endpoint"
    assert subject_line and "[NIPPAN][TURN_FAILED]" in subject_line, (
        "alert subject missing critical-event prefix"
    )
    assert f"From: {FROM_ADDR}" in text
    assert "TRACE" not in text  # room content must never leak into alerts
    assert "trace_id: " in text  # ...but the operational trace id must

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "=== T-071 live firing proof ===\n"
        "pipeline: AlertingEventSink -> SmtpEmailAlertTransport -> SMTP\n"
        "endpoint (To): " + OWNER_ENDPOINT + "\n"
        + "=== SMTP envelope ===\n"
        + envelope
        + "\n=== message ===\n"
        + text,
        encoding="utf-8",
    )
    print("LIVE PROOF OK")
    print("  endpoint (to):", OWNER_ENDPOINT)
    print("  subject:", subject_line)
    print("  evidence file:", output.resolve())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scripts/owner_alert_live_proof.py <output.txt>")
        raise SystemExit(2)
    asyncio.run(main(sys.argv[1]))
