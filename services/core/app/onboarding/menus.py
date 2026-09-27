"""Fixed menus — the ONLY values the onboarding assistant may produce.

Every produced config value must be a member of one of these enumerations.
Anything the prospect typed is parsed into one of these choices; if it
cannot be mapped, it is rejected (never guessed, never stored as free text).
"""

from __future__ import annotations

from enum import Enum


class Tone(str, Enum):
    """Fixed tone menu (CUSTOMER_FACING_RULES.md §3 — response tone from a
    fixed list)."""

    POLITE = "polite"
    FRIENDLY = "friendly"
    CONCISE = "concise"
    CHEERFUL = "cheerful"
    FORMAL = "formal"


class EnabledTool(str, Enum):
    """Fixed tool menu — only real tools from MCP_TOOLS_V1.md the onboarding
    flow may enable (`chat-bot-core`, `web-fetch`, `file-reader` per the
    card mandate; `web-fetch`/`file-reader` remain onboarding-only tools and
    are listed here as session tools, not bot runtime tools)."""

    CHAT_BOT_CORE = "chat-bot-core"
    MEMORY_STORE = "memory-store"
    HANDOFF_TO_OWNER = "handoff-to-owner"
    SECRETARY_BOT = "secretary-bot"


class BusinessType(str, Enum):
    """Fixed business-type menu (CUSTOMER_SEGMENTS.md chat/secretary style)."""

    CAFE = "cafe"
    RESTAURANT = "restaurant"
    RETAIL_SHOP = "retail_shop"
    SALON = "salon"
    SERVICES = "services"
    OTHER = "other"


# Fixed task menu for "which tasks do you want the bot to do?" — maps to
# EnabledTool choices the customer can turn on.identification of Thai and English phrasings to fixed keys.
TASK_MENU: dict[str, EnabledTool] = {
    "answer_customer_questions": EnabledTool.CHAT_BOT_CORE,
    "take_bookings": EnabledTool.SECRETARY_BOT,
    "remind_customers": EnabledTool.SECRETARY_BOT,
    "hand_off_to_owner": EnabledTool.HANDOFF_TO_OWNER,
}

# Thai/English phrases a prospect might say → fixed task-menu keys.
TASK_HINTS: dict[str, tuple[str, ...]] = {
    "answer_customer_questions": ("ตอบคำถาม", "คำถามลูกค้า"),
    "take_bookings": ("จองคิว", "จอง", "book"),
    "remind_customers": ("แจ้งเตือน", "เตือน", "remind"),
    "hand_off_to_owner": ("โอนให้เจ้าของ", "เจ้าของจัดการ"),
}


# Fixed tone question options presented to the prospect, mapped to Tone.
TONE_MENU: dict[str, Tone] = {
    "1": Tone.POLITE,
    "2": Tone.FRIENDLY,
    "3": Tone.CONCISE,
    "4": Tone.CHEERFUL,
    "5": Tone.FORMAL,
}


HOURS_PATTERN_LABEL = "HH:MM-HH:MM"


class UnmappedInputError(ValueError):
    """Customer input does not map to any fixed-menu value — REJECT, never
    guess (FAIL-CLOSED)."""
