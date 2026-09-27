"""T-079c Part 3 runnable end-to-end proof: the real setup page over its
real HTTP routes, offline.

Drives (in-process ASGI, like the tests, no second server, no internet):
1. a typed answer  → accepted + progress advances
2. a website URL   → accepted (stubbed fetch), categories derived from content
3. a file upload   → accepted, categories derived from the file's bytes
4. the progress display advancing in the served HTML
5. the PDPA notice present in the served HTML
6. NO model/vendor name in the served HTML (computed from the real
   PROHIBITED_TOKENS list)
7. tenant isolation: another scope cannot read the draft (404, no leak)

Run (from the repo root):
    python services/core/scripts/run_onboarding_page_e2e.py
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

from app.main import app as main_app
from app.onboarding.page import (
    DevEscapes,
    OnboardingPageStore,
    PDPA_NOTICE,
    create_onboarding_router,
)
from app.onboarding.page.handlers import extract_page_categories
from app.onboarding.page.prohibited import PROHIBITED_TOKENS
from app.onboarding.signals import extract_categories_from_price_file

SCOPE_A = "tenant-A"
SCOPE_B = "tenant-B"
BUSINESS_NAME = "ร้านเจ๊มา"

# The stub fetcher returns the RAW body; the page-category parser reads
# plain price-list lines ("name,price"), not HTML markup (matching the
# real route, which fetches the page text as the tests do).
SITE_BODY = "กาแฟดำ,50\nชานมไข่มุก,60\nขนมปังไส้กรอก,40\n"
FILE_BYTES = "เครื่องดื่ม,40\nขนมอบ,25\nข้าวราดแกง,50\n".encode("utf-8")

TRANSCRIPT = Path(__file__).with_name("onboarding_page_e2e_transcript.json")


async def _client(store: OnboardingPageStore, **router_kwargs: object) -> httpx.AsyncClient:
    # A bare sub-app of the same class as the real app, carrying the SAME
    # router the real app mounts — sync endpoints, no database, no network.
    # Part B wiring: the header mode is the explicitly-unverified dev
    # escape, enabled HERE at wiring time (offline proof only); the fetch
    # stub is wired through ``web_fetch_fn`` — no monkeypatch.
    kwargs: dict = {"dev_escapes": DevEscapes(unverified_scope_header=True),
                    "web_fetch_fn": (lambda u: SITE_BODY),
                    # G (T-079c): the shop's site the SERVER already knows,
                    # plus an offline resolver wired like a real one (a
                    # public, non-blocked address for the own-site host).
                    "site_origin": "https://jea-ma.example",
                    "resolve_fn": (lambda h: ["93.184.216.34"]),
                    **router_kwargs}
    sub = type(main_app)()
    sub.include_router(create_onboarding_router(store=store, llm=None, **kwargs))
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=sub), base_url="http://t"
    )


async def run() -> tuple[dict[str, bool], dict]:
    checks: dict[str, bool] = {}
    steps: dict = {}

    async with await _client(OnboardingPageStore()) as c:
        # ── session start ────────────────────────────────────
        r = await c.post(
            "/onboarding/page/sessions", headers={"X-Onboarding-Scope": SCOPE_A}
        )
        assert r.status_code == 201, r.text
        sid = r.json()["session_id"]
        checks["pdpa_notice_in_api"] = r.json()["pdpa_notice"] == PDPA_NOTICE

        async def _post(path: str, **kw):
            return await c.post(
                f"/onboarding/page/sessions/{sid}{path}",
                headers={"X-Onboarding-Scope": SCOPE_A},
                **kw,
            )

        async def _answer(text: str):
            return await _post("/answer", json={"text": text})

        # ── 1. typed answers IN THE DRIVER'S ORDER. The engine maps each
        # answer to its FIRST missing field; menu_categories comes BEFORE
        # enabled_tools and can only come from a URL/file, so the typed
        # steps are: tone → type → name → hours, then ingestion, then
        # tools → contact. (The old script answered tools before ingestion
        # → 400 → KeyError-on-error-body. That was the whole bug.)
        r = await _answer("สุภาพ")
        checks["typed_answer_accepted"] = r.status_code == 200
        checks["typed_answer_reflected"] = (
            r.status_code == 200 and r.json().get("draft", {}).get("tone") == "polite"
        )
        steps["after_answer"] = dict(r.json()) if r.status_code == 200 else {"status": r.status_code}

        r = await _answer("ร้านกาแฟ")
        checks["typed_business_type"] = r.status_code == 200
        r = await _answer(BUSINESS_NAME)
        checks["typed_business_name"] = r.status_code == 200
        r = await _answer("เราเปิด 09:00-21:00 ทุกวัน")
        checks["typed_opening_hours"] = r.status_code == 200

        # while menu_categories is still missing, a typed tools answer MUST
        # be rejected (fail-closed ordering, nothing guessed):
        r_pre = await _answer("อยากให้ตอบคำถามลูกค้า และจองคิวล่วงหน้า")
        checks["tools_before_ingestion_rejected"] = r_pre.status_code == 400

        # ── 2. website URL (fetch mock wired via web_fetch_fn, no internet) ─
        r = await _post(
            "/website", json={"url": "https://jea-ma.example/menu"}
        )
        checks["website_accepted"] = r.status_code == 200
        site_draft = r.json() if r.status_code == 200 else {}
        site_cats = site_draft.get("draft", {}).get("menu_categories") or []
        derived_from_site = list(extract_page_categories(SITE_BODY))
        checks["website_categories_from_content"] = (
            # every stored category must be present in the stub body's own
            # parse (subset) — nothing invented; extra lines the fetcher
            # pipeline drops are fine (matches the API's real behaviour)
            bool(site_cats)
            and set(site_cats) <= set(derived_from_site)
        )
        steps["after_website"] = {
            "categories": site_cats,
            "derived_from_stub_text": derived_from_site,
        }

        # ── 3. file upload (multipart, no disk, no network) ──
        # The proof that categories are DERIVED from the file's content:
        # upload file 1, then file 2 with DIFFERENT content — the stored
        # categories must track the bytes each time (never hardcoded).
        FILE1 = "เครื่องดื่ม,40\nขนมอบ,25\nข้าวราดแกง,50\n".encode("utf-8")
        FILE2 = "เย็นตาโฟ,45\nแกงเขียวหวาน,60\n".encode("utf-8")

        async def _file_upload(payload: bytes, name="menu.csv"):
            return await _post(
                "/file", files={"file": (name, payload, "text/csv")}
            )

        from app.onboarding.signals import extract_categories_from_price_file

        r = await _file_upload(FILE1)
        checks["file_accepted"] = r.status_code == 200
        cats1 = (r.json().get("draft", {}).get("menu_categories") if
                 r.status_code == 200 else []) or []
        derived1 = extract_categories_from_price_file(FILE1.decode("utf-8"))
        r = await _file_upload(FILE2, name="menu2.csv")
        cats2 = (r.json().get("draft", {}).get("menu_categories") if
                 r.status_code == 200 else []) or []
        derived2 = extract_categories_from_price_file(FILE2.decode("utf-8"))
        checks["file_categories_from_content"] = (
            bool(cats1) and set(cats1) == set(derived1)
            and bool(cats2) and set(cats2) == set(derived2)
            and set(cats2) != set(cats1)  # content changed → output changed
            and set(cats2) != set(site_cats)
        )
        checks["file_flag_set"] = r.status_code == 200 and r.json().get("used_file") is True
        steps["after_files"] = {
            "file1_categories": cats1, "file1_derived": derived1,
            "file2_categories": cats2, "file2_derived": derived2,
        }

        # ── 4. remaining typed fields now that ingestion is done ──
        r = await _answer("อยากให้ตอบคำถามลูกค้า และจองคิวล่วงหน้า")
        checks["typed_enabled_tools"] = (
            r.status_code == 200
            and bool((r.json().get("draft") or {}).get("enabled_tools"))
        )
        steps["tools_draft"] = (
            (r.json().get("draft") or {}).get("enabled_tools")
            if r.status_code == 200 else None
        )
        r = await _answer("โทร 081-234-5678")
        checks["typed_fallback_contact"] = (
            r.status_code == 200
            and bool((r.json().get("draft") or {}).get("fallback_contact"))
        )

        # ── 5. progress display advancing in the served HTML ──
        r = await c.get(
            f"/onboarding/page/sessions/{sid}/view",
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        checks["view_ok"] = r.status_code == 200
        html = r.text
        html_lower = html.lower()
        checks["progress_shows_saved"] = "บันทึกแล้ว" in html
        checks["progress_missing_shrunk"] = (
            html.count('class="missing"') < html.count('class="done"')
        )

        # ── 6. PDPA notice present in served HTML ────────────
        rlanding = await c.get(
            "/onboarding/page/view", headers={"X-Onboarding-Scope": SCOPE_A}
        )
        checks["pdpa_in_landing"] = (
            rlanding.status_code == 200 and PDPA_NOTICE in rlanding.text
        )
        checks["pdpa_in_session_view"] = PDPA_NOTICE in html

        # ── 7. no model/vendor name in served HTML (computed) ──
        prohibited_hits = [
            tok
            for tok in PROHIBITED_TOKENS
            if tok.lower() in html_lower or tok.lower() in rlanding.text.lower()
        ]
        checks["no_prohibited_names"] = prohibited_hits == []
        steps["prohibited_hits"] = prohibited_hits

        # ── 8. tenant isolation inside the same run ──────────
        r_other = await c.get(
            f"/onboarding/page/sessions/{sid}",
            headers={"X-Onboarding-Scope": SCOPE_B},
        )
        body = r_other.text
        secrets_ = [BUSINESS_NAME, "กาแฟดำ", "ขนมอบ", "polite", SCOPE_A]
        checks["other_scope_404"] = r_other.status_code == 404
        checks["other_scope_leaks_nothing"] = (
            r_other.status_code == 404 and all(
                s not in body for s in secrets_
            )
        )
        rwo = await c.post(
            f"/onboarding/page/sessions/{sid}/answer",
            json={"text": "สุภาพ"},
            headers={"X-Onboarding-Scope": SCOPE_B},
        )
        checks["other_scope_write_blocked"] = rwo.status_code == 404

        # ── 9. unmapped typed input is rejected, nothing guessed ──
        r_junk = await _answer("qwertyzzz-9")
        checks["unmapped_answer_rejected"] = r_junk.status_code in (400, 422)

    # ── 10. Part B wiring proofs (outside the dev-escape sub-app) ──
    # 10a: mounted with NO server scope and NO escape → the router refuses
    # any client-chosen scope header (fail-closed, nothing served).
    async with await _client(OnboardingPageStore(),
                             dev_escapes=DevEscapes(),
                             web_fetch_fn=None) as c3:
        r_refuse = await c3.post(
            "/onboarding/page/sessions",
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        checks["no_scope_no_escape_refused"] = (
            r_refuse.status_code == 401
            and SCOPE_A not in r_refuse.text
        )
    # 10b: /website with no fetcher wired → clean handled 503, no traceback
    async with await _client(OnboardingPageStore(), web_fetch_fn=None) as c4:
        r_start = await c4.post(
            "/onboarding/page/sessions", headers={"X-Onboarding-Scope": SCOPE_A}
        )
        sid2 = r_start.json()["session_id"]
        r503 = await c4.post(
            f"/onboarding/page/sessions/{sid2}/website",
            json={"url": "https://jea-ma.example/menu"},
            headers={"X-Onboarding-Scope": SCOPE_A},
        )
        body = (r503.text or "").lower()
        checks["website_without_fetcher_clean_503"] = (
            r503.status_code == 503
            and all(s not in body for s in ("traceback", "typeerror",
                                            "handlers.py", "jea-ma"))
        )

    final = {"checks": checks, "steps": steps}

    # ── 11. production wiring: the REAL main.py app (including the
    # BodyLimitMiddleware) must still serve all three POST routes with a
    # real multipart/JSON body. The sub-apps above never mount it, which
    # is how the first middleware version broke every POST unnoticed.
    from app.main import app as production_app
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=production_app),
            base_url="http://t",
        ) as c_real:
            r_health = await c_real.get("/health")
            wiring_ok = r_health.status_code == 200
            # a session start on the real app fails CLOSED (no scope
            # bound) — that is CORRECT there; what must NOT happen is the
            # middleware turning a good body into a 400 parse error. A
            # 401/403 = body parsed fine; 400-with-parse-error = broken.
            r_w1 = await c_real.post("/onboarding/page/sessions")
            r_w2 = await c_real.post(
                "/onboarding/page/sessions/x/answer",
                json={"text": "ping"},
            )
            r_w3 = await c_real.post(
                "/onboarding/page/sessions/x/file",
                files={"file": ("m.csv", FILE_BYTES, "text/csv")},
            )
            statuses = (r_w1.status_code, r_w2.status_code, r_w3.status_code)
            wiring_ok = wiring_ok and all(s in (200, 201, 401, 403, 404)
                                          for s in statuses)
            print(f"[wiring] real-app POST statuses: {statuses}")
            final["wiring_statuses"] = list(statuses)
    except Exception as exc:  # noqa: BLE001
        wiring_ok = False
        final["wiring_error"] = repr(exc)
    checks["production_wiring_serves_all_post_routes"] = wiring_ok
    final["checks"] = checks

    TRANSCRIPT.write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    print(f"transcript: {TRANSCRIPT}")
    uncomputed = [k for k, v in checks.items() if v is None]
    ok = all(v is not None and v for v in checks.values())
    if uncomputed:
        print(f"FAILED: uncomputed checks: {uncomputed}")
    return 0 if ok else 1


def main() -> int:
    return asyncio.run(run())


if __name__ == "__main__":
    raise SystemExit(main())
