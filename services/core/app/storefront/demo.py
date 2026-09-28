"""The live storefront demo bot and its OWN daily cap (T-079f Part 2).

Policy sources (read, never edited):
- ``docs/product/STOREFRONT.md`` Rules: the demo runs on the cheapest model
  tier and has its own daily cap; same honesty rules; same consent notice.
- ``docs/product/MODEL_POLICY.md`` "Tier by task": routine end-customer
  chat -> cheapest viable model (free tier or lowest-cost paid). The demo
  is routine chat, so its tier is the cheapest tier. The MODEL PIN itself
  lives in the roster — never hardcoded here (policy: "Never hardcode a
  model into a role").

Cap number: NO document defines a numeric demo daily cap (verified
2026-09-28 against STOREFRONT.md and MODEL_POLICY.md). It is therefore an
explicit configuration value (``NIPPAN_STOREFRONT_DEMO_DAILY_CAP``);
``None`` means the demo stays CLOSED (fail-closed) until the Owner sets a
number. No guessed default is buried in code.

Isolation: this service takes NO tenant repository, NO usage-tracker, NO
config access. Its counter is its own, keyed by UTC date. Demo traffic can
never spend a tenant's quota because there is no path to one.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime

from app.onboarding.page.prohibited import PROHIBITED_TOKENS

__all__ = [
    "DEMO_MODEL_TIER",
    "DEMO_CAP_REACHED_MESSAGE",
    "DEMO_UNAVAILABLE_MESSAGE",
    "DemoReply",
    "StorefrontDemoService",
    "demo_model_tier",
]

# MODEL_POLICY.md, "Tier by task, not by tenant", row 1: routine
# end-customer chat -> "Cheapest viable model (free tier or lowest-cost
# paid)". The demo is routine chat, so this is its tier — by policy, not
# by an invented routing rule.
DEMO_MODEL_TIER = "cheapest-viable (routine end-customer chat)"


def demo_model_tier() -> str:
    """The tier the demo runs on, per MODEL_POLICY.md tier-by-task."""
    return DEMO_MODEL_TIER


# Clean, non-technical stop message. No model or vendor name.
DEMO_CAP_REACHED_MESSAGE = (
    "ขอบคุณที่ลองคุยกับบอทตัวอย่าง วันนี้มีผู้ลองใช้เต็มจำนวนแล้ว "
    "กรุณากลับมาลองใหม่พรุ่งนี้ หรือกดปุ่มตั้งค่าบอทของคุณได้เลย"
)
DEMO_UNAVAILABLE_MESSAGE = (
    "เดโมบอทยังไม่เปิดให้ลองในขณะนี้ กรุณากลับมาใหม่ภายหลัง"
)


class DemoReply:
    def __init__(self, *, text: str, stopped: bool, remaining: int | None):
        self.text = text
        self.stopped = stopped  # True when the cap stopped the demo
        self.remaining = remaining  # demo exchanges left today (None if closed)


class StorefrontDemoService:
    """Answers demo visitors; enforces its own daily cap, server-side.

    ``llm`` is an injectable callable ``(visitor_text) -> reply_text`` —
    tests and the e2e proof use a stub; deployment wires the cheapest-tier
    model per the roster. ``daily_cap=None`` keeps the demo closed.
    """

    def __init__(
        self,
        *,
        llm: Callable[[str], str] | None,
        daily_cap: int | None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if daily_cap is not None and daily_cap < 1:
            raise ValueError("daily_cap must be a positive integer or None")
        self._llm = llm
        self._cap = daily_cap
        self._clock = clock or (lambda: datetime.now(UTC))
        self._count = 0
        self._day: date = self._today()

    def _today(self) -> date:
        return self._clock().astimezone(UTC).date()

    def _roll_day(self) -> None:
        today = self._today()
        if today != self._day:
            self._day = today
            self._count = 0

    @property
    def used_today(self) -> int:
        self._roll_day()
        return self._count

    def reply(self, visitor_text: str) -> DemoReply:
        """One demo exchange. The cap is checked BEFORE any model call."""
        self._roll_day()
        if self._cap is None or self._llm is None:
            return DemoReply(
                text=DEMO_UNAVAILABLE_MESSAGE, stopped=True, remaining=None
            )
        remaining = self._cap - self._count
        if remaining <= 0:
            return DemoReply(
                text=DEMO_CAP_REACHED_MESSAGE, stopped=True, remaining=0
            )
        text = self._llm(visitor_text)
        # Honesty rule: no model/vendor name may leave in a demo reply.
        lowered = text.lower()
        for token in PROHIBITED_TOKENS:
            if token.lower() in lowered:
                raise ValueError(
                    "demo reply contained a prohibited model/vendor name"
                )
        self._count += 1  # counts ONLY demo traffic; no tenant sink exists
        return DemoReply(
            text=text, stopped=False, remaining=self._cap - self._count
        )
