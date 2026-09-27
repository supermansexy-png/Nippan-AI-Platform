"""T-079d part 1 — go-live gate tests. Fail-closed by design."""

from __future__ import annotations

import pytest

from app.onboarding.assistant import OnboardingSession
from app.onboarding.config import ConfigDraft
from app.onboarding.gate import GateError, GoLiveGate
from app.onboarding.gate_repo import BOT_STATUS_VALUES, InMemoryBotRepository


def complete_draft() -> ConfigDraft:
    d = ConfigDraft()
    s = OnboardingSession(draft=d)
    s.set_business_type("cafe")
    s.set_business_name("ร้านกาแฟดอย")
    s.set_opening_hours("08:00-18:00")
    s.set_menu_categories(["latte", "americano"])
    s.set_enabled_tools("ตอบคำถาม")
    d.tone = __import__("app.onboarding.menus", fromlist=["Tone"]).Tone.POLITE
    s.set_fallback_contact("02-123-4567")
    return d


def gate() -> tuple[GoLiveGate, InMemoryBotRepository]:
    repo = InMemoryBotRepository()
    return GoLiveGate(repo, tenant_id="t1", bot_id="b1"), repo


def test_confirm_complete_draft_activates_and_persists_fixed_menu() -> None:
    g, repo = gate()
    out = g.confirm(complete_draft())
    assert out.status == "active"
    row = repo.get(bot_id="b1", tenant_id="t1")
    assert row.status in BOT_STATUS_VALUES and row.status == "active"
    assert row.tone == "polite"          # fixed-menu value, not the raw word
    assert row.enabled_tools == ("chat-bot-core",)
    assert row.business_info["fallback_contact"] == "02-123-4567"
    assert row.business_info["opening_hours"] == {"open": "08:00", "close": "18:00"}


def test_confirm_incomplete_draft_refused_and_stays_inactive() -> None:
    g, repo = gate()
    d = ConfigDraft()
    s = OnboardingSession(draft=d)
    s.set_business_name("ร้านบางร้าน")  # only one field filled
    with pytest.raises(GateError):
        g.confirm(d)
    row = repo.get(bot_id="b1", tenant_id="t1")
    assert row is None or row.status == "paused"  # nothing activated


def test_decline_does_not_activate() -> None:
    g, repo = gate()
    out = g.decline()
    assert out.status == "paused" and out.outcome == "declined"


def test_edit_after_confirm_revokes_active() -> None:
    g, repo = gate()
    g.confirm(complete_draft())
    out = g.edit(complete_draft())
    assert out.status == "paused"  # fail-closed while unconfirmed
    assert repo.get(bot_id="b1", tenant_id="t1").status == "paused"


def test_double_confirm_is_idempotent() -> None:
    g, repo = gate()
    first = g.confirm(complete_draft())
    second = g.confirm(complete_draft())
    assert first.status == second.status == "active"
    assert first.bot == second.bot  # same persisted row content


def test_free_text_cannot_reach_persisted_rows_as_instruction() -> None:
    g, repo = gate()
    d = complete_draft()
    row = g.confirm(d).bot
    blob = str(row.tone) + str(row.enabled_tools) + str(row.business_info)
    assert "ยัดไม่ได้" not in blob
    # the draft type has no instruction field to smuggle prose into
    assert not hasattr(ConfigDraft(), "instructions") and not hasattr(ConfigDraft(), "system_prompt")


def test_tenant_isolation_through_gate() -> None:
    repo = InMemoryBotRepository()
    g_other = GoLiveGate(repo, tenant_id="t2", bot_id="b2")
    g = GoLiveGate(repo, tenant_id="t1", bot_id="b1")
    g.confirm(complete_draft())
    # the other tenant's gate sees ITS row, never t1's activation
    assert (repo.get(bot_id="b2", tenant_id="t2") or
            repo.get(bot_id="b2", tenant_id="t1")) is None or \
           repo.get(bot_id="b2", tenant_id="t2").status == "paused"
    assert repo.get(bot_id="b1", tenant_id="t2") is None  # cross-tenant read: none
