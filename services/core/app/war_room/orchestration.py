from __future__ import annotations

from dataclasses import dataclass

from .contracts import (
    AgendaPolicy,
    BudgetSnapshot,
    HaltReason,
    Participant,
    ParticipantRole,
    RoomMode,
    RoomState,
    validate_participants,
)


@dataclass(frozen=True, slots=True)
class TurnRequest:
    room_state: RoomState
    mode: RoomMode
    round_number: int
    participants: tuple[Participant, ...]
    completed_participant_ids: frozenset[str]
    budget: BudgetSnapshot
    agenda_policy: AgendaPolicy = AgendaPolicy()
    triggered_by_participant_id: str | None = None
    owner_decision_pending: bool = False

    def __post_init__(self) -> None:
        if self.round_number < 1:
            raise ValueError("round_number must be positive")
        validate_participants(
            mode=self.mode,
            participants=self.participants,
            max_automatic_participants=self.agenda_policy.max_automatic_participants,
        )


@dataclass(frozen=True, slots=True)
class ScheduleDecision:
    participant_id: str | None
    halt_reason: HaltReason | None

    @classmethod
    def scheduled(cls, participant_id: str) -> "ScheduleDecision":
        return cls(participant_id=participant_id, halt_reason=None)

    @classmethod
    def halted(cls, reason: HaltReason) -> "ScheduleDecision":
        return cls(participant_id=None, halt_reason=reason)


class DeterministicTurnScheduler:
    """Pure scheduler: no network, model, database, or tool side effects."""

    def choose_next(self, request: TurnRequest) -> ScheduleDecision:
        if (
            request.owner_decision_pending
            or request.room_state is RoomState.NEEDS_OWNER_DECISION
        ):
            return ScheduleDecision.halted(HaltReason.OWNER_DECISION_REQUIRED)

        if request.room_state is not RoomState.RUNNING:
            return ScheduleDecision.halted(HaltReason.STATE_NOT_RUNNING)

        global_halt = request.budget.global_halt_reason()
        if global_halt is not None:
            return ScheduleDecision.halted(global_halt)

        if request.round_number > request.agenda_policy.automatic_round_limit:
            return ScheduleDecision.halted(HaltReason.ROUND_LIMIT_REACHED)

        skipped_self = False
        skipped_budget = False
        automatic_participants = [
            participant
            for participant in request.participants
            if participant.automatic_turn_eligible
            and participant.role is not ParticipantRole.OWNER
        ]

        for participant in automatic_participants:
            if participant.participant_id in request.completed_participant_ids:
                continue

            if (
                request.triggered_by_participant_id is not None
                and participant.participant_id == request.triggered_by_participant_id
            ):
                skipped_self = True
                continue

            if request.budget.participant_exhausted(participant.participant_id):
                skipped_budget = True
                continue

            return ScheduleDecision.scheduled(participant.participant_id)

        unfinished = [
            participant
            for participant in automatic_participants
            if participant.participant_id not in request.completed_participant_ids
        ]

        if not unfinished:
            if request.round_number >= request.agenda_policy.automatic_round_limit:
                return ScheduleDecision.halted(HaltReason.ROUND_LIMIT_REACHED)
            return ScheduleDecision.halted(HaltReason.ROUND_COMPLETE)

        if skipped_self and all(
            participant.participant_id == request.triggered_by_participant_id
            or request.budget.participant_exhausted(participant.participant_id)
            for participant in unfinished
        ):
            if any(
                participant.participant_id == request.triggered_by_participant_id
                and not request.budget.participant_exhausted(
                    participant.participant_id
                )
                for participant in unfinished
            ):
                return ScheduleDecision.halted(HaltReason.SELF_RECURSION_BLOCKED)

        if skipped_budget:
            return ScheduleDecision.halted(HaltReason.PARTICIPANT_BUDGET_EXHAUSTED)

        return ScheduleDecision.halted(HaltReason.NO_ELIGIBLE_PARTICIPANT)
