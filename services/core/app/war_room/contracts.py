from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping
from uuid import UUID


class ContractViolation(ValueError):
    """Raised when a War Room contract violates a deterministic invariant."""


class RoomMode(StrEnum):
    FREE_DISCUSSION = "FREE_DISCUSSION"
    FORMAL_MEETING = "FORMAL_MEETING"
    AUDIT_REVIEW = "AUDIT_REVIEW"


class RoomState(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    NEEDS_OWNER_DECISION = "NEEDS_OWNER_DECISION"
    SUMMARIZING = "SUMMARIZING"
    CLOSED = "CLOSED"
    STOPPED = "STOPPED"


class ParticipantType(StrEnum):
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class ParticipantRole(StrEnum):
    OWNER = "OWNER"
    CHAIR = "CHAIR"
    ARCHITECT = "ARCHITECT"
    BUILDER = "BUILDER"
    SECURITY_REVIEWER = "SECURITY_REVIEWER"
    COST_OPS_REVIEWER = "COST_OPS_REVIEWER"
    INDEPENDENT_AUDITOR = "INDEPENDENT_AUDITOR"
    SECRETARY = "SECRETARY"


class MessageType(StrEnum):
    OWNER_MESSAGE = "OWNER_MESSAGE"
    AGENT_MESSAGE = "AGENT_MESSAGE"
    CHAIR_PROMPT = "CHAIR_PROMPT"
    CHAIR_SYNTHESIS = "CHAIR_SYNTHESIS"
    EVIDENCE_REQUEST = "EVIDENCE_REQUEST"
    EVIDENCE_REFERENCE = "EVIDENCE_REFERENCE"
    FINDING = "FINDING"
    DECISION_PROPOSAL = "DECISION_PROPOSAL"
    OWNER_DECISION = "OWNER_DECISION"
    ACTION_ITEM = "ACTION_ITEM"
    SYSTEM_EVENT = "SYSTEM_EVENT"
    BUDGET_WARNING = "BUDGET_WARNING"
    ERROR = "ERROR"


class EvidenceKind(StrEnum):
    VERIFIED_EVIDENCE = "VERIFIED_EVIDENCE"
    PROVIDED_CLAIM = "PROVIDED_CLAIM"
    INFERENCE = "INFERENCE"
    OPINION = "OPINION"
    UNKNOWN = "UNKNOWN"


class HaltReason(StrEnum):
    STATE_NOT_RUNNING = "STATE_NOT_RUNNING"
    OWNER_DECISION_REQUIRED = "OWNER_DECISION_REQUIRED"
    ROUND_COMPLETE = "ROUND_COMPLETE"
    ROUND_LIMIT_REACHED = "ROUND_LIMIT_REACHED"
    ROOM_BUDGET_EXHAUSTED = "ROOM_BUDGET_EXHAUSTED"
    AGENDA_BUDGET_EXHAUSTED = "AGENDA_BUDGET_EXHAUSTED"
    PARTICIPANT_BUDGET_EXHAUSTED = "PARTICIPANT_BUDGET_EXHAUSTED"
    PARTICIPANT_FAILURE_LIMIT_REACHED = "PARTICIPANT_FAILURE_LIMIT_REACHED"
    SELF_RECURSION_BLOCKED = "SELF_RECURSION_BLOCKED"
    NO_ELIGIBLE_PARTICIPANT = "NO_ELIGIBLE_PARTICIPANT"


@dataclass(frozen=True, slots=True)
class Participant:
    participant_id: str
    participant_type: ParticipantType
    role: ParticipantRole
    agent_id: UUID | None = None
    model_policy_ref: str | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if not self.participant_id.strip():
            raise ContractViolation("participant_id must not be blank")
        if self.participant_type is ParticipantType.AGENT and self.agent_id is None:
            raise ContractViolation("AGENT participant requires agent_id")

    @property
    def automatic_turn_eligible(self) -> bool:
        return self.active and self.participant_type is ParticipantType.AGENT


@dataclass(frozen=True, slots=True)
class AgendaPolicy:
    automatic_round_limit: int = 2
    max_automatic_participants: int = 5

    def __post_init__(self) -> None:
        if not 1 <= self.automatic_round_limit <= 2:
            raise ContractViolation(
                "automatic_round_limit must be between 1 and 2 for War Room V1"
            )
        if not 1 <= self.max_automatic_participants <= 5:
            raise ContractViolation(
                "max_automatic_participants must be between 1 and 5 for War Room V1"
            )


@dataclass(frozen=True, slots=True)
class BudgetSnapshot:
    room_tokens_used: int
    room_token_limit: int
    agenda_tokens_used: int
    agenda_token_limit: int
    participant_token_limit: int
    participant_tokens_used: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        values = (
            self.room_tokens_used,
            self.agenda_tokens_used,
            self.participant_token_limit,
            self.room_token_limit,
            self.agenda_token_limit,
        )
        if any(value < 0 for value in values):
            raise ContractViolation("budget values must not be negative")
        if self.room_token_limit == 0 or self.agenda_token_limit == 0:
            raise ContractViolation("room and agenda token limits must be positive")
        if self.participant_token_limit == 0:
            raise ContractViolation("participant token limit must be positive")
        if any(value < 0 for value in self.participant_tokens_used.values()):
            raise ContractViolation("participant token usage must not be negative")

    def global_halt_reason(self) -> HaltReason | None:
        if self.room_tokens_used >= self.room_token_limit:
            return HaltReason.ROOM_BUDGET_EXHAUSTED
        if self.agenda_tokens_used >= self.agenda_token_limit:
            return HaltReason.AGENDA_BUDGET_EXHAUSTED
        return None

    def participant_exhausted(self, participant_id: str) -> bool:
        return (
            self.participant_tokens_used.get(participant_id, 0)
            >= self.participant_token_limit
        )


@dataclass(frozen=True, slots=True)
class RoomContract:
    room_id: UUID
    mode: RoomMode
    state: RoomState
    participants: tuple[Participant, ...]
    agenda_policy: AgendaPolicy = field(default_factory=AgendaPolicy)

    def __post_init__(self) -> None:
        validate_participants(
            mode=self.mode,
            participants=self.participants,
            max_automatic_participants=self.agenda_policy.max_automatic_participants,
        )


@dataclass(frozen=True, slots=True)
class RoomMessageContract:
    message_type: MessageType
    participant_id: str | None = None
    round_number: int | None = None
    evidence_kind: EvidenceKind | None = None
    content_reference: str | None = None

    def __post_init__(self) -> None:
        if self.round_number is not None and self.round_number < 1:
            raise ContractViolation("round_number must be positive when present")
        if self.participant_id is not None and not self.participant_id.strip():
            raise ContractViolation("participant_id must not be blank when present")
        if self.content_reference is not None and not self.content_reference.strip():
            raise ContractViolation("content_reference must not be blank when present")


def validate_participants(
    *,
    mode: RoomMode,
    participants: tuple[Participant, ...],
    max_automatic_participants: int,
) -> None:
    participant_ids = [participant.participant_id for participant in participants]
    if len(participant_ids) != len(set(participant_ids)):
        raise ContractViolation("participant_id values must be unique within a room")

    automatic_count = sum(
        participant.automatic_turn_eligible for participant in participants
    )
    if automatic_count > max_automatic_participants:
        raise ContractViolation(
            "automatic participant count exceeds agenda policy maximum"
        )

    if mode is not RoomMode.AUDIT_REVIEW:
        return

    auditors = [
        participant
        for participant in participants
        if participant.role is ParticipantRole.INDEPENDENT_AUDITOR and participant.active
    ]
    if len(auditors) != 1:
        raise ContractViolation(
            "AUDIT_REVIEW requires exactly one active INDEPENDENT_AUDITOR"
        )

    auditor = auditors[0]
    builders = [
        participant
        for participant in participants
        if participant.role is ParticipantRole.BUILDER and participant.active
    ]

    if auditor.agent_id is not None and any(
        builder.agent_id == auditor.agent_id for builder in builders
    ):
        raise ContractViolation(
            "Independent Auditor must not share agent identity with Builder"
        )
