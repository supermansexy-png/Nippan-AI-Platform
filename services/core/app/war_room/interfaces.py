from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import AsyncContextManager, Protocol
from uuid import UUID

from .contracts import HaltReason, MessageType, ParticipantRole, ParticipantType, RoomMode, RoomState


class InterfaceViolation(ValueError):
    """Raised when an Increment C boundary object is internally inconsistent."""


class RoomCommandType(StrEnum):
    PREPARE = "PREPARE"
    START = "START"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    STOP = "STOP"
    ASK_ROLE = "ASK_ROLE"
    ASK_ALL = "ASK_ALL"
    REQUEST_OWNER_DECISION = "REQUEST_OWNER_DECISION"
    SUBMIT_OWNER_DECISION = "SUBMIT_OWNER_DECISION"
    BEGIN_SUMMARY = "BEGIN_SUMMARY"
    CLOSE = "CLOSE"


class RoomEventType(StrEnum):
    ROOM_STATE_CHANGED = "ROOM_STATE_CHANGED"
    TURN_SCHEDULED = "TURN_SCHEDULED"
    SCHEDULER_HALTED = "SCHEDULER_HALTED"
    MESSAGE_APPENDED = "MESSAGE_APPENDED"
    OWNER_DECISION_REQUIRED = "OWNER_DECISION_REQUIRED"
    BUDGET_HARD_STOP = "BUDGET_HARD_STOP"
    TURN_FAILED = "TURN_FAILED"


class TurnFailureKind(StrEnum):
    TIMEOUT = "TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    POLICY_REJECTED = "POLICY_REJECTED"


class RealtimeTransport(StrEnum):
    SERVER_SENT_EVENTS = "SERVER_SENT_EVENTS"


class RoomReadKind(StrEnum):
    SNAPSHOT = "SNAPSHOT"
    EVENT_STREAM = "EVENT_STREAM"


@dataclass(frozen=True, slots=True)
class CorrelationContext:
    tenant_id: UUID
    application_id: UUID
    room_id: UUID
    agenda_item_id: UUID
    request_id: UUID
    trace_id: str

    def __post_init__(self) -> None:
        if len(self.trace_id) != 32 or any(
            char not in "0123456789abcdef" for char in self.trace_id
        ):
            raise InterfaceViolation(
                "trace_id must be 32 lowercase hexadecimal characters"
            )


@dataclass(frozen=True, slots=True)
class TrustedActorContext:
    """Server-established actor scope. Never trust model/client-supplied scope as authority."""

    tenant_id: UUID
    application_id: UUID
    principal_type: ParticipantType
    principal_id: str

    def __post_init__(self) -> None:
        if not self.principal_id.strip():
            raise InterfaceViolation("principal_id must not be blank")


@dataclass(frozen=True, slots=True)
class RoomReadRequest:
    tenant_id: UUID
    application_id: UUID
    room_id: UUID
    read_kind: RoomReadKind
    after_sequence: int | None = None

    def __post_init__(self) -> None:
        if self.after_sequence is not None and self.after_sequence < 0:
            raise InterfaceViolation("after_sequence must not be negative")


@dataclass(frozen=True, slots=True)
class RoomCommand:
    command: RoomCommandType
    correlation: CorrelationContext
    expected_state: RoomState
    target_participant_id: str | None = None
    target_role: ParticipantRole | None = None
    content_text: str | None = None
    content_reference: str | None = None

    def __post_init__(self) -> None:
        if self.command is RoomCommandType.ASK_ROLE and self.target_role is None:
            raise InterfaceViolation("ASK_ROLE requires target_role")
        if self.target_participant_id is not None and not self.target_participant_id.strip():
            raise InterfaceViolation("target_participant_id must not be blank")
        if self.content_text is not None and not self.content_text.strip():
            raise InterfaceViolation("content_text must not be blank")
        if self.content_reference is not None and not self.content_reference.strip():
            raise InterfaceViolation("content_reference must not be blank")
        content_commands = {
            RoomCommandType.ASK_ROLE,
            RoomCommandType.ASK_ALL,
            RoomCommandType.SUBMIT_OWNER_DECISION,
        }
        if (
            self.command in content_commands
            and self.content_text is None
            and self.content_reference is None
        ):
            raise InterfaceViolation(f"{self.command.value} requires content")


@dataclass(frozen=True, slots=True)
class BudgetLimit:
    token_limit: int
    cost_limit: Decimal | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        if self.token_limit <= 0:
            raise InterfaceViolation("token_limit must be positive")
        if self.cost_limit is not None and self.cost_limit < 0:
            raise InterfaceViolation("cost_limit must not be negative")
        if (self.cost_limit is None) != (self.currency is None):
            raise InterfaceViolation("cost_limit and currency must be set together")
        if self.currency is not None and (
            len(self.currency) != 3
            or not self.currency.isascii()
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise InterfaceViolation("currency must be a three-letter uppercase code")


@dataclass(frozen=True, slots=True)
class UsageDelta:
    input_tokens: int
    output_tokens: int
    normalized_cost: Decimal | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        if self.input_tokens < 0 or self.output_tokens < 0:
            raise InterfaceViolation("token usage must not be negative")
        if self.normalized_cost is not None and self.normalized_cost < 0:
            raise InterfaceViolation("normalized_cost must not be negative")
        if (self.normalized_cost is None) != (self.currency is None):
            raise InterfaceViolation("normalized_cost and currency must be set together")
        if self.currency is not None and (
            len(self.currency) != 3
            or not self.currency.isascii()
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise InterfaceViolation("currency must be a three-letter uppercase code")

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True, slots=True)
class ModelTurnRequest:
    correlation: CorrelationContext
    participant_id: str
    role: ParticipantRole
    model_policy_ref: str
    agenda_objective: str
    max_output_tokens: int
    context_references: tuple[str, ...] = ()
    prior_round_synthesis: str | None = None

    def __post_init__(self) -> None:
        required = (
            self.participant_id,
            self.model_policy_ref,
            self.agenda_objective,
        )
        if any(not value.strip() for value in required):
            raise InterfaceViolation("model turn identifiers and objective must not be blank")
        if any(not reference.strip() for reference in self.context_references):
            raise InterfaceViolation("context references must not be blank")
        if self.max_output_tokens <= 0:
            raise InterfaceViolation("max_output_tokens must be positive")


@dataclass(frozen=True, slots=True)
class ModelTurnResult:
    content_text: str | None
    content_reference: str | None
    usage: UsageDelta
    provider_request_id: str | None = None

    def __post_init__(self) -> None:
        if not any(
            value is not None and value.strip()
            for value in (self.content_text, self.content_reference)
        ):
            raise InterfaceViolation("model result requires content text or reference")


@dataclass(frozen=True, slots=True)
class BudgetDecision:
    allowed: bool
    halt_reason: HaltReason | None = None
    max_output_tokens: int | None = None

    def __post_init__(self) -> None:
        if self.allowed == (self.halt_reason is not None):
            raise InterfaceViolation(
                "allowed decisions cannot have a halt reason and denied decisions require one"
            )
        if self.allowed:
            if self.max_output_tokens is None or self.max_output_tokens <= 0:
                raise InterfaceViolation(
                    "allowed budget decisions require positive max_output_tokens"
                )
        elif self.max_output_tokens is not None:
            raise InterfaceViolation(
                "denied budget decisions cannot grant output tokens"
            )


@dataclass(frozen=True, slots=True)
class RoomEventDraft:
    event_type: RoomEventType
    correlation: CorrelationContext
    occurred_at: datetime
    room_state: RoomState | None = None
    participant_id: str | None = None
    message_type: MessageType | None = None
    halt_reason: HaltReason | None = None
    payload: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class OrderedRoomEvent:
    event_id: UUID
    sequence: int
    event_type: RoomEventType
    correlation: CorrelationContext
    occurred_at: datetime
    room_state: RoomState | None = None
    participant_id: str | None = None
    message_type: MessageType | None = None
    halt_reason: HaltReason | None = None
    payload: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sequence <= 0:
            raise InterfaceViolation("event sequence must be positive")


@dataclass(frozen=True, slots=True)
class RoomParticipantSnapshot:
    participant_id: UUID
    role: ParticipantRole
    display_name: str
    active: bool

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise InterfaceViolation("display_name must not be blank")


@dataclass(frozen=True, slots=True)
class RoomAgendaSnapshot:
    agenda_item_id: UUID
    sequence: int
    title: str
    objective: str
    status: str
    round_limit: int

    def __post_init__(self) -> None:
        if self.sequence <= 0:
            raise InterfaceViolation("agenda sequence must be positive")
        if not self.title.strip() or not self.objective.strip():
            raise InterfaceViolation("agenda title/objective must not be blank")
        if not self.status.strip():
            raise InterfaceViolation("agenda status must not be blank")
        if not 1 <= self.round_limit <= 2:
            raise InterfaceViolation("agenda round_limit must be between 1 and 2")


@dataclass(frozen=True, slots=True)
class RoomFindingSnapshot:
    finding_id: UUID
    severity: str
    status: str
    summary: str

    def __post_init__(self) -> None:
        if not self.severity.strip() or not self.status.strip():
            raise InterfaceViolation("finding severity/status must not be blank")
        if not self.summary.strip():
            raise InterfaceViolation("finding summary must not be blank")


@dataclass(frozen=True, slots=True)
class RoomDecisionSnapshot:
    decision_id: UUID
    decision_type: str
    status: str
    decision: str
    owner_principal_id: str | None = None

    def __post_init__(self) -> None:
        if not self.decision_type.strip() or not self.status.strip():
            raise InterfaceViolation("decision type/status must not be blank")
        if not self.decision.strip():
            raise InterfaceViolation("decision text must not be blank")
        if (
            self.owner_principal_id is not None
            and not self.owner_principal_id.strip()
        ):
            raise InterfaceViolation("owner_principal_id must not be blank")


@dataclass(frozen=True, slots=True)
class RoomUsageSnapshot:
    input_tokens: int
    output_tokens: int
    normalized_cost: Decimal | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        if self.input_tokens < 0 or self.output_tokens < 0:
            raise InterfaceViolation("snapshot token usage must not be negative")
        if self.normalized_cost is not None and self.normalized_cost < 0:
            raise InterfaceViolation("snapshot cost must not be negative")
        if (self.normalized_cost is None) != (self.currency is None):
            raise InterfaceViolation("snapshot cost and currency must be set together")
        if self.currency is not None and (
            len(self.currency) != 3
            or not self.currency.isascii()
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise InterfaceViolation(
                "snapshot currency must be a three-letter uppercase code"
            )

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True, slots=True)
class RoomSnapshot:
    tenant_id: UUID
    application_id: UUID
    room_id: UUID
    mode: RoomMode
    state: RoomState
    generated_at: datetime
    last_sequence: int
    participants: tuple[RoomParticipantSnapshot, ...]
    agenda: tuple[RoomAgendaSnapshot, ...]
    findings: tuple[RoomFindingSnapshot, ...]
    decisions: tuple[RoomDecisionSnapshot, ...]
    usage: RoomUsageSnapshot
    recent_events: tuple[OrderedRoomEvent, ...] = ()

    def __post_init__(self) -> None:
        if self.last_sequence < 0:
            raise InterfaceViolation("snapshot last_sequence must not be negative")
        participant_ids = [item.participant_id for item in self.participants]
        if len(participant_ids) != len(set(participant_ids)):
            raise InterfaceViolation("snapshot participant IDs must be unique")

        sequences = [event.sequence for event in self.recent_events]
        if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
            raise InterfaceViolation("snapshot recent_events must be strictly ordered")
        if sequences and sequences[-1] > self.last_sequence:
            raise InterfaceViolation(
                "snapshot recent event cannot exceed last_sequence"
            )
        for event in self.recent_events:
            correlation = event.correlation
            if (
                correlation.tenant_id != self.tenant_id
                or correlation.application_id != self.application_id
                or correlation.room_id != self.room_id
            ):
                raise InterfaceViolation(
                    "snapshot event scope must match room scope"
                )


class ModelGateway(Protocol):
    async def generate_turn(self, request: ModelTurnRequest) -> ModelTurnResult: ...


class BudgetAuthority(Protocol):
    async def authorize_turn(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
    ) -> BudgetDecision: ...

    async def record_usage(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
        usage: UsageDelta,
    ) -> None: ...


class TurnExecutionGuard(Protocol):
    def hold(
        self,
        *,
        correlation: CorrelationContext,
    ) -> AsyncContextManager[None]: ...


class RoomReadAuthorizer(Protocol):
    async def authorize_read(
        self,
        *,
        request: RoomReadRequest,
        actor: TrustedActorContext,
    ) -> bool: ...


class RoomSnapshotSource(Protocol):
    async def load_snapshot(
        self,
        *,
        tenant_id: UUID,
        application_id: UUID,
        room_id: UUID,
        recent_event_limit: int = 100,
    ) -> RoomSnapshot: ...


class RoomCommandAuthorizer(Protocol):
    async def authorize(
        self,
        *,
        command: RoomCommand,
        actor: TrustedActorContext,
    ) -> bool: ...


class RoomEventSink(Protocol):
    async def append(
        self,
        event: RoomEventDraft,
        *,
        expected_state: RoomState | None = None,
        new_state: RoomState | None = None,
    ) -> OrderedRoomEvent: ...
