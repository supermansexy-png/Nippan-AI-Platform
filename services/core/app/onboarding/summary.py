"""Confirmation summary (T-079d part 2): show the customer the extracted
fixed-menu config plus a sample conversation ("your bot will say things
like…"), per ONBOARDING_FLOW.md steps 4-5.

Rules:
- The sample conversation is GENERATED from the fixed-menu values
  (business_name, hours, categories, contact) — never invented free text.
- No model or vendor name anywhere (honesty rule 2; checked by a test
  against the real PROHIBITED_TOKENS list).
- If the draft is incomplete, the summary SAYS what is still missing —
  it never papers over gaps.
- No new front-end framework: server-rendered strings in the same style
  as ``app/onboarding/page/render.py`` (xml.sax.saxutils.escape).
"""

from __future__ import annotations

from xml.sax.saxutils import escape as esc

from .config import ConfigDraft
from .menus import BusinessType, Tone
from .page.render import _FIELD_LABELS  # reuse the same field labels

__all__ = ["sample_conversation", "render_confirmation_summary"]

# Fixed phrase templates per tone — the filler words differ, the FACTS in
# every line come from the draft's values only.
_TONE_SUFFIX: dict[Tone, str] = {
    Tone.POLITE: "ครับ/ค่ะ",
    Tone.FRIENDLY: "นะคะ",
    Tone.CONCISE: "",
    Tone.CHEERFUL: "ค่ะ!",
    Tone.FORMAL: "ครับ/ค่ะ",
}

_TYPE_LABEL = {t: t.value for t in BusinessType}


def sample_conversation(draft: ConfigDraft) -> tuple[tuple[str, str], ...]:
    """Walk-through lines generated ONLY from fixed-menu values.

    Each bot line is one of a few fixed templates filled with the draft's
    own values; missing values are left out of the lines entirely (never
    fabricated).
    """
    suffix = _TONE_SUFFIX.get(draft.tone, "") if draft.tone else ""
    lines: list[tuple[str, str]] = []
    if draft.business_name:
        lines.append(("ลูกค้า", "มีเมนูอะไรบ้าง"))
        cats = "และ ".join(draft.menu_categories[:3]) if draft.menu_categories else ""
        greet = f"{draft.business_name} ยินดีต้อนรับ{suffix}".strip()
        menu_line = "ทางร้านมีเมนู" + (f" เช่น {cats}" if cats else "") + suffix
        lines.append(("บอท", greet))
        lines.append(("ลูกค้า", f"ขอดูเมนูทางร้าน {draft.business_name}"))
        lines.append(("บอท", menu_line))
        lines.append(("ลูกค้า", "เปิดกี่โมง"))
        lines.append(("บอท", f"เปิด {draft.opening_hours.open}-{draft.opening_hours.close}{suffix}"))
    if draft.fallback_contact:
        lines.append(("ลูกค้า", "ติดต่อเจ้าของร้านยังไง"))
        lines.append(("บอท", f"ฝากข้อความไว้ได้ ทางร้านจะติดต่อกลับที่ {draft.fallback_contact}{suffix}"))
    return tuple(lines)


def _config_rows(draft: ConfigDraft) -> str:
    rows = []
    hours = (
        f"{draft.opening_hours.open}-{draft.opening_hours.close}"
        if draft.opening_hours else None
    )
    shown = {
        "tone": draft.tone.value if draft.tone else None,
        "business_type": (_TYPE_LABEL[draft.business_type]
                          if draft.business_type else None),
        "business_name": draft.business_name,
        "opening_hours": hours,
        "menu_categories": ", ".join(draft.menu_categories) or None,
        "enabled_tools": ", ".join(t.value for t in draft.enabled_tools) or None,
        "fallback_contact": draft.fallback_contact,
    }
    for key, value in shown.items():
        label = _FIELD_LABELS.get(key, key)
        if value is None:
            rows.append(f'<li class="missing">{esc(label)}: ยังไม่มี</li>')
        else:
            rows.append(f'<li class="done">{esc(label)}: {esc(str(value))}</li>')
    return "".join(rows)


def render_confirmation_summary(draft: ConfigDraft) -> str:
    """Full summary: config rows + sample conversation + honest gaps."""
    missing = draft.missing_fields()
    parts = [
        '<section id="confirm-summary" class="confirm-summary">',
        "<h2>สรุปการตั้งค่าบอทของคุณ</h2>",
        f'<ul id="config-rows">{_config_rows(draft)}</ul>',
    ]
    if missing:
        listed = esc(", ".join(missing))
        parts.append(
            '<p id="summary-missing" class="summary-missing">'
            f"ยังตั้งค่าไม่ครบ จะยืนยันเปิดใช้ไม่ได้จนกว่าจะครบ: {listed}</p>"
        )
    parts.append("<h2>ตัวอย่างบทสนทนา</h2>")
    conv = sample_conversation(draft)
    if conv:
        parts.append('<ul id="sample-conversation">')
        parts.extend(
            f'<li><strong>{esc(speaker)}</strong>: {esc(text)}</li>'
            for speaker, text in conv
        )
        parts.append("</ul>")
    else:
        parts.append('<p id="sample-conversation-empty">ยังไม่มีข้อมูลพอสำหรับตัวอย่าง</p>')
    parts.append("</section>")
    return "\n".join(parts)
