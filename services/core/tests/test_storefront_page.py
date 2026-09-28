"""T-079f Part 1 tests — the public storefront page.

Checks, all against the HTML the running app actually serves:
1. all six sections from docs/product/STOREFRONT.md are present
2. NO model name and NO vendor name anywhere (honesty rule 2) — the
   forbidden list is the real one (``PROHIBITED_TOKENS`` built from the
   roster slugs and provider names), not invented strings
3. the PDPA consent notice is present (reused verbatim from the
   already-merged onboarding page — no new legal wording invented)
4. the price shown matches docs/product/PRICING_V1.md (299 THB/month)
"""

import httpx
import pytest

from app.main import app
from app.onboarding.page import PDPA_NOTICE
from app.onboarding.page.prohibited import PROHIBITED_TOKENS
from app.storefront.render import PRICE_LINE


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _fetch() -> str:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        r = await c.get("/")
        assert r.status_code == 200, r.text
        return r.text


@pytest.mark.anyio
async def test_all_six_sections_present() -> None:
    html = await _fetch()
    for section_id in (
        "headline",
        "live-demo",
        "what-it-does",
        "price",
        "cta",
        "small-print",
    ):
        assert f'id="{section_id}"' in html, f"missing section {section_id}"
    # the one button, opening the onboarding assistant
    assert 'id="setup-button"' in html
    assert "/onboarding/page/view" in html


@pytest.mark.anyio
async def test_no_model_or_vendor_names_in_page() -> None:
    lowered = (await _fetch()).lower()
    for token in PROHIBITED_TOKENS:
        assert token.lower() not in lowered, (
            f"prohibited name {token!r} appears in the storefront page"
        )


@pytest.mark.anyio
async def test_consent_notice_present() -> None:
    html = await _fetch()
    assert PDPA_NOTICE in html


@pytest.mark.anyio
async def test_price_matches_pricing_v1() -> None:
    html = await _fetch()
    # docs/product/PRICING_V1.md: "299 THB/month per bot, flat. One tier."
    assert "299" in html
    assert PRICE_LINE in html
    assert "ยกเลิกได้ทุกเมื่อ" in html
