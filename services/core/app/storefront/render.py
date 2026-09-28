"""Server-rendered HTML for the public storefront (T-079f Part 1).

The six sections follow ``docs/product/STOREFRONT.md`` exactly:
headline, live demo, what it does, price, one button, small print.
The price literal (299 THB/month) and the consent notice are read from
the already-approved sources — never re-invented here.
"""

from __future__ import annotations

from xml.sax.saxutils import escape as esc

from app.onboarding.page import PDPA_NOTICE

__all__ = ["render_storefront"]

_PAGE_TITLE = "ผู้ช่วยร้านของคุณ ตอบแชทตลอด 24 ชั่วโมง"

# Price literal comes from docs/product/PRICING_V1.md ("299 THB/month
# per bot, flat. One tier."). The test asserts this exact number.
PRICE_LINE = "299 บาทต่อเดือน"
PRICE_INCLUDED = (
    "บอทหนึ่งตัวสำหรับร้านของคุณ พร้อมโควตาข้อความรายเดือน "
    "และการตั้งค่าแบบสนทนาฟรีหนึ่งครั้ง"
)
PRICE_CANCEL = "ยกเลิกได้ทุกเมื่อ"

_HEADLINE = "ผู้ช่วยร้านของคุณ ตอบแชทลูกค้าตลอด 24 ชั่วโมง"
_WHAT_IT_DOES = (
    "ตอบคำถามลูกค้าอัตโนมัติ",
    "รับจองคิวแทนคุณ",
    "ส่งข้อความเตือนนัดหมาย",
)
_BUTTON_LABEL = "ตั้งค่าบอทของฉัน"
_BUTTON_HREF = "/onboarding/page/view"


def render_storefront() -> str:
    """Build the whole storefront page (six sections, one page)."""
    parts = [
        "<!DOCTYPE html>",
        '<html lang="th"><head><meta charset="utf-8">',
        f"<title>{esc(_PAGE_TITLE)}</title>",
        "</head><body>",
        _headline(),
        _live_demo(),
        _what_it_does(),
        _price(),
        _cta_button(),
        _small_print(),
        "</body></html>",
    ]
    return "\n".join(parts)


def _headline() -> str:
    return f'<section id="headline"><h1>{esc(_HEADLINE)}</h1></section>'


def _live_demo() -> str:
    # The working demo bot (web-chat channel) is wired in T-079f Part 2.
    # Part 1 renders the section and the shared consent notice only.
    return (
        '<section id="live-demo">'
        "<h2>ลองคุยกับบอทตัวอย่าง</h2>"
        '<div id="demo-slot">เดโมบอทจะเปิดให้ลองคุยที่นี่</div>'
        f'<p class="pdpa-notice" id="pdpa-notice">{esc(PDPA_NOTICE)}</p>'
        "</section>"
    )


def _what_it_does() -> str:
    items = "".join(f"<li>{esc(t)}</li>" for t in _WHAT_IT_DOES)
    return (
        '<section id="what-it-does">'
        "<h2>บอททำอะไรได้บ้าง</h2>"
        f"<ul>{items}</ul>"
        "</section>"
    )


def _price() -> str:
    return (
        '<section id="price">'
        "<h2>ราคา</h2>"
        f'<p class="price-line">{esc(PRICE_LINE)}</p>'
        f'<p class="price-included">{esc(PRICE_INCLUDED)}</p>'
        f'<p class="price-cancel">{esc(PRICE_CANCEL)}</p>'
        "</section>"
    )


def _cta_button() -> str:
    return (
        '<section id="cta">'
        f'<a class="cta-button" id="setup-button" href="{esc(_BUTTON_HREF)}">'
        f"{esc(_BUTTON_LABEL)}</a>"
        "</section>"
    )


def _small_print() -> str:
    return (
        '<section id="small-print">'
        '<nav id="small-print-links">'
        '<a href="#pdpa-notice" id="link-privacy">นโยบายความเป็นส่วนตัว (PDPA)</a>'
        '<span id="link-terms">เงื่อนไขการใช้บริการ</span>'
        '<span id="link-contact">ติดต่อเรา</span>'
        "</nav>"
        "</section>"
    )
