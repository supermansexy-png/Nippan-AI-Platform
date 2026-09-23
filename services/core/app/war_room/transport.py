from __future__ import annotations

import asyncio
import json
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, urlencode
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)
from pydantic import BaseModel, ConfigDict

from app.db import Database
from app.settings import Settings

from .auth import DatabaseRoomCommandAuthorizer, DatabaseRoomReadAuthorizer
from .budget import PostgresRoomTurnGuard
from .contracts import ParticipantRole, ParticipantType, RoomState
from .event_reader import PostgresRoomEventReader
from .interfaces import (
    CorrelationContext,
    RoomCommand,
    RoomCommandType,
    RoomReadKind,
    RoomReadRequest,
    TrustedActorContext,
)
from .persistence import (
    PostgresRoomEventSink,
    PostgresRoomFailureHistorySource,
    RoomPersistenceConflict,
)
from .preview_auth import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
    PreviewLoginRateLimiter,
    PreviewSession,
    access_token_matches,
    csrf_matches,
    issue_preview_session,
    remote_auth_configured,
    request_origin_allowed,
    verify_preview_session,
)
from .read_model import (
    PostgresRoomSnapshotSource,
    RoomSnapshotError,
    RoomSnapshotNotFound,
    serialize_ordered_event,
    serialize_room_snapshot,
)
from .service import (
    RoomSession,
    StaleRoomCommand,
    UnauthorizedRoomCommand,
    WarRoomOrchestrator,
)
from .state_machine import InvalidRoomTransition


_ASSET_ROOT = Path(__file__).resolve().parents[3] / "control-plane-web" / "war-room"


class CorrelationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID
    application_id: UUID
    room_id: UUID
    agenda_item_id: UUID
    request_id: UUID
    trace_id: str


class RoomCommandPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: RoomCommandType
    correlation: CorrelationPayload
    expected_state: RoomState
    target_participant_id: str | None = None
    target_role: ParticipantRole | None = None
    content_text: str | None = None
    content_reference: str | None = None

    def to_contract(self) -> RoomCommand:
        correlation = self.correlation
        return RoomCommand(
            command=self.command,
            correlation=CorrelationContext(
                tenant_id=correlation.tenant_id,
                application_id=correlation.application_id,
                room_id=correlation.room_id,
                agenda_item_id=correlation.agenda_item_id,
                request_id=correlation.request_id,
                trace_id=correlation.trace_id,
            ),
            expected_state=self.expected_state,
            target_participant_id=self.target_participant_id,
            target_role=self.target_role,
            content_text=self.content_text,
            content_reference=self.content_reference,
        )


class _DisabledModelGateway:
    async def generate_turn(self, _request):
        raise RuntimeError("billable model turns are not exposed by preview transport")


class _DisabledBudgetAuthority:
    async def authorize_turn(self, **_):
        raise RuntimeError("billable budget authorization is not exposed by preview transport")

    async def record_usage(self, **_):
        raise RuntimeError("billable usage recording is not exposed by preview transport")


def preview_mount_allowed(settings: Settings) -> bool:
    return (
        settings.war_room_preview_enabled
        and settings.environment.lower() in {"development", "test"}
    )


def trusted_preview_actor(settings: Settings) -> TrustedActorContext:
    if not preview_mount_allowed(settings):
        raise RuntimeError("War Room preview is disabled outside development/test")

    if (
        settings.war_room_preview_tenant_id is None
        or settings.war_room_preview_application_id is None
        or settings.war_room_preview_principal_id is None
        or not settings.war_room_preview_principal_id.strip()
    ):
        raise RuntimeError("War Room preview trusted actor settings are incomplete")

    return TrustedActorContext(
        tenant_id=settings.war_room_preview_tenant_id,
        application_id=settings.war_room_preview_application_id,
        principal_type=ParticipantType.HUMAN,
        principal_id=settings.war_room_preview_principal_id,
    )


def _client_key(request: Request) -> str:
    client = request.scope.get("client")
    if isinstance(client, tuple) and client:
        return str(client[0])
    return "unknown"


def _safe_room_id(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    try:
        return str(UUID(value.strip()))
    except ValueError:
        return None


def _login_url(request: Request) -> str:
    room_id = _safe_room_id(request.query_params.get("room_id"))
    if room_id is None:
        return "/war-room/login"
    return f"/war-room/login?{urlencode({'room_id': room_id})}"


def _post_login_url(room_id: str | None) -> str:
    safe_room_id = _safe_room_id(room_id)
    if safe_room_id is None:
        return "/war-room/"
    return f"/war-room/?{urlencode({'room_id': safe_room_id})}"


def _remote_session(
    request: Request,
    settings: Settings,
) -> PreviewSession | None:
    if not settings.war_room_preview_remote_auth_enabled:
        return None
    if not remote_auth_configured(settings):
        raise HTTPException(
            status_code=503,
            detail="war_room_preview_remote_auth_misconfigured",
        )
    return verify_preview_session(
        request.cookies.get(SESSION_COOKIE_NAME),
        settings,
    )


def _enforce_preview_access(
    request: Request,
    settings: Settings,
) -> PreviewSession | None:
    if settings.environment.lower() == "test":
        return None

    if settings.war_room_preview_remote_auth_enabled:
        session = _remote_session(request, settings)
        if session is None:
            raise HTTPException(
                status_code=401,
                detail="war_room_preview_remote_auth_required",
            )
        return session

    host = request.client.host if request.client is not None else ""
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=403, detail="war_room_preview_loopback_only")
    return None


def _enforce_remote_origin(request: Request, settings: Settings) -> None:
    if (
        settings.environment.lower() == "test"
        or not settings.war_room_preview_remote_auth_enabled
    ):
        return
    if not request_origin_allowed(request.headers.get("origin"), settings):
        raise HTTPException(
            status_code=403,
            detail="war_room_preview_origin_forbidden",
        )


def _enforce_remote_mutation(
    request: Request,
    settings: Settings,
    session: PreviewSession | None,
) -> None:
    if (
        settings.environment.lower() == "test"
        or not settings.war_room_preview_remote_auth_enabled
    ):
        return
    if session is None:
        raise HTTPException(
            status_code=401,
            detail="war_room_preview_remote_auth_required",
        )
    _enforce_remote_origin(request, settings)
    if not csrf_matches(
        session=session,
        cookie_value=request.cookies.get(CSRF_COOKIE_NAME),
        header_value=request.headers.get(CSRF_HEADER_NAME),
    ):
        raise HTTPException(
            status_code=403,
            detail="war_room_preview_csrf_forbidden",
        )


def _login_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store",
        "Content-Security-Policy": (
            "default-src 'none'; style-src 'unsafe-inline'; "
            "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        ),
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
    }


def _login_page(*, room_id: str | None, error: str | None = None) -> str:
    safe_room = escape(_safe_room_id(room_id) or "", quote=True)
    error_html = (
        f'<p class="error">{escape(error)}</p>'
        if error
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Nippan War Room Preview</title>
  <style>
    :root {{ color-scheme: dark; font-family: system-ui, sans-serif; }}
    body {{ margin:0; min-height:100vh; display:grid; place-items:center; background:#0d1117; }}
    main {{ width:min(92vw,420px); padding:28px; border:1px solid #30363d; border-radius:14px; background:#161b22; }}
    h1 {{ margin-top:0; font-size:1.35rem; }}
    p {{ color:#9da7b3; }}
    .error {{ color:#ff7b72; }}
    label {{ display:block; margin:18px 0 8px; }}
    input,button {{ box-sizing:border-box; width:100%; padding:12px; border-radius:8px; border:1px solid #3d444d; }}
    input {{ background:#0d1117; color:#f0f6fc; }}
    button {{ margin-top:14px; cursor:pointer; font-weight:700; }}
  </style>
</head>
<body>
  <main>
    <h1>Nippan War Room Preview</h1>
    <p>Enter the server-issued preview access token.</p>
    {error_html}
    <form method="post" action="/war-room/login" autocomplete="off">
      <input type="hidden" name="room_id" value="{safe_room}">
      <label for="token">Access token</label>
      <input id="token" name="token" type="password" minlength="32" required autofocus>
      <button type="submit">Open War Room</button>
    </form>
  </main>
</body>
</html>"""


def _validate_command_scope(
    *,
    command: RoomCommand,
    actor: TrustedActorContext,
    path_room_id: UUID,
) -> None:
    correlation = command.correlation
    if (
        correlation.tenant_id != actor.tenant_id
        or correlation.application_id != actor.application_id
        or correlation.room_id != path_room_id
    ):
        raise HTTPException(status_code=403, detail="command_scope_not_authoritative")


def _cursor_from_inputs(
    *,
    after_sequence: int | None,
    last_event_id: str | None,
) -> int:
    if after_sequence is not None:
        return after_sequence
    if last_event_id is None or not last_event_id.strip():
        return 0
    try:
        cursor = int(last_event_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid_last_event_id") from exc
    if cursor < 0:
        raise HTTPException(status_code=400, detail="invalid_last_event_id")
    return cursor


def create_war_room_preview_router(
    *,
    settings: Settings,
    database: Database,
) -> APIRouter:
    """Development-only Track D transport. No route invokes run_next_turn."""

    router = APIRouter()
    login_rate_limiter = PreviewLoginRateLimiter()
    read_authorizer = DatabaseRoomReadAuthorizer(database)
    command_authorizer = DatabaseRoomCommandAuthorizer(database)
    snapshot_source = PostgresRoomSnapshotSource(database)
    event_reader = PostgresRoomEventReader(database)
    orchestrator = WarRoomOrchestrator(
        model_gateway=_DisabledModelGateway(),
        budget_authority=_DisabledBudgetAuthority(),
        command_authorizer=command_authorizer,
        turn_execution_guard=PostgresRoomTurnGuard(database),
        failure_history_source=PostgresRoomFailureHistorySource(database),
        event_sink=PostgresRoomEventSink(database),
    )

    async def authorize_read(
        *,
        actor: TrustedActorContext,
        room_id: UUID,
        read_kind: RoomReadKind,
        after_sequence: int | None = None,
    ) -> RoomReadRequest:
        read_request = RoomReadRequest(
            tenant_id=actor.tenant_id,
            application_id=actor.application_id,
            room_id=room_id,
            read_kind=read_kind,
            after_sequence=after_sequence,
        )
        if not await read_authorizer.authorize_read(
            request=read_request,
            actor=actor,
        ):
            raise HTTPException(status_code=403, detail="room_read_forbidden")
        return read_request

    @router.get("/war-room/login")
    async def war_room_login_page(request: Request):
        if not settings.war_room_preview_remote_auth_enabled:
            raise HTTPException(status_code=404, detail="not_found")
        if not remote_auth_configured(settings):
            raise HTTPException(
                status_code=503,
                detail="war_room_preview_remote_auth_misconfigured",
            )

        if verify_preview_session(
            request.cookies.get(SESSION_COOKIE_NAME),
            settings,
        ) is not None:
            return RedirectResponse(
                url=_post_login_url(request.query_params.get("room_id")),
                status_code=303,
                headers=_login_headers(),
            )

        return HTMLResponse(
            _login_page(room_id=request.query_params.get("room_id")),
            headers=_login_headers(),
        )

    @router.post("/war-room/login")
    async def war_room_login(request: Request):
        if not settings.war_room_preview_remote_auth_enabled:
            raise HTTPException(status_code=404, detail="not_found")
        if not remote_auth_configured(settings):
            raise HTTPException(
                status_code=503,
                detail="war_room_preview_remote_auth_misconfigured",
            )
        _enforce_remote_origin(request, settings)

        content_type = request.headers.get("content-type", "").split(";", 1)[0].strip()
        if content_type != "application/x-www-form-urlencoded":
            raise HTTPException(status_code=415, detail="unsupported_media_type")

        raw_body = await request.body()
        if len(raw_body) > 4096:
            raise HTTPException(status_code=413, detail="login_payload_too_large")
        try:
            fields = parse_qs(
                raw_body.decode("utf-8"),
                keep_blank_values=True,
                strict_parsing=False,
            )
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="invalid_login_payload") from exc

        token = fields.get("token", [""])[0]
        room_id = fields.get("room_id", [""])[0]
        client_key = _client_key(request)

        if not login_rate_limiter.allowed(client_key):
            raise HTTPException(
                status_code=429,
                detail="war_room_preview_login_rate_limited",
            )

        if not access_token_matches(token, settings):
            login_rate_limiter.record_failure(client_key)
            await asyncio.sleep(
                settings.war_room_preview_remote_login_failure_delay_seconds
            )
            return HTMLResponse(
                _login_page(
                    room_id=room_id,
                    error="Invalid access token.",
                ),
                status_code=401,
                headers=_login_headers(),
            )

        login_rate_limiter.record_success(client_key)
        cookie_value, session = issue_preview_session(settings)
        response = RedirectResponse(
            url=_post_login_url(room_id),
            status_code=303,
            headers=_login_headers(),
        )
        response.set_cookie(
            SESSION_COOKIE_NAME,
            cookie_value,
            max_age=settings.war_room_preview_remote_session_seconds,
            secure=True,
            httponly=True,
            samesite="strict",
            path="/war-room",
        )
        response.set_cookie(
            CSRF_COOKIE_NAME,
            session.csrf_token,
            max_age=settings.war_room_preview_remote_session_seconds,
            secure=True,
            httponly=False,
            samesite="strict",
            path="/war-room",
        )
        return response

    @router.post("/war-room/logout")
    async def war_room_logout(request: Request):
        session = _enforce_preview_access(request, settings)
        _enforce_remote_mutation(request, settings, session)
        response = Response(status_code=204, headers={"Cache-Control": "no-store"})
        response.delete_cookie(
            SESSION_COOKIE_NAME,
            path="/war-room",
            secure=True,
            httponly=True,
            samesite="strict",
        )
        response.delete_cookie(
            CSRF_COOKIE_NAME,
            path="/war-room",
            secure=True,
            httponly=False,
            samesite="strict",
        )
        return response

    @router.get("/war-room")
    async def war_room_redirect(request: Request):
        if (
            settings.environment.lower() != "test"
            and settings.war_room_preview_remote_auth_enabled
        ):
            if not remote_auth_configured(settings):
                raise HTTPException(
                    status_code=503,
                    detail="war_room_preview_remote_auth_misconfigured",
                )
            if verify_preview_session(
                request.cookies.get(SESSION_COOKIE_NAME),
                settings,
            ) is None:
                return RedirectResponse(url=_login_url(request), status_code=307)
        else:
            _enforce_preview_access(request, settings)

        suffix = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(url=f"/war-room/{suffix}", status_code=307)

    @router.get("/war-room/")
    async def war_room_index(request: Request):
        if (
            settings.environment.lower() != "test"
            and settings.war_room_preview_remote_auth_enabled
        ):
            if not remote_auth_configured(settings):
                raise HTTPException(
                    status_code=503,
                    detail="war_room_preview_remote_auth_misconfigured",
                )
            if verify_preview_session(
                request.cookies.get(SESSION_COOKIE_NAME),
                settings,
            ) is None:
                return RedirectResponse(url=_login_url(request), status_code=307)

        _enforce_preview_access(request, settings)
        trusted_preview_actor(settings)
        return FileResponse(_ASSET_ROOT / "index.html")

    @router.get("/war-room/war-room.css")
    async def war_room_css(request: Request):
        _enforce_preview_access(request, settings)
        trusted_preview_actor(settings)
        return FileResponse(_ASSET_ROOT / "war-room.css", media_type="text/css")

    @router.get("/war-room/war-room.js")
    async def war_room_js(request: Request):
        _enforce_preview_access(request, settings)
        trusted_preview_actor(settings)
        return FileResponse(
            _ASSET_ROOT / "war-room.js",
            media_type="text/javascript",
        )

    @router.get("/war-room/rooms/{room_id}/snapshot")
    async def room_snapshot(room_id: UUID, request: Request):
        _enforce_preview_access(request, settings)
        actor = trusted_preview_actor(settings)
        await authorize_read(
            actor=actor,
            room_id=room_id,
            read_kind=RoomReadKind.SNAPSHOT,
        )
        try:
            snapshot = await snapshot_source.load_snapshot(
                tenant_id=actor.tenant_id,
                application_id=actor.application_id,
                room_id=room_id,
            )
        except RoomSnapshotNotFound as exc:
            raise HTTPException(status_code=404, detail="room_not_found") from exc
        except RoomSnapshotError as exc:
            raise HTTPException(status_code=409, detail="snapshot_projection_failed") from exc
        return serialize_room_snapshot(snapshot)

    @router.get("/war-room/rooms/{room_id}/events")
    async def room_events(
        room_id: UUID,
        request: Request,
        after_sequence: int | None = Query(default=None, ge=0),
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ):
        _enforce_preview_access(request, settings)
        _enforce_remote_origin(request, settings)
        actor = trusted_preview_actor(settings)
        cursor = _cursor_from_inputs(
            after_sequence=after_sequence,
            last_event_id=last_event_id,
        )
        await authorize_read(
            actor=actor,
            room_id=room_id,
            read_kind=RoomReadKind.EVENT_STREAM,
            after_sequence=cursor,
        )

        async def stream():
            current = cursor
            idle_seconds = 0.0
            while True:
                if await request.is_disconnected():
                    return

                read_request = RoomReadRequest(
                    tenant_id=actor.tenant_id,
                    application_id=actor.application_id,
                    room_id=room_id,
                    read_kind=RoomReadKind.EVENT_STREAM,
                    after_sequence=current,
                )
                if not await read_authorizer.authorize_read(
                    request=read_request,
                    actor=actor,
                ):
                    return

                events = await event_reader.load_after(
                    tenant_id=actor.tenant_id,
                    application_id=actor.application_id,
                    room_id=room_id,
                    after_sequence=current,
                )
                if events:
                    idle_seconds = 0.0
                    for event in events:
                        current = event.sequence
                        payload = json.dumps(
                            serialize_ordered_event(event),
                            separators=(",", ":"),
                            sort_keys=True,
                        )
                        yield (
                            f"id: {event.sequence}\n"
                            f"event: {event.event_type.value}\n"
                            f"data: {payload}\n\n"
                        )
                    continue

                await asyncio.sleep(settings.war_room_preview_poll_seconds)
                idle_seconds += settings.war_room_preview_poll_seconds
                if idle_seconds >= 15.0:
                    idle_seconds = 0.0
                    yield ": keepalive\n\n"

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @router.post("/war-room/rooms/{room_id}/commands")
    async def room_command(
        room_id: UUID,
        payload: RoomCommandPayload,
        request: Request,
    ):
        session = _enforce_preview_access(request, settings)
        _enforce_remote_mutation(request, settings, session)
        actor = trusted_preview_actor(settings)
        command = payload.to_contract()
        _validate_command_scope(
            command=command,
            actor=actor,
            path_room_id=room_id,
        )

        correlation = command.correlation
        try:
            async with database.tenant_transaction(
                tenant_id=actor.tenant_id,
                application_id=actor.application_id,
                request_id=correlation.request_id,
            ) as conn:
                request_cursor = await conn.execute(
                    """
                    insert into public.requests (
                      request_id,
                      trace_id,
                      tenant_id,
                      application_id,
                      environment,
                      request_kind,
                      source,
                      privacy_class,
                      current_status,
                      received_at
                    ) values (
                      %s, %s, %s, %s,
                      'development', 'admin_action', 'war-room-preview',
                      'INTERNAL', 'RUNNING', now()
                    )
                    on conflict (request_id) do nothing
                    returning request_id
                    """,
                    (
                        correlation.request_id,
                        correlation.trace_id,
                        actor.tenant_id,
                        actor.application_id,
                    ),
                )
                if await request_cursor.fetchone() is None:
                    raise HTTPException(
                        status_code=409,
                        detail="request_id_already_used",
                    )

                snapshot = await snapshot_source.load_snapshot(
                    tenant_id=actor.tenant_id,
                    application_id=actor.application_id,
                    room_id=room_id,
                )
                session = RoomSession(
                    mode=snapshot.mode,
                    state=snapshot.state,
                    participants=(),
                    owner_decision_pending=(
                        snapshot.state is RoomState.NEEDS_OWNER_DECISION
                    ),
                )
                event = await orchestrator.apply_command(
                    session,
                    command,
                    actor=actor,
                )
                await conn.execute(
                    """
                    update public.requests
                    set current_status = 'SUCCEEDED',
                        completed_at = now()
                    where tenant_id = %s
                      and application_id = %s
                      and request_id = %s
                    """,
                    (
                        actor.tenant_id,
                        actor.application_id,
                        correlation.request_id,
                    ),
                )
        except UnauthorizedRoomCommand as exc:
            raise HTTPException(status_code=403, detail="owner_command_forbidden") from exc
        except (StaleRoomCommand, RoomPersistenceConflict, InvalidRoomTransition) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except RoomSnapshotNotFound as exc:
            raise HTTPException(status_code=404, detail="room_not_found") from exc
        except RoomSnapshotError as exc:
            raise HTTPException(status_code=409, detail="snapshot_projection_failed") from exc

        return serialize_ordered_event(event)

    return router
