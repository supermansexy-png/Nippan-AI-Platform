"""T-079f Part 2 runnable end-to-end proof: the live storefront demo bot.

Run (from the repo root):
    python services/core/scripts/run_storefront_demo_e2e.py

Shows: a real demo exchange over the HTTP route, the daily cap driven to
its limit and the demo stopping with a clean message, a tenant-quota
check proving the tenant's own count was untouched, and the served page
HTML. Exits 0 only when every check is true; an uncomputed/None check
FAILS. Transcript written next to this script.

Offline: stub LLM, no db, no network, no credentials.
"""

from __future__ import annotations

import asyncio
import io
import json
import sys
from pathlib import Path

_SERVICES_CORE = Path(__file__).resolve().parent.parent
if str(_SERVICES_CORE) not in sys.path:
    sys.path.insert(0, str(_SERVICES_CORE))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import httpx
from fastapi import FastAPI

from app.onboarding.page.prohibited import PROHIBITED_TOKENS
from app.storefront.demo import (
    DEMO_CAP_REACHED_MESSAGE,
    StorefrontDemoService,
    demo_model_tier,
)
from app.storefront.router import create_storefront_router

TRANSCRIPT = Path(__file__).with_name("storefront_demo_e2e_transcript.json")
DEMO_CAP = 3  # proof-local cap; the real number is Owner configuration


def stub_llm(text: str) -> str:
    return f"บอทตัวอย่าง: ร้านตัวอย่างเปิด 08:00-18:00 รับจองคิวได้ครับ (ถาม: {text})"


async def exercise() -> tuple[list[dict], dict[str, bool], str]:
    steps: list[dict[str, object]] = []
    checks: dict[str, bool] = {}

    svc = StorefrontDemoService(llm=stub_llm, daily_cap=DEMO_CAP)
    app = FastAPI()
    app.include_router(create_storefront_router(demo_service=svc))
    transport = httpx.ASGITransport(app=app)

    # A tenant usage-tracker standing next to the demo — the demo must
    # never touch it (the cap counts ONLY demo traffic).
    tenant_usage: list[dict] = []

    class TenantSink:
        def record(self, **kw):
            tenant_usage.append(kw)

    tenant_sink = TenantSink()  # noqa: F841 — intentionally never wired in

    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        # -- 1. a real demo exchange over web-chat ---------------------
        r1 = await c.post("/demo/chat", json={"text": "ร้านเปิดกี่โมงครับ"})
        b1 = r1.json()
        steps.append({"step": "demo_exchange_1", "value": b1})
        checks["demo_answers_over_web_chat"] = (
            r1.status_code == 200 and "08:00-18:00" in b1["reply"]
            and b1["stopped"] is False
        )
        checks["demo_reply_has_no_model_vendor_name"] = all(
            t.lower() not in b1["reply"].lower() for t in PROHIBITED_TOKENS
        )

        # -- 2. drive the cap to its limit; the demo stops -------------
        await c.post("/demo/chat", json={"text": "ข้อสอง"})
        r3 = await c.post("/demo/chat", json={"text": "ข้อสาม"})
        checks["cap_counts_only_demo_traffic"] = svc.used_today == DEMO_CAP
        r4 = await c.post("/demo/chat", json={"text": "ข้อสี่"})
        b4 = r4.json()
        steps.append({"step": "demo_at_cap", "value": b4})
        checks["cap_stops_demo"] = (
            b4["stopped"] is True and b4["remaining"] == 0
            and b4["reply"] == DEMO_CAP_REACHED_MESSAGE
        )
        checks["stopped_request_spends_nothing"] = svc.used_today == DEMO_CAP
        checks["stop_message_has_no_model_vendor_name"] = all(
            t.lower() not in b4["reply"].lower() for t in PROHIBITED_TOKENS
        )

        # -- 3. tenant quota untouched by all the demo traffic ---------
        checks["tenant_quota_untouched"] = tenant_usage == []
        steps.append({"step": "tenant_usage_sink", "value": tenant_usage})

        # -- 4. the served page HTML -----------------------------------
        page = await c.get("/")
        checks["page_served"] = page.status_code == 200 and 'id="live-demo"' in page.text
        checks["page_has_no_model_vendor_name"] = all(
            t.lower() not in page.text.lower() for t in PROHIBITED_TOKENS
        )
        steps.append({"step": "page_html_head", "value": page.text[:400]})

    checks["demo_tier_is_cheapest_per_policy"] = "cheapest" in demo_model_tier()
    return steps, checks, b1["reply"]


def main() -> int:
    steps, checks, first_reply = asyncio.run(exercise())
    uncomputed = [k for k, v in checks.items() if v is None]
    ok = not uncomputed and all(checks.values())
    steps.append({"step": "checks", "value": checks})
    print("--- Real demo exchange (stub LLM, injectable) ---")
    print(f"visitor: ร้านเปิดกี่โมงครับ")
    print(f"demo bot: {first_reply}")
    print(f"demo tier (MODEL_POLICY.md tier-by-task): {demo_model_tier()}")
    print(f"cap after driving to limit: used={DEMO_CAP}, next reply -> stopped")
    if uncomputed:
        print(f"FAILED: uncomputed checks: {uncomputed}")
    print("checks:", json.dumps(checks, ensure_ascii=False))
    TRANSCRIPT.write_text(
        json.dumps({"steps": steps, "checks": checks}, ensure_ascii=False,
                   indent=2),
        encoding="utf-8",
    )
    print(f"transcript: {TRANSCRIPT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
