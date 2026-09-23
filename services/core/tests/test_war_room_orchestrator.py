from uuid import UUID

import pytest

from app.war_room import (
    BudgetDecision,
    BudgetSnapshot,
    CorrelationContext,
    HaltReason,
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
    UnauthorizedRoomCommand,
    UsageDelta,
    WarRoomOrchestrator,
)


class Gateway:
    def __init__(self, *, fail_roles: set[ParticipantRole] | None = None) -> None:
        self.fail_roles = fail_roles or set()
        self.calls = []

    async def generate_turn(self, request):
        self.calls.append(request)
        if request.role in self.fail_roles:
            raise RuntimeError("provider failed")
        return ModelTurnResult(
            content_text=f"{request.role.value} response",
            content_reference=None,
            usage=UsageDelta(input_tokens=10, output_tokens=5),
        )


class Budget:
    async def authorize_turn(self, **_):
        return BudgetDecision(allowed=True)

    async def record_usage(self, **_):
        return None


class FailingSink:
    async def append(self, event, *, expected_state=None, new_state=None):
        raise RuntimeError("persistence failed")


class Authorizer:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls = []

    async def authorize(self, **values) -> bool:
        self.calls.append(values)
        return self.allowed


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


def snapshot() -> BudgetSnapshot:
    return BudgetSnapshot(
        room_tokens_used=0,
        room_token_limit=1000,
        agenda_tokens_used=0,
        agenda_token_limit=500,
        participant_token_limit=200,
    )


def participant(
    participant_id: str,
    role: ParticipantRole,
    *,
    human: bool = False,
) -> Participant:
    return Participant(
        participant_id=participant_id,
        participant_type=ParticipantType.HUMAN if human else ParticipantType.AGENT,
        role=role,
        agent_id=None if human else UUID(int=10 + len(participant_id)),
        model_policy_ref=None if human else f"policy/{participant_id}",
    )


@pytest.mark.anyio
async def test_pause_resume_stop_are_authoritative_state_transitions() -> None:
    sink = Sink()
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.READY,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("builder", ParticipantRole.BUILDER),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=Gateway(),
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        event_sink=sink,
    )

    for command, expected_before, expected_after in (
        (RoomCommandType.START, RoomState.READY, RoomState.RUNNING),
        (RoomCommandType.PAUSE, RoomState.RUNNING, RoomState.PAUSED),
        (RoomCommandType.RESUME, RoomState.PAUSED, RoomState.RUNNING),
        (RoomCommandType.STOP, RoomState.RUNNING, RoomState.STOPPED),
    ):
        event = await orchestrator.apply_command(
            room,
            RoomCommand(
                command=command,
                correlation=correlation(),
                expected_state=expected_before,
            ),
            actor=TrustedActorContext(
                tenant_id=UUID(int=1),
                application_id=UUID(int=2),
                principal_type=ParticipantType.HUMAN,
                principal_id="owner",
            ),
        )
        assert room.state is expected_after
        assert event.event_type is RoomEventType.ROOM_STATE_CHANGED

    assert [event.sequence for event in sink.events] == [1, 2, 3, 4]


@pytest.mark.anyio
async def test_owner_decision_gate_halts_before_model_invocation() -> None:
    gateway = Gateway()
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.RUNNING,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("builder", ParticipantRole.BUILDER),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=gateway,
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        event_sink=Sink(),
    )

    await orchestrator.apply_command(
        room,
        RoomCommand(
            command=RoomCommandType.REQUEST_OWNER_DECISION,
            correlation=correlation(),
            expected_state=RoomState.RUNNING,
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
        agenda_objective="Need owner choice",
    )

    assert room.state is RoomState.NEEDS_OWNER_DECISION
    assert event.event_type is RoomEventType.SCHEDULER_HALTED
    assert event.halt_reason is HaltReason.OWNER_DECISION_REQUIRED
    assert gateway.calls == []


@pytest.mark.anyio
async def test_chair_provider_failure_pauses_room() -> None:
    gateway = Gateway(fail_roles={ParticipantRole.CHAIR})
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.RUNNING,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("chair", ParticipantRole.CHAIR),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=gateway,
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        event_sink=Sink(),
    )

    event = await orchestrator.run_next_turn(
        room,
        correlation=correlation(),
        budget=snapshot(),
        agenda_objective="Chair the meeting",
    )

    assert event.event_type is RoomEventType.TURN_FAILED
    assert room.state is RoomState.PAUSED


@pytest.mark.anyio
async def test_synthetic_room_runs_two_bounded_rounds_with_ordered_trace() -> None:
    gateway = Gateway()
    sink = Sink()
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.RUNNING,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("builder", ParticipantRole.BUILDER),
            participant("security", ParticipantRole.SECURITY_REVIEWER),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=gateway,
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        event_sink=sink,
    )

    results = []
    for _ in range(6):
        results.append(
            await orchestrator.run_next_turn(
                room,
                correlation=correlation(),
                budget=snapshot(),
                agenda_objective="Synthetic end-to-end review",
            )
        )

    assert [request.participant_id for request in gateway.calls] == [
        "builder",
        "security",
        "builder",
        "security",
    ]
    assert results[2].halt_reason is HaltReason.ROUND_COMPLETE
    assert results[5].halt_reason is HaltReason.ROUND_LIMIT_REACHED
    assert room.round_number == 2
    assert [event.sequence for event in sink.events] == list(
        range(1, len(sink.events) + 1)
    )
    assert all(
        event.correlation.trace_id == "0123456789abcdef0123456789abcdef"
        for event in sink.events
    )


@pytest.mark.anyio
async def test_owner_command_is_rejected_before_state_mutation_when_not_authorized() -> None:
    authorizer = Authorizer(allowed=False)
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.READY,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("builder", ParticipantRole.BUILDER),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=Gateway(),
        budget_authority=Budget(),
        command_authorizer=authorizer,
        event_sink=Sink(),
    )

    with pytest.raises(UnauthorizedRoomCommand):
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
                principal_id="not-owner",
            ),
        )

    assert room.state is RoomState.READY
    assert len(authorizer.calls) == 1


@pytest.mark.anyio
async def test_authorization_receives_trusted_actor_and_command_scope() -> None:
    authorizer = Authorizer()
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.READY,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("builder", ParticipantRole.BUILDER),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=Gateway(),
        budget_authority=Budget(),
        command_authorizer=authorizer,
        event_sink=Sink(),
    )
    actor = TrustedActorContext(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        principal_type=ParticipantType.HUMAN,
        principal_id="owner-principal",
    )
    command = RoomCommand(
        command=RoomCommandType.START,
        correlation=correlation(),
        expected_state=RoomState.READY,
    )

    await orchestrator.apply_command(room, command, actor=actor)

    call = authorizer.calls[0]
    assert call["actor"] == actor
    assert call["command"].correlation.tenant_id == UUID(int=1)
    assert call["command"].correlation.application_id == UUID(int=2)


@pytest.mark.anyio
async def test_state_does_not_mutate_when_persistence_fails() -> None:
    room = RoomSession(
        mode=RoomMode.FORMAL_MEETING,
        state=RoomState.READY,
        participants=(
            participant("owner", ParticipantRole.OWNER, human=True),
            participant("builder", ParticipantRole.BUILDER),
        ),
    )
    orchestrator = WarRoomOrchestrator(
        model_gateway=Gateway(),
        budget_authority=Budget(),
        command_authorizer=Authorizer(),
        event_sink=FailingSink(),
    )

    with pytest.raises(RuntimeError, match="persistence failed"):
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

    assert room.state is RoomState.READY
    assert room.owner_decision_pending is False
