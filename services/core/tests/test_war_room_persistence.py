import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.war_room import (
    CorrelationContext,
    PostgresRoomEventSink,
    PostgresRoomFailureHistorySource,
    RoomEventDraft,
    RoomEventType,
    RoomMode,
    RoomPersistenceConflict,
    RoomSession,
    RoomSessionFailureReconstructor,
    RoomState,
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
