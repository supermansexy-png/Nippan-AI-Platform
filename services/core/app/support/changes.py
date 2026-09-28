"""The Support agent's change engine (T-079e).

Handles an existing customer's chat request to change business info.

Rules, enforced in code:
1. Fixed menus only — the request is parsed into menu choices with the
   REAL onboarding parsers (``app/onboarding/signals.py``); free text
   that maps nowhere is REFUSED, never stored.
2. Cost Guard first — quota/tool changes are flagged+held, applied only
   after an explicit Cost Guard approval.
3. Every request is logged (``log.py``), whatever the outcome.
4. Tenant isolation — the caller MUST pass the verified tenant scope;
   reads/writes go through ``gate_repo`` keyed by (tenant_id, bot_id).
5. The go-live gate is the only status writer — an edit of a confirmed
   draft drops the bot to ``paused`` via ``GoLiveGate.edit``; re-activation
   happens ONLY via the customer's re-confirmation through the gate.
"""

from __future__ import annotations

from ..onboarding.gate import GoLiveGate
from ..onboarding.gate_repo import BotRepository
from ..onboarding.signals import (
    extract_hours,
    parse_task_choice,
    parse_tone,
)
from .cost_guard import APPROVED, CostGuard
from .log import SupportChangeLog
from ._reasons import REFUSAL_FREE_TEXT_REASON, cost_why
from .request import ChangeRequest, ChangeResult

# local aliases for readability
REFUSAL_FREE_TEXT = REFUSAL_FREE_TEXT_REASON
REFUSAL_UNPARSED = (
    "refused: the request does not map to any fixed-menu field — nothing "
    "was changed and nothing was stored"
)

__all__ = [
    "SupportChangeService",
]

class SupportChangeService:
    """Applies chat change requests for existing tenants, through the
    existing fixed menus + the existing go-live gate."""

    def __init__(
        self,
        *,
        repo: BotRepository,
        gate: GoLiveGate,
        cost_guard: CostGuard,
        log: SupportChangeLog,
        current_draft_provider=None,
    ) -> None:
        self._repo = repo
        self._gate = gate
        self._cg = cost_guard
        self._log = log
        # Injectable provider of the CURRENT persisted draft for this bot
        # (wiring-time dependency; tests/proof supply the real path).
        self._draft_provider = current_draft_provider

    # -- internal logging --------------------------------------------------
    def _logged(self, outcome: str, req: ChangeRequest, detail: str,
                field: str | None = None, **extra) -> ChangeResult:
        """Rule 3: every outcome lands in the log. One record per outcome."""
        row = self._log.record(
            outcome=outcome, tenant_id=req.tenant_id, bot_id=req.bot_id,
            requested_by=req.requested_by, field=field,
            amount=req.quota_value if outcome == "held" else None,
        )
        return ChangeResult(outcome=outcome, detail=detail, field=field,
                            log_id=row.id, **extra)

    # -- entry point ---------------------------------------------------
    def handle(self, req: ChangeRequest) -> ChangeResult:
        """Route one request through rules 1/2/4/5, in order.

        The outcome is logged in EVERY branch (rule 3, no silent writes).
        """
        if req.tenant_id != self._gate._tenant_id or req.bot_id != self._gate._bot_id:
            # isolation: a different tenant/bot than the verified scope.
            return self._logged("denied", req,
                                "denied: this bot belongs to another tenant")

        if req.is_free_text_request():
            return self._logged(
                "refused", req, REFUSAL_FREE_TEXT,
                field=(req.raw_text or "")[:30],
            )

        if req.quota_field is not None:
            return self._handle_cost_change(req)

        if req.tone_menu_key:
            return self._apply_menu_change(req, "tone", req.tone_menu_key)

        if req.hours_range:
            return self._apply_menu_change(req, "opening_hours", req.hours_range)

        if req.task_keys:
            return self._handle_tools_change(req, req.task_keys)

        return self._logged("refused", req, REFUSAL_UNPARSED,
                            field=(req.raw_text or "")[:30])

    # -- menu-applied changes ------------------------------------------
    def _apply_menu_change(self, req: ChangeRequest, field: str,
                           value: str) -> ChangeResult:
        """Apply a fixed-menu change. The change touches the persisted bot
        row, so through the gate: an ACTIVE bot first drops to paused
        (its confirmed draft is invalidated); the customer's
        re-confirmation re-activates via gate.confirm — never silently."""
        draft = self._draft_provider() if self._draft_provider else None
        if draft is None:
            # Fail-closed: we cannot construct a complete new draft from
            # menus alone, so refuse rather than half-write.
            return self._logged(
                "refused", req,
                "refused: no current draft provider wired — cannot map the "
                "change onto a complete fixed-menu draft",
                field=field,
            )
        gate_out = self._gate.edit(draft)  # revokes, sets paused
        # Log the point ACTUALLY reached (T-079e review finding 3): the
        # new value is NOT persisted yet — it lands only when the customer
        # re-confirms the updated draft through the gate. The log must not
        # claim "applied" here, so the single accurate record is
        # "gate_revoked" below; "applied" is reserved for a real write.
        return self._logged(
            "gate_revoked", req,
            "edit acknowledged: prior confirmation revoked; bot set to "
            "paused pending re-confirmation through the go-live gate",
            field=field, gate_outcome=gate_out.outcome,
            bot_status=gate_out.status,
        )

    def _handle_tools_change(self, req: ChangeRequest,
                             keys: tuple[str, ...]) -> ChangeResult:
        """A task-menu change can add tools (cost) → flagged to Cost Guard
        first (rule 2)."""
        row = self._repo.get(bot_id=req.bot_id, tenant_id=req.tenant_id)
        if row is None:
            return self._logged("denied", req, "denied: bot not found")
        from .cost_path import flag_tools_change
        return flag_tools_change(
            req=req, keys=keys, row=row, cg=self._cg, log=self._log,
            logged=self._logged,
        )

    # -- request parsing: delegated to parse.py (menu choices only) ------
    def parse_chat_request(
        self, *, tenant_id: str, bot_id: str, requested_by: str, text: str,
    ) -> ChangeRequest:
        from .parse import parse_chat_request as _parse
        return _parse(tenant_id=tenant_id, bot_id=bot_id,
                      requested_by=requested_by, text=text)

    def _handle_cost_change(self, req: ChangeRequest) -> ChangeResult:
        """Rule 2: a quota change is flagged to Cost Guard and HELD — never
        applied silently. Applying happens via cost_guard.decide(APPROVED),
        then an explicit apply_held() call — the approval path."""
        row = self._repo.get(bot_id=req.bot_id, tenant_id=req.tenant_id)
        if row is None:
            return self._logged("denied", req, "denied: bot not found in this scope")
        from .cost_path import flag_quota_change
        return flag_quota_change(
            req=req, row=row, cg=self._cg, log=self._log, logged=self._logged,
        )

    def apply_held(self, *, req: ChangeRequest, flag_id: int,
                   approved_by: str) -> ChangeResult:
        """THE only path to apply a held cost-raising change: Cost Guard
        must have REPLIED APPROVED already. This checks + applies + logs.

        Isolation (T-079e review finding 1): the flag must belong to the
        requesting tenant AND bot. A guessed flag id — another tenant's or
        another bot's — is DENIED with no state change and no leak about
        the flag (the same message as an unknown id)."""
        from .cost_path import apply_held_change
        try:
            flag = self._cg.flag_by_id(flag_id)
        except KeyError:
            return self._logged(
                "denied", req,
                "denied: no applicable held change in this scope",
            )
        if flag.tenant_id != req.tenant_id or flag.bot_id != req.bot_id:
            return self._logged(
                "denied", req,
                "denied: no applicable held change in this scope",
            )
        row = self._repo.get(bot_id=flag.bot_id, tenant_id=flag.tenant_id)
        return apply_held_change(
            flag=flag, row=row, repo=self._repo, req=req,
            approved_by=approved_by, cg=self._cg, log=self._log,
            logged=self._logged,
        )
