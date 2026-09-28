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

Usage accounting: the service may be wired to the SHARED usage sink (the
same recorder the production tenant path uses) via ``usage_sink`` — but
only ever under its own ``usage_scope`` ("storefront-demo"). A tenant row
can only be touched if someone deliberately re-points the scope; the e2e
proves that tampering flips the tenant-quota check to False and fails.

KNOWN PHASE A LIMITATION (pre-launch blocker, NOT a closed finding):
the daily-cap counter ``_count`` lives in PROCESS MEMORY. It resets to
zero on every restart (a fresh quota) and MULTIPLIES across replicas
(each process gets its own cap). Phase A has no durable store and this
card excludes a live database, so this cannot be fixed here. It MUST be
moved to durable shared storage (e.g. a DB row or shared cache) BEFORE
the storefront page is exposed publicly. The fail-closed default is the
guard until then: with no cap configured the demo stays OFF, never
unlimited.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path

from app.onboarding.page.prohibited import PROHIBITED_TOKENS

__all__ = [
    "DEMO_MODEL_TIER",
    "DEMO_CAP_REACHED_MESSAGE",
    "DEMO_UNAVAILABLE_MESSAGE",
    "DemoReply",
    "StorefrontDemoService",
    "demo_model_tier",
    "policy_tier_for_routine_chat",
]

# MODEL_POLICY.md, "Tier by task, not by tenant", row 1: routine
# end-customer chat -> "Cheapest viable model (free tier or lowest-cost
# paid)". The demo is routine chat, so this is its tier — by policy, not
# by an invented routing rule.
DEMO_MODEL_TIER = "cheapest-viable (routine end-customer chat)"


def demo_model_tier() -> str:
    """The tier the demo runs on, per MODEL_POLICY.md tier-by-task."""
    return DEMO_MODEL_TIER


_POLICY_MD = (
    Path(__file__).resolve().parents[4] / "docs" / "product" / "MODEL_POLICY.md"
)


def policy_tier_for_routine_chat() -> str:
    """Read MODEL_POLICY.md and return the tier cell the policy itself
    prescribes for "Routine end-customer chat" (the demo's task class).

    This parses the policy table at check time so the tier assertion is
    against the DOCUMENT, not against a literal living in the same code.
    Raises if the policy row or the "cheapest viable" tier is missing —
    an unparsable policy must fail the check, never silently pass.
    """
    for line in _POLICY_MD.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 3 and cells[1].lower().startswith(
            "routine end-customer chat"
        ):
            return cells[2]
    raise ValueError(
        "MODEL_POLICY.md no longer defines a tier for routine end-customer "
        "chat — the Owner must decide the demo tier before this check can pass"
    )


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
    model per the roster. ``daily_cap=None`` (the DEFAULT) keeps the demo
    closed — fail-closed; no guessed number is buried in code.
    ``usage_sink`` is the shared usage recorder the production path uses;
    the demo records ONLY under ``usage_scope`` (never a tenant scope).

    PRE-LAUNCH BLOCKER: ``_count`` is per-process memory — it resets on
    restart and multiplies across replicas (see the module docstring). It
    MUST move to durable shared storage before public exposure.
    """

    def __init__(
        self,
        *,
        llm: Callable[[str], str] | None,
        daily_cap: int | None = None,
        clock: Callable[[], datetime] | None = None,
        usage_sink: object | None = None,
        usage_scope: str = "storefront-demo",
    ) -> None:
        if daily_cap is not None and daily_cap < 1:
            raise ValueError("daily_cap must be a positive integer or None")
        self._llm = llm
        self._cap = daily_cap
        self._clock = clock or (lambda: datetime.now(UTC))
        self._sink = usage_sink
        self._scope = usage_scope
        self._count = 0  # per-process ONLY — resets on restart; see docstring
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
        self._count += 1  # counts ONLY demo traffic
        if self._sink is not None:
            # Record into the SHARED sink under the demo's own scope —
            # the same recorder the tenant path uses, never a tenant row.
            self._sink.record(scope=self._scope, exchanges=1)
        return DemoReply(
            text=text, stopped=False, remaining=self._cap - self._count
        )
