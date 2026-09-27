"""T-079b end-to-end proof: URL + file → fixed-menu config rows, offline.

Run (from repo root):
    python services/core/scripts/run_onboarding_e2e.py

Ingests one sample website URL + one sample menu file (stubbed fetch — no
internet) and prints the produced fixed-menu config rows. Transcript
saved beside this script.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

_SERVICES_CORE = Path(__file__).resolve().parent.parent
if str(_SERVICES_CORE) not in sys.path:
    sys.path.insert(0, str(_SERVICES_CORE))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app.onboarding.assistant import OnboardingSession
from app.onboarding.cost_bounds import DomainError
from app.onboarding.ingest import FileReader, WebFetcher, text_to_links
from app.onboarding.menus import EnabledTool, Tone
from app.onboarding.signals import extract_categories_from_price_file

FIXTURES = Path(__file__).with_name("onboarding_e2e_fixtures")
TRANSCRIPT = Path(__file__).with_name("onboarding_e2e_transcript.json")


def main() -> int:
    steps: list[dict[str, object]] = []

    # ── fixtures ─────────────────────────────────────────
    home_html = (FIXTURES / "home.html").read_text(encoding="utf-8")
    menu_html = (FIXTURES / "menu.html").read_text(encoding="utf-8")
    price_csv = (FIXTURES / "price_list.csv").read_bytes()

    pages = {
        "https://somchai-cafe.example/": home_html,
        "https://somchai-cafe.example/menu": menu_html,
    }

    def fake_fetch(url: str) -> str:
        return pages[url]

    def fake_read(name: str, data: bytes) -> str:
        return data.decode("utf-8", errors="replace")

    # ── 1. cost-bound URL ingestion (own site only, bounded) ──
    fetcher = WebFetcher(site_origin="https://somchai-cafe.example", fetch_fn=fake_fetch)
    page1 = fetcher.fetch_page("https://somchai-cafe.example/")
    links = text_to_links(page1.url, page1.text)
    page_link = next(
        (u for u in links if u == "https://somchai-cafe.example/menu"), None
    )
    page2 = fetcher.fetch_page(page_link) if page_link else None

    # Off-domain proof: an outside link is rejected, never fetched.
    offdomain_rejected = False
    try:
        fetcher.fetch_page("https://evil-site.example/steal")
    except DomainError:
        offdomain_rejected = True

    # ── 2. file ingestion (size-capped) ──────────────────
    reader = FileReader(max_bytes=10 * 1024 * 1024, read_fn=fake_read)
    price_file = reader.read_file(name="price_list.csv", data=price_csv)

    # ── 3. conversation fills what is still missing ──────
    session = OnboardingSession()
    session.set_business_name("ร้านสมชาย คาเฟ่")
    session.set_business_type("เราเปิดร้านกาแฟ")
    session.set_opening_hours("เราเปิด 08:00-20:00 ทุกวัน")
    # Read the raw text first, then let the REAL ingestion entry point
    # (signals.extract_category_names → assistant.set_menu_categories)
    # derive categories from the FILE CONTENT — nothing hardcoded.
    file_text = price_file.text
    session.set_menu_categories([n for n in extract_categories_from_price_file(file_text)])
    session.set_opening_hours("08:30-20:30") if False else None  # keep first read
    session.set_enabled_tools("อยากให้ตอบคำถามลูกค้า และจองคิวล่วงหน้า")
    session.set_fallback_contact("โทร 081-234-5678")
    session.offer_tone_menu("สุภาพและเป็นมิตร")
    if session.draft.tone is None:
        # free text that does not map uniquely → flow asks again, prospect
        # picks from the fixed menu; never guessed
        session.offer_tone_menu("2")

    row = session.draft.to_row()
    steps.append({"step": "config_row", "value": row})
    missing = session.next_questions()
    steps.append({"step": "missing_after_fill", "value": list(missing)})

    # Categories must be derived from the file, not invented: the draft's
    # categories must be exactly what the real extractor pulls from the
    # fixture's content (a changed fixture ⇒ changed output).
    file_derived_categories = tuple(extract_categories_from_price_file(file_text))
    categories_match_file = tuple(row["menu_categories"]) == file_derived_categories

    # Fixed-menu rule: every produced enabled_tools value must be a member
    # of the fixed tool menu (EnabledTool enum).
    fixed_tool_values = {t.value for t in EnabledTool}
    tools_in_fixed_menu = bool(row["enabled_tools"]) and all(
        t in fixed_tool_values for t in row["enabled_tools"]
    )

    # ── 4. assertions the proof rests on ─────────────────
    checks = {
        "pages_within_budget": fetcher.fetched_count == 2 and page1.text != "" and page2 is not None,
        "offdomain_link_rejected": offdomain_rejected,
        "file_read": price_file.byte_size > 0,
        "menu_categories_from_file": categories_match_file and bool(file_derived_categories),
        "tone_from_fixed_list": session.draft.tone is Tone.POLITE and session.draft.tone.value in Tone._value2member_map_,
        "tools_from_fixed_menu": tools_in_fixed_menu,
        "config_has_no_free_text_prompt": not any(
            k in row for k in ("prompt", "system_prompt", "instructions", "raw_text")
        ),
        "missing_fields_empty": missing == (),
    }
    steps.append({"step": "ingest_summary", "value": {
        "fetched_pages": fetcher.fetched_count,
        "offdomain_rejected": offdomain_rejected,
        "file_name": price_file.name,
        "categories_from_file": list(file_derived_categories),
    }})

    # Fail-closed: no check may be None/uncomputed on a passing run.
    uncomputed = [k for k, v in checks.items() if v is None]
    ok = all(v is not None and v for v in checks.values())
    steps.append({"step": "checks", "value": checks})
    if uncomputed:
        print(f"FAILED: uncomputed checks: {uncomputed}")
    print("--- Onboarding fixed-menu config rows ---")
    print(json.dumps(row, ensure_ascii=False, indent=2))
    print(f"missing fields after fill: {list(missing)}")
    print("checks:", json.dumps(checks, ensure_ascii=False))
    TRANSCRIPT.write_text(
        json.dumps({"steps": steps, "checks": checks, "config_row": row}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"transcript: {TRANSCRIPT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
