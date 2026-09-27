"""PART A security tests — HTTP surface & store (A1 router, A2/A3 upload,
A4 bounded store). Split from test_onboarding_page_security.py to keep
each file small."""

import httpx
import pytest

from app.onboarding.page import DevEscapes, create_onboarding_router
from app.onboarding.page.handlers import sanitize_filename
from app.onboarding.page.store import (
    OnboardingPageStore, SessionLimitError, SessionScopeError,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def _client(store: OnboardingPageStore, **router_kwargs: object):
    router = create_onboarding_router(
        store=store, llm=None,
        dev_escapes=DevEscapes(unverified_scope_header=True),
        **router_kwargs,
    )
    sub = type(__import__("app.main", fromlist=["app"]).app)()
    sub.include_router(router)
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=sub), base_url="http://t"
    )


async def _start(c: httpx.AsyncClient) -> str:
    r = await c.post(
        "/onboarding/page/sessions", headers={"X-Onboarding-Scope": "t"}
    )
    assert r.status_code == 201, r.text
    return r.json()["session_id"]


# ── A1 — HTTP: internal target → 400, fetch code NEVER invoked ──
@pytest.mark.anyio
async def test_a1_router_rejects_internal_url_before_fetch() -> None:
    import app.onboarding.page.handlers as handlers_mod
    from app.onboarding.ingest import WebFetcher

    calls: list[str] = []

    def fn(u: str) -> str:
        calls.append(u)
        return "กาแฟดำ,50\n"

    class Guarded(WebFetcher):
        def __init__(self, *, site_origin, fetch_fn=None, max_pages=None):
            super().__init__(site_origin=site_origin, fetch_fn=fn)

    orig = handlers_mod.WebFetcher
    handlers_mod.WebFetcher = Guarded
    try:
        store = OnboardingPageStore()
        async with await _client(store, web_fetch_fn=fn) as c:
            sid = await _start(c)
            r = await c.post(
                f"/onboarding/page/sessions/{sid}/website",
                json={"url": "http://169.254.169.254/latest/meta-data/"},
                headers={"X-Onboarding-Scope": "t"},
            )
            assert r.status_code == 400, r.text
            assert "169.254" not in r.text  # never a 500 / no detail leak
            r2 = await c.post(
                f"/onboarding/page/sessions/{sid}/website",
                json={"url": "http://localhost:8080/"},
                headers={"X-Onboarding-Scope": "t"},
            )
            assert r2.status_code == 400
            assert calls == []  # proven: zero bytes fetched for internals
    finally:
        handlers_mod.WebFetcher = orig


# ── A3 — uploaded filename is sanitized, rewrite is recorded ──
@pytest.mark.anyio
async def test_a3_filename_sanitized_and_recorded() -> None:
    store = OnboardingPageStore()
    async with await _client(store) as c:
        sid = await _start(c)
        payload = "กาแฟดำ,50\n".encode("utf-8")
        r = await c.post(
            f"/onboarding/page/sessions/{sid}/file",
            files={"file": ('<img src=x onerror=alert(1)>.csv',
                            payload, "text/csv")},
            headers={"X-Onboarding-Scope": "t"},
        )
        assert r.status_code == 200, r.text
        text = r.text.lower()
        assert "<img" not in text
        assert "<" not in text and ">" not in text  # markup neutralized
        assert "rewritten" in text  # sanitization is recorded, not silent


def test_a3_sanitize_filename_unit() -> None:
    assert sanitize_filename("/etc/passwd/evil.csv") == "evil.csv"
    assert sanitize_filename("..\\..\\win.ini") == "win.ini"
    out = sanitize_filename('<img src=x onerror=alert(1)>.csv')
    assert "<" not in out and ">" not in out and "'" not in out
    assert sanitize_filename("a\tb\x7f.csv") == "ab.csv"
    assert sanitize_filename("") == "upload"


# ── A4 — bounded store: cap, eviction, TTL, hard refusal ──
def test_a4_store_evicts_oldest_at_cap() -> None:
    store = OnboardingPageStore(max_sessions=2)
    a = store.create(tenant_scope_id="t")
    store.create(tenant_scope_id="t")
    c = store.create(tenant_scope_id="t")
    assert store.active_count() == 2
    with pytest.raises(SessionScopeError):
        store.get(tenant_scope_id="t", session_id=a.session_id)
    store.get(tenant_scope_id="t", session_id=c.session_id)  # newest kept


def test_a4_store_ttl_expires_sessions() -> None:
    import app.onboarding.page.store as sm

    store = OnboardingPageStore(ttl_seconds=1)
    row = store.create(tenant_scope_id="t")
    row.created_at -= 2  # backdate past the TTL
    with pytest.raises(sm.SessionScopeError):  # expired == not found
        store.get(tenant_scope_id="t", session_id=row.session_id)


def test_a4_store_hards_stops_when_nothing_freeable() -> None:
    store = OnboardingPageStore(max_sessions=0)
    with pytest.raises(SessionLimitError):
        store.create(tenant_scope_id="t")
