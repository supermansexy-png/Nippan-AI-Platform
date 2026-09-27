"""Server-rendered HTML for the customer setup page (T-079c Part 2).

No front-end framework, no build step: one function builds the page from
the EXISTING session state (``handlers.state_of``), so progress comes from
the real missing fields, never re-computed here. Honesty rule 2: no model
name and no vendor name anywhere — enforced by ``test_page_rendering.py``.
"""

from __future__ import annotations

from xml.sax.saxutils import escape as esc

__all__ = ["render_page"]

_PAGE_TITLE = "ตั้งค่าบอทร้านคุณ"
_FIELD_LABELS = {
    "tone": "สไตล์การตอบ",
    "business_type": "ประเภทร้าน",
    "business_name": "ชื่อร้าน",
    "opening_hours": "เวลาทำการ",
    "menu_categories": "รายการเมนู",
    "enabled_tools": "เครื่องมือที่เปิดใช้",
    "fallback_contact": "ช่องทางติดต่อสำรอง",
}


def render_page(*, pdpa_notice: str, missing_fields: list[str],
                draft: dict, done: bool, banner: str = "") -> str:
    """Build the whole page: three inputs, progress, PDPA notice.

    ``banner`` is an optional pre-escaped HTML paragraph rendered before
    the form — used ONLY by the router to state plainly, when the dev
    escape is enabled, that identity is UNVERIFIED (never to advertise
    anything else).
    """
    parts = [
        "<!DOCTYPE html>",
        '<html lang="th"><head><meta charset="utf-8">',
        f"<title>{esc(_PAGE_TITLE)}</title>",
        "</head><body>",
        f"<h1>{esc(_PAGE_TITLE)}</h1>",
        banner,
        _progress(missing_fields, draft, done),
        _form(pdpa_notice),
        "</body></html>",
    ]
    return "\n".join(parts)


def _progress(missing_fields: list[str], draft: dict, done: bool) -> str:
    if done:
        return '<p id="progress">สถานะ: เสร็จสมบูรณ์</p>'
    done_items = [
        k for k in _FIELD_LABELS if k not in missing_fields and draft.get(k)
    ]
    remaining = [_FIELD_LABELS[f] for f in missing_fields if f in _FIELD_LABELS]
    done_html = "".join(
        f'<li class="done">{esc(_FIELD_LABELS[k])}: บันทึกแล้ว</li>'
        for k in done_items
    )
    left_html = "".join(
        f'<li class="missing">{esc(t)}: ยังไม่มี</li>' for t in remaining
    )
    return (
        '<section id="progress">'
        "<h2>ความคืบหน้า</h2>"
        f'<ul id="done-fields">{done_html}</ul>'
        f'<ul id="missing-fields">{left_html}</ul>'
        "</section>"
    )


def _form(pdpa_notice: str) -> str:
    pdpa = f'<p class="pdpa-notice" id="pdpa-notice">{esc(pdpa_notice)}</p>'
    text_input = (
        '<label>พิมพ์คำตอบ: '
        '<input type="text" name="answer" id="answer-input">'
        "</label>"
    )
    url_input = (
        '<label>ที่อยู่เว็บไซต์ร้าน: '
        '<input type="url" name="website" id="website-url" placeholder="https://">'
        "</label>"
    )
    file_input = (
        '<label>แนบไฟล์รายการเมนู: '
        '<input type="file" name="menu-file" id="menu-file">'
        "</label>"
    )
    return (
        '<form method="post" id="setup-form">'
        f"{text_input}{url_input}{file_input}{pdpa}"
        '<button type="submit" id="submit-answer">บันทึกคำตอบ</button>'
        "</form>"
    )
