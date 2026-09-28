"""T-079c / T-079f — the PDPA notice is a PLACEHOLDER pending a lawyer.

Owner decision 2026-09-28: the current wording is a dev-time SAMPLE; a
lawyer writes the final wording before launch. Tests here assert:
1. the original notice text is still present, unmodified, on both pages
2. the visible sample marker is present on both rendered pages

The marker is displayed next to the notice only — the API field
``pdpa_notice`` stays the raw notice text (existing e2e asserts it verbatim).
"""

import httpx
import pytest

from app.main import app
from app.onboarding.page import (
    DevEscapes, OnboardingPageStore, PDPA_NOTICE, PDPA_SAMPLE_MARKER,
    create_onboarding_router,
)

SCOPE = "tenant-A"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _onboarding_html() -> str:
    store = OnboardingPageStore()
    router = create_onboarding_router(
        store=store, llm=None,
        dev_escapes=DevEscapes(unverified_scope_header=True),
    )
    sub = type(app)()
    sub.include_router(router)
    transport = httpx.ASGITransport(app=sub)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        r = await c.get("/onboarding/page/view", headers={"X-Onboarding-Scope": SCOPE})
        assert r.status_code == 200, r.text
        return r.text


async def _storefront_html() -> str:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        r = await c.get("/")
        assert r.status_code == 200, r.text
        return r.text


@pytest.mark.anyio
async def test_pdpa_placeholder_marker_on_both_pages() -> None:
    for html in (await _onboarding_html(), await _storefront_html()):
        # original notice text unchanged
        assert PDPA_NOTICE in html
        # visible sample marker present, wrapped in its distinct element
        assert 'class="pdpa-sample-marker"' in html
        assert f">{PDPA_SAMPLE_MARKER}</span>" in html


@pytest.mark.anyio
async def test_pdpa_notice_text_is_unchanged_placeholder() -> None:
    # The notice constant itself is untouched; it is exactly the wording
    # that was already serving before the marker was added.
    assert PDPA_NOTICE == (
        "เว็บไซต์นี้เก็บข้อมูลที่คุณกรอกเพื่อตั้งค่าบอทของร้านคุณเท่านั้น "
        "และปฏิบัติตาม PDPA — คุณสามารถขอลบข้อมูลได้ทุกเมื่อ"
    )
