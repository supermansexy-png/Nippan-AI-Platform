from contextlib import asynccontextmanager
from uuid import UUID

import pytest

from app.war_room import (
    BudgetDecision,
    BudgetSnapshot,
    CorrelationContext,
    ModelTurnResult,
    OrderedRoomEvent,
    Participant,
    ParticipantRole,
    ParticipantType,
    RoomCommand,
    RoomCommandType,
    RoomEventType,
    RoomMode,
    RoomSession,
    RoomState,
    TrustedActorContext,
    UsageDelta,
    WarRoomOrchestrator,
)


class Gateway:
    def __init__(self) -> None:
        self.calls = 0

    async def generate_turn(self, request):
        self.calls += 1
        return ModelTurnResult(
            content_text=f"{request.role.value} response",
            content_reference=None,
            usage=UsageDelta(input_tokens=10, output_tokens=5),
            provider_request_id="req-service-unit",
            responded_model="model-service-unit",
        )


class Budget:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.recorded = []

    async def authorize_turn(self, **_):
        from app.war_room import HaltReason

        return BudgetDecision(
            allowed=self.allowed,
            halt_reason=None if self.allowed else HaltReason.ROOM_BUDGET_EXHAUSTED,
            max_output_tokens=128 if self.allowed else None,
        )

    async def record_usage(self, **values):
        self.recorded.append(values)


class FailureHistory:
    async def load_failed_participant_ids(self, **_):
        return frozenset()


class TurnGuard:
    def __init__(self) -> None:
        self.entries = 0

    @asynccontextmanager
    async def hold(self, **_):
        self.entries += 1
        yield RoomState.RUNNING


class Authorizer:
    async def authorize(self, **_) -> bool:
        return True


class Sink:
    def __init__(self) -> None:
        self.events = []

    async def append(self, event, *, expected_state=None, new_state=None):
        ordered = OrderedRoomEvent(
            event_id=UUID(int=100 + len(self.events)),
            sequence=len(self.events) + 1,
            event_type=event.event_type,
            correlation=event.correlation,
            occurred_at=event.occurred_at,
            room_state=event.room_state,
            participant_id=event.participant_id,
            message_type=event.message_type,
            halt_reason=event.halt_reason,
            payload=event.payload,
        )
        self.events.append(ordered)
        return ordered


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


def session() -> RoomSession:
    return RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.READY,
        participants=(
            Participant(
                participant_id="owner",
                participant_type=ParticipantType.HUMAN,
                role=ParticipantRole.OWNER,
            ),
            Participant(
                participant_id="builder",
                participant_type=ParticipantType.AGENT,
                role=ParticipantRole.BUILDER,
                agent_id=UUID(int=10),
                model_policy_ref="policy/builder",
            ),
        ),
    )


def snapshot() -> BudgetSnapshot:
    return BudgetSnapshot(
        room_tokens_used=0,
        room_token_limit=1000,
        agenda_tokens_used=0,
        agenda_token_limit=500,
        participant_token_limit=200,
    )


@pytest.mark.anyio
async def test_lifecycle_start_and_one_model_turn_are_ordered() -> None:
    gateway = Gateway()
    sink = Sink()
    orchestrator = WarRoomOrchestrator(
        model_gateway=gateway,
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        turn_execution_guard=TurnGuard(),
        failure_history_source=FailureHistory(),
        event_sink=sink,
    )
    room = session()

    await orchestrator.apply_command(
        room,
        RoomCommand(
            command=RoomCommandType.START,
            correlation=correlation(),
            expected_state=RoomState.READY,
        ),
        actor=TrustedActorContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            principal_type=ParticipantType.HUMAN,
            principal_id="owner",
        ),
    )
    event = await orchestrator.run_next_turn(
        room,
        correlation=correlation(),
        budget=snapshot(),
        agenda_objective="Review the implementation",
    )

    assert room.state is RoomState.RUNNING
    assert event.event_type is RoomEventType.MESSAGE_APPENDED
    assert [item.sequence for item in sink.events] == [1, 2, 3]
    assert gateway.calls == 1


@pytest.mark.anyio
async def test_budget_denial_stops_before_provider_call() -> None:
    gateway = Gateway()
    sink = Sink()
    room = session()
    room.state = RoomState.RUNNING
    orchestrator = WarRoomOrchestrator(
        model_gateway=gateway,
        budget_authority=Budget(allowed=False),
        command_authorizer=Authorizer(),
        turn_execution_guard=TurnGuard(),
        failure_history_source=FailureHistory(),
        event_sink=sink,
    )

    event = await orchestrator.run_next_turn(
        room,
        correlation=correlation(),
        budget=snapshot(),
        agenda_objective="Review the implementation",
    )

    assert event.event_type is RoomEventType.BUDGET_HARD_STOP
    assert room.state is RoomState.NEEDS_OWNER_DECISION
    assert gateway.calls == 0


@pytest.mark.anyio
async def test_round_completion_is_not_reported_as_turn_failure() -> None:
    room = session()
    room.state = RoomState.RUNNING
    room.completed_participant_ids.add("builder")
    orchestrator = WarRoomOrchestrator(
        model_gateway=Gateway(),
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        turn_execution_guard=TurnGuard(),
        failure_history_source=FailureHistory(),
        event_sink=Sink(),
    )

    event = await orchestrator.run_next_turn(
        room,
        correlation=correlation(),
        budget=snapshot(),
        agenda_objective="Review the implementation",
    )

    assert event.event_type is RoomEventType.SCHEDULER_HALTED
    assert room.round_number == 2
