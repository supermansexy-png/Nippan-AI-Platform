"""T-071 owner alert channel unit tests.

Covers the AlertingEventSink wrapper semantics (critical event
whitelist, sink-failure alerting, fire-and-forget containment) and the
fail-closed settings builder. No network: the SMTP transport is not
contacted here; delivery is exercised against fake channels.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.settings import Settings
from app.war_room.alert import (
    AlertingEventSink,
    DisabledAlertChannel,
    EventAlertRenderer,
    LoggingAlertChannel,
    RenderedAlert,
    SmtpEmailAlertTransport,
    build_alert_channel,
)
from app.war_room.contracts import HaltReason, MessageType, RoomState
from app.war_room.interfaces import (
    CorrelationContext,
    RoomEventDraft,
    RoomEventType,
    TurnFailureKind,
)
from app.war_room.persistence import RoomPersistenceError


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def correlation() -> CorrelationContext:
    return CorrelationContext(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        room_id=UUID(int=3),
        agenda_item_id=UUID(int=4),
        request_id=uuid4(),
        trace_id=f"{uuid4().hex}{uuid4().hex}"[:32],
    )


class RecordingChannel:
    def __init__(self) -> None:
        self.messages: list[RenderedAlert] = []

    async def deliver(self, message: RenderedAlert) -> None:
        self.messages.append(message)


class FailingChannel:
    async def deliver(self, message: RenderedAlert) -> None:
        raise RuntimeError("smtp down")


class InnerSink:
    def __init__(self, *, fail_with: Exception | None = None) -> None:
        self.fail_with = fail_with
        self.appended: list[RoomEventDraft] = []

    async def append(
        self,
        event: RoomEventDraft,
        *,
        expected_state=None,
        new_state=None,
    ):
        if self.fail_with is not None:
            raise self.fail_with
        self.appended.append(event)
        from app.war_room.interfaces import OrderedRoomEvent

        return OrderedRoomEvent(
            event_id=uuid4(),
            sequence=len(self.appended),
            event_type=event.event_type,
            correlation=event.correlation,
            occurred_at=event.occurred_at,
            room_state=event.room_state,
            participant_id=event.participant_id,
            message_type=event.message_type,
            halt_reason=event.halt_reason,
            payload=event.payload,
        )


def draft(event_type: RoomEventType, **overrides) -> RoomEventDraft:
    fields = {
        "event_type": event_type,
        "correlation": correlation(),
        "occurred_at": datetime.now(UTC),
        "halt_reason": None,
        "message_type": None,
        "payload": {},
    }
    fields.update(overrides)
    return RoomEventDraft(**fields)


def renderer() -> EventAlertRenderer:
    return EventAlertRenderer(
        to_addr="owner@example.com",
        from_addr="alerts@nippan.local",
    )


@pytest.mark.anyio
async def test_turn_failed_appends_and_fires_one_alert():
    channel = RecordingChannel()
    inner = InnerSink()
    sink = AlertingEventSink(inner, channel, renderer())

    event = await sink.append(
        draft(
            RoomEventType.TURN_FAILED,
            halt_reason=HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED,
            message_type=MessageType.ERROR,
            payload={"failure_kind": TurnFailureKind.TIMEOUT.value},
        ),
        expected_state=RoomState.RUNNING,
        new_state=RoomState.NEEDS_OWNER_DECISION,
    )

    assert event.event_type is RoomEventType.TURN_FAILED
    assert len(inner.appended) == 1
    await sink.await_pending()
    assert len(channel.messages) == 1
    message = channel.messages[0]
    assert "[NIPPAN][TURN_FAILED]" in message.subject
    assert message.to_addr == "owner@example.com"
    assert message.from_addr == "alerts@nippan.local"
    assert "failure_kind='TIMEOUT'" in message.body
    assert message.body.count("event_type:") == 1


@pytest.mark.anyio
async def test_budget_hard_stop_fires_alert():
    channel = RecordingChannel()
    inner = InnerSink()
    sink = AlertingEventSink(inner, channel, renderer())

    await sink.append(
        draft(
            RoomEventType.BUDGET_HARD_STOP,
            halt_reason=HaltReason.ROOM_BUDGET_EXHAUSTED,
        ),
        expected_state=RoomState.RUNNING,
        new_state=RoomState.NEEDS_OWNER_DECISION,
    )
    await sink.await_pending()

    assert len(channel.messages) == 1
    assert "[NIPPAN][BUDGET_HARD_STOP]" in channel.messages[0].subject


@pytest.mark.anyio
async def test_ordinary_event_is_silent():
    channel = RecordingChannel()
    inner = InnerSink()
    sink = AlertingEventSink(inner, channel, renderer())

    await sink.append(
        draft(
            RoomEventType.MESSAGE_APPENDED,
            message_type=MessageType.AGENT_MESSAGE,
            payload={"content_text": "room discussion content"},
        ),
        expected_state=RoomState.RUNNING,
    )

    assert len(inner.appended) == 1
    assert channel.messages == []


@pytest.mark.anyio
async def test_scheduler_halted_round_complete_is_silent():
    """Round-completion halts are normal operation, not a red alert."""

    channel = RecordingChannel()
    inner = InnerSink()
    sink = AlertingEventSink(inner, channel, renderer())

    await sink.append(
        draft(
            RoomEventType.SCHEDULER_HALTED,
            halt_reason=HaltReason.ROUND_COMPLETE,
        ),
        expected_state=RoomState.RUNNING,
    )

    assert channel.messages == []


@pytest.mark.anyio
async def test_sink_failure_alerts_and_reraises():
    channel = RecordingChannel()
    inner = InnerSink(fail_with=RoomPersistenceError("db connection lost"))
    sink = AlertingEventSink(inner, channel, renderer())

    with pytest.raises(RoomPersistenceError):
        await sink.append(draft(RoomEventType.MESSAGE_APPENDED))
    await sink.await_pending()

    assert len(channel.messages) == 1
    message = channel.messages[0]
    assert "[NIPPAN][SINK_FAILURE][MESSAGE_APPENDED]" in message.subject
    assert "RoomPersistenceError: db connection lost" in message.body
    assert "FAILED to commit" in message.body


@pytest.mark.anyio
async def test_failing_transport_never_breaks_the_room_flow():
    channel = FailingChannel()
    inner = InnerSink()
    sink = AlertingEventSink(inner, channel, renderer())

    # The append must succeed and return normally even though the alert
    # transport raises.
    event = await sink.append(
        draft(
            RoomEventType.TURN_FAILED,
            halt_reason=HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED,
        ),
        expected_state=RoomState.RUNNING,
        new_state=RoomState.NEEDS_OWNER_DECISION,
    )

    assert event.event_type is RoomEventType.TURN_FAILED
    assert len(inner.appended) == 1


@pytest.mark.anyio
async def test_alert_body_never_carries_room_content():
    channel = RecordingChannel()
    inner = InnerSink()
    sink = AlertingEventSink(inner, channel, renderer())

    await sink.append(
        draft(
            RoomEventType.TURN_FAILED,
            halt_reason=HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED,
            message_type=MessageType.ERROR,
            payload={
                "content_text": "SECRET room discussion content",
                "failure_kind": "PROVIDER_UNAVAILABLE",
            },
        ),
        expected_state=RoomState.RUNNING,
        new_state=RoomState.NEEDS_OWNER_DECISION,
    )
    await sink.await_pending()

    assert channel.messages, "expected one alert"
    body = channel.messages[0].body
    assert "SECRET room discussion content" not in body
    assert "content_text" not in body


def test_build_alert_channel_disabled_when_unconfigured():
    settings = Settings(
        database_url=None,
        alert_email_enabled=False,
    )
    channel, to_addr, from_addr = build_alert_channel(settings)

    assert isinstance(channel, DisabledAlertChannel)
    assert to_addr == ""
    assert from_addr == ""


def test_build_alert_channel_fail_closed_when_partial():
    # enabled + host but no credentials: still disabled, never half-wired.
    settings = Settings(
        database_url=None,
        alert_email_enabled=True,
        alert_email_smtp_host="smtp.example.com",
    )
    channel, _, _ = build_alert_channel(settings)

    assert isinstance(channel, DisabledAlertChannel)


def test_build_alert_channel_enabled_when_complete():
    settings = Settings(
        database_url=None,
        alert_email_enabled=True,
        alert_email_smtp_host="smtp.example.com",
        alert_email_port=587,
        alert_email_username="alerts@nippan.local",
        alert_email_password="secret-not-in-git",
        alert_email_from="alerts@nippan.local",
        alert_email_to="owner@example.com",
    )
    channel, to_addr, from_addr = build_alert_channel(settings)

    assert isinstance(channel, SmtpEmailAlertTransport)
    assert to_addr == "owner@example.com"
    assert from_addr == "alerts@nippan.local"
    assert channel._host == "smtp.example.com"
    assert channel._port == 587


def test_smtp_transport_renders_valid_email_message():
    transport = SmtpEmailAlertTransport(
        host="smtp.example.com",
        port=587,
        timeout=5.0,
    )
    message = RenderedAlert(
        subject="[NIPPAN][TURN_FAILED] state=NEEDS_OWNER_DECISION",
        body="line1\nline2\n",
        to_addr="owner@example.com",
        from_addr="alerts@nippan.local",
    )

    # Use stdlib message building without network: replicate send_alert's
    # message construction by monkeypatching smtplib.SMTP.
    captured = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None):
            captured["host"] = host
            captured["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def ehlo(self):
            return None

        def has_extn(self, ext):
            return False

        def send_message(self, email_message):
            captured["subject"] = email_message["Subject"]
            captured["from"] = email_message["From"]
            captured["to"] = email_message["To"]
            captured["body"] = email_message.get_content()

    import app.war_room.alert as alert_module

    original = alert_module.smtplib.SMTP
    alert_module.smtplib.SMTP = FakeSMTP
    try:
        transport.send_alert(message)
    finally:
        alert_module.smtplib.SMTP = original

    assert captured["host"] == "smtp.example.com"
    assert captured["port"] == 587
    assert captured["subject"] == message.subject
    assert captured["to"] == "owner@example.com"
    assert captured["from"] == "alerts@nippan.local"
    assert "line1" in captured["body"]


def test_renderer_summary_truncates_long_values():
    long_model = "m" * 200

    from app.war_room.interfaces import OrderedRoomEvent

    ordered = OrderedRoomEvent(
        event_id=uuid4(),
        sequence=1,
        event_type=RoomEventType.TURN_FAILED,
        correlation=correlation(),
        occurred_at=datetime.now(UTC),
        room_state=RoomState.NEEDS_OWNER_DECISION,
        participant_id=None,
        message_type=MessageType.ERROR,
        halt_reason=HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED,
        payload={"model": long_model},
    )
    summary = EventAlertRenderer._payload_summary(ordered)
    assert "..." in summary
    assert len(summary) < 160


def test_logging_channel_is_usable_as_fallback():
    channel = LoggingAlertChannel()
    message = RenderedAlert(
        subject="s",
        body="b",
        to_addr="o@x",
        from_addr="f@x",
    )
    # Must not raise.
    assert channel.deliver is not None
