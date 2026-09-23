from __future__ import annotations

import asyncio
import json
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
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


def _enforce_local_preview(request: Request, settings: Settings) -> None:
    if settings.environment.lower() == "test":
        return
    host = request.client.host if request.client is not None else ""
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=403, detail="war_room_preview_loopback_only")


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

    @router.get("/war-room")
    async def war_room_redirect(request: Request):
        _enforce_local_preview(request, settings)
        suffix = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(url=f"/war-room/{suffix}", status_code=307)

    @router.get("/war-room/")
    async def war_room_index(request: Request):
        _enforce_local_preview(request, settings)
        trusted_preview_actor(settings)
        return FileResponse(_ASSET_ROOT / "index.html")

    @router.get("/war-room/war-room.css")
    async def war_room_css(request: Request):
        _enforce_local_preview(request, settings)
        trusted_preview_actor(settings)
        return FileResponse(_ASSET_ROOT / "war-room.css", media_type="text/css")

    @router.get("/war-room/war-room.js")
    async def war_room_js(request: Request):
        _enforce_local_preview(request, settings)
        trusted_preview_actor(settings)
        return FileResponse(
            _ASSET_ROOT / "war-room.js",
            media_type="text/javascript",
        )

    @router.get("/war-room/rooms/{room_id}/snapshot")
    async def room_snapshot(room_id: UUID, request: Request):
        _enforce_local_preview(request, settings)
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
        _enforce_local_preview(request, settings)
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
        _enforce_local_preview(request, settings)
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
