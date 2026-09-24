import os
from uuid import UUID

import psycopg
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.db import Database
from app.settings import Settings
from app.war_room.event_reader import PostgresRoomEventReader
from app.war_room.transport import create_war_room_preview_router


TENANT_ID = UUID("b1111111-1111-4111-8111-111111111111")
APPLICATION_ID = UUID("b2222222-2222-4222-8222-222222222222")
ROOM_ID = UUID("b3333333-3333-4333-8333-333333333333")
OWNER_PARTICIPANT_ID = UUID("b4444444-4444-4444-8444-444444444444")
AGENDA_ID = UUID("b5555555-5555-4555-8555-555555555555")
OWNER_PRINCIPAL_ID = "owner-http-preview"

REQUEST_IDS = (
    UUID("b6000000-0000-4000-8000-000000000001"),
    UUID("b6000000-0000-4000-8000-000000000002"),
    UUID("b6000000-0000-4000-8000-000000000003"),
    UUID("b6000000-0000-4000-8000-000000000004"),
    UUID("b6000000-0000-4000-8000-000000000005"),
    UUID("b6000000-0000-4000-8000-000000000006"),
)
TRACE_IDS = (
    "10000000000000000000000000000001",
    "10000000000000000000000000000002",
    "10000000000000000000000000000003",
    "10000000000000000000000000000004",
    "10000000000000000000000000000005",
    "10000000000000000000000000000006",
)


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
            ) values (
              %s, 'war-http-preview-it', 'War HTTP Preview IT',
              'internal', 'active'
            )
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
              %s, %s, 'war-http-preview-it', 'War HTTP Preview IT',
              'test', 'active'
            )
            on conflict (application_id) do nothing
            """,
            (APPLICATION_ID, TENANT_ID),
        )
        conn.execute(
            """
            insert into public.project_rooms (
              room_id, tenant_id, application_id, project_key, title,
              mode, state, created_by_principal_id, token_budget
            ) values (
              %s, %s, %s, 'war-http-preview-it', 'War HTTP Preview IT',
              'FORMAL_MEETING', 'DRAFT', %s, 1000
            )
            on conflict (room_id) do nothing
            """,
            (ROOM_ID, TENANT_ID, APPLICATION_ID, OWNER_PRINCIPAL_ID),
        )
        conn.execute(
            """
            insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, agent_id, participant_type,
              role, display_name, active
            ) values (
              %s, %s, %s, %s,
              'HUMAN', %s, null, 'HUMAN',
              'OWNER', 'Preview Owner', true
            )
            on conflict (participant_id) do nothing
            """,
            (
                OWNER_PARTICIPANT_ID,
                TENANT_ID,
                APPLICATION_ID,
                ROOM_ID,
                OWNER_PRINCIPAL_ID,
            ),
        )
        conn.execute(
            """
            insert into public.project_room_agenda_items (
              agenda_item_id, tenant_id, application_id, room_id,
              sequence, title, objective, status, round_limit, token_budget
            ) values (
              %s, %s, %s, %s,
              1, 'Preview agenda', 'Exercise Track D HTTP transport',
              'OPEN', 2, 500
            )
            on conflict (agenda_item_id) do nothing
            """,
            (AGENDA_ID, TENANT_ID, APPLICATION_ID, ROOM_ID),
        )


def _cleanup(admin_dsn: str) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        request_ids = list(REQUEST_IDS)
        conn.execute(
            "delete from public.usage_events where request_id = any(%s)",
            (request_ids,),
        )
        conn.execute(
            "delete from public.ai_calls where request_id = any(%s)",
            (request_ids,),
        )
        conn.execute(
            "delete from public.project_room_messages where room_id = %s",
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
            "delete from public.requests where request_id = any(%s)",
            (request_ids,),
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


def _command_payload(
    *,
    command: str,
    expected_state: str,
    request_id: UUID,
    trace_id: str,
    content_text: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "command": command,
        "correlation": {
            "tenant_id": str(TENANT_ID),
            "application_id": str(APPLICATION_ID),
            "room_id": str(ROOM_ID),
            "agenda_item_id": str(AGENDA_ID),
            "request_id": str(request_id),
            "trace_id": trace_id,
        },
        "expected_state": expected_state,
    }
    if content_text is not None:
        payload["content_text"] = content_text
    return payload


@pytest.mark.anyio
async def test_track_d_http_preview_persists_owner_commands_without_provider_spend() -> None:
    admin_dsn = _dsn("NIPPAN_TEST_POSTGRES_ADMIN_DSN")
    runtime_dsn = _dsn("NIPPAN_TEST_POSTGRES_RUNTIME_DSN")
    _seed(admin_dsn)

    settings = Settings(
        environment="test",
        database_url=runtime_dsn,
        database_pool_min_size=1,
        database_pool_max_size=2,
        war_room_preview_enabled=True,
        war_room_preview_local_access_enabled=True,
        war_room_preview_tenant_id=TENANT_ID,
        war_room_preview_application_id=APPLICATION_ID,
        war_room_preview_principal_id=OWNER_PRINCIPAL_ID,
        war_room_preview_poll_seconds=0.1,
    )
    database = Database(settings)
    app = FastAPI()
    app.include_router(
        create_war_room_preview_router(
            settings=settings,
            database=database,
        )
    )

    await database.open()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            ui = await client.get("/war-room/")
            assert ui.status_code == 200
            assert "Nippan AI War Room" in ui.text

            initial = await client.get(
                f"/war-room/rooms/{ROOM_ID}/snapshot"
            )
            assert initial.status_code == 200
            initial_body = initial.json()
            assert initial_body["state"] == "DRAFT"
            assert initial_body["last_sequence"] == 0
            assert initial_body["participants"][0]["display_name"] == "Preview Owner"

            commands = (
                ("PREPARE", "DRAFT", None),
                ("START", "READY", None),
                ("ASK_ALL", "RUNNING", "Status check from owner"),
                ("PAUSE", "RUNNING", None),
                ("RESUME", "PAUSED", None),
                ("STOP", "RUNNING", None),
            )
            responses = []
            for index, (command, expected_state, content_text) in enumerate(commands):
                response = await client.post(
                    f"/war-room/rooms/{ROOM_ID}/commands",
                    json=_command_payload(
                        command=command,
                        expected_state=expected_state,
                        request_id=REQUEST_IDS[index],
                        trace_id=TRACE_IDS[index],
                        content_text=content_text,
                    ),
                )
                assert response.status_code == 200, response.text
                responses.append(response.json())

            assert [item["sequence"] for item in responses] == [1, 2, 3, 4, 5, 6]
            assert responses[2]["event_type"] == "MESSAGE_APPENDED"
            assert responses[2]["message_type"] == "OWNER_MESSAGE"
            assert responses[2]["payload"]["content_text"] == "Status check from owner"

            final = await client.get(
                f"/war-room/rooms/{ROOM_ID}/snapshot"
            )
            assert final.status_code == 200
            final_body = final.json()
            assert final_body["state"] == "STOPPED"
            assert final_body["last_sequence"] == 6
            assert [event["sequence"] for event in final_body["recent_events"]] == [
                1,
                2,
                3,
                4,
                5,
                6,
            ]

        replay = await PostgresRoomEventReader(database).load_after(
            tenant_id=TENANT_ID,
            application_id=APPLICATION_ID,
            room_id=ROOM_ID,
            after_sequence=2,
        )
        assert [event.sequence for event in replay] == [3, 4, 5, 6]

        with psycopg.connect(admin_dsn) as conn:
            requests = conn.execute(
                """
                select request_id, current_status, completed_at
                from public.requests
                where request_id = any(%s)
                order by request_id
                """,
                (list(REQUEST_IDS),),
            ).fetchall()
            ai_call_count = conn.execute(
                "select count(*) from public.ai_calls where request_id = any(%s)",
                (list(REQUEST_IDS),),
            ).fetchone()
            usage_count = conn.execute(
                "select count(*) from public.usage_events where request_id = any(%s)",
                (list(REQUEST_IDS),),
            ).fetchone()

        assert len(requests) == 6
        assert all(row[1] == "SUCCEEDED" and row[2] is not None for row in requests)
        assert ai_call_count == (0,)
        assert usage_count == (0,)
    finally:
        await database.close()
        _cleanup(admin_dsn)
