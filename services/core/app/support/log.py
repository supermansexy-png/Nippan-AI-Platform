"""Support agent change path (T-079e) — logging seam.

Rule 3 (every change is logged, no silent writes): every request the
Support agent handles — applied, held, refused, or denied — produces one
``SupportChange_log`` record. This is the visible run log; Phase A has no
admin page (`TASKS.md` T-079e scope), so the in-process log IS the record.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

__all__ = [
    "SUPPORT_CHANGE_OUTCOMES",
    "SupportChange_log",
    "SupportChangeLog",
]


# Outcomes are CLOSED: a request never disappears unrecorded. HOLD is the
# Cost Guard state (flagged + not applied); DENIED is tenant isolation;
# REFUSED is fixed-menu; APPLIED is a real write.
SUPPORT_CHANGE_OUTCOMES = ("applied", "held", "refused", "denied", "gate_revoked")


@dataclass
class SupportChange_log:
    """One logged change request (structured, no free text stored as
    instructions — ``detail`` carries the refused free text ONLY in the
    log record so the run can show the refusal; it is never persisted to
    the bot config)."""

    id: int
    outcome: str  # one of SUPPORT_CHANGE_OUTCOMES
    tenant_id: str
    bot_id: str
    field: str | None  # the config field the request touched, if any
    requested_by: str
    created_at: float = field(default_factory=time.time)
    note: str = ""  # short fixed-phrase note, not customer prose
    amount: int | None = None  # for held cost changes: the requested value


class SupportChangeLog:
    """In-process append-only log with a tenant-scoped read seam."""

    def __init__(self) -> None:
        self._rows: list[SupportChange_log] = []
        self._next_id = 1

    def record(
        self,
        *,
        outcome: str,
        tenant_id: str,
        bot_id: str,
        requested_by: str,
        field: str | None = None,
        note: str = "",
        amount: int | None = None,
    ) -> SupportChange_log:
        if outcome not in SUPPORT_CHANGE_OUTCOMES:
            raise ValueError(f"unknown outcome {outcome!r}")
        if not tenant_id or not bot_id:
            raise ValueError("tenant_id and bot_id are required")
        row = SupportChange_log(
            id=self._next_id,
            outcome=outcome,
            tenant_id=tenant_id,
            bot_id=bot_id,
            field=field,
            requested_by=requested_by,
            note=note,
            amount=amount,
        )
        self._next_id += 1
        self._rows.append(row)
        return row

    def for_tenant(self, *, tenant_id: str) -> tuple[SupportChange_log, ...]:
        """Isolation: a scope only reads its own log rows."""
        return tuple(r for r in self._rows if r.tenant_id == tenant_id)
