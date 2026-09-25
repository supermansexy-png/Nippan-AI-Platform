import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.war_room import (
    CorrelationContext,
    MessageType,
    PostgresRoomEventSink,
    PostgresRoomFailureHistorySource,
    PostgresRoomSnapshotSource,
    RoomDecisionSnapshot,
    RoomEventDraft,
    RoomEventType,
    RoomMode,
    RoomPersistenceConflict,
    RoomPersistenceError,
    RoomSession,
    RoomSessionFailureReconstructor,
    RoomState,
    serialize_room_snapshot,
)


class FakeCursor:
    def __init__(self, fetch_rows):
        self.fetch_rows = list(fetch_rows)
        self.statements = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def execute(self, query, params) -> None:
        self.statements.append((query, params))

    async def fetchone(self):
        if not self.fetch_rows:
            return None
        return self.fetch_rows.pop(0)

    async def fetchall(self):
        rows = list(self.fetch_rows)
        self.fetch_rows.clear()
        return rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self):
        return self._cursor


class FakeDatabase:
    def __init__(self, fetch_rows) -> None:
        self.cursor = FakeCursor(fetch_rows)
        self.scopes = []

    @asynccontextmanager
    async def tenant_transaction(self, **scope):
        self.scopes.append(scope)
        yield FakeConnection(self.cursor)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def correlation() -> CorrelationContext:
    return CorrelationContext(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        room_id=UUID(int=3),
        agenda_item_id=UUID(int=4),
        request_id=UUID(int=5),
        trace_id="0123456789abcdef0123456789abcdef",
    )


def draft() -> RoomEventDraft:
    return RoomEventDraft(
        event_type=RoomEventType.ROOM_STATE_CHANGED,
        correlation=correlation(),
        occurred_at=datetime(2026, 9, 23, 1, 30, tzinfo=UTC),
        room_state=RoomState.RUNNING,
        payload={"previous_state": "READY"},
    )


@pytest.mark.anyio
async def test_state_change_and_event_append_share_one_locked_transaction() -> None:
    database = FakeDatabase(
        fetch_rows=[
            ("READY",),
            (7,),
        ]
    )
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]

    event = await sink.append(
        draft(),
        expected_state=RoomState.READY,
        new_state=RoomState.RUNNING,
    )

    assert event.sequence == 7
    assert database.scopes == [
        {
            "tenant_id": UUID(int=1),
            "application_id": UUID(int=2),
            "request_id": UUID(int=5),
        }
    ]

    statements = [statement for statement, _ in database.cursor.statements]
    assert "for update" in statements[0].lower()
    assert "update public.project_rooms" in statements[1].lower()
    assert "max(sequence)" in statements[2].lower()
    assert "insert into public.project_room_messages" in statements[3].lower()


@pytest.mark.anyio
async def test_durable_state_conflict_fails_before_event_insert() -> None:
    database = FakeDatabase(fetch_rows=[("PAUSED",)])
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]

    with pytest.raises(RoomPersistenceConflict):
        await sink.append(
            draft(),
            expected_state=RoomState.READY,
            new_state=RoomState.RUNNING,
        )

    statements = [statement for statement, _ in database.cursor.statements]
    assert len(statements) == 1
    assert "for update" in statements[0].lower()


@pytest.mark.anyio
async def test_expected_state_only_append_rejects_stale_non_state_event() -> None:
    database = FakeDatabase(fetch_rows=[("PAUSED",)])
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]
    event = RoomEventDraft(
        event_type=RoomEventType.TURN_SCHEDULED,
        correlation=correlation(),
        occurred_at=datetime(2026, 9, 23, 1, 31, tzinfo=UTC),
        participant_id=str(UUID(int=10)),
        payload={"round_number": 1},
    )

    with pytest.raises(RoomPersistenceConflict):
        await sink.append(
            event,
            expected_state=RoomState.RUNNING,
        )

    statements = [statement for statement, _ in database.cursor.statements]
    assert len(statements) == 1
    assert "for update" in statements[0].lower()


@pytest.mark.anyio
async def test_failure_history_restores_only_failure_limit_turn_events() -> None:
    failed_id = UUID(int=10)
    other_id = UUID(int=11)
    database = FakeDatabase(
        fetch_rows=[
            (
                failed_id,
                json.dumps(
                    {
                        "event_type": "TURN_FAILED",
                        "halt_reason": "PARTICIPANT_FAILURE_LIMIT_REACHED",
                        "payload": {
                            "failure_kind": "PROVIDER_UNAVAILABLE",
                            "automatic_retry_allowed": False,
                        },
                    }
                ),
            ),
            (
                other_id,
                json.dumps(
                    {
                        "event_type": "OTHER_ERROR",
                        "halt_reason": None,
                        "payload": {},
                    }
                ),
            ),
        ]
    )
    source = PostgresRoomFailureHistorySource(database)  # type: ignore[arg-type]

    failed = await source.load_failed_participant_ids(
        correlation=correlation(),
    )

    assert failed == frozenset({str(failed_id)})
    query, params = database.cursor.statements[0]
    assert "message_type = 'ERROR'" in query
    assert "order by sequence" in query.lower()
    assert params == (UUID(int=1), UUID(int=2), UUID(int=3))


@pytest.mark.anyio
async def test_fresh_session_reconstructs_failure_cap_from_durable_turn_failed_event() -> None:
    failed_id = UUID(int=12)
    database = FakeDatabase(
        fetch_rows=[
            (
                failed_id,
                json.dumps(
                    {
                        "event_type": "TURN_FAILED",
                        "halt_reason": "PARTICIPANT_FAILURE_LIMIT_REACHED",
                        "payload": {
                            "failure_kind": "TIMEOUT",
                            "automatic_retry_allowed": False,
                        },
                    }
                ),
            ),
        ]
    )
    source = PostgresRoomFailureHistorySource(database)  # type: ignore[arg-type]
    reconstructor = RoomSessionFailureReconstructor(source)
    session = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.RUNNING,
        participants=(),
    )

    await reconstructor.restore(
        session,
        correlation=correlation(),
    )

    assert session.failed_participant_ids == {str(failed_id)}


def owner_decision_event(
    *,
    content_text: str | None = "  Continue with remaining healthy agents.  ",
    content_reference: str | None = None,
    participant_id: str | None = "owner-preview",
    message_type: MessageType | None = MessageType.OWNER_DECISION,
    event_type: RoomEventType = RoomEventType.ROOM_STATE_CHANGED,
) -> RoomEventDraft:
    """Build the SUBMIT_OWNER_DECISION event shape the orchestrator emits."""
    payload: dict[str, object] = {"previous_state": "NEEDS_OWNER_DECISION"}
    if content_text is not None:
        payload["content_text"] = content_text
    if content_reference is not None:
        payload["content_reference"] = content_reference
    return RoomEventDraft(
        event_type=event_type,
        correlation=correlation(),
        occurred_at=datetime(2026, 9, 25, 10, 0, tzinfo=UTC),
        room_state=RoomState.RUNNING,
        participant_id=participant_id,
        message_type=message_type,
        payload=payload,
    )


@pytest.mark.anyio
async def test_owner_decision_event_writes_durable_decision_row() -> None:
    occurred_at = datetime(2026, 9, 25, 10, 0, tzinfo=UTC)
    database = FakeDatabase(fetch_rows=[("NEEDS_OWNER_DECISION",), (9,)])
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]

    event = await sink.append(
        owner_decision_event(),
        expected_state=RoomState.NEEDS_OWNER_DECISION,
        new_state=RoomState.RUNNING,
    )

    assert event.sequence == 9
    statements = [statement for statement, _ in database.cursor.statements]
    assert "update public.project_rooms" in statements[1].lower()
    assert "insert into public.project_room_messages" in statements[3].lower()
    assert "insert into public.project_room_decisions" in statements[4].lower()

    query, params = database.cursor.statements[4]
    assert "public.project_room_decisions" in query.lower()
    assert "decided_at" in query.lower()
    assert params == (
        UUID(int=1),
        UUID(int=2),
        UUID(int=3),
        UUID(int=4),
        "owner-preview",
        "Continue with remaining healthy agents.",
        occurred_at,
    )


@pytest.mark.anyio
async def test_owner_decision_event_falls_back_to_content_reference() -> None:
    database = FakeDatabase(fetch_rows=[("NEEDS_OWNER_DECISION",), (9,)])
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]

    await sink.append(
        owner_decision_event(
            content_text=None,
            content_reference="decisions/owner-ref-9",
        ),
        expected_state=RoomState.NEEDS_OWNER_DECISION,
        new_state=RoomState.RUNNING,
    )

    _, params = database.cursor.statements[4]
    assert params[4] == "owner-preview"
    assert params[5] == "decisions/owner-ref-9"


@pytest.mark.anyio
async def test_state_change_without_owner_decision_message_writes_no_decision_row() -> None:
    database = FakeDatabase(fetch_rows=[("READY",), (4,)])
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]

    await sink.append(
        draft(),
        expected_state=RoomState.READY,
        new_state=RoomState.RUNNING,
    )

    statements = [statement for statement, _ in database.cursor.statements]
    assert all(
        "project_room_decisions" not in statement.lower()
        for statement in statements
    )


def test_owner_decision_fields_returns_validated_record() -> None:
    event = owner_decision_event()
    fields = PostgresRoomEventSink._owner_decision_fields(event)
    assert fields == (
        "Continue with remaining healthy agents.",
        "owner-preview",
    )


def test_owner_decision_fields_missing_content_text_fails_closed() -> None:
    event = owner_decision_event(content_text=None)
    with pytest.raises(RoomPersistenceError):
        PostgresRoomEventSink._owner_decision_fields(event)


def test_owner_decision_fields_blank_participant_id_fails_closed() -> None:
    event = owner_decision_event(participant_id="   ")
    with pytest.raises(RoomPersistenceError):
        PostgresRoomEventSink._owner_decision_fields(event)


def test_owner_decision_fields_ignores_non_owner_decision_events() -> None:
    plain_state_change = owner_decision_event(message_type=None)
    assert PostgresRoomEventSink._owner_decision_fields(plain_state_change) is None

    other_event_type = owner_decision_event(
        event_type=RoomEventType.MESSAGE_APPENDED
    )
    assert PostgresRoomEventSink._owner_decision_fields(other_event_type) is None


@pytest.mark.anyio
@pytest.mark.parametrize(
    "event_kwargs",
    [
        # Blank decision text with no usable reference.
        {"content_text": "   "},
        {"content_text": None, "content_reference": "   "},
        # Decision text beyond the durable 4000 character limit.
        {"content_text": "x" * 4001},
        {"content_text": None, "content_reference": "x" * 4001},
        # Missing acting owner principal_id.
        {"participant_id": None},
        {"participant_id": "   "},
    ],
)
async def test_invalid_owner_decision_event_fails_closed(
    event_kwargs: dict,
) -> None:
    database = FakeDatabase(fetch_rows=[("NEEDS_OWNER_DECISION",), (9,)])
    sink = PostgresRoomEventSink(database)  # type: ignore[arg-type]

    with pytest.raises(RoomPersistenceError):
        await sink.append(
            owner_decision_event(**event_kwargs),
            expected_state=RoomState.NEEDS_OWNER_DECISION,
            new_state=RoomState.RUNNING,
        )

    statements = [statement for statement, _ in database.cursor.statements]
    # Fail closed: only the room lock ran; no state change, message or
    # decision row was written.
    assert len(statements) == 1
    assert "for update" in statements[0].lower()


class ScriptedCursor:
    """Serves one queued result set per executed statement, in order."""

    def __init__(self, results):
        self.results = [list(result) for result in results]
        self.statements = []
        self._current: list[tuple] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def execute(self, query, params=None) -> None:
        self.statements.append((query, params))
        if not self.results:
            raise AssertionError("unexpected statement: result queue empty")
        self._current = list(self.results.pop(0))

    async def fetchone(self):
        if self._current:
            return self._current.pop(0)
        return None

    async def fetchall(self):
        rows = list(self._current)
        self._current.clear()
        return rows


class ScriptedDatabase:
    def __init__(self, results) -> None:
        self.cursor = ScriptedCursor(results)
        self.scopes = []

    @asynccontextmanager
    async def tenant_transaction(self, **scope):
        self.scopes.append(scope)
        yield FakeConnection(self.cursor)


@pytest.mark.anyio
async def test_durable_owner_decision_is_readable_through_snapshot() -> None:
    decision_id = UUID(int=6)
    database = ScriptedDatabase(
        results=[
            [("FORMAL_MEETING", "RUNNING")],
            [],
            [],
            [],
            [
                (
                    decision_id,
                    "OWNER_DECISION",
                    "ACCEPTED",
                    "Continue with remaining healthy agents.",
                    "owner-preview",
                )
            ],
            [(0,)],
            [],
            [(0, 0)],
            [],
        ]
    )
    source = PostgresRoomSnapshotSource(database)  # type: ignore[arg-type]

    snapshot = await source.load_snapshot(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        room_id=UUID(int=3),
    )

    assert snapshot.decisions == (
        RoomDecisionSnapshot(
            decision_id=decision_id,
            decision_type="OWNER_DECISION",
            status="ACCEPTED",
            decision="Continue with remaining healthy agents.",
            owner_principal_id="owner-preview",
        ),
    )

    queries = [query for query, _ in database.cursor.statements]
    assert "public.project_room_decisions" in queries[4].lower()

    wire = serialize_room_snapshot(snapshot)
    assert wire["decisions"] == [
        {
            "decision_id": str(decision_id),
            "decision_type": "OWNER_DECISION",
            "status": "ACCEPTED",
            "decision": "Continue with remaining healthy agents.",
            "owner_principal_id": "owner-preview",
        }
    ]
