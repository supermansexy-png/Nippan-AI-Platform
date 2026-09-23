from contextlib import asynccontextmanager
from uuid import UUID

import pytest

from app.war_room import (
    CorrelationContext,
    DatabaseRoomCommandAuthorizer,
    DatabaseRoomReadAuthorizer,
    ParticipantType,
    RoomReadKind,
    RoomReadRequest,
    RoomCommand,
    RoomCommandType,
    RoomState,
    TrustedActorContext,
)


class FakeCursor:
    def __init__(self, result: bool) -> None:
        self.result = result
        self.query = None
        self.params = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def execute(self, query, params) -> None:
        self.query = query
        self.params = params

    async def fetchone(self):
        return (self.result,)


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self):
        return self._cursor


class FakeDatabase:
    def __init__(self, result: bool = True, *, fail: bool = False) -> None:
        self.cursor = FakeCursor(result)
        self.calls = []
        self.fail = fail

    @asynccontextmanager
    async def tenant_transaction(self, **scope):
        self.calls.append(scope)
        if self.fail:
            raise RuntimeError("database unavailable")
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


def command() -> RoomCommand:
    return RoomCommand(
        command=RoomCommandType.START,
        correlation=correlation(),
        expected_state=RoomState.READY,
    )


@pytest.mark.anyio
async def test_scope_mismatch_denies_before_database_query() -> None:
    database = FakeDatabase()
    authorizer = DatabaseRoomCommandAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize(
        command=command(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=99),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="owner-1",
        ),
    )

    assert allowed is False
    assert database.calls == []


@pytest.mark.anyio
async def test_active_owner_lookup_binds_full_room_and_principal_scope() -> None:
    database = FakeDatabase(result=True)
    authorizer = DatabaseRoomCommandAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize(
        command=command(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="owner-1",
        ),
    )

    assert allowed is True
    assert database.calls == [
        {
            "tenant_id": UUID(int=1),
            "application_id": UUID(int=2),
            "request_id": UUID(int=5),
        }
    ]
    assert database.cursor.params == (
        UUID(int=1),
        UUID(int=2),
        UUID(int=3),
        "HUMAN",
        "owner-1",
    )


@pytest.mark.anyio
async def test_non_owner_lookup_fails_closed() -> None:
    database = FakeDatabase(result=False)
    authorizer = DatabaseRoomCommandAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize(
        command=command(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="member-not-owner",
        ),
    )

    assert allowed is False


@pytest.mark.anyio
async def test_agent_principal_cannot_authorize_owner_command() -> None:
    database = FakeDatabase(result=True)
    authorizer = DatabaseRoomCommandAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize(
        command=command(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.AGENT,
            principal_id="agent-owner-row",
        ),
    )

    assert allowed is False
    assert database.calls == []



def read_request(
    *,
    tenant_id: UUID = UUID(int=1),
    application_id: UUID = UUID(int=2),
) -> RoomReadRequest:
    return RoomReadRequest(
        tenant_id=tenant_id,
        application_id=application_id,
        room_id=UUID(int=3),
        read_kind=RoomReadKind.SNAPSHOT,
    )


@pytest.mark.anyio
async def test_read_scope_mismatch_denies_before_database_query() -> None:
    database = FakeDatabase()
    authorizer = DatabaseRoomReadAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize_read(
        request=read_request(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=99),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="member-1",
        ),
    )

    assert allowed is False
    assert database.calls == []


@pytest.mark.anyio
async def test_active_non_owner_participant_may_read_room() -> None:
    database = FakeDatabase(result=True)
    authorizer = DatabaseRoomReadAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize_read(
        request=read_request(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.AGENT,
            principal_id="security-reviewer",
        ),
    )

    assert allowed is True
    assert database.calls == [
        {
            "tenant_id": UUID(int=1),
            "application_id": UUID(int=2),
        }
    ]
    assert database.cursor.params == (
        UUID(int=1),
        UUID(int=2),
        UUID(int=3),
        "AGENT",
        "security-reviewer",
    )
    assert "role = 'OWNER'" not in database.cursor.query


@pytest.mark.anyio
async def test_inactive_or_missing_participant_read_fails_closed() -> None:
    database = FakeDatabase(result=False)
    authorizer = DatabaseRoomReadAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize_read(
        request=read_request(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="not-active",
        ),
    )

    assert allowed is False


@pytest.mark.anyio
async def test_database_failure_on_read_authorization_fails_closed() -> None:
    database = FakeDatabase(fail=True)
    authorizer = DatabaseRoomReadAuthorizer(database)  # type: ignore[arg-type]

    allowed = await authorizer.authorize_read(
        request=read_request(),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="member-1",
        ),
    )

    assert allowed is False
