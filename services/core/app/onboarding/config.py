"""Fixed-menu bot config — the ONLY storable output shape of onboarding.

Every field is a menu enum member or a structured, typed field. There is
no free-text instruction field anywhere in this module, which makes rule
2 (no raw customer text as instructions) structurally obvious: the type
system has nowhere to put customer prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from .menus import BusinessType, EnabledTool, Tone

__all__ = ["BusinessHours", "ConfigDraft", "MissingField"]


@dataclass(frozen=True)
class BusinessHours:
    open: str  # e.g. "08:00"
    close: str  # e.g. "20:00"


@dataclass
class ConfigDraft:
    """The fixed-menu config rows this flow produces (BOTS table fields)."""

    tone: Tone | None = None
    business_type: BusinessType | None = None
    business_name: str | None = None
    opening_hours: BusinessHours | None = None
    menu_categories: tuple[str, ...] = ()
    enabled_tools: tuple[EnabledTool, ...] = ()
    fallback_contact: str | None = None  # phone / LINE — ND-2 required field
    monthly_message_quota: int = 300  # PRICING_V1 starter chat quota
    monthly_push_quota: int = 200  # LITE_SCHEMA default push cap

    def to_row(self) -> dict[str, Any]:
        """Serialize to fixed-menu config rows (bots.* shaped)."""
        return asdict(self)

    # ── ask only what is missing ─────────────────────────
    def missing_fields(self) -> tuple[str, ...]:
        """Fields still required before this draft can go live — the driver
        asks ONLY these, never a filled one again."""
        out: list[str] = []
        if self.tone is None:
            out.append("tone")
        if self.business_type is None:
            out.append("business_type")
        if not (self.business_name or "").strip():
            out.append("business_name")
        if self.opening_hours is None:
            out.append("opening_hours")
        if not self.menu_categories:
            out.append("menu_categories")
        if not self.enabled_tools:
            out.append("enabled_tools")
        if not (self.fallback_contact or "").strip():
            out.append("fallback_contact")
        return tuple(out)


@dataclass(frozen=True)
class MissingField:
    field_name: str
    question_key: str
