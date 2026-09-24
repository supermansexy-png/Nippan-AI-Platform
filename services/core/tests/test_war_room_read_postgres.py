import os
from datetime import UTC, datetime
from uuid import UUID

import psycopg
import pytest

from app.db import Database
from app.settings import Settings
from app.war_room import (
    CorrelationContext,
    DatabaseRoomReadAuthorizer,
    ParticipantType,
    PostgresRoomEventSink,
    PostgresRoomSnapshotSource,
    RoomEventDraft,
    RoomEventType,
    RoomReadKind,
    RoomReadRequest,
    RoomState,
    TrustedActorContext,
    serialize_room_snapshot,
)


TENANT_ID = UUID("a1111111-1111-4111-8111-111111111111")
APPLICATION_ID = UUID("a2222222-2222-4222-8222-222222222222")
AGENT_ID = UUID("a2aaaaaa-2222-4222-8222-222222222222")
REQUEST_ID = UUID("a3333333-3333-4333-8333-333333333333")
ROOM_ID = UUID("a4444444-4444-4444-8444-444444444444")
OWNER_PARTICIPANT_ID = UUID("a5555555-5555-4555-8555-555555555555")
BUILDER_PARTICIPANT_ID = UUID("a6666666-6666-4666-8666-666666666666")
AGENDA_ID = UUID("a7777777-7777-4777-8777-777777777777")
FINDING_ID = UUID("a8888888-8888-4888-8888-888888888888")
DECISION_ID = UUID("a9999999-9999-4999-8999-999999999999")
TRACE_ID = "1234567890abcdef1234567890abcdef"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _dsn(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"{name} is required for PostgreSQL integration test")
    return value


def _seed(admin_dsn: str) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute("alter role nippan_runtime login password 'runtime_test'")
        conn.execute(
            """
            insert into public.tenants (
              tenant_id, slug, display_name, tenant_type, status
            ) values (%s, 'war-read-it', 'War Read IT', 'internal', 'active')
            on conflict (tenant_id) do nothing
            """,
            (TENANT_ID,),
        )
        conn.execute(
            """
            insert into public.applications (
              application_id, tenant_id, slug, display_name,
              application_type, status
            ) values (
              %s, %s, 'war-read-it', 'War Read IT', 'test', 'active'
            )
            on conflict (application_id) do nothing
            """,
            (APPLICATION_ID, TENANT_ID),
        )
        conn.execute(
            """
            insert into public.agents (
              agent_id, tenant_id, application_id, slug,
              display_name, role, status
            ) values (
              %s, %s, %s, 'builder-read', 'Builder Read', 'builder', 'active'
            )
            on conflict (agent_id) do nothing
            """,
            (AGENT_ID, TENANT_ID, APPLICATION_ID),
        )
        conn.execute(
            """
            insert into public.requests (
              request_id, trace_id, tenant_id, application_id,
              environment, request_kind, source, privacy_class,
              current_status, received_at
            ) values (
              %s, %s, %s, %s,
              'development', 'admin_action', 'war-read-it', 'INTERNAL',
              'RUNNING', now()
            )
            on conflict (request_id) do nothing
            """,
            (REQUEST_ID, TRACE_ID, TENANT_ID, APPLICATION_ID),
        )
        conn.execute(
            """
            insert into public.project_rooms (
              room_id, tenant_id, application_id, project_key, title,
              mode, state, created_by_principal_id, token_budget
            ) values (
              %s, %s, %s, 'war-read-it', 'War Read IT',
              'FORMAL_MEETING', 'DRAFT', 'owner-read', 1000
            )
            on conflict (room_id) do nothing
            """,
            (ROOM_ID, TENANT_ID, APPLICATION_ID),
        )
        conn.execute(
            """
            insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, agent_id, participant_type, role,
              display_name, active
            ) values
              (%s, %s, %s, %s, 'HUMAN', 'owner-read', null, 'HUMAN',
               'OWNER', 'Owner Read', true),
              (%s, %s, %s, %s, 'AGENT', 'builder-read', %s, 'AGENT',
               'BUILDER', 'Builder Read', true)
            on conflict (participant_id) do nothing
            """,
            (
                OWNER_PARTICIPANT_ID,
                TENANT_ID,
                APPLICATION_ID,
                ROOM_ID,
                BUILDER_PARTICIPANT_ID,
                TENANT_ID,
                APPLICATION_ID,
                ROOM_ID,
                AGENT_ID,
            ),
        )
        conn.execute(
            """
            insert into public.project_room_agenda_items (
              agenda_item_id, tenant_id, application_id, room_id,
              sequence, title, objective, status, round_limit, token_budget
            ) values (
              %s, %s, %s, %s,
              1, 'Read agenda', 'Exercise snapshot projection',
              'OPEN', 2, 500
            )
            on conflict (agenda_item_id) do nothing
            """,
            (AGENDA_ID, TENANT_ID, APPLICATION_ID, ROOM_ID),
        )
        conn.execute(
            """
            insert into public.project_room_findings (
              finding_id, tenant_id, application_id, room_id,
              agenda_item_id, raised_by_participant_id,
              severity, status, summary
            ) values (
              %s, %s, %s, %s, %s, %s,
              'NOTE', 'OPEN', 'Snapshot finding'
            )
            on conflict (finding_id) do nothing
            """,
            (
                FINDING_ID,
                TENANT_ID,
                APPLICATION_ID,
                ROOM_ID,
                AGENDA_ID,
                OWNER_PARTICIPANT_ID,
            ),
        )
        conn.execute(
            """
            insert into public.project_room_decisions (
              decision_id, tenant_id, application_id, room_id,
              agenda_item_id, decision_type, proposed_by_participant_id,
              decision, status
            ) values (
              %s, %s, %s, %s, %s,
              'PROPOSAL', %s, 'Snapshot decision', 'PROPOSED'
            )
            on conflict (decision_id) do nothing
            """,
            (
                DECISION_ID,
                TENANT_ID,
                APPLICATION_ID,
                ROOM_ID,
                AGENDA_ID,
                OWNER_PARTICIPANT_ID,
            ),
        )


def _cleanup(admin_dsn: str) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(
            "delete from public.project_room_messages where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_findings where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_decisions where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_agenda_items where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_participants where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_rooms where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.requests where request_id = %s",
            (REQUEST_ID,),
        )
        conn.execute(
            "delete from public.agents where agent_id = %s",
            (AGENT_ID,),
        )
        conn.execute(
            "delete from public.applications where application_id = %s",
            (APPLICATION_ID,),
        )
        conn.execute(
            "delete from public.tenants where tenant_id = %s",
            (TENANT_ID,),
        )
        conn.execute("alter role nippan_runtime nologin")


@pytest.mark.anyio
async def test_runtime_read_authorization_and_snapshot_projection() -> None:
    admin_dsn = _dsn("NIPPAN_TEST_POSTGRES_ADMIN_DSN")
    runtime_dsn = _dsn("NIPPAN_TEST_POSTGRES_RUNTIME_DSN")
    _seed(admin_dsn)

    database = Database(
        Settings(
            database_url=runtime_dsn,
            database_pool_min_size=1,
            database_pool_max_size=2,
        )
    )
    await database.open()
    try:
        correlation = CorrelationContext(
            tenant_id=TENANT_ID,
            application_id=APPLICATION_ID,
            room_id=ROOM_ID,
            agenda_item_id=AGENDA_ID,
            request_id=REQUEST_ID,
            trace_id=TRACE_ID,
        )
        sink = PostgresRoomEventSink(database)
        await sink.append(
            RoomEventDraft(
                event_type=RoomEventType.ROOM_STATE_CHANGED,
                correlation=correlation,
                occurred_at=datetime.now(UTC),
                room_state=RoomState.READY,
                payload={"previous_state": RoomState.DRAFT.value},
            ),
            expected_state=RoomState.DRAFT,
            new_state=RoomState.READY,
        )

        read_request = RoomReadRequest(
            tenant_id=TENANT_ID,
            application_id=APPLICATION_ID,
            room_id=ROOM_ID,
            read_kind=RoomReadKind.SNAPSHOT,
        )
        authorizer = DatabaseRoomReadAuthorizer(database)
        allowed = await authorizer.authorize_read(
            request=read_request,
            actor=TrustedActorContext(
                tenant_id=TENANT_ID,
                application_id=APPLICATION_ID,
                principal_type=ParticipantType.AGENT,
                principal_id="builder-read",
            ),
        )
        denied = await authorizer.authorize_read(
            request=read_request,
            actor=TrustedActorContext(
                tenant_id=TENANT_ID,
                application_id=APPLICATION_ID,
                principal_type=ParticipantType.HUMAN,
                principal_id="not-a-participant",
            ),
        )

        assert allowed is True
        assert denied is False

        source = PostgresRoomSnapshotSource(
            database,
            clock=lambda: datetime(2026, 9, 23, 3, 30, tzinfo=UTC),
        )
        snapshot = await source.load_snapshot(
            tenant_id=TENANT_ID,
            application_id=APPLICATION_ID,
            room_id=ROOM_ID,
        )
        wire = serialize_room_snapshot(snapshot)

        assert snapshot.state is RoomState.READY
        assert snapshot.last_sequence == 1
        assert [item.display_name for item in snapshot.participants] == [
            "Owner Read",
            "Builder Read",
        ]
        assert snapshot.agenda[0].title == "Read agenda"
        assert snapshot.findings[0].summary == "Snapshot finding"
        assert snapshot.decisions[0].decision == "Snapshot decision"
        assert snapshot.usage.input_tokens == 0
        assert snapshot.usage.output_tokens == 0
        assert snapshot.usage.normalized_cost is None
        assert len(snapshot.recent_events) == 1
        assert snapshot.recent_events[0].event_type is RoomEventType.ROOM_STATE_CHANGED

        assert wire["tenant_id"] == str(TENANT_ID)
        assert wire["state"] == "READY"
        assert wire["usage"]["normalized_cost"] is None
        assert wire["recent_events"][0]["sequence"] == 1
        assert wire["recent_events"][0]["correlation"]["request_id"] == str(REQUEST_ID)
    finally:
        await database.close()
        _cleanup(admin_dsn)
