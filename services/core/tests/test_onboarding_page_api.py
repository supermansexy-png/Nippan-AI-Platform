"""T-079c Part 1 tests — HTTP surface: all 3 input kinds, tenant
isolation (fail-closed), the shared upload cap, and a stubbed LLM with
no network. Runs on the ASGI transport like ``test_health.py``."""

import httpx
import pytest

from app.onboarding.page import DevEscapes, OnboardingPageStore, PDPA_NOTICE
from app.onboarding.page import create_onboarding_router

SCOPE_A = "tenant-A"
SCOPE_B = "tenant-B"

# Part B: the header mode is now an explicitly-UNVERIFIED dev escape,
# enabled here at wiring time only — production mounts must pass either a
# server ``tenant_scope_id`` or nothing (fail-closed).
DEV = DevEscapes(unverified_scope_header=True)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _transport(store: OnboardingPageStore, *, fetch_fn=None):
    router = create_onboarding_router(store=store, llm=None) if fetch_fn is None else None
    if fetch_fn is None:
        pass
    return router


async def _client(store: OnboardingPageStore, **router_kwargs: object):
    kwargs: dict = {"dev_escapes": DEV, **router_kwargs}
    router = create_onboarding_router(store=store, llm=None, **kwargs)
    sub = type(__import__("app.main", fromlist=["app"]).app)()
    sub.include_router(router)
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=sub), base_url="http://t"
    )


async def _start(c: httpx.AsyncClient, scope: str) -> str:
    r = await c.post(
        "/onboarding/page/sessions", headers={"X-Onboarding-Scope": scope}
    )
    assert r.status_code == 201, r.text
    return r.json()["session_id"]


# ── 1. typed answer ──────────────────────────────────────
@pytest.mark.anyio
async def test_typed_answer_accepted() -> None:
    store = OnboardingPageStore()
    transport = await _client(store)
    async with transport as c:
        sid = await _start(c, SCOPE_A)
        r = await c.post(
            f"/onboarding/page/sessions/{sid}/answer",
            json={"text": "สุภาพ"},
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["draft"]["tone"] == "polite"
        assert "tone" not in data["missing_fields"]
        # unmapped is rejected, nothing guessed
        r2 = await c.post(
            f"/onboarding/page/sessions/{sid}/answer",
            json={"text": "qwertyzzz"},
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        assert r2.status_code == 400


# ── 2. tenant isolation ──────────────────────────────────
@pytest.mark.anyio
async def test_tenant_isolation_fail_closed() -> None:
    store = OnboardingPageStore()
    transport = await _client(store)
    async with transport as c:
        sid = await _start(c, SCOPE_A)
        # scope B reading A's draft: 404, body must not leak ANY of A's data
        rb = await c.get(
            f"/onboarding/page/sessions/{sid}",
            headers={"X-Onboarding-Scope": SCOPE_B},
        )
        assert rb.status_code == 404
        body = rb.text
        for leaked in ("business_name", "menu_categories", "opening_hours",
                       "fallback_contact", SCOPE_A, sid):
            assert leaked not in body, f"leaked {leaked!r}"
        # B writing to A's session is also blocked
        rw = await c.post(
            f"/onboarding/page/sessions/{sid}/answer",
            json={"text": "polite"},
            headers={"X-Onboarding-Scope": SCOPE_B},
        )
        assert rw.status_code == 404
        # A still gets its own draft back
        ra = await c.get(
            f"/onboarding/page/sessions/{sid}",
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        assert ra.status_code == 200
        assert "tone" in ra.json()["missing_fields"]


@pytest.mark.anyio
async def test_missing_scope_rejected_fail_closed() -> None:
    store = OnboardingPageStore()
    transport = await _client(store)
    async with transport as c:
        r = await c.post("/onboarding/page/sessions")
        assert r.status_code == 401  # no identity → no access, no default tenant


# ── 3. website URL ingestion (stubbed fetch, no network) ─
@pytest.mark.anyio
async def test_website_url_ingestion() -> None:
    import app.onboarding.page.handlers as handlers_mod
    from app.onboarding.ingest import WebFetcher

    def fake_fetch(url: str) -> str:
        # a text price-list page (fetch_fn returns the raw body)
        return "กาแฟดำ,50\nชานมไข่มุก,60\nขนมปังไส้กรอก,40\n"

    class StubFetcher(WebFetcher):
        def __init__(self, *, site_origin, fetch_fn=None, max_pages=None):
            super().__init__(site_origin=site_origin, fetch_fn=fake_fetch)

    orig = handlers_mod.WebFetcher
    handlers_mod.WebFetcher = StubFetcher
    try:
        store = OnboardingPageStore()
        transport = await _client(store, web_fetch_fn=fake_fetch,
                                  site_origin="https://shiba.example",
                                  resolve_fn=lambda h: ["93.184.216.34"])
        async with transport as c:
            sid = await _start(c, SCOPE_A)
            r = await c.post(
                f"/onboarding/page/sessions/{sid}/website",
                json={"url": "https://shiba.example/menu"},
                headers={"X-Onboarding-Scope": SCOPE_A},
            )
            assert r.status_code == 200, r.text
            cats = r.json()["draft"]["menu_categories"]
            assert "กาแฟดำ" in cats
            # non-web scheme is rejected (DomainError → 400)
            r2 = await c.post(
                f"/onboarding/page/sessions/{sid}/website",
                json={"url": "ftp://warehouse.example/menu"},
                headers={"X-Onboarding-Scope": SCOPE_A},
            )
            assert r2.status_code == 400
            assert "warehouse" not in r2.text
    finally:
        handlers_mod.WebFetcher = orig


# ── 4. file upload + shared size cap ─────────────────────
@pytest.mark.anyio
async def test_file_upload_and_cap() -> None:
    from app.onboarding.cost_bounds import MAX_FILE_BYTES

    store = OnboardingPageStore()
    transport = await _client(store)
    async with transport as c:
        sid = await _start(c, SCOPE_A)
        payload = "กาแฟดำ,50\nชานมไข่มุก,60\n".encode("utf-8")
        r = await c.post(
            f"/onboarding/page/sessions/{sid}/file",
            files={"file": ("menu.csv", payload, "text/csv")},
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        assert r.status_code == 200, r.text
        assert "กาแฟดำ" in r.json()["draft"]["menu_categories"]
        # over-cap is rejected with 413 using the EXISTING constant
        big = b"x" * (MAX_FILE_BYTES + 1)
        rbig = await c.post(
            f"/onboarding/page/sessions/{sid}/file",
            files={"file": ("big.txt", big, "text/plain")},
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        assert rbig.status_code == 413
        assert str(MAX_FILE_BYTES) in rbig.text


# ── 5. stubbed LLM, no network / no provider anywhere ────
@pytest.mark.anyio
async def test_stub_llm_injected_no_network() -> None:
    from app.onboarding.page import create_onboarding_router

    class StubLLM:
        def __init__(self):
            self.calls = []

        def complete(self, *, system_prompt, user_text):
            self.calls.append(system_prompt)
            return "1"

    store = OnboardingPageStore()
    llm = StubLLM()
    router = create_onboarding_router(store=store, llm=llm, dev_escapes=DEV)
    sub = type(__import__("app.main", fromlist=["app"]).app)()
    sub.include_router(router)
    transport = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=sub), base_url="http://t"
    )
    async with transport as c:
        r = await c.post(
            "/onboarding/page/sessions", headers={"X-Onboarding-Scope": SCOPE_A}
        )
    assert r.status_code == 201
    assert r.json()["pdpa_notice"] == PDPA_NOTICE
    assert llm.calls == []  # no LLM call unless a classify step requests it
