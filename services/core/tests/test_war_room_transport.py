from pathlib import Path
from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from app.db import Database
from app.settings import Settings
from app.war_room import ParticipantType, RoomState
from app.war_room.remote_auth import AccessAuthenticationError
from app.war_room.transport import (
    CorrelationPayload,
    RoomCommandPayload,
    _cursor_from_inputs,
    _validate_command_scope,
    create_war_room_preview_router,
    preview_mount_allowed,
    trusted_preview_actor,
)


TENANT_ID = UUID("11111111-1111-4111-8111-111111111111")
APPLICATION_ID = UUID("22222222-2222-4222-8222-222222222222")
ROOM_ID = UUID("33333333-3333-4333-8333-333333333333")
AGENDA_ID = UUID("44444444-4444-4444-8444-444444444444")
REQUEST_ID = UUID("55555555-5555-4555-8555-555555555555")


def preview_settings(**overrides) -> Settings:
    values = {
        "environment": "test",
        "database_url": "postgresql://example",
        "war_room_preview_enabled": True,
        "war_room_preview_tenant_id": TENANT_ID,
        "war_room_preview_application_id": APPLICATION_ID,
        "war_room_preview_principal_id": "owner-preview",
    }
    values.update(overrides)
    return Settings(**values)


def command_payload(**correlation_overrides) -> RoomCommandPayload:
    correlation = {
        "tenant_id": TENANT_ID,
        "application_id": APPLICATION_ID,
        "room_id": ROOM_ID,
        "agenda_item_id": AGENDA_ID,
        "request_id": REQUEST_ID,
        "trace_id": "0123456789abcdef0123456789abcdef",
    }
    correlation.update(correlation_overrides)
    return RoomCommandPayload(
        command="START",
        correlation=CorrelationPayload(**correlation),
        expected_state=RoomState.READY,
    )


def test_preview_mount_is_explicit_and_non_production() -> None:
    assert preview_mount_allowed(preview_settings()) is True
    assert preview_mount_allowed(
        preview_settings(war_room_preview_enabled=False)
    ) is False
    assert preview_mount_allowed(
        preview_settings(environment="production")
    ) is False


def test_preview_actor_comes_only_from_server_settings() -> None:
    actor = trusted_preview_actor(preview_settings())

    assert actor.tenant_id == TENANT_ID
    assert actor.application_id == APPLICATION_ID
    assert actor.principal_type is ParticipantType.HUMAN
    assert actor.principal_id == "owner-preview"

    with pytest.raises(RuntimeError, match="incomplete"):
        trusted_preview_actor(
            preview_settings(war_room_preview_principal_id=None)
        )


def test_preview_router_has_track_d_routes_and_model_turns_default_off() -> None:
    settings = preview_settings()
    router = create_war_room_preview_router(
        settings=settings,
        database=Database(settings),
    )
    routes = {
        (method, route.path)
        for route in router.routes
        for method in (route.methods or set())
    }

    assert ("GET", "/war-room/") in routes
    assert ("GET", "/war-room/rooms/{room_id}/snapshot") in routes
    assert ("GET", "/war-room/rooms/{room_id}/events") in routes
    assert ("POST", "/war-room/rooms/{room_id}/commands") in routes
    assert not any("turn" in path for _, path in routes)
    assert settings.war_room_preview_model_turns_enabled is False

    source = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "war_room"
        / "transport.py"
    ).read_text()
    assert "war_room_preview_model_turns_enabled" in source


def test_client_correlation_cannot_change_authoritative_scope() -> None:
    actor = trusted_preview_actor(preview_settings())

    _validate_command_scope(
        command=command_payload().to_contract(),
        actor=actor,
        path_room_id=ROOM_ID,
    )

    with pytest.raises(HTTPException) as tenant_error:
        _validate_command_scope(
            command=command_payload(tenant_id=UUID(int=99)).to_contract(),
            actor=actor,
            path_room_id=ROOM_ID,
        )
    assert tenant_error.value.status_code == 403

    with pytest.raises(HTTPException) as room_error:
        _validate_command_scope(
            command=command_payload().to_contract(),
            actor=actor,
            path_room_id=UUID(int=98),
        )
    assert room_error.value.status_code == 403


def test_sse_cursor_prefers_query_and_rejects_invalid_header() -> None:
    assert _cursor_from_inputs(after_sequence=7, last_event_id="3") == 7
    assert _cursor_from_inputs(after_sequence=None, last_event_id="3") == 3
    assert _cursor_from_inputs(after_sequence=None, last_event_id=None) == 0

    with pytest.raises(HTTPException) as invalid:
        _cursor_from_inputs(after_sequence=None, last_event_id="not-an-int")
    assert invalid.value.status_code == 400

class _FakeRemoteVerifier:
    def __init__(self) -> None:
        self.assertions: list[str] = []

    async def authenticate(self, assertion: str) -> str:
        self.assertions.append(assertion)
        if assertion != "valid-access-token":
            raise AccessAuthenticationError("invalid test token")
        return "owner@example.com"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_remote_preview_requires_verified_cloudflare_access_header() -> None:
    settings = preview_settings(
        environment="development",
        war_room_preview_remote_access_enabled=True,
        cloudflare_access_team_domain="https://nippan-test.cloudflareaccess.com",
        cloudflare_access_audience="war-room-preview-audience",
        cloudflare_access_owner_email="owner@example.com",
    )
    verifier = _FakeRemoteVerifier()
    app = FastAPI()
    app.include_router(
        create_war_room_preview_router(
            settings=settings,
            database=Database(settings),
            remote_access_verifier=verifier,
        )
    )

    transport = ASGITransport(
        app=app,
        client=("203.0.113.10", 43123),
    )
    async with AsyncClient(
        transport=transport,
        base_url="https://war-room.example.test",
    ) as client:
        missing = await client.get("/war-room/")
        assert missing.status_code == 403
        assert missing.json()["detail"] == (
            "war_room_preview_remote_auth_required"
        )

        invalid = await client.get(
            "/war-room/",
            headers={"Cf-Access-Jwt-Assertion": "bad-token"},
        )
        assert invalid.status_code == 403
        assert invalid.json()["detail"] == (
            "war_room_preview_remote_auth_failed"
        )

        allowed = await client.get(
            "/war-room/",
            headers={"Cf-Access-Jwt-Assertion": "valid-access-token"},
        )
        assert allowed.status_code == 200
        assert "Nippan AI War Room" in allowed.text

    assert verifier.assertions == ["bad-token", "valid-access-token"]


@pytest.mark.anyio
async def test_remote_preview_stays_loopback_only_until_explicitly_enabled() -> None:
    settings = preview_settings(environment="development")
    app = FastAPI()
    app.include_router(
        create_war_room_preview_router(
            settings=settings,
            database=Database(settings),
        )
    )
    transport = ASGITransport(
        app=app,
        client=("203.0.113.11", 43124),
    )
    async with AsyncClient(
        transport=transport,
        base_url="https://war-room.example.test",
    ) as client:
        response = await client.get("/war-room/")

    assert response.status_code == 403
    assert response.json()["detail"] == "war_room_preview_loopback_only"

