"""T-079d small fixes (Finding 4): unit tests for the summary renderer."""

from __future__ import annotations

from xml.sax.saxutils import escape as esc

import pytest

from app.onboarding.assistant import OnboardingSession
from app.onboarding.config import ConfigDraft
from app.onboarding.menus import EnabledTool, Tone
from app.onboarding.summary import render_confirmation_summary, sample_conversation


def full_draft() -> ConfigDraft:
    d = ConfigDraft()
    s = OnboardingSession(draft=d)
    s.set_business_type("เราเปิดร้านกาแฟ")
    s.set_business_name("ร้านกาแฟดอย")
    s.set_opening_hours("เราเปิด 08:00-18:00 ทุกวัน")
    s.set_menu_categories(["ลาเต้", "อเมริกาโน่"])
    s.set_enabled_tools("อยากให้ตอบคำถามลูกค้า")
    s.set_fallback_contact("02-123-4567")
    s.offer_tone_menu("สุภาพและเป็นมิตร")
    if d.tone is None:
        s.offer_tone_menu("1")
    return d


def test_fixed_menu_values_appear_in_output() -> None:
    html = render_confirmation_summary(full_draft())
    assert "config-rows" in html
    assert "ลาเต้" in html and "อเมริกาโน่" in html
    assert any(t.value in html for t in EnabledTool)
    assert "ลาเต้" in html and "อเมริกาโน่" in html


def test_incomplete_draft_shows_missing_notice() -> None:
    d = full_draft()
    d.fallback_contact = None
    html = render_confirmation_summary(d)
    assert "ยังตั้งค่าไม่ครบ" in html
    assert "fallback_contact" in html


def test_html_escaping_of_markup_in_values() -> None:
    d = full_draft()
    d.business_name = "<b>ร้าน</b>&ยา"
    html = render_confirmation_summary(d)
    assert "<b>ร้าน</b>" not in html
    assert esc("<b>ร้าน</b>&ยา") in html


def test_empty_draft_renders_no_conversation() -> None:
    html = render_confirmation_summary(ConfigDraft())
    assert sample_conversation(ConfigDraft()) == ()
    assert 'id="sample-conversation-empty"' in html


def test_every_tone_suffix_branch_renders() -> None:
    for tone in Tone:
        d = full_draft()
        d.tone = tone
        conv = sample_conversation(d)
        assert conv, f"tone {tone} must still generate a conversation"
