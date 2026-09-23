from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest

from app.war_room import (
    BudgetDecision,
    BudgetLimit,
    CorrelationContext,
    HaltReason,
    InterfaceViolation,
    OrderedRoomEvent,
    ParticipantRole,
    RoomCommand,
    RoomCommandType,
    RoomEventType,
    RoomState,
    UsageDelta,
)


def correlation() -> CorrelationContext:
    return CorrelationContext(
        tenant_id=UUID("11111111-1111-4111-8111-111111111111"),
        application_id=UUID("22222222-2222-4222-8222-222222222222"),
        room_id=UUID("33333333-3333-4333-8333-333333333333"),
        agenda_item_id=UUID("44444444-4444-4444-8444-444444444444"),
        request_id=UUID("55555555-5555-4555-8555-555555555555"),
        trace_id="0123456789abcdef0123456789abcdef",
    )


def test_correlation_rejects_non_w3c_trace_id() -> None:
    with pytest.raises(InterfaceViolation):
        CorrelationContext(
            tenant_id=UUID(int=1),
            application_id=UUID(int=2),
            room_id=UUID(int=3),
            agenda_item_id=UUID(int=4),
            request_id=UUID(int=5),
            trace_id="not-a-trace-id",
        )


def test_ask_role_requires_a_target_role() -> None:
    with pytest.raises(InterfaceViolation):
        RoomCommand(
            command=RoomCommandType.ASK_ROLE,
            correlation=correlation(),
            expected_state=RoomState.RUNNING,
        )


def test_cost_limit_requires_currency() -> None:
    with pytest.raises(InterfaceViolation):
        BudgetLimit(token_limit=1000, cost_limit=Decimal("1.00"))


def test_usage_delta_exposes_total_without_becoming_a_ledger() -> None:
    usage = UsageDelta(input_tokens=20, output_tokens=30)

    assert usage.total_tokens == 50


def test_budget_decision_is_unambiguous() -> None:
    assert BudgetDecision(allowed=True).halt_reason is None
    assert BudgetDecision(
        allowed=False,
        halt_reason=HaltReason.ROOM_BUDGET_EXHAUSTED,
    ).allowed is False

    with pytest.raises(InterfaceViolation):
        BudgetDecision(allowed=False)


def test_ordered_event_requires_positive_sequence() -> None:
    with pytest.raises(InterfaceViolation):
        OrderedRoomEvent(
            event_id=UUID(int=6),
            sequence=0,
            event_type=RoomEventType.TURN_SCHEDULED,
            correlation=correlation(),
            occurred_at=datetime.now(UTC),
        )


def test_scheduler_halt_is_distinct_from_turn_failure() -> None:
    assert RoomEventType.SCHEDULER_HALTED is not RoomEventType.TURN_FAILED


def test_ask_role_accepts_frozen_role_contract() -> None:
    command = RoomCommand(
        command=RoomCommandType.ASK_ROLE,
        correlation=correlation(),
        expected_state=RoomState.RUNNING,
        target_role=ParticipantRole.SECURITY_REVIEWER,
        content_text="Review the isolation evidence.",
    )

    assert command.target_role is ParticipantRole.SECURITY_REVIEWER
