from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db import Database
from app.settings import Settings
from app.war_room.preview_auth import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
    PreviewLoginRateLimiter,
    csrf_matches,
    issue_preview_session,
    request_origin_allowed,
    verify_preview_session,
)
from app.war_room.transport import create_war_room_preview_router, preview_mount_allowed


TENANT_ID = UUID("11111111-1111-4111-8111-111111111111")
APPLICATION_ID = UUID("22222222-2222-4222-8222-222222222222")
ROOM_ID = UUID("33333333-3333-4333-8333-333333333333")
ORIGIN = "https://preview.example"
TOKEN = "preview-auth-token-" + ("a" * 48)


def remote_settings(**overrides) -> Settings:
    values = {
        "environment": "development",
        "database_url": "postgresql://example",
        "war_room_preview_enabled": True,
        "war_room_preview_tenant_id": TENANT_ID,
        "war_room_preview_application_id": APPLICATION_ID,
        "war_room_preview_principal_id": "owner-preview",
        "war_room_preview_remote_auth_enabled": True,
        "war_room_preview_remote_auth_token": TOKEN,
        "war_room_preview_remote_origin": ORIGIN,
        "war_room_preview_remote_session_seconds": 3600,
        "war_room_preview_remote_login_failure_delay_seconds": 0.0,
    }
    values.update(overrides)
    return Settings(**values)


def preview_client(settings: Settings) -> TestClient:
    app = FastAPI()
    app.include_router(
        create_war_room_preview_router(
            settings=settings,
            database=Database(settings),
        )
    )
    return TestClient(app, base_url=ORIGIN, follow_redirects=False)


def test_signed_session_expires_and_token_rotation_invalidates_it() -> None:
    settings = remote_settings()
    cookie, session = issue_preview_session(settings, now=1_000)

    verified = verify_preview_session(cookie, settings, now=1_001)
    assert verified is not None
    assert verified.csrf_token == session.csrf_token

    assert verify_preview_session(cookie, settings, now=4_601) is None

    rotated = remote_settings(
        war_room_preview_remote_auth_token="rotated-preview-token-" + ("b" * 48)
    )
    assert verify_preview_session(cookie, rotated, now=1_001) is None


def test_csrf_proof_is_bound_to_signed_session() -> None:
    settings = remote_settings()
    _, session = issue_preview_session(settings, now=1_000)

    assert csrf_matches(
        session=session,
        cookie_value=session.csrf_token,
        header_value=session.csrf_token,
    )
    assert not csrf_matches(
        session=session,
        cookie_value="wrong",
        header_value=session.csrf_token,
    )


def test_remote_origin_must_be_exact_https_origin() -> None:
    settings = remote_settings()

    assert request_origin_allowed(ORIGIN, settings)
    assert request_origin_allowed(f"{ORIGIN}/", settings)
    assert not request_origin_allowed("http://preview.example", settings)
    assert not request_origin_allowed("https://evil.example", settings)
    assert not request_origin_allowed(None, settings)


def test_remote_index_redirects_to_login_until_authenticated() -> None:
    client = preview_client(remote_settings())

    response = client.get(f"/war-room/?room_id={ROOM_ID}")

    assert response.status_code == 307
    assert response.headers["location"] == f"/war-room/login?room_id={ROOM_ID}"


def test_login_requires_origin_and_sets_hardened_cookies() -> None:
    client = preview_client(remote_settings())

    missing_origin = client.post(
        "/war-room/login",
        data={"token": TOKEN, "room_id": str(ROOM_ID)},
    )
    assert missing_origin.status_code == 403
    assert missing_origin.json()["detail"] == "war_room_preview_origin_forbidden"

    bad = client.post(
        "/war-room/login",
        data={"token": "wrong-token-value", "room_id": str(ROOM_ID)},
        headers={"Origin": ORIGIN},
    )
    assert bad.status_code == 401

    good = client.post(
        "/war-room/login",
        data={"token": TOKEN, "room_id": str(ROOM_ID)},
        headers={"Origin": ORIGIN},
    )
    assert good.status_code == 303
    assert good.headers["location"] == f"/war-room/?room_id={ROOM_ID}"

    cookies = good.headers.get_list("set-cookie")
    session_cookie = next(value for value in cookies if SESSION_COOKIE_NAME in value)
    csrf_cookie = next(value for value in cookies if CSRF_COOKIE_NAME in value)

    assert "Secure" in session_cookie
    assert "HttpOnly" in session_cookie
    assert "SameSite=strict" in session_cookie
    assert "Path=/war-room" in session_cookie

    assert "Secure" in csrf_cookie
    assert "HttpOnly" not in csrf_cookie
    assert "SameSite=strict" in csrf_cookie
    assert "Path=/war-room" in csrf_cookie

    index = client.get(f"/war-room/?room_id={ROOM_ID}")
    assert index.status_code == 200


def test_logout_requires_origin_and_double_submit_csrf() -> None:
    client = preview_client(remote_settings())
    login = client.post(
        "/war-room/login",
        data={"token": TOKEN},
        headers={"Origin": ORIGIN},
    )
    assert login.status_code == 303

    missing_csrf = client.post(
        "/war-room/logout",
        headers={"Origin": ORIGIN},
    )
    assert missing_csrf.status_code == 403
    assert missing_csrf.json()["detail"] == "war_room_preview_csrf_forbidden"

    csrf = client.cookies.get(CSRF_COOKIE_NAME)
    assert csrf
    logout = client.post(
        "/war-room/logout",
        headers={
            "Origin": ORIGIN,
            CSRF_HEADER_NAME: csrf,
        },
    )
    assert logout.status_code == 204


def test_remote_auth_misconfiguration_fails_closed() -> None:
    client = preview_client(
        remote_settings(war_room_preview_remote_origin=None)
    )

    response = client.get("/war-room/")

    assert response.status_code == 503
    assert response.json()["detail"] == "war_room_preview_remote_auth_misconfigured"


def test_remote_auth_disabled_preserves_loopback_only_boundary() -> None:
    settings = remote_settings(
        war_room_preview_remote_auth_enabled=False,
        war_room_preview_remote_auth_token=None,
        war_room_preview_remote_origin=None,
    )
    client = preview_client(settings)

    response = client.get("/war-room/")

    assert response.status_code == 403
    assert response.json()["detail"] == "war_room_preview_loopback_only"


def test_production_never_mounts_preview_even_with_remote_auth_enabled() -> None:
    settings = remote_settings(environment="production")

    assert preview_mount_allowed(settings) is False


def test_login_rate_limiter_has_client_and_global_caps() -> None:
    limiter = PreviewLoginRateLimiter(
        window_seconds=10,
        per_client_limit=2,
        global_limit=3,
    )

    assert limiter.allowed("a", now=0)
    limiter.record_failure("a", now=0)
    limiter.record_failure("a", now=1)
    assert not limiter.allowed("a", now=2)

    assert limiter.allowed("b", now=2)
    limiter.record_failure("b", now=2)
    assert not limiter.allowed("c", now=3)

    assert limiter.allowed("a", now=12)
