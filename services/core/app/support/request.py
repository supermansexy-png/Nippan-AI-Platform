"""Change request shapes for the Support agent (T-079e).

A chat request is parsed into menu choices ONLY — the same rule
T-079b/T-079c enforce: the prospect's/customer's message is never stored
as an instruction; unmapped text stays in ``raw_text`` solely so the run
log can show the refusal, and is persisted nowhere.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "SUPPORTED_FIELDS",
    "FREE_TEXT_FIELDS",
    "ChangeRequest",
    "ChangeResult",
]

# The fixed fields an existing customer may change via Support — each one
# maps onto the same fixed menus Onboarding produces (CUSTOMER_FACING_RULES §3).
SUPPORTED_FIELDS = ("tone", "opening_hours", "enabled_tools",
                    "monthly_message_quota", "monthly_push_quota")

# Anything else a customer might ask to set — refused by name.
FREE_TEXT_FIELDS = ("instructions", "system_prompt", "prompt", "custom_message",
                    "free_text", "raw_text", "persona")


@dataclass
class ChangeRequest:
    """One parsed chat change request — menu choices only, no raw text."""
    tenant_id: str
    bot_id: str
    requested_by: str  # e.g. "owner:<contact>" — who asked, for the log
    tone_menu_key: str | None = None  # '1'..'5' from parse_tone
    hours_range: str | None = None  # "HH:MM-HH:MM" from extract_hours
    task_keys: tuple[str, ...] = ()  # fixed task-menu keys from parse_task_choice
    quota_field: str | None = None  # monthly_message_quota / monthly_push_quota
    quota_value: int | None = None
    raw_text: str | None = None  # kept for the run log only, never persisted

    def is_free_text_request(self) -> bool:
        """A request whose text asks for instructions/prompt changes —
        refused outright, never parsed as a menu choice."""
        low = (self.raw_text or "").lower()
        return any(tok in low for tok in FREE_TEXT_FIELDS)


@dataclass
class ChangeResult:
    """What the Support agent did with one request — the visible outcome."""
    outcome: str  # applied / held / refused / denied / gate_revoked
    detail: str  # fixed phrase; never customer prose
    field: str | None = None
    flag_id: int | None = None  # set when outcome == "held"
    log_id: int | None = None
    gate_outcome: str | None = None  # e.g. "edit_acknowledged" (goes paused)
    bot_status: str | None = None  # status after the request, if known
