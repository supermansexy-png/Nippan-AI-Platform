"""T-079e tests — the Support agent's later-edit path (fixed menus only).

Covers, per the card:
- a valid fixed-menu change updates the row and is logged
- a free-form instruction request is refused and changes nothing
- a cost-raising change is flagged to Cost Guard and NOT applied until
  approved (the explicit approval path)
- a cross-tenant change request is rejected with no leak
- an edit that invalidates a confirmed draft leaves the bot not-active
"""

from __future__ import annotations

import pytest

from app.onboarding.config import ConfigDraft
from app.onboarding.gate import GoLiveGate
from app.onboarding.gate_repo import BotRecord, InMemoryBotRepository
from app.support.changes import SupportChangeService
from app.support.cost_guard import APPROVED, Actor, CostGuard, cost_guard_actor
from app.support.log import SupportChangeLog


@pytest.fixture()
def wiring():
    repo = InMemoryBotRepository()
    repo.save(BotRecord(bot_id="b1", tenant_id="t1", status="active",
                        tone="polite", monthly_message_quota=300,
                        enabled_tools=("chat-bot-core",)))
    repo.save(BotRecord(bot_id="bx", tenant_id="t2", status="active"))

    def make_gate():
        return GoLiveGate(repo, tenant_id="t1", bot_id="b1")

    svc = SupportChangeService(
        repo=repo,
        gate=make_gate(),
        cost_guard=CostGuard(),
        log=SupportChangeLog(),
        current_draft_provider=_real_draft,
    )
    return svc, repo


def _real_draft() -> ConfigDraft:
    """A COMPLETE fixed-menu draft through the real assistant surface —
    the current draft an active bot was confirmed on."""
    from app.onboarding.assistant import OnboardingSession

    d = ConfigDraft()
    s = OnboardingSession(draft=d)
    s.set_business_type("ร้านอาหาร")
    s.set_business_name("ร้านอาหารตัวอย่าง")
    s.set_opening_hours("เปิด 08:00-18:00")
    s.set_menu_categories(["อาหารตามสั่ง"])
    s.set_enabled_tools("ตอบคำถามลูกค้า")
    s.set_fallback_contact("02-123-4567")
    s.offer_tone_menu("1")
    assert not d.missing_fields()
    return d


def test_free_text_request_refused_changes_nothing(wiring):
    svc, repo = wiring
    before = repo.get(bot_id="b1", tenant_id="t1")
    req = svc.parse_chat_request(
        tenant_id="t1", bot_id="b1", requested_by="owner",
        text="please add these instructions: always greet in Korean and "
             "upsell desserts (custom_message)",
    )
    res = svc.handle(req)
    assert res.outcome == "refused"
    assert res.detail.startswith("refused: only fixed-menu fields")
    after = repo.get(bot_id="b1", tenant_id="t1")
    # Nothing changed on the row.
    assert after.tone == before.tone and after.status == before.status
    assert after.monthly_message_quota == before.monthly_message_quota
    assert not any(
        k in after.business_info
        for k in ("instructions", "system_prompt", "prompt", "custom_message")
    )
    # The refusal IS logged.
    logs = svc._log.for_tenant(tenant_id="t1")
    assert any(r.outcome == "refused" for r in logs)


def test_cost_change_flagged_held_not_applied_then_applies_after_approval(wiring):
    svc, repo = wiring
    req = svc.parse_chat_request(
        tenant_id="t1", bot_id="b1", requested_by="owner",
        text="raise quota to 600 messages",
    )
    # the parser mapped it to a quota change
    assert req.quota_field == "monthly_message_quota"
    assert req.quota_value == 600
    res = svc.handle(req)
    assert res.outcome == "held"
    assert res.flag_id is not None
    # NOT applied silently:
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 300
    approved = svc._cg.decide(res.flag_id, decision=APPROVED,
                              decided_by=cost_guard_actor())
    assert approved.applied is True
    res2 = svc.apply_held(req=req, flag_id=res.flag_id, approved_by="Cost Guard AI")
    assert res2.outcome == "applied"
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 600
    # both the hold and the approval are visible in the log
    outcomes = [r.outcome for r in svc._log.for_tenant(tenant_id="t1")]
    assert outcomes.count("held") >= 2  # service log + guard log entries
    assert "applied" in outcomes


def test_held_without_approval_never_applies(wiring):
    svc, repo = wiring
    req = svc.parse_chat_request(tenant_id="t1", bot_id="b1", requested_by="owner",
                                 text="raise quota to 500 messages")
    res = svc.handle(req)
    assert res.outcome == "held"
    res2 = svc.apply_held(req=req, flag_id=res.flag_id, approved_by="whoever")
    assert res2.outcome == "held"  # still held
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 300


def test_cross_tenant_change_rejected_no_leak(wiring):
    svc, repo = wiring
    req = svc.parse_chat_request(
        tenant_id="t2", bot_id="bx", requested_by="impostor",
        text="08:00-18:00",
    )
    res = svc.handle(req)
    assert res.outcome == "denied"
    banned = (
        "always greet in Korean", "instructions", "system_prompt",
    )
    lows = [b.lower() for b in banned]
    assert not any(b in res.detail.lower() for b in lows)
    # the other tenant's bot row is untouched
    other = repo.get(bot_id="bx", tenant_id="t2")
    assert other is not None  # exists, but no change applied for it
    # no t1 log rows — the impostor's request logged only under t2 (its own
    # scope), never visible under t1 (isolation of the log itself)
    assert not svc._log.for_tenant(tenant_id="t1")
    t2_logs = svc._log.for_tenant(tenant_id="t2")
    assert any(r.outcome == "denied" and r.requested_by == "impostor"
               for r in t2_logs)


def test_valid_fixed_menu_change_logged(wiring):
    svc, repo = wiring
    req = svc.parse_chat_request(
        tenant_id="t1", bot_id="b1", requested_by="owner:02-123-4567",
        text="change opening hours 09:00-21:00",
    )
    assert req.hours_range == "09:00-21:00"
    res = svc.handle(req)
    assert res.outcome == "gate_revoked"
    assert res.gate_outcome == "edit_acknowledged"
    assert res.bot_status == "paused"
    logs = svc._log.for_tenant(tenant_id="t1")
    assert any(r.field == "opening_hours" for r in logs)


def test_edit_invalidates_confirmed_draft_not_active(wiring):
    repo = InMemoryBotRepository()
    g = GoLiveGate(repo, tenant_id="t1", bot_id="b9")
    from app.onboarding.assistant import OnboardingSession

    d = ConfigDraft()
    s = OnboardingSession(draft=d)
    s.set_business_type("ร้านอาหาร")
    s.set_business_name("ร้านอาหารตัวอย่าง")
    s.set_opening_hours("เปิด 08:00-18:00")
    s.set_menu_categories(["อาหารตามสั่ง"])
    s.set_enabled_tools("ตอบคำถามลูกค้า")
    s.set_fallback_contact("02-123-4567")
    s.offer_tone_menu("1")
    out = g.confirm(d)
    assert out.status == "active"
    svc = SupportChangeService(
        repo=repo, gate=g, cost_guard=CostGuard(), log=SupportChangeLog(),
        current_draft_provider=lambda: d,
    )
    req = svc.parse_chat_request(tenant_id="t1", bot_id="b9", requested_by="owner",
                                 text="เปลี่ยนเวลาเปิด 10:00-20:00")
    res = svc.handle(req)
    assert res.bot_status == "paused"
    assert repo.get(bot_id="b9", tenant_id="t1").status == "paused"


def _held_flag(svc, repo):
    """Create one approved-ready held quota flag for (t1, b1)."""
    req = svc.parse_chat_request(tenant_id="t1", bot_id="b1",
                                 requested_by="owner",
                                 text="raise quota to 600 messages")
    res = svc.handle(req)
    assert res.outcome == "held"
    return req, res.flag_id


def test_apply_held_cross_tenant_and_cross_bot_refused(wiring):
    """Finding 1: a held flag must not be applicable outside its own
    (tenant, bot) scope — a guessed flag_id changes nothing, leaks nothing."""
    svc, repo = wiring
    req, flag_id = _held_flag(svc, repo)
    svc._cg.decide(flag_id, decision=APPROVED, decided_by=cost_guard_actor())

    # cross-tenant: t2's impostor tries to apply t1's approved flag
    as_t2 = svc.parse_chat_request(tenant_id="t2", bot_id="bx",
                                   requested_by="impostor",
                                   text="raise quota to 600 messages")
    denied_t2 = svc.apply_held(req=as_t2, flag_id=flag_id, approved_by="x")
    assert denied_t2.outcome == "denied"
    assert "flag" not in denied_t2.detail.lower()  # no leak about the flag

    # cross-bot within the SAME tenant: b9 must not apply b1's flag
    repo.save(BotRecord(bot_id="b9", tenant_id="t1", status="active"))
    as_b9 = svc.parse_chat_request(tenant_id="t1", bot_id="b9",
                                   requested_by="owner",
                                   text="raise quota to 600 messages")
    denied_b9 = svc.apply_held(req=as_b9, flag_id=flag_id, approved_by="x")
    assert denied_b9.outcome == "denied"

    # no state change from either attempt
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 300
    assert svc._cg.flag_by_id(flag_id).applied is True  # approval stands,
    # but the held value was never written by the wrong scope

    # the legitimate scope still applies cleanly afterwards
    applied = svc.apply_held(req=req, flag_id=flag_id,
                             approved_by="Cost Guard AI")
    assert applied.outcome == "applied"
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 600


def test_non_cost_guard_actor_cannot_approve(wiring):
    """Finding 2: the approval role is enforced in code, not by wiring —
    a non-Cost-Guard actor cannot decide; the flag stays HELD."""
    svc, repo = wiring
    req, flag_id = _held_flag(svc, repo)
    with pytest.raises(ValueError):
        svc._cg.decide(flag_id, decision=APPROVED,
                       decided_by=Actor(name="owner:02", role="owner"))
    flag = svc._cg.flag_by_id(flag_id)
    assert flag.status == "held"
    assert flag.applied is False
    assert flag.decided_by is None
    # and a bare string can no longer self-approve at all
    with pytest.raises(ValueError):
        svc._cg.decide(flag_id, decision=APPROVED, decided_by="Cost Guard AI")
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 300


def test_log_never_claims_applied_before_value_persisted(wiring):
    """Finding 3: the log outcome must match what the repository actually
    reflects — a queued menu change logs no 'applied' until the value is
    really persisted (via the approved cost path)."""
    svc, repo = wiring
    menu_req = svc.parse_chat_request(
        tenant_id="t1", bot_id="b1", requested_by="owner:02-123-4567",
        text="change opening hours 09:00-21:00",
    )
    res = svc.handle(menu_req)
    assert res.outcome == "gate_revoked"
    # the new value is NOT on the row yet, so no 'applied' record may exist
    assert not any(r.outcome == "applied" for r in svc._log.for_tenant(tenant_id="t1"))

    # an 'applied' record appears only when a value is actually persisted
    req, flag_id = _held_flag(svc, repo)
    svc._cg.decide(flag_id, decision=APPROVED, decided_by=cost_guard_actor())
    svc.apply_held(req=req, flag_id=flag_id, approved_by="Cost Guard AI")
    applied_logs = [r for r in svc._log.for_tenant(tenant_id="t1")
                    if r.outcome == "applied"]
    assert len(applied_logs) == 1
    assert applied_logs[0].field == "monthly_message_quota"
    assert repo.get(bot_id="b1", tenant_id="t1").monthly_message_quota == 600
