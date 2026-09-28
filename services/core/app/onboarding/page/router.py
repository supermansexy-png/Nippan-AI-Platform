"""HTTP surface for the customer setup page (T-079c Part 1).

Every route is thin: it resolves the session identity fail-closed (see
``store.py``), then delegates to ``handlers.py`` — which in turn delegates
to the existing ``app/onboarding/`` rules. No HTML rendering here (Part 2).

Tenant isolation: the tenant scope comes from an explicit header or a
constructor-bound scope, never defaulted. A missing/unknown scope or a
session that does not belong to it → 404/403 with NO other-tenant data.
"""

from __future__ import annotations

import logging

from dataclasses import dataclass

from fastapi import APIRouter, Header, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse

__all__ = [
    "PDPA_NOTICE",
    "PDPA_SAMPLE_MARKER",
    "OnboardingPageStore",
    "create_onboarding_router",
]

logger = logging.getLogger("app.onboarding.page.router")

from ..menus import UnmappedInputError
from ..ingest import FetchBudgetExhausted
from ..cost_bounds import DomainError
from .handlers import (
    MAX_FILE_BYTES,
    apply_answer,
    start_session,
    state_of,
    submit_url,
    upload_file,
)
from .render import render_page
from .store import OnboardingPageStore, SessionScopeError

__all__ = [
    "PDPA_NOTICE",
    "PDPA_SAMPLE_MARKER",
    "OnboardingPageStore",
    "create_onboarding_router",
]

# PDPA_NOTICE — PLACEHOLDER / SAMPLE ONLY.
# This wording is a dev-time draft. It has NOT been reviewed by a lawyer.
# Owner decision (2026-09-28, verbatim): "เดียวตอนก่อนเปิด จะให้ทนายเขียนใหม่
# ตอนนี้ให้ใช้แบบที่เขียนมาก่อนเป็นเพียงตัวอย่าง" — a lawyer will write the
# final wording before the site is publicly launched, and this text MUST be
# replaced before launch. Cards: T-079c / T-079f.
PDPA_NOTICE = (
    "เว็บไซต์นี้เก็บข้อมูลที่คุณกรอกเพื่อตั้งค่าบอทของร้านคุณเท่านั้น "
    "และปฏิบัติตาม PDPA — คุณสามารถขอลบข้อมูลได้ทุกเมื่อ"
)

# Visible, non-legal marker shown next to the notice wherever it is
# rendered to a person (onboarding page + storefront). Text only — no
# legal claim. Pair with PDPA_NOTICE above (same placeholder status).
PDPA_SAMPLE_MARKER = "ตัวอย่าง — รอถ้อยคำฉบับสุดท้ายจากทนาย"

SCOPE_HEADER = "X-Onboarding-Scope"

_B1_MSG_NO_SCOPE = (
    "service is not configured with a verified tenant identity; "
    "this deployment refuses to serve onboarding data (fail-closed)"
)
_B1_MSG_IGNORED_HEADER = (
    "this deployment is bound to a server-side tenant scope; "
    "client-supplied scope headers are ignored"
)


@dataclass(frozen=True)
class DevEscapes:
    """Narrow, OFF-by-default dev escape hatches (Part B, finding B1).

    Every flag here is usable ONLY at wiring time in process — never
    through a request parameter or header. Where ``unverified_scope_header``
    is True, responses DECLARE that identity is unverified, so nothing
    pretends to be protected when it is not. Default: all False.
    """

    unverified_scope_header: bool = False


def create_onboarding_router(
    *,
    store: OnboardingPageStore | None = None,
    tenant_scope_id: str | None = None,
    llm: object | None = None,
    web_fetch_fn=None,
    site_origin: str | None = None,
    resolve_fn=None,
    dev_escapes: DevEscapes | None = None,
) -> APIRouter:
    """Build the session router (fail-closed, Part B finding B1).

    Identity rule: the tenant scope comes from the SERVER at wiring time.
    - With ``tenant_scope_id`` set, that scope is the ONLY one used; any
      ``X-Onboarding-Scope`` header the client sends is IGNORED and the
      ignoring is logged (never silently trusted).
    - With no server scope and ``dev_escapes.unverified_scope_header``
      False (the default), the router REFUSES to serve data: 401 with a
      clear message — it never falls back to trusting the client header.
    - The dev escape flips the router into an explicitly UNVERIFIED mode
      (header scope accepted, but flagged as unverified in responses);
      offline scripts (e2e/tests) enable it at wiring time only.

    ``llm`` stays injectable — a stub is enough for every route here.

    G (T-079c): ``site_origin`` is the shop's site the SERVER already
    knows (tenant config) — every session created here is stamped with
    it, and /website validates submitted URLs against IT, never against
    the submitted URL itself. ``resolve_fn`` is the injectable DNS
    resolver (offline dev wiring); production uses the OS resolver and
    FAILS CLOSED when DNS errors.
    """
    store = store or OnboardingPageStore()
    router = APIRouter(prefix="/onboarding/page", tags=["onboarding-page"])
    escapes = dev_escapes or DevEscapes()

    def _scope(request_scope: str | None) -> str:
        if tenant_scope_id:
            if request_scope and request_scope.strip():
                logger.info(
                    "onboarding page: ignored client %s header "
                    "(server scope %r is authoritative)", SCOPE_HEADER,
                    tenant_scope_id,
                )
            return tenant_scope_id
        if escapes.unverified_scope_header:
            if not request_scope or not request_scope.strip():
                raise HTTPException(status_code=401, detail=_B1_MSG_NO_SCOPE)
            return request_scope.strip()
        # fail-closed: no verified server identity → no data served at all
        raise HTTPException(status_code=401, detail=_B1_MSG_NO_SCOPE)

    UNVERIFIED_IDENTITY_NOTICE = (
        "dev escape enabled: tenant identity is UNVERIFIED "
        "(X-Onboarding-Scope header is not an authenticate signal)"
    )

    def _state_flags() -> dict:
        # When the dev escape is on, every response/page PLAINLY says so —
        # nothing pretends to be protected when identity is not verified.
        if escapes.unverified_scope_header:
            return {"identity_verified": False,
                    "identity_notice": UNVERIFIED_IDENTITY_NOTICE}
        return {"identity_verified": True, "identity_notice": None}

    def _row(scope: str, session_id: str):
        try:
            return store.get(tenant_scope_id=scope, session_id=session_id)
        except SessionScopeError:
            # 404, not 403 — never even confirms the session exists elsewhere.
            raise HTTPException(status_code=404, detail="session not found")

    @router.post("/sessions", status_code=201)
    def create_session(x_onboarding_scope: str | None = Header(default=None, alias=SCOPE_HEADER)):
        scope = _scope(x_onboarding_scope)
        state = start_session(store, tenant_scope_id=scope, llm=llm,
                              site_origin=site_origin)
        return {"pdpa_notice": PDPA_NOTICE, **_state_flags(), **state}

    @router.get("/sessions/{session_id}")
    def read_session(session_id: str, x_onboarding_scope: str | None = Header(default=None, alias=SCOPE_HEADER)):
        scope = _scope(x_onboarding_scope)
        row = _row(scope, session_id)
        return {**_state_flags(), **state_of(row)}

    @router.post("/sessions/{session_id}/answer")
    def post_answer(
        session_id: str,
        body: dict,
        x_onboarding_scope: str | None = Header(default=None, alias=SCOPE_HEADER),
    ):
        scope = _scope(x_onboarding_scope)
        row = _row(scope, session_id)
        text = body.get("text") if isinstance(body, dict) else None
        if not isinstance(text, str):
            raise HTTPException(status_code=400, detail="text required")
        try:
            return {**_state_flags(), **apply_answer(row, text)}
        except UnmappedInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def _banner() -> str:
        flags = _state_flags()
        if flags["identity_notice"] is None:
            return ""
        from xml.sax.saxutils import escape as _esc
        return (
            '<p class="warning" role="alert">'
            + _esc(flags["identity_notice"]) + "</p>"
        )

    @router.get("/sessions/{session_id}/view", response_class=HTMLResponse)
    def view_page(session_id: str, x_onboarding_scope: str | None = Header(default=None, alias=SCOPE_HEADER)):
        """The rendered setup page (Part 2): three inputs + progress + PDPA."""
        scope = _scope(x_onboarding_scope)
        row = _row(scope, session_id)
        state = state_of(row)
        html = render_page(
            pdpa_notice=PDPA_NOTICE,
            missing_fields=state["missing_fields"],
            draft=state["draft"],
            done=state["done"],
            banner=_banner(),
        )
        return HTMLResponse(content=html, media_type="text/html; charset=utf-8")

    @router.get("/view", response_class=HTMLResponse)
    def view_landing(x_onboarding_scope: str | None = Header(default=None, alias=SCOPE_HEADER)):
        """Setup entry page: same three inputs + PDPA, no session yet."""
        # Data routes refuse without a verified scope; the landing page is
        # still scoped the same way so nothing about this router serves
        # content in a deployment that has not been wired an identity.
        scope = _scope(x_onboarding_scope)  # used only to gate, not to key
        return HTMLResponse(
            content=render_page(
                pdpa_notice=PDPA_NOTICE,
                missing_fields=["tone", "business_type", "business_name",
                                "opening_hours", "menu_categories",
                                "enabled_tools", "fallback_contact"],
                draft={},
                done=False,
                banner=_banner(),
            ),
            media_type="text/html; charset=utf-8",
        )

    @router.post("/sessions/{session_id}/website")
    def post_website(
        session_id: str,
        body: dict,
        x_onboarding_scope: str | None = Header(default=None, alias=SCOPE_HEADER),
    ):
        scope = _scope(x_onboarding_scope)
        row = _row(scope, session_id)
        url = body.get("url") if isinstance(body, dict) else None
        if not isinstance(url, str) or not url.strip():
            raise HTTPException(status_code=400, detail="url required")
        # B2: an absent fetcher is a DELIBERATE handled state — a clean 503
        # with a non-informative body; the real reason lives server-side
        # only. No TypeError, no traceback, no internal path ever escapes.
        if web_fetch_fn is None:
            logger.warning(
                "onboarding /website called but no fetcher is configured "
                "at wiring time (create_onboarding_router(web_fetch_fn=...)); "
                "responding 503 fail-closed"
            )
            # even the URL the client asked for is never echoed here
            raise HTTPException(
                status_code=503,
                detail="website ingestion is not available",
            )
        try:
            return submit_url(row, url, fetch_fn=web_fetch_fn,
                              resolve=resolve_fn)
        except FetchBudgetExhausted as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except DomainError:
            raise HTTPException(
                status_code=400, detail="only same-domain web links are accepted"
            )
        except ValueError:
            # non-informative: str(exc) may name internal paths/modules
            raise HTTPException(status_code=400, detail="url could not be used")
        except UnmappedInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/sessions/{session_id}/file")
    def post_file(
        session_id: str,
        file: UploadFile = File(...),
        x_onboarding_scope: str | None = Header(default=None, alias="X-Onboarding-Scope"),
    ):
        scope = _scope(x_onboarding_scope)
        row = _row(scope, session_id)
        # A2: enforce the cap DURING the read, not after a full read —
        # bounded chunks, reject as soon as the cap is exceeded.
        declared = file.headers.get("content-length") if file.headers else None
        if declared and declared.isdigit() and int(declared) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"file over the {MAX_FILE_BYTES}-byte cap",
            )
        if file.file is None:
            data = b""
        else:
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = file.file.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_FILE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"file over the {MAX_FILE_BYTES}-byte cap",
                    )
                chunks.append(chunk)
            data = b"".join(chunks)
        try:
            return upload_file(
                row, name=file.filename or "upload", data=data
            )
        except UnmappedInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return router

