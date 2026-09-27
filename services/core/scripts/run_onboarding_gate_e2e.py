"""T-079d Part 2 runnable end-to-end proof: summary renders, gate paths,
fail-closed evidence — offline, no db, no network.

Run (from the repo root):
    python services/core/scripts/run_onboarding_gate_e2e.py

Prints both the rendered summary (extracted config + sample conversation)
and the checks dict. Exits 0 only when every check is true; an uncomputed
or None check FAILS. Transcript saved beside this script.
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
from app.onboarding.config import ConfigDraft
from app.onboarding.gate import GateError, GoLiveGate
from app.onboarding.gate_repo import InMemoryBotRepository
from app.onboarding.menus import EnabledTool, Tone
from app.onboarding.signals import extract_categories_from_price_file
from app.onboarding.summary import render_confirmation_summary, sample_conversation
from app.onboarding.page.prohibited import PROHIBITED_TOKENS

TRANSCRIPT = Path(__file__).with_name("onboarding_gate_e2e_transcript.json")


def build_draft(fill: bool) -> tuple[ConfigDraft, list[str]]:
    """Fill a draft through the REAL assistant surface (menu-mapped only).

    ``fill=False`` leaves fallback_contact unset to make an INCOMPLETE
    draft — the missing list is returned for the honesty check.
    """
    d = ConfigDraft()
    s = OnboardingSession(draft=d)
    s.set_business_type("เราเปิดร้านกาแฟ")
    s.set_business_name("ร้านกาแฟดอย")
    s.set_opening_hours("เราเปิด 08:00-18:00 ทุกวัน")
    file_text = "ลาเต้,55\nอเมริกาโน่,45\nชานมไข่มุก,50\n"
    s.set_menu_categories([n for n in extract_categories_from_price_file(file_text)])
    s.set_enabled_tools("อยากให้ตอบคำถามลูกค้า")
    if fill:
        s.set_fallback_contact("02-123-4567")
    s.offer_tone_menu("สุภาพและเป็นมิตร")
    if d.tone is None:
        s.offer_tone_menu("1")  # explicit fixed-menu pick, never guessed
    return d, list(s.draft.missing_fields())


def no_prohibited_text(text: str) -> bool:
    low = text.lower()
    return not any(tok in low for tok in (t.lower() for t in PROHIBITED_TOKENS))


FIXED_TOOL_VALUES = {t.value for t in EnabledTool}


def main() -> int:
    steps: list[dict[str, object]] = []
    checks: dict[str, bool] = {}
    gate_repo = InMemoryBotRepository()
    g = GoLiveGate(gate_repo, tenant_id="t1", bot_id="b1")

    # ── draft + summary ──────────────────────────────────
    draft, missing = build_draft(fill=True)
    summary_html = render_confirmation_summary(draft)
    conv = sample_conversation(draft)
    steps.append({"step": "summary_html", "value": summary_html})
    steps.append({"step": "sample_conversation", "value": conv})

    checks["summary_shows_config"] = "config-rows" in summary_html and "เวลาทำการ: 08:00-18:00" in summary_html
    checks["summary_shows_sample_conversation"] = bool(conv) and 'id="sample-conversation"' in summary_html
    checks["conversation_generated_from_config"] = any(
        "ร้านกาแฟดอย" in text or "08:00-18:00" in text for _, text in conv
    )
    checks["no_model_or_vendor_name_in_summary"] = (
        no_prohibited_text(summary_html) and all(no_prohibited_text(t) for _, t in conv)
    )
    checks["summary_complete_draft_gaps_empty"] = (
        "summary-missing" not in summary_html and missing == []
    )

    # ── happy path: confirm → active with fixed-menu rows ──
    out_ok = g.confirm(draft)
    row = gate_repo.get(bot_id="b1", tenant_id="t1")
    row_after_confirm = {
        "status": row.status, "tone": row.tone,
        "enabled_tools": list(row.enabled_tools),
        "business_info": row.business_info,
    }
    steps.append({"step": "persisted_row_after_confirm", "value": row_after_confirm})
    checks["confirm_persists_active"] = out_ok.status == "active" and row.status == "active"
    # Real assertion: the persisted row must CONTAIN the expected fixed-menu
    # values (not a string dump that is always truthy).
    persisted_actual = {
        "tone": row.tone, "tools": sorted(row.enabled_tools),
        "hours": row.business_info.get("opening_hours"),
        "contact": row.business_info.get("fallback_contact"),
        "status": row.status,
    }
    persisted_expected = {
        "tone": draft.tone.value if draft.tone else None,
        "tools": sorted(t.value for t in draft.enabled_tools),
        "hours": draft.opening_hours.open + "-" + draft.opening_hours.close
        if draft.opening_hours else None,
        "contact": draft.fallback_contact,
        "status": "active",
    }
    # Opening hours are persisted as a dict {"open": ..., "close": ...};
    # normalise the actual value into the same string form for the comparison.
    persisted_actual["hours"] = (
        f'{persisted_actual["hours"]["open"]}-{persisted_actual["hours"]["close"]}'
        if isinstance(persisted_actual["hours"], dict)
        and persisted_actual["hours"].get("open")
        and persisted_actual["hours"].get("close")
        else None
    )
    checks["persisted_config_shown"] = (
        persisted_actual == persisted_expected
        and all(v is not None for v in persisted_actual.values())
    )
    steps.append({"step": "persisted_row_summary", "value": row_after_confirm})
    steps.append({"step": "persisted_expected", "value": persisted_expected})
    checks["persisted_values_are_fixed_menu"] = (
        row.tone in Tone._value2member_map_
        and bool(row.enabled_tools)
        and all(t in FIXED_TOOL_VALUES for t in row.enabled_tools)
    )
    checks["persisted_no_free_text_instruction_keys"] = not any(
        k in row.business_info for k in ("prompt", "system_prompt", "instructions", "raw_text")
    )

    # ── edit path: edit revokes active, bot not live on unconfirmed edit ──
    g.edit(draft)
    row_after_edit = gate_repo.get(bot_id="b1", tenant_id="t1")
    steps.append({"step": "row_after_edit", "value": {"status": row_after_edit.status}})
    checks["edit_revokes_active"] = row_after_edit.status == "paused"
    re_confirm = g.confirm(draft)
    checks["reconfirm_after_edit_reactivates"] = re_confirm.status == "active"

    # ── fail-closed path: INCOMPLETE draft cannot be confirmed ──
    incomplete, incomplete_missing = build_draft(fill=False)
    if incomplete.fallback_contact is not None:
        incomplete.fallback_contact = None
    refused = False
    status_during = None
    try:
        g.confirm(incomplete)
    except GateError:
        refused = True
        status_during = gate_repo.get(bot_id="b1", tenant_id="t1").status
    checks["incomplete_confirm_refused"] = refused and status_during == "paused"
    checks["incomplete_summary_says_missing"] = (
        "ยังตั้งค่าไม่ครบ" in render_confirmation_summary(incomplete)
        and "fallback_contact" in list(incomplete.missing_fields())
    )

    # ── decline path: declining activates nothing ──
    out_dec = g.decline()
    checks["decline_never_activates"] = out_dec.outcome == "declined" and out_dec.status == "paused"

    # ── fail-closed guard on the proof itself ─────────────
    uncomputed = [k for k, v in checks.items() if v is None]
    ok = not uncomputed and all(checks.values())
    steps.append({"step": "checks", "value": checks})
    print("--- Confirmation summary (rendered HTML) ---")
    print(summary_html)
    print("--- Sample conversation ---")
    for speaker, text in conv:
        print(f"{speaker}: {text}")
    print("--- Persisted bot row after confirm ---")
    print(json.dumps(row_after_confirm, ensure_ascii=False, indent=2))
    if uncomputed:
        print(f"FAILED: uncomputed checks: {uncomputed}")
    print("checks:", json.dumps(checks, ensure_ascii=False))
    TRANSCRIPT.write_text(
        json.dumps({"steps": steps, "checks": checks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"transcript: {TRANSCRIPT}")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
