from uuid import UUID

import pytest

from app.war_room import (
    AgendaPolicy,
    BudgetSnapshot,
    ContractViolation,
    DeterministicTurnScheduler,
    HaltReason,
    InvalidRoomTransition,
    Participant,
    ParticipantRole,
    ParticipantType,
    RoomAction,
    RoomContract,
    RoomMode,
    RoomState,
    TurnRequest,
    transition_room_state,
)


OWNER = Participant(
    participant_id="owner",
    participant_type=ParticipantType.HUMAN,
    role=ParticipantRole.OWNER,
)

BUILDER = Participant(
    participant_id="builder",
    participant_type=ParticipantType.AGENT,
    role=ParticipantRole.BUILDER,
    agent_id=UUID("11111111-1111-4111-8111-111111111111"),
)

SECURITY = Participant(
    participant_id="security",
    participant_type=ParticipantType.AGENT,
    role=ParticipantRole.SECURITY_REVIEWER,
    agent_id=UUID("22222222-2222-4222-8222-222222222222"),
)

AUDITOR = Participant(
    participant_id="auditor",
    participant_type=ParticipantType.AGENT,
    role=ParticipantRole.INDEPENDENT_AUDITOR,
    agent_id=UUID("33333333-3333-4333-8333-333333333333"),
)


def budget(
    *,
    room_used: int = 0,
    agenda_used: int = 0,
    participant_used: dict[str, int] | None = None,
) -> BudgetSnapshot:
    return BudgetSnapshot(
        room_tokens_used=room_used,
        room_token_limit=1000,
        agenda_tokens_used=agenda_used,
        agenda_token_limit=500,
        participant_token_limit=200,
        participant_tokens_used=participant_used or {},
    )


def request(**overrides: object) -> TurnRequest:
    values: dict[str, object] = {
        "room_state": RoomState.RUNNING,
        "mode": RoomMode.FORMAL_MEETING,
        "round_number": 1,
        "participants": (OWNER, BUILDER, SECURITY),
        "completed_participant_ids": frozenset(),
        "budget": budget(),
    }
    values.update(overrides)
    return TurnRequest(**values)


def test_state_machine_allows_controlled_lifecycle() -> None:
    state = transition_room_state(RoomState.DRAFT, RoomAction.PREPARE)
    state = transition_room_state(state, RoomAction.START)
    state = transition_room_state(state, RoomAction.PAUSE)
    state = transition_room_state(state, RoomAction.RESUME)
    state = transition_room_state(state, RoomAction.REQUEST_OWNER_DECISION)
    state = transition_room_state(state, RoomAction.RESOLVE_OWNER_DECISION)
    state = transition_room_state(state, RoomAction.BEGIN_SUMMARY)
    state = transition_room_state(state, RoomAction.CLOSE)

    assert state is RoomState.CLOSED


def test_terminal_room_cannot_restart() -> None:
    with pytest.raises(InvalidRoomTransition):
        transition_room_state(RoomState.CLOSED, RoomAction.START)


def test_stop_is_available_from_non_terminal_state() -> None:
    assert (
        transition_room_state(RoomState.NEEDS_OWNER_DECISION, RoomAction.STOP)
        is RoomState.STOPPED
    )


def test_v1_automatic_round_limit_cannot_exceed_two() -> None:
    with pytest.raises(ContractViolation):
        AgendaPolicy(automatic_round_limit=3)


def test_audit_review_requires_independent_auditor_agent_identity() -> None:
    shared_agent = UUID("11111111-1111-4111-8111-111111111111")
    auditor = Participant(
        participant_id="auditor",
        participant_type=ParticipantType.AGENT,
        role=ParticipantRole.INDEPENDENT_AUDITOR,
        agent_id=shared_agent,
    )

    with pytest.raises(ContractViolation):
        RoomContract(
            room_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
            mode=RoomMode.AUDIT_REVIEW,
            state=RoomState.READY,
            participants=(OWNER, BUILDER, auditor),
        )


def test_scheduler_is_deterministic_and_skips_human_owner() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(request())

    assert decision.participant_id == "builder"
    assert decision.halt_reason is None


def test_scheduler_advances_in_declared_participant_order() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(
        request(completed_participant_ids=frozenset({"builder"}))
    )

    assert decision.participant_id == "security"


def test_scheduler_blocks_direct_self_recursion() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(
        request(
            participants=(OWNER, BUILDER),
            triggered_by_participant_id="builder",
        )
    )

    assert decision.participant_id is None
    assert decision.halt_reason is HaltReason.SELF_RECURSION_BLOCKED


def test_scheduler_halts_for_owner_decision() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(
        request(room_state=RoomState.NEEDS_OWNER_DECISION)
    )

    assert decision.halt_reason is HaltReason.OWNER_DECISION_REQUIRED


def test_scheduler_halts_when_room_budget_is_exhausted() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(request(budget=budget(room_used=1000)))

    assert decision.halt_reason is HaltReason.ROOM_BUDGET_EXHAUSTED


def test_scheduler_skips_participant_with_exhausted_budget() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(
        request(budget=budget(participant_used={"builder": 200}))
    )

    assert decision.participant_id == "security"


def test_scheduler_halts_after_second_round_completes() -> None:
    scheduler = DeterministicTurnScheduler()

    decision = scheduler.choose_next(
        request(
            round_number=2,
            completed_participant_ids=frozenset({"builder", "security"}),
        )
    )

    assert decision.halt_reason is HaltReason.ROUND_LIMIT_REACHED


def test_audit_review_with_distinct_builder_and_auditor_is_valid() -> None:
    contract = RoomContract(
        room_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        mode=RoomMode.AUDIT_REVIEW,
        state=RoomState.READY,
        participants=(OWNER, BUILDER, AUDITOR),
    )

    assert contract.mode is RoomMode.AUDIT_REVIEW
