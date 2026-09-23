from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.war_room import (
    CorrelationContext,
    PostgresRoomEventSink,
    RoomEventDraft,
    RoomEventType,
    RoomPersistenceConflict,
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
