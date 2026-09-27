"""T-079c Part 2 tests — the rendered page itself.

Three checks, all against the HTML the running app actually serves:
1. the three input affordances (text, url, file) exist
2. the PDPA notice text appears verbatim
3. NO model name and NO vendor name appears anywhere in the HTML —
   the forbidden list is built from the real roster slugs/providers
   (see ``prohibited.py``), not from invented strings.
"""

import httpx
import pytest

from app.onboarding.page import (
    DevEscapes, PDPA_NOTICE, OnboardingPageStore, create_onboarding_router,
)
from app.onboarding.page.prohibited import PROHIBITED_TOKENS

SCOPE = "tenant-A"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _setup():
    store = OnboardingPageStore()
    router = create_onboarding_router(
        store=store, llm=None,
        dev_escapes=DevEscapes(unverified_scope_header=True),
    )
    sub = type(__import__("app.main", fromlist=["app"]).app)()
    sub.include_router(router)
    return router, sub


async def _open_view(c: httpx.AsyncClient, url: str):
    r = await c.get(url, headers={"X-Onboarding-Scope": SCOPE})
    assert r.status_code == 200, r.text
    return r


@pytest.mark.anyio
async def test_three_input_affordances() -> None:
    from app.main import app as main_app  # noqa: F401 — just to reuse its class

    _, sub = await _setup()
    asgi = httpx.AsyncClient(transport=httpx.ASGITransport(app=sub), base_url="http://t")
    async with asgi as c:
        # entry page
        r = await _open_view(c, "/onboarding/page/view")
        assert "text" in r.text
        assert "url" in r.text
        assert "file" in r.text
        # session page too (create session, then view it)
        r = await c.post("/onboarding/page/sessions", headers={"X-Onboarding-Scope": SCOPE})
        sid = r.json()["session_id"]
        r2 = await _open_view(c, f"/onboarding/page/sessions/{sid}/view")
        assert "text" in r2.text
        assert "url" in r2.text
        assert "file" in r2.text


@pytest.mark.anyio
async def test_pdpa_notice_present() -> None:
    from app.main import app as main_app  # noqa: F401

    _, sub = await _setup()
    asgi = httpx.AsyncClient(transport=httpx.ASGITransport(app=sub), base_url="http://t")
    async with asgi as c:
        r = await _open_view(c, "/onboarding/page/view")
        assert PDPA_NOTICE in r.text


@pytest.mark.anyio
async def test_no_model_or_vendor_names_in_page() -> None:
    from app.main import app as main_app  # noqa: F401

    _, sub = await _setup()
    asgi = httpx.AsyncClient(transport=httpx.ASGITransport(app=sub), base_url="http://t")
    async with asgi as c:
        html = (await _open_view(c, "/onboarding/page/view")).text
        # also scan a real session view (create one first)
        r = await c.post("/onboarding/page/sessions", headers={"X-Onboarding-Scope": SCOPE})
        sid = r.json()["session_id"]
        html_no_session = (await _open_view(c, f"/onboarding/page/sessions/{sid}/view")).text
        for page in (html, html_no_session):
            lowered = page.lower()
            for token in PROHIBITED_TOKENS:
                token_l = token.lower()
                assert token_l not in lowered,(
                    f"prohibited name {token!r} appears in the rendered page"
                )


@pytest.mark.anyio
async def test_progress_display_uses_real_state() -> None:
    from app.main import app as main_app  # noqa: F401

    _, sub = await _setup()
    asgi = httpx.AsyncClient(transport=httpx.ASGITransport(app=sub), base_url="http://t")
    async with asgi as c:
        r = await c.post("/onboarding/page/sessions", headers={"X-Onboarding-Scope": SCOPE})
        sid = r.json()["session_id"]
        # missing tone -> progress claims nothing saved yet
        page = (await _open_view(c, f"/onboarding/page/sessions/{sid}/view")).text
        assert "missing" in page.lower()
        assert "ยังไม่มี" in page
        # answer tone -> progress notes it saved
        r = await c.post(
            f"/onboarding/page/sessions/{sid}/answer",
            json={"text": "สุภาพ"}, headers={"X-Onboarding-Scope": SCOPE},
        )
        assert r.status_code == 200
        page2 = (await _open_view(c, f"/onboarding/page/sessions/{sid}/view")).text
        assert "บันทึกแล้ว" in page2