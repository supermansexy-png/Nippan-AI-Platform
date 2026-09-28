"""Cost Guard first (T-079e rule 2) — hold-and-approve for cost-raising
changes.

A change that could raise cost (a quota increase, enabling a more
expensive tool) is FLAGGED and HELD — never applied silently. It is
applied only through :meth:`CostGuard.decide` with an explicit
``APPROVED`` decision; the approval path is explicit in the code, not a
return value the caller can ignore. Anything else keeps the hold.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "COST_GUARD_STATUSES",
    "COST_GUARD_ROLE",
    "APPROVED",
    "REJECTED",
    "Actor",
    "cost_guard_actor",
    "CostGuardFlag",
    "CostGuard",
]

COST_GUARD_STATUSES = ("flagged", "held", "approved", "rejected")

APPROVED = "approved"
REJECTED = "rejected"

# The ONLY role allowed to decide a held flag (T-079e review finding 2) —
# enforced in code below, never by wiring convention.
COST_GUARD_ROLE = "cost_guard"


@dataclass(frozen=True)
class Actor:
    """Who makes a decision: a name plus an explicit role. A decision is
    attributable only when the actor object carries the Cost Guard role —
    a bare string cannot self-approve."""

    name: str
    role: str


def cost_guard_actor(name: str = "Cost Guard AI") -> Actor:
    """The canonical Cost Guard decider."""
    return Actor(name=name, role=COST_GUARD_ROLE)

# Which fields can raise cost — per LITE_SCHEMA_V1.md bots + PRICING_V1.
COST_FIELDS = ("monthly_message_quota", "monthly_push_quota", "enabled_tools")


@dataclass
class CostGuardFlag:
    """One held cost-raising change. ``applied`` flips True ONLY via
    :meth:`CostGuard.decide` — the explicit approval path."""

    flag_id: int
    tenant_id: str
    bot_id: str
    field: str
    current_value: object
    requested_value: object
    status: str = "flagged"  # flagged -> held -> approved/rejected
    explanation: str = ""  # fixed phrases from _reasons, never customer text
    applied: bool = False
    decided_by: str | None = None

    def decide(self, decision: str, decided_by: Actor) -> None:
        if self.applied:
            return
        if not isinstance(decided_by, Actor) or decided_by.role != COST_GUARD_ROLE:
            # fail-closed: no state change at all — the flag stays HELD.
            raise ValueError(
                "only an actor with the Cost Guard role may decide a flag"
            )
        self.status = decision
        self.decided_by = decided_by.name
        if decision == APPROVED:
            self.applied = True


class CostGuard:
    """Holds cost-raising changes until an explicit decision lands."""

    def __init__(self) -> None:
        self._flags: dict[int, CostGuardFlag] = {}
        self._next_id = 1

    def flag(self, *, tenant_id: str, bot_id: str, field: str,
             current_value: object, requested_value: object) -> CostGuardFlag:
        from ._reasons import cost_why

        row = CostGuardFlag(
            flag_id=self._next_id,
            tenant_id=tenant_id,
            bot_id=bot_id,
            field=field,
            current_value=current_value,
            requested_value=requested_value,
            status="held",
            explanation=cost_why(field),
        )
        self._next_id += 1
        self._flags[row.flag_id] = row
        return row

    def pending(self, *, tenant_id: str, bot_id: str) -> tuple[CostGuardFlag, ...]:
        return tuple(
            f for f in self._flags.values()
            if f.tenant_id == tenant_id and f.bot_id == bot_id and f.status == "held"
            and not f.applied
        )

    def flag_by_id(self, flag_id: int) -> CostGuardFlag:
        row = self._flags.get(flag_id)
        if row is None:
            raise KeyError(f"unknown flag {flag_id}")
        return row

    def decide(self, flag_id: int, *, decision: str, decided_by: Actor) -> CostGuardFlag:
        """THE approval path. ``decision`` must be APPROVED or REJECTED.

        Only an explicit APPROVED sets ``applied`` True; everything else
        keeps the hold (fail-closed: no approval -> no write ever.
        """
        if decision not in (APPROVED, REJECTED):
            raise ValueError(f"decision must be {APPROVED!r} or {REJECTED!r}")
        row = self.flag_by_id(flag_id)
        row.decide(decision, decided_by)
        return row
