from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from decimal import Decimal
from typing import AsyncIterator, Protocol

from app.db import Database

from .contracts import HaltReason
from .interfaces import (
    BudgetDecision,
    BudgetLimit,
    CorrelationContext,
    UsageDelta,
)


@dataclass(frozen=True, slots=True)
class UsageTotals:
    room_tokens: int = 0
    agenda_tokens: int = 0
    participant_tokens: int = 0
    room_cost: Decimal = Decimal("0")
    agenda_cost: Decimal = Decimal("0")
    participant_cost: Decimal = Decimal("0")
    currency: str = "USD"

    def __post_init__(self) -> None:
        numeric = (
            self.room_tokens,
            self.agenda_tokens,
            self.participant_tokens,
        )
        if any(value < 0 for value in numeric):
            raise ValueError("usage token totals must not be negative")
        costs = (self.room_cost, self.agenda_cost, self.participant_cost)
        if any(value < 0 for value in costs):
            raise ValueError("usage cost totals must not be negative")


@dataclass(frozen=True, slots=True)
class BudgetPolicy:
    room: BudgetLimit
    agenda: BudgetLimit
    participant: BudgetLimit


class BudgetPolicyResolver(Protocol):
    async def resolve(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
    ) -> BudgetPolicy: ...


class UsageEvidenceStore(Protocol):
    """Adapter over the platform request/ai_call/UsageEvent source of truth."""

    async def read_totals(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
    ) -> UsageTotals: ...

    async def record_usage(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
        usage: UsageDelta,
    ) -> None: ...


class UsageBackedBudgetAuthority:
    """Enforces hard limits without creating a second usage/cost ledger."""

    def __init__(
        self,
        *,
        policy_resolver: BudgetPolicyResolver,
        usage_store: UsageEvidenceStore,
    ) -> None:
        self._policy_resolver = policy_resolver
        self._usage_store = usage_store

    async def authorize_turn(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
    ) -> BudgetDecision:
        policy = await self._policy_resolver.resolve(
            correlation=correlation,
            participant_id=participant_id,
        )
        totals = await self._usage_store.read_totals(
            correlation=correlation,
            participant_id=participant_id,
        )

        checks = (
            (
                totals.room_tokens,
                totals.room_cost,
                policy.room,
                HaltReason.ROOM_BUDGET_EXHAUSTED,
            ),
            (
                totals.agenda_tokens,
                totals.agenda_cost,
                policy.agenda,
                HaltReason.AGENDA_BUDGET_EXHAUSTED,
            ),
            (
                totals.participant_tokens,
                totals.participant_cost,
                policy.participant,
                HaltReason.PARTICIPANT_BUDGET_EXHAUSTED,
            ),
        )

        remaining_tokens: list[int] = []
        for used_tokens, used_cost, limit, reason in checks:
            token_remaining = limit.token_limit - used_tokens
            if token_remaining <= 0:
                return BudgetDecision(allowed=False, halt_reason=reason)
            remaining_tokens.append(token_remaining)

            if limit.cost_limit is not None:
                if totals.currency != limit.currency:
                    raise ValueError(
                        "budget currency does not match usage evidence currency"
                    )
                if used_cost >= limit.cost_limit:
                    return BudgetDecision(allowed=False, halt_reason=reason)

        return BudgetDecision(
            allowed=True,
            max_output_tokens=min(remaining_tokens),
        )

    async def record_usage(
        self,
        *,
        correlation: CorrelationContext,
        participant_id: str,
        usage: UsageDelta,
    ) -> None:
        await self._usage_store.record_usage(
            correlation=correlation,
            participant_id=participant_id,
            usage=usage,
        )



class PostgresRoomTurnGuard:
    """Serializes billable War Room turns per tenant/application/room.

    The advisory transaction lock is held across budget authorization, the
    single provider request, usage recording, and event persistence. This
    removes the War Room check-then-act race without introducing a second
    reservation ledger.
    """

    def __init__(self, database: Database) -> None:
        self._database = database

    @asynccontextmanager
    async def hold(
        self,
        *,
        correlation: CorrelationContext,
    ) -> AsyncIterator[None]:
        lock_key = (
            f"{correlation.tenant_id}:"
            f"{correlation.application_id}:"
            f"{correlation.room_id}"
        )
        async with self._database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            await conn.execute(
                "select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (lock_key,),
            )
            yield
