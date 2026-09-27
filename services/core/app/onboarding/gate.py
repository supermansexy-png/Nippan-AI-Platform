"""Go-live gate (T-079d part 1) — the ONLY way a bot reaches ``active``.

Three outcomes, and only these: CONFIRM (of the current draft), EDIT
(invalidation of a prior confirmation), DECLINE. Activation requires an
explicit confirmation of a COMPLETE draft; every other path is
fail-closed. No page, no payment, no model config — Part 2 renders.

Edit-after-confirm semantics (the safe behaviour, settled here): any edit
to the session draft REVOKES the confirmation and sets the persisted bot
status back to ``paused`` — an active bot never keeps running on a draft
the customer has not re-confirmed (fail-closed). Confirming an incomplete
draft is refused and never persists ``active``.
"""

from __future__ import annotations

from types import MappingProxyType

from .config import ConfigDraft
from .gate_repo import BotRecord, BotRepository
from .menus import Tone

__all__ = [
    "GateOutcome",
    "GateError",
    "GoLiveGate",
]

# Column names/shape per LITE_SCHEMA_V1.md §bots; every persisted value is
# fixed-menu output of ConfigDraft — never raw prospect text as instructions.
_WHITELIST = MappingProxyType({
    "tone": lambda d: d.tone.value if isinstance(d.tone, Tone) else None,
    "business_info": lambda d: d.to_row(),  # structured fields incl. fallback contact, hours, categories
    "enabled_tools": lambda d: tuple(t.value for t in d.enabled_tools),
    "monthly_message_quota": lambda d: d.monthly_message_quota,
    "monthly_push_quota": lambda d: d.monthly_push_quota,
})


class GateError(RuntimeError):
    """A gate transition was refused — the bot stays inactive."""


class GateOutcome:
    """Result facts: what happened and what the bot row now says."""

    __slots__ = ("outcome", "status", "bot")

    def __init__(self, outcome: str, status: str, bot: BotRecord) -> None:
        self.outcome = outcome
        self.status = status
        self.bot = bot


class GoLiveGate:
    """Drives the existing onboarding draft's go-live transitions."""

    def __init__(self, repo: BotRepository, *, tenant_id: str, bot_id: str) -> None:
        self._repo = repo
        self._tenant_id = tenant_id
        self._bot_id = bot_id

    # ── current persisted row (fail-closed: missing row reads as paused) ──
    def _row(self) -> BotRecord:
        row = self._repo.get(bot_id=self._bot_id, tenant_id=self._tenant_id)
        if row is None:
            row = BotRecord(bot_id=self._bot_id, tenant_id=self._tenant_id, status="paused")
        return row

    def _draft_complete(self, draft: ConfigDraft) -> bool:
        return not draft.missing_fields()

    # ── CONFIRM: the only path to active ─────────────────────────────────
    def confirm(self, draft: ConfigDraft) -> GateOutcome:
        """Explicit confirmation of the CURRENT draft.

        Refused when the draft is incomplete: nothing is written with
        ``active`` — the persisted status stays/becomes ``paused``.
        Idempotent: re-confirming the same complete draft writes the same
        row; no double activation, no duplicate side effects.
        """
        if not self._draft_complete(draft):
            row = self._row()
            # Persist nothing as active; ensure it is (or becomes) paused.
            if row.status != "paused":
                row.status = "paused"
                self._repo.save(row)
            raise GateError(
                "confirm refused: draft incomplete (" + ", ".join(draft.missing_fields()) + ")"
            )
        row = self._row()
        _apply_draft(row, draft)
        row.status = "active"
        saved = self._repo.save(row)
        return GateOutcome("confirmed", saved.status, saved)

    # ── EDIT: revokes prior confirmation, fail-closed ────────────────────
    def edit(self, draft: ConfigDraft) -> GateOutcome:
        """Any edit invalidates the confirmation: the active bot is set back
        to ``paused`` IMMEDIATELY (never left running on an unconfirmed
        draft). The edited draft is not persisted as config until the
        customer confirms again — the stale row simply drops to paused."""
        row = self._row()
        row.status = "paused"
        saved = self._repo.save(row)
        return GateOutcome("edit_acknowledged", saved.status, saved)

    # ── DECLINE: never activates anything ────────────────────────────────
    def decline(self) -> GateOutcome:
        row = self._row()
        row.status = "paused"
        saved = self._repo.save(row)
        return GateOutcome("declined", saved.status, saved)


def _apply_draft(row: BotRecord, draft: ConfigDraft) -> None:
    """Copy ONLY whitelisted fixed-menu fields onto the row."""
    from dataclasses import asdict

    info = draft.to_row()
    # business_info carries structured fields the schema expects, excluding
    # the scalar columns kept in their own bots columns.
    info.pop("tone", None)
    business_info = {
        "business_name": info["business_name"],
        "business_type": info["business_type"],
        "opening_hours": asdict(draft.opening_hours) if draft.opening_hours else None,
        "menu_categories": list(info["menu_categories"]),
        "fallback_contact": info["fallback_contact"],
    }
    row.tone = _WHITELIST["tone"](draft)
    row.business_info = business_info
    row.enabled_tools = _WHITELIST["enabled_tools"](draft)
    row.monthly_message_quota = _WHITELIST["monthly_message_quota"](draft)
    row.monthly_push_quota = _WHITELIST["monthly_push_quota"](draft)
