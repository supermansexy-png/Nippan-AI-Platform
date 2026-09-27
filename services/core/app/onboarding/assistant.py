"""The onboarding session driver with an injectable LLM.

Structural guarantee: the ONLY text ever sent to the model on the
instruction side is ``SYSTEM_PROMPTS`` — fixed constants written by the
platform in code. The prospect's words go to the model only inside the
``user_text`` data slot of the parse request, and the model's answer is
discarded — the driver parses the prospect's text itself into menu keys.
The model's ONLY job here is picking a menu key from a fixed list, and
that output is validated against the menu — an invalid/guessed value is
REJECTED, never stored.
"""

from __future__ import annotations

from typing import Protocol

from .config import ConfigDraft
from .menus import TONE_MENU, BusinessType, EnabledTool, Tone, UnmappedInputError

__all__ = ["LLMClient", "OnboardingSession", "SYSTEM_PROMPTS"]


class LLMClient(Protocol):
    """Injectable model call — the whole flow runs with a stub, no paid
    call, no network. No provider, key, or model slug is hardcoded here."""

    def complete(self, *, system_prompt: str, user_text: str) -> str: ...


# Fixed system prompts — platform text, never built from customer words.
SYSTEM_PROMPTS: dict[str, str] = {
    "parse": (
        "You are Nippan onboarding assistant. You classify the prospect's "
        "answer into EXACTLY one of the numbered menu options given in the "
        "user data. Reply with ONLY the option number. If nothing fits, "
        "reply NONE."
    ),
}


class OnboardingSession:
    """Conversation driver: ingest signals → fill ConfigDraft → ask missing.

    Ask-only-what-is-missing: ``next_questions`` derives from
    ``draft.missing_fields()`` — a filled field is never re-asked.
    """

    def __init__(self, *, draft: ConfigDraft | None = None, llm: LLMClient | None = None) -> None:
        self.draft = draft or ConfigDraft()
        self._llm = llm

    # ── tone ─────────────────────────────────────────────
    def offer_tone_menu(self, answer: str | None) -> str | None:
        """Update tone from the prospect's answer, mapped strictly to the
        fixed ``TONE_MENU`` options ('1'..'5'). Unknown text → ``None`` and
        the tone stays unset — the caller re-asks; never guessed."""
        if not answer or not answer.strip():
            return None
        key = answer.strip() if answer.strip() in TONE_MENU else _tone_menu_key(answer)
        if key is None:
            return None
        self.draft.tone = TONE_MENU[key]
        return self.draft.tone.value

    # ── business type ────────────────────────────────────
    def set_business_type(self, answer: str) -> str | None:
        """Business type strictly from the fixed menu — unmapped text raises
        ``UnmappedInputError`` (REJECT, never guess)."""
        from .signals import parse_business_type

        value = parse_business_type(answer)
        if value is None:
            raise UnmappedInputError(f"business type not in fixed menu: {answer!r}")
        self.draft.business_type = BusinessType(value)
        return value

    def set_business_name(self, name: str) -> None:
        name = (name or "").strip()[:80]
        if not name:
            raise ValueError("business_name is required")
        self.draft.business_name = name

    # ── hours ────────────────────────────────────────────
    def set_opening_hours(self, answer: str) -> str | None:
        """Parse HH:MM-HH:MM out of what the prospect typed; stores only the
        structured range, never the raw sentence."""
        from .signals import extract_hours

        hours = extract_hours(answer)
        if hours is None:
            raise UnmappedInputError(f"no HH:MM-HH:MM range found in {answer!r}")
        o, c = hours.split("-")
        from .config import BusinessHours

        self.draft.opening_hours = BusinessHours(open=o, close=c)
        return hours

    # ── categories (from file/URL reads) ─────────────────
    def set_menu_categories(self, names: list[str]) -> tuple[str, ...]:
        from .signals import extract_category_names
        from .cost_bounds import MAX_CATEGORIES

        # Re-filter every candidate through the data-only extractor:
        # values failing the charset whitelist are dropped, and if nothing
        # valid remains the input is REJECTED (never stored, never guessed).
        cleaned: list[str] = []
        for candidate in names:
            for n in extract_category_names(candidate or ""):
                if n and n not in cleaned:
                    cleaned.append(n)
                if len(cleaned) >= MAX_CATEGORIES:
                    break
            if len(cleaned) >= MAX_CATEGORIES:
                break
        if not cleaned:
            raise UnmappedInputError("no valid category names extracted")
        self.draft.menu_categories = tuple(cleaned)
        return self.draft.menu_categories

    # ── enabled tools (fixed task menu only) ─────────────
    def set_enabled_tools(self, answer: str) -> tuple[EnabledTool, ...]:
        """Map a task answer onto the fixed task menu. Unmapped-only input
        raises ``UnmappedInputError`` (REJECT)."""
        from .menus import TASK_MENU
        from .signals import parse_task_choice

        keys = parse_task_choice(answer)
        if not keys:
            raise UnmappedInputError(f"task answer not in fixed menu: {answer!r}")
        tools: list[EnabledTool] = []
        for k in keys:
            tool = TASK_MENU[k]
            if tool not in tools:
                tools.append(tool)
        if EnabledTool.CHAT_BOT_CORE not in tools:
            tools.insert(0, EnabledTool.CHAT_BOT_CORE)
        self.draft.enabled_tools = tuple(tools)
        return self.draft.enabled_tools

    def set_fallback_contact(self, contact: str) -> None:
        contact = (contact or "").strip()[:60]
        if not contact:
            raise ValueError("fallback_contact is required")
        self.draft.fallback_contact = contact

    # ── ask only what is missing ─────────────────────────
    def next_questions(self) -> tuple[str, ...]:
        """What is still missing — the ONLY questions the flow asks."""
        return self.draft.missing_fields()

    # ── optional model call (stub-able; menu-choice only) ─
    def classify_with_llm(self, *, menu: dict[str, str], user_text: str) -> str:
        """Optional assist: a model picks ONE of the given menu options.

        The system prompt is a fixed constant; ``user_text`` carries the
        prospect's words as DATA. The model's output must be one of the
        menu keys — anything else (freestyle prose, invented option) is
        REJECTED with ``UnmappedInputError``; nothing guessed is stored.
        No LLM configured → raises (no hidden paid call).
        """
        if self._llm is None:
            raise UnmappedInputError("no LLM configured for classify (stub-only flow)")
        options = "\n".join(f"{k}. {v}" for k, v in menu.items())
        user = f"Menu options:\n{options}\n\nProspect said: {user_text}"
        reply = self._llm.complete(system_prompt=SYSTEM_PROMPTS["parse"], user_text=user)
        key = reply.strip()
        if key not in menu:
            raise UnmappedInputError(f"model returned non-menu value: {key!r}")
        return key


def _tone_menu_key(text: str) -> str | None:
    """Map free-form tone wording onto a TONE_MENU key; None if no fit."""
    from .signals import parse_tone

    return parse_tone(text)
