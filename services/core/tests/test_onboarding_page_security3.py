"""T-079c PART B tests — B1 identity fail-closed (server-scoped mount,
dev escape) and B2 the unconfigured fetcher (handled 503, no leak)."""

import httpx
import pytest

from app.onboarding.page import DevEscapes, OnboardingPageStore


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _sub(router) -> httpx.AsyncClient:
    sub = type(__import__("app.main", fromlist=["app"]).app)()
    sub.include_router(router)
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=sub), base_url="http://t"
    )


# ── B1 — mounted WITHOUT a server scope and WITHOUT the escape ──
@pytest.mark.anyio
async def test_b1_no_server_scope_refuses_client_header() -> None:
    from app.onboarding.page import create_onboarding_router

    router = create_onboarding_router(store=OnboardingPageStore())
    async with _sub(router) as c:
        # the client picks its own scope — the router must refuse, never
        # trust it, never create a session under it
        r = await c.post(
            "/onboarding/page/sessions",
            headers={"X-Onboarding-Scope": "tenant-A"},
        )
        assert r.status_code == 401
        body = r.text
        assert "not configured" in body  # explicit, non-misleading message
        assert "tenant-A" not in body    # never echoes back the picked scope
        # no data route serves anything either
        rv = await c.get(
            "/onboarding/page/sessions/s-0001-aaaaaaaa/view",
            headers={"X-Onboarding-Scope": "tenant-A"},
        )
        assert rv.status_code == 401


# ── B1 — dev escape: enabled OFF by default, invisible to requests ──
def test_b1_dev_escape_off_by_default() -> None:
    e = DevEscapes()
    assert e.unverified_scope_header is False


@pytest.mark.anyio
async def test_b1_dev_escape_mode_marks_identity_unverified() -> None:
    from app.onboarding.page import create_onboarding_router

    router = create_onboarding_router(
        store=OnboardingPageStore(),
        dev_escapes=DevEscapes(unverified_scope_header=True),
    )
    async with _sub(router) as c:
        r = await c.post(
            "/onboarding/page/sessions",
            headers={"X-Onboarding-Scope": "tenant-A"},
        )
        assert r.status_code == 201, r.text
        data = r.json()
        assert data["identity_verified"] is False
        assert "UNVERIFIED" in data["identity_notice"]
        # the page says it too
        rv = await c.get(
            f"/onboarding/page/sessions/{data['session_id']}/view",
            headers={"X-Onboarding-Scope": "tenant-A"},
        )
        assert rv.status_code == 200
        assert "UNVERIFIED" in rv.text


# ── B1 — server scope: client header NEVER widens or narrows access ──
@pytest.mark.anyio
async def test_b1_server_scope_ignores_client_header() -> None:
    from app.onboarding.page import create_onboarding_router

    store = OnboardingPageStore()
    router = create_onboarding_router(store=store, tenant_scope_id="tenant-A")
    async with _sub(router) as c:
        # same header, different value → still works, scoped to tenant-A
        # only (the header is ignored, not consulted)
        r = await c.post(
            "/onboarding/page/sessions",
            headers={"X-Onboarding-Scope": "tenant-EVIL"},
        )
        assert r.status_code == 201, r.text
        sid = r.json()["session_id"]
        assert r.json()["tenant_scope_id"] == "tenant-A"
        assert r.json()["identity_verified"] is True
        # reading under a DIFFERENT claim finds only tenant-A data —
        # the request cannot act as another tenant...
        r_evil = store.create(tenant_scope_id="tenant-B")
        rb = await c.get(
            f"/onboarding/page/sessions/{r_evil.session_id}",
            headers={"X-Onboarding-Scope": "tenant-B"},
        )
        assert rb.status_code == 404
        assert r_evil.session_id not in rb.text
        # ...nor can it write into another tenant's session
        rw = await c.post(
            f"/onboarding/page/sessions/{r_evil.session_id}/answer",
            json={"text": "x"}, headers={"X-Onboarding-Scope": "tenant-B"},
        )
        assert rw.status_code == 404


# ── B2 — /website without a fetcher: handled 503, no leak ──
@pytest.mark.anyio
async def test_b2_website_without_fetcher_is_clean_503() -> None:
    from app.onboarding.page import create_onboarding_router

    router = create_onboarding_router(
        store=OnboardingPageStore(),
        tenant_scope_id="tenant-A",
    )
    async with _sub(router) as c:
        r = await c.post("/onboarding/page/sessions")  # header-free by design
        assert r.status_code == 201, r.text
        sid = r.json()["session_id"]
        rw = await c.post(
            f"/onboarding/page/sessions/{sid}/website",
            json={"url": "http://shop.example/menu"},
            headers={"X-Onboarding-Scope": "garbage-scope-ignored"},
        )
        assert rw.status_code == 503, rw.text
        body = rw.text.lower()
        for leak in ("typeerror", "traceback", "handlers.py", "ingest.py",
                     "webfetcher", "shop.example", "fetch_fn"):
            assert leak not in body, f"leaked {leak!r}"
        # with a server scope, an odd client scope header gets IGNORED,
        # so the route still reaches the fetcher gate cleanly (503 here)
