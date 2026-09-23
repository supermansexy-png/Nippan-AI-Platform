from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Callable
from .contracts import (
    AgendaPolicy,
    BudgetSnapshot,
    HaltReason,
    MessageType,
    Participant,
    ParticipantRole,
    RoomMode,
    RoomState,
)
from .interfaces import (
    BudgetAuthority,
    CorrelationContext,
    ModelGateway,
    ModelTurnRequest,
    OrderedRoomEvent,
    RoomCommand,
    RoomCommandAuthorizer,
    RoomCommandType,
    RoomEventDraft,
    RoomEventSink,
    RoomEventType,
    RoomFailureHistorySource,
    TrustedActorContext,
    TurnExecutionGuard,
    TurnFailureKind,
)
from .orchestration import DeterministicTurnScheduler, TurnRequest
from .state_machine import RoomAction, transition_room_state


class StaleRoomCommand(ValueError):
    """Raised when a command was prepared against an obsolete room state."""


class UnauthorizedRoomCommand(PermissionError):
    """Raised when the trusted actor is not the active owner for the room scope."""


@dataclass(slots=True)
class RoomSession:
    mode: RoomMode
    state: RoomState
    participants: tuple[Participant, ...]
    agenda_policy: AgendaPolicy = field(default_factory=AgendaPolicy)
    round_number: int = 1
    completed_participant_ids: set[str] = field(default_factory=set)
    failed_participant_ids: set[str] = field(default_factory=set)
    owner_decision_pending: bool = False
    last_speaker_id: str | None = None


_LIFECYCLE_ACTIONS = {
    RoomCommandType.PREPARE: RoomAction.PREPARE,
    RoomCommandType.START: RoomAction.START,
    RoomCommandType.PAUSE: RoomAction.PAUSE,
    RoomCommandType.RESUME: RoomAction.RESUME,
    RoomCommandType.STOP: RoomAction.STOP,
    RoomCommandType.REQUEST_OWNER_DECISION: RoomAction.REQUEST_OWNER_DECISION,
    RoomCommandType.SUBMIT_OWNER_DECISION: RoomAction.RESOLVE_OWNER_DECISION,
    RoomCommandType.BEGIN_SUMMARY: RoomAction.BEGIN_SUMMARY,
    RoomCommandType.CLOSE: RoomAction.CLOSE,
}


class WarRoomOrchestrator:
    def __init__(
        self,
        *,
        model_gateway: ModelGateway,
        budget_authority: BudgetAuthority,
        command_authorizer: RoomCommandAuthorizer,
        turn_execution_guard: TurnExecutionGuard,
        failure_history_source: RoomFailureHistorySource,
        event_sink: RoomEventSink,
        scheduler: DeterministicTurnScheduler | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._model_gateway = model_gateway
        self._budget_authority = budget_authority
        self._command_authorizer = command_authorizer
        self._turn_execution_guard = turn_execution_guard
        self._failure_history_source = failure_history_source
        self._event_sink = event_sink
        self._scheduler = scheduler or DeterministicTurnScheduler()
        self._clock = clock or (lambda: datetime.now(UTC))

    async def apply_command(
        self,
        session: RoomSession,
        command: RoomCommand,
        *,
        actor: TrustedActorContext,
    ) -> OrderedRoomEvent:
        authorized = await self._command_authorizer.authorize(
            command=command,
            actor=actor,
        )
        if not authorized:
            raise UnauthorizedRoomCommand(
                "trusted actor is not authorized as active owner for this room scope"
            )

        async with self._turn_execution_guard.hold(
            correlation=command.correlation,
        ):
            if command.expected_state is not session.state:
                raise StaleRoomCommand(
                    f"expected {command.expected_state.value}, "
                    f"memory={session.state.value}"
                )

            if command.command in {
                RoomCommandType.ASK_ROLE,
                RoomCommandType.ASK_ALL,
            }:
                return await self._emit(
                    session,
                    command.correlation,
                    RoomEventType.MESSAGE_APPENDED,
                    message_type=MessageType.OWNER_MESSAGE,
                    payload={
                        "content_text": command.content_text,
                        "content_reference": command.content_reference,
                        "target_role": (
                            command.target_role.value
                            if command.target_role
                            else None
                        ),
                    },
                    expected_state=command.expected_state,
                )

            action = _LIFECYCLE_ACTIONS[command.command]
            previous_state = command.expected_state
            new_state = transition_room_state(previous_state, action)
            event = await self._emit(
                session,
                command.correlation,
                RoomEventType.ROOM_STATE_CHANGED,
                room_state=new_state,
                payload={"previous_state": previous_state.value},
                expected_state=previous_state,
                new_state=new_state,
            )
            session.state = new_state
            session.owner_decision_pending = (
                new_state is RoomState.NEEDS_OWNER_DECISION
            )
            return event

    async def run_next_turn(
        self,
        session: RoomSession,
        *,
        correlation: CorrelationContext,
        budget: BudgetSnapshot,
        agenda_objective: str,
        context_references: tuple[str, ...] = (),
        prior_round_synthesis: str | None = None,
    ) -> OrderedRoomEvent:
        async with self._turn_execution_guard.hold(
            correlation=correlation,
        ) as durable_state:
            durable_failures = (
                await self._failure_history_source.load_failed_participant_ids(
                    correlation=correlation,
                )
            )
            session.failed_participant_ids.update(durable_failures)

            if durable_state is not RoomState.RUNNING:
                event = await self._emit(
                    session,
                    correlation,
                    RoomEventType.SCHEDULER_HALTED,
                    room_state=durable_state,
                    halt_reason=HaltReason.STATE_NOT_RUNNING,
                    payload={"round_number": session.round_number},
                    expected_state=durable_state,
                )
                session.state = durable_state
                session.owner_decision_pending = (
                    durable_state is RoomState.NEEDS_OWNER_DECISION
                )
                return event

            session.state = durable_state
            return await self._run_next_turn_locked(
                session,
                correlation=correlation,
                budget=budget,
                agenda_objective=agenda_objective,
                context_references=context_references,
                prior_round_synthesis=prior_round_synthesis,
            )

    async def _run_next_turn_locked(
        self,
        session: RoomSession,
        *,
        correlation: CorrelationContext,
        budget: BudgetSnapshot,
        agenda_objective: str,
        context_references: tuple[str, ...] = (),
        prior_round_synthesis: str | None = None,
    ) -> OrderedRoomEvent:
        decision = self._scheduler.choose_next(
            TurnRequest(
                room_state=session.state,
                mode=session.mode,
                round_number=session.round_number,
                participants=session.participants,
                completed_participant_ids=frozenset(
                    session.completed_participant_ids
                ),
                budget=budget,
                failed_participant_ids=frozenset(
                    session.failed_participant_ids
                ),
                agenda_policy=session.agenda_policy,
                triggered_by_participant_id=session.last_speaker_id,
                owner_decision_pending=session.owner_decision_pending,
            )
        )

        if decision.participant_id is None:
            return await self._handle_scheduler_halt(
                session,
                correlation,
                decision.halt_reason or HaltReason.NO_ELIGIBLE_PARTICIPANT,
            )

        participant = next(
            item
            for item in session.participants
            if item.participant_id == decision.participant_id
        )
        authorization = await self._budget_authority.authorize_turn(
            correlation=correlation,
            participant_id=participant.participant_id,
        )
        if not authorization.allowed:
            return await self._hard_stop_for_budget(
                session,
                correlation,
                authorization.halt_reason or HaltReason.ROOM_BUDGET_EXHAUSTED,
            )

        await self._emit(
            session,
            correlation,
            RoomEventType.TURN_SCHEDULED,
            participant_id=participant.participant_id,
            payload={"round_number": session.round_number},
            expected_state=RoomState.RUNNING,
        )

        try:
            result = await self._model_gateway.generate_turn(
                ModelTurnRequest(
                    correlation=correlation,
                    participant_id=participant.participant_id,
                    role=participant.role,
                    model_policy_ref=participant.model_policy_ref or "",
                    agenda_objective=agenda_objective,
                    max_output_tokens=authorization.max_output_tokens or 1,
                    context_references=context_references,
                    prior_round_synthesis=prior_round_synthesis,
                )
            )
        except TimeoutError:
            return await self._turn_failed(
                session,
                correlation,
                participant.participant_id,
                TurnFailureKind.TIMEOUT,
            )
        except Exception:
            return await self._turn_failed(
                session,
                correlation,
                participant.participant_id,
                TurnFailureKind.PROVIDER_UNAVAILABLE,
            )

        await self._budget_authority.record_usage(
            correlation=correlation,
            participant_id=participant.participant_id,
            usage=result.usage,
        )

        message_type = (
            MessageType.CHAIR_SYNTHESIS
            if participant.role is ParticipantRole.CHAIR
            else MessageType.AGENT_MESSAGE
        )
        event = await self._emit(
            session,
            correlation,
            RoomEventType.MESSAGE_APPENDED,
            participant_id=participant.participant_id,
            message_type=message_type,
            payload={
                "content_text": result.content_text,
                "content_reference": result.content_reference,
                "round_number": session.round_number,
                "usage_tokens": result.usage.total_tokens,
            },
            expected_state=RoomState.RUNNING,
        )
        session.completed_participant_ids.add(participant.participant_id)
        session.last_speaker_id = participant.participant_id
        return event

    async def _handle_scheduler_halt(
        self,
        session: RoomSession,
        correlation: CorrelationContext,
        reason: HaltReason,
    ) -> OrderedRoomEvent:
        if (
            reason is HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED
            and session.state is RoomState.RUNNING
        ):
            previous_state = session.state
            new_state = transition_room_state(
                previous_state,
                RoomAction.REQUEST_OWNER_DECISION,
            )
            event = await self._emit(
                session,
                correlation,
                RoomEventType.SCHEDULER_HALTED,
                room_state=new_state,
                halt_reason=reason,
                payload={"round_number": session.round_number},
                expected_state=previous_state,
                new_state=new_state,
            )
            session.state = new_state
            session.owner_decision_pending = True
            return event

        next_round = (
            session.round_number + 1
            if reason is HaltReason.ROUND_COMPLETE
            else session.round_number
        )
        event = await self._emit(
            session,
            correlation,
            RoomEventType.SCHEDULER_HALTED,
            halt_reason=reason,
            payload={"round_number": next_round},
            expected_state=session.state,
        )
        if reason is HaltReason.ROUND_COMPLETE:
            session.round_number = next_round
            session.completed_participant_ids.clear()
        return event

    async def _hard_stop_for_budget(
        self,
        session: RoomSession,
        correlation: CorrelationContext,
        reason: HaltReason,
    ) -> OrderedRoomEvent:
        if session.state is RoomState.RUNNING:
            previous_state = session.state
            new_state = transition_room_state(
                previous_state,
                RoomAction.REQUEST_OWNER_DECISION,
            )
            event = await self._emit(
                session,
                correlation,
                RoomEventType.BUDGET_HARD_STOP,
                room_state=new_state,
                halt_reason=reason,
                expected_state=previous_state,
                new_state=new_state,
            )
            session.state = new_state
            session.owner_decision_pending = True
            return event
        return await self._emit(
            session,
            correlation,
            RoomEventType.BUDGET_HARD_STOP,
            room_state=session.state,
            halt_reason=reason,
        )

    async def _turn_failed(
        self,
        session: RoomSession,
        correlation: CorrelationContext,
        participant_id: str,
        failure: TurnFailureKind,
    ) -> OrderedRoomEvent:
        is_chair = any(
            participant.participant_id == participant_id
            and participant.role is ParticipantRole.CHAIR
            for participant in session.participants
        )
        previous_state = session.state
        action = (
            RoomAction.PAUSE
            if is_chair
            else RoomAction.REQUEST_OWNER_DECISION
        )
        new_state = transition_room_state(previous_state, action)
        event = await self._emit(
            session,
            correlation,
            RoomEventType.TURN_FAILED,
            room_state=new_state,
            participant_id=participant_id,
            halt_reason=HaltReason.PARTICIPANT_FAILURE_LIMIT_REACHED,
            payload={
                "failure_kind": failure.value,
                "automatic_retry_allowed": False,
            },
            expected_state=previous_state,
            new_state=new_state,
        )
        session.state = new_state
        session.failed_participant_ids.add(participant_id)
        session.owner_decision_pending = (
            new_state is RoomState.NEEDS_OWNER_DECISION
        )
        return event

    async def _emit(
        self,
        session: RoomSession,
        correlation: CorrelationContext,
        event_type: RoomEventType,
        *,
        room_state: RoomState | None = None,
        participant_id: str | None = None,
        message_type: MessageType | None = None,
        halt_reason: HaltReason | None = None,
        payload: dict[str, object] | None = None,
        expected_state: RoomState | None = None,
        new_state: RoomState | None = None,
    ) -> OrderedRoomEvent:
        draft = RoomEventDraft(
            event_type=event_type,
            correlation=correlation,
            occurred_at=self._clock(),
            room_state=room_state,
            participant_id=participant_id,
            message_type=message_type,
            halt_reason=halt_reason,
            payload=payload or {},
        )
        return await self._event_sink.append(
            draft,
            expected_state=expected_state,
            new_state=new_state,
        )
