import os
from datetime import UTC, datetime
from uuid import UUID

import psycopg
import pytest

from app.db import Database
from app.settings import Settings
from app.war_room import (
    CorrelationContext,
    PostgresRoomEventSink,
    RoomEventDraft,
    RoomEventType,
    RoomState,
)


TENANT_ID = UUID("91111111-1111-4111-8111-111111111111")
APPLICATION_ID = UUID("92222222-2222-4222-8222-222222222222")
REQUEST_ID = UUID("93333333-3333-4333-8333-333333333333")
ROOM_ID = UUID("94444444-4444-4444-8444-444444444444")
AGENDA_ID = UUID("95555555-5555-4555-8555-555555555555")
TRACE_ID = "abcdefabcdefabcdefabcdefabcdefab"


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
        conn.execute(
            "alter role nippan_runtime login password 'runtime_test'"
        )
        conn.execute(
            """
            insert into public.tenants (
              tenant_id, slug, display_name, tenant_type, status
            ) values (%s, 'war-sink-it', 'War Sink IT', 'internal', 'active')
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
              %s, %s, 'war-sink-it', 'War Sink IT', 'test', 'active'
            )
            on conflict (application_id) do nothing
            """,
            (APPLICATION_ID, TENANT_ID),
        )
        conn.execute(
            """
            insert into public.requests (
              request_id, trace_id, tenant_id, application_id,
              environment, request_kind, source, privacy_class,
              current_status, received_at
            ) values (
              %s, %s, %s, %s,
              'development', 'admin_action', 'war-sink-it', 'INTERNAL',
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
              %s, %s, %s, 'war-sink-it', 'War Sink IT',
              'FORMAL_MEETING', 'DRAFT', 'integration-test', 1000
            )
            on conflict (room_id) do nothing
            """,
            (ROOM_ID, TENANT_ID, APPLICATION_ID),
        )
        conn.execute(
            """
            insert into public.project_room_agenda_items (
              agenda_item_id, tenant_id, application_id, room_id,
              sequence, title, objective, token_budget
            ) values (
              %s, %s, %s, %s,
              1, 'Integration agenda', 'Exercise runtime sink', 500
            )
            on conflict (agenda_item_id) do nothing
            """,
            (AGENDA_ID, TENANT_ID, APPLICATION_ID, ROOM_ID),
        )


def _cleanup(admin_dsn: str) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(
            "delete from public.project_room_messages where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_agenda_items where room_id = %s",
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
            "delete from public.applications where application_id = %s",
            (APPLICATION_ID,),
        )
        conn.execute(
            "delete from public.tenants where tenant_id = %s",
            (TENANT_ID,),
        )
        conn.execute("alter role nippan_runtime nologin")


@pytest.mark.anyio
async def test_postgres_room_event_sink_writes_as_runtime_under_rls() -> None:
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
        sink = PostgresRoomEventSink(database)
        correlation = CorrelationContext(
            tenant_id=TENANT_ID,
            application_id=APPLICATION_ID,
            room_id=ROOM_ID,
            agenda_item_id=AGENDA_ID,
            request_id=REQUEST_ID,
            trace_id=TRACE_ID,
        )
        event = await sink.append(
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

        assert event.sequence == 1
        assert event.room_state is RoomState.READY

        with psycopg.connect(admin_dsn) as conn:
            room = conn.execute(
                """
                select state
                from public.project_rooms
                where tenant_id = %s
                  and application_id = %s
                  and room_id = %s
                """,
                (TENANT_ID, APPLICATION_ID, ROOM_ID),
            ).fetchone()
            message = conn.execute(
                """
                select message_type, sequence, request_id, content_text
                from public.project_room_messages
                where tenant_id = %s
                  and application_id = %s
                  and room_id = %s
                """,
                (TENANT_ID, APPLICATION_ID, ROOM_ID),
            ).fetchone()

        assert room == ("READY",)
        assert message is not None
        assert message[0] == "SYSTEM_EVENT"
        assert message[1] == 1
        assert message[2] == REQUEST_ID
        assert '"event_type":"ROOM_STATE_CHANGED"' in message[3]
    finally:
        await database.close()
        _cleanup(admin_dsn)
