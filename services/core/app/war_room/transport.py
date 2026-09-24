from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict

from app.db import Database
from app.model_gateway import ModelPolicy, ModelRoute, OpenRouterGateway
from app.settings import Settings

from .auth import DatabaseRoomCommandAuthorizer, DatabaseRoomReadAuthorizer
from .budget import PostgresRoomTurnGuard
from .contracts import (
    AgendaPolicy,
    BudgetSnapshot,
    HaltReason,
    Participant,
    ParticipantRole,
    ParticipantType,
    RoomState,
)
from .event_reader import PostgresRoomEventReader
from .interfaces import (
    BudgetDecision,
    CorrelationContext,
    RoomCommand,
    RoomCommandType,
    RoomEventType,
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
from .remote_auth import (
    AccessAuthenticationError,
    CloudflareAccessVerifier,
    RemoteAccessVerifier,
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


class _PreviewModelPolicyResolver:
    def __init__(self, *, model_id: str, max_output_tokens: int) -> None:
        self._policy = ModelPolicy(
            primary=ModelRoute(model_id=model_id),
            timeout_seconds=25.0,
            max_output_tokens=max_output_tokens,
        )

    async def resolve(self, _model_policy_ref: str) -> ModelPolicy:
        return self._policy


class _PreviewBudgetAuthority:
    """Small preview-only guard backed by the platform UsageEvent ledger."""

    def __init__(
        self,
        *,
        database: Database,
        model_id: str,
        max_output_tokens: int,
        room_token_limit: int,
        room_cost_limit_usd: float,
    ) -> None:
        self._database = database
        self._model_id = model_id
        self._max_output_tokens = max_output_tokens
        self._room_token_limit = room_token_limit
        self._room_cost_limit = Decimal(str(room_cost_limit_usd))

    async def authorize_turn(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
    ) -> BudgetDecision:
        del participant_id
        async with self._database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            cursor = await conn.execute(
                """
                with room_requests as (
                  select distinct request_id
                  from public.project_room_messages
                  where tenant_id = %s
                    and application_id = %s
                    and room_id = %s
                    and request_id is not null
                )
                select
                  coalesce(sum(
                    case when u.event_type = 'ai_tokens' then u.quantity else 0 end
                  ), 0),
                  coalesce(sum(
                    case when u.event_type = 'ai_cost' then u.normalized_cost else 0 end
                  ), 0)
                from public.usage_events u
                join room_requests r on r.request_id = u.request_id
                where u.tenant_id = %s
                  and u.application_id = %s
                """,
                (
                    correlation.tenant_id,
                    correlation.application_id,
                    correlation.room_id,
                    correlation.tenant_id,
                    correlation.application_id,
                ),
            )
            row = await cursor.fetchone()

        used_tokens = int(row[0] or 0) if row else 0
        used_cost = Decimal(str(row[1] or 0)) if row else Decimal("0")
        if used_tokens >= self._room_token_limit or used_cost >= self._room_cost_limit:
            return BudgetDecision(
                allowed=False,
                halt_reason=HaltReason.ROOM_BUDGET_EXHAUSTED,
            )
        return BudgetDecision(
            allowed=True,
            max_output_tokens=self._max_output_tokens,
        )

    async def record_usage(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
        usage,
    ) -> None:
        async with self._database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            participant_cursor = await conn.execute(
                """
                select agent_id
                from public.project_room_participants
                where tenant_id = %s
                  and application_id = %s
                  and room_id = %s
                  and participant_id = %s
                limit 1
                """,
                (
                    correlation.tenant_id,
                    correlation.application_id,
                    correlation.room_id,
                    participant_id,
                ),
            )
            participant_row = await participant_cursor.fetchone()
            agent_id = participant_row[0] if participant_row else None

            token_rows = (
                ("input_tokens", usage.input_tokens, "input"),
                ("output_tokens", usage.output_tokens, "output"),
            )
            for unit, quantity, suffix in token_rows:
                await conn.execute(
                    """
                    insert into public.usage_events (
                      usage_event_id, occurred_at, tenant_id, application_id,
                      request_id, agent_id, event_type, quantity, unit,
                      dedupe_key, source_type, source_id, provider, model, metadata
                    ) values (
                      %s, now(), %s, %s, %s, %s,
                      'ai_tokens', %s, %s, %s,
                      'request', %s, 'openrouter', %s, '{}'::jsonb
                    )
                    on conflict (tenant_id, dedupe_key) do nothing
                    """,
                    (
                        uuid4(),
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.request_id,
                        agent_id,
                        quantity,
                        unit,
                        f"war-room:{correlation.request_id}:{participant_id}:{suffix}",
                        str(correlation.request_id),
                        self._model_id,
                    ),
                )

            if usage.normalized_cost is not None:
                currency = usage.currency or "USD"
                await conn.execute(
                    """
                    insert into public.usage_events (
                      usage_event_id, occurred_at, tenant_id, application_id,
                      request_id, agent_id, event_type, quantity, unit,
                      dedupe_key, source_type, source_id, provider, model,
                      provider_reported_cost, normalized_cost, currency,
                      pricing_rate_version, metadata
                    ) values (
                      %s, now(), %s, %s, %s, %s,
                      'ai_cost', 1, 'request', %s,
                      'request', %s, 'openrouter', %s,
                      %s, %s, %s, 'openrouter-reported', '{}'::jsonb
                    )
                    on conflict (tenant_id, dedupe_key) do nothing
                    """,
                    (
                        uuid4(),
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.request_id,
                        agent_id,
                        f"war-room:{correlation.request_id}:{participant_id}:cost",
                        str(correlation.request_id),
                        self._model_id,
                        usage.normalized_cost,
                        usage.normalized_cost,
                        currency,
                    ),
                )


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


async def _authorize_preview_request(
    request: Request,
    settings: Settings,
    remote_access_verifier: RemoteAccessVerifier | None,
) -> None:
    if not settings.war_room_preview_remote_access_enabled:
        if settings.war_room_preview_local_access_enabled:
            return
        raise HTTPException(
            status_code=403,
            detail="war_room_preview_access_disabled",
        )

    if remote_access_verifier is None:
        raise HTTPException(
            status_code=403,
            detail="war_room_preview_remote_auth_not_configured",
        )

    assertion = request.headers.get("Cf-Access-Jwt-Assertion")
    if assertion is None or not assertion.strip():
        raise HTTPException(
            status_code=403,
            detail="war_room_preview_remote_auth_required",
        )
    try:
        await remote_access_verifier.authenticate(assertion)
    except AccessAuthenticationError as exc:
        raise HTTPException(
            status_code=403,
            detail="war_room_preview_remote_auth_failed",
        ) from exc


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
    remote_access_verifier: RemoteAccessVerifier | None = None,
) -> APIRouter:
    """Development-only Track D transport. No route invokes run_next_turn."""

    router = APIRouter()
    if (
        remote_access_verifier is None
        and settings.war_room_preview_remote_access_enabled
    ):
        remote_access_verifier = CloudflareAccessVerifier(settings)

    read_authorizer = DatabaseRoomReadAuthorizer(database)
    command_authorizer = DatabaseRoomCommandAuthorizer(database)
    snapshot_source = PostgresRoomSnapshotSource(database)
    event_reader = PostgresRoomEventReader(database)

    model_turns_ready = bool(
        settings.war_room_preview_model_turns_enabled
        and settings.openrouter_api_key
        and settings.war_room_preview_model_id.strip()
    )
    if model_turns_ready:
        model_gateway = OpenRouterGateway(
            api_key=settings.openrouter_api_key or "",
            policy_resolver=_PreviewModelPolicyResolver(
                model_id=settings.war_room_preview_model_id,
                max_output_tokens=settings.war_room_preview_max_output_tokens,
            ),
            base_url=settings.openrouter_base_url,
        )
        budget_authority = _PreviewBudgetAuthority(
            database=database,
            model_id=settings.war_room_preview_model_id,
            max_output_tokens=settings.war_room_preview_max_output_tokens,
            room_token_limit=settings.war_room_preview_room_token_limit,
            room_cost_limit_usd=settings.war_room_preview_room_cost_limit_usd,
        )
    else:
        model_gateway = _DisabledModelGateway()
        budget_authority = _DisabledBudgetAuthority()

    orchestrator = WarRoomOrchestrator(
        model_gateway=model_gateway,
        budget_authority=budget_authority,
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
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
        suffix = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(url=f"/war-room/{suffix}", status_code=307)

    @router.get("/war-room/")
    async def war_room_index(request: Request):
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
        trusted_preview_actor(settings)
        return FileResponse(_ASSET_ROOT / "index.html")

    @router.get("/war-room/war-room.css")
    async def war_room_css(request: Request):
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
        trusted_preview_actor(settings)
        return FileResponse(_ASSET_ROOT / "war-room.css", media_type="text/css")

    @router.get("/war-room/war-room.js")
    async def war_room_js(request: Request):
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
        trusted_preview_actor(settings)
        return FileResponse(
            _ASSET_ROOT / "war-room.js",
            media_type="text/javascript",
        )

    @router.get("/war-room/rooms/{room_id}/snapshot")
    async def room_snapshot(room_id: UUID, request: Request):
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
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
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
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

    async def load_turn_participants(
        *,
        correlation: CorrelationContext,
        target_role: ParticipantRole | None,
    ) -> tuple[Participant, ...]:
        async with database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            cursor = await conn.execute(
                """
                select participant_id, participant_type, role, agent_id,
                       model_policy_ref, active
                from public.project_room_participants
                where tenant_id = %s
                  and application_id = %s
                  and room_id = %s
                  and active = true
                  and participant_type = 'AGENT'
                """,
                (
                    correlation.tenant_id,
                    correlation.application_id,
                    correlation.room_id,
                ),
            )
            rows = await cursor.fetchall()

        participants = [
            Participant(
                participant_id=str(row[0]),
                participant_type=ParticipantType(row[1]),
                role=ParticipantRole(row[2]),
                agent_id=row[3],
                model_policy_ref=row[4],
                active=bool(row[5]),
            )
            for row in rows
            if row[3] is not None
        ]
        if target_role is not None:
            participants = [p for p in participants if p.role is target_role]
        else:
            priority = {
                ParticipantRole.CHAIR: 0,
                ParticipantRole.BUILDER: 1,
                ParticipantRole.SECURITY_REVIEWER: 2,
                ParticipantRole.COST_OPS_REVIEWER: 3,
                ParticipantRole.SECRETARY: 4,
                ParticipantRole.ARCHITECT: 5,
                ParticipantRole.INDEPENDENT_AUDITOR: 6,
            }
            participants.sort(key=lambda item: priority.get(item.role, 99))

        return tuple(
            participants[: settings.war_room_preview_max_turns_per_command]
        )

    @router.post("/war-room/rooms/{room_id}/commands")
    async def room_command(
        room_id: UUID,
        payload: RoomCommandPayload,
        request: Request,
    ):
        await _authorize_preview_request(
            request,
            settings,
            remote_access_verifier,
        )
        actor = trusted_preview_actor(settings)
        command = payload.to_contract()
        wants_model_turn = command.command in {
            RoomCommandType.ASK_ROLE,
            RoomCommandType.ASK_ALL,
        }
        if (
            wants_model_turn
            and settings.war_room_preview_model_turns_enabled
            and not model_turns_ready
        ):
            raise HTTPException(
                status_code=503,
                detail="war_room_preview_openrouter_not_configured",
            )
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

        if wants_model_turn and model_turns_ready:
            participants = await load_turn_participants(
                correlation=correlation,
                target_role=(
                    command.target_role
                    if command.command is RoomCommandType.ASK_ROLE
                    else None
                ),
            )
            if participants:
                objective = (
                    command.content_text
                    or (snapshot.agenda[0].objective if snapshot.agenda else None)
                    or "ตอบคำถามของเจ้าของห้องอย่างกระชับ"
                )
                turn_session = RoomSession(
                    mode=snapshot.mode,
                    state=snapshot.state,
                    participants=participants,
                    agenda_policy=AgendaPolicy(
                        automatic_round_limit=1,
                        max_automatic_participants=len(participants),
                    ),
                    owner_decision_pending=False,
                )
                used_tokens = (
                    snapshot.usage.input_tokens + snapshot.usage.output_tokens
                )
                budget = BudgetSnapshot(
                    room_tokens_used=used_tokens,
                    room_token_limit=settings.war_room_preview_room_token_limit,
                    agenda_tokens_used=used_tokens,
                    agenda_token_limit=settings.war_room_preview_room_token_limit,
                    participant_token_limit=(
                        settings.war_room_preview_max_output_tokens * 2
                    ),
                )
                for _ in range(len(participants)):
                    turn_event = await orchestrator.run_next_turn(
                        turn_session,
                        correlation=correlation,
                        budget=budget,
                        agenda_objective=objective,
                    )
                    event = turn_event
                    if turn_event.event_type is not RoomEventType.MESSAGE_APPENDED:
                        break

        return serialize_ordered_event(event)

    return router
