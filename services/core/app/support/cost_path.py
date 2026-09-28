"""Cost-raising change handlers for the Support path (T-079e rule 2).

A quota increase or a tool change is FLAGGED to Cost Guard and HELD —
never applied silently. Applying happens ONLY through the explicit
approval path: ``CostGuard.decide(flag_id, decision=APPROVED, ...)`` then
``SupportChangeService.apply_held(...)``.
"""

from __future__ import annotations

from .cost_guard import APPROVED, CostGuard
from ._reasons import cost_why
from .request import ChangeRequest, ChangeResult
from .log import SupportChangeLog

__all__ = ["flag_quota_change", "apply_held_change", "flag_tools_change"]

QUOTA_FIELDS = ("monthly_message_quota", "monthly_push_quota")


def flag_quota_change(
    *, req: ChangeRequest, row, cg: CostGuard, log: SupportChangeLog,
    logged,  # the service's _logged bound method for uniform outcomes
) -> ChangeResult:
    if req.quota_field not in QUOTA_FIELDS:
        from .changes import REFUSAL_UNPARSED
        return logged("refused", req, REFUSAL_UNPARSED, field=req.quota_field)
    if req.quota_value is None or not isinstance(req.quota_value, int):
        return logged("refused", req,
                      "refused: quota must be an integer value",
                      field=req.quota_field)
    current = getattr(row, req.quota_field, None)
    flag = cg.flag(
        tenant_id=req.tenant_id, bot_id=req.bot_id,
        field=req.quota_field,
        current_value=current, requested_value=req.quota_value,
    )
    res = logged(
        "held", req, cost_why(req.quota_field), field=req.quota_field,
        flag_id=flag.flag_id,
    )
    log.record(
        outcome="held", tenant_id=req.tenant_id, bot_id=req.bot_id,
        requested_by=req.requested_by, field=req.quota_field,
        note="cost guard flag id=%d" % flag.flag_id, amount=req.quota_value,
    )
    return res


def apply_held_change(
    *, flag, row, repo, req: ChangeRequest, approved_by: str,
    cg: CostGuard, log: SupportChangeLog, logged,
) -> ChangeResult:
    """Guard + write + log. The write happens ONLY when the flag already
    says APPROVED (fail-closed: no explicit approval → no write)."""
    if flag.status != APPROVED:
        return logged(
            "held", req,
            "not applied: flag %d is still held — explicit Cost Guard "
            "approval required first" % flag.flag_id,
            field=flag.field,
        )
    if row is None:
        return logged("denied", req, "denied: bot not found")
    setattr(row, flag.field, flag.requested_value)
    repo.save(row)
    flag.applied = True
    return logged(
        "applied", req,
        "applied: Cost Guard approved by %r; %s set to %r" % (
            approved_by, flag.field, flag.requested_value),
        field=flag.field,
    )


def flag_tools_change(
    *, req: ChangeRequest, keys: tuple[str, ...], row, cg: CostGuard,
    log: SupportChangeLog, logged,
) -> ChangeResult:
    """A tools change can ADD per-call cost → flagged+held like quotas
    (one simple, safe rule for every cost-raising change)."""
    from ..onboarding.menus import TASK_MENU

    if any(k not in TASK_MENU for k in keys):
        return logged("refused", req, "refused: task not in fixed menu",
                      field="enabled_tools")
    new_tools = tuple(sorted({TASK_MENU[k].value for k in keys}))
    flag = cg.flag(
        tenant_id=req.tenant_id, bot_id=req.bot_id,
        field="enabled_tools",
        current_value=tuple(row.enabled_tools),
        requested_value=new_tools,
    )
    res = logged("held", req, cost_why("enabled_tools"),
                 field="enabled_tools", flag_id=flag.flag_id)
    log.record(
        outcome="held", tenant_id=req.tenant_id, bot_id=req.bot_id,
        requested_by=req.requested_by, field="enabled_tools",
        note="cost guard flag id=%d" % flag.flag_id,
    )
    return res
