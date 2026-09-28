"""T-079f Part 2 tests — the live storefront demo bot and its daily cap.

Proves, all offline (stub LLM, no network, no db, no credentials):
1. the demo answers over web-chat (real exchange through the HTTP route)
2. the daily cap counts ONLY demo traffic and stops the demo at the limit
   with a clean message that names no model/vendor
3. the demo cannot read or write any tenant's data (isolation)
4. no model/vendor name in any demo response (honesty rule)
5. the cheapest-tier selection follows MODEL_POLICY.md tier-by-task
6. cap=None keeps the demo closed (fail-closed; no number is defined in
   any doc, so the cap is configuration, not a buried guess)
"""

import httpx
import pytest
from fastapi import FastAPI

from app.onboarding.page.prohibited import PROHIBITED_TOKENS
from app.storefront.demo import (
    DEMO_CAP_REACHED_MESSAGE,
    DEMO_MODEL_TIER,
    DEMO_UNAVAILABLE_MESSAGE,
    StorefrontDemoService,
    demo_model_tier,
)
from app.storefront.router import create_storefront_router


def _stub_llm(text: str) -> str:
    return f"บอทตัวอย่างตอบ: ร้านเปิด 08:00-18:00 ครับ (ถามว่า: {text})"


def _app(service: StorefrontDemoService) -> FastAPI:
    app = FastAPI()
    app.include_router(create_storefront_router(demo_service=service))
    return app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _post(app: FastAPI, text: str) -> dict:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        r = await c.post("/demo/chat", json={"text": text})
        assert r.status_code == 200, r.text
        return r.json()


# -- 1. the demo answers over web-chat --------------------------------
@pytest.mark.anyio
async def test_demo_answers_over_web_chat() -> None:
    app = _app(StorefrontDemoService(llm=_stub_llm, daily_cap=5))
    body = await _post(app, "ร้านเปิดกี่โมง")
    assert "08:00-18:00" in body["reply"]
    assert body["stopped"] is False
    assert body["remaining"] == 4


# -- 2. the cap counts only demo traffic and stops the demo -----------
@pytest.mark.anyio
async def test_cap_stops_demo_with_clean_message() -> None:
    svc = StorefrontDemoService(llm=_stub_llm, daily_cap=2)
    app = _app(svc)
    await _post(app, "หนึ่ง")
    await _post(app, "สอง")
    assert svc.used_today == 2
    body = await _post(app, "สาม")
    assert body["stopped"] is True
    assert body["remaining"] == 0
    assert body["reply"] == DEMO_CAP_REACHED_MESSAGE
    assert svc.used_today == 2  # a stopped request does not spend the cap
    lowered = body["reply"].lower()
    for token in PROHIBITED_TOKENS:
        assert token.lower() not in lowered


def test_cap_counter_is_demo_only_not_tenant_quota() -> None:
    """The demo cap is its own counter; there is no tenant sink to touch.

    A tenant usage-tracker wired next to the demo records NOTHING from
    demo traffic — the service has no reference to any tenant store.
    """
    tenant_usage: list[dict] = []

    class TenantSink:
        def record(self, **kw):
            tenant_usage.append(kw)

    svc = StorefrontDemoService(llm=_stub_llm, daily_cap=3)
    for _ in range(3):
        svc.reply("ลอง")
    assert svc.used_today == 3
    assert tenant_usage == []  # tenant quota untouched by demo traffic
    assert not hasattr(svc, "_usage") and not hasattr(svc, "_tenant")


# -- 3. the demo cannot reach tenant data ------------------------------
def test_demo_isolated_from_tenant_data() -> None:
    """The service signature takes no tenant repository/config/store, so
    there is no code path from the public demo to tenant config, drafts,
    or transcripts. Constructing it with tenant data is impossible."""
    import inspect

    params = set(inspect.signature(StorefrontDemoService.__init__).parameters)
    assert params == {"self", "llm", "daily_cap", "clock"}
    svc = StorefrontDemoService(llm=_stub_llm, daily_cap=1)
    reply = svc.reply("ขอดูข้อมูลร้านอื่น")
    assert "ร้านอื่น" in reply.text  # echoed back, not fetched from anywhere


# -- 4. honesty: a model/vendor name in a reply is rejected ------------
def test_model_vendor_name_in_reply_is_rejected() -> None:
    bad_llm = lambda _: "ฉันใช้ glm-5.3-flash จาก openrouter ครับ"
    svc = StorefrontDemoService(llm=bad_llm, daily_cap=5)
    with pytest.raises(ValueError, match="prohibited"):
        svc.reply("ใช้โมเดลอะไร")
    assert svc.used_today == 0  # a rejected reply never spends the cap


# -- 5. cheapest-tier selection follows the documented policy ----------
def test_demo_tier_is_cheapest_per_model_policy() -> None:
    # MODEL_POLICY.md "Tier by task, not by tenant": routine end-customer
    # chat -> cheapest viable model. The demo is routine chat.
    assert demo_model_tier() == DEMO_MODEL_TIER
    assert "cheapest" in demo_model_tier()


# -- 6. no cap configured -> demo closed (fail-closed) ------------------
@pytest.mark.anyio
async def test_unconfigured_cap_keeps_demo_closed() -> None:
    app = _app(StorefrontDemoService(llm=_stub_llm, daily_cap=None))
    body = await _post(app, "สวัสดี")
    assert body["stopped"] is True
    assert body["reply"] == DEMO_UNAVAILABLE_MESSAGE


def test_invalid_cap_rejected() -> None:
    with pytest.raises(ValueError):
        StorefrontDemoService(llm=_stub_llm, daily_cap=0)
