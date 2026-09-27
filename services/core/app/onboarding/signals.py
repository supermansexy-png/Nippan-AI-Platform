"""Signals — parse what the prospect gave into fixed-menu choices.

Structural rule: customer text enters ONLY through ``parse_*`` functions
that return menu enum members or ``None``. There is no path from customer
text to a stored free-text instruction; the type system makes it so — the
only storable values are the enums and typed fields in ``config.py``.
"""

from __future__ import annotations

import re

from .menus import TASK_MENU, TONE_MENU, BusinessType

__all__ = [
    "parse_tone",
    "parse_task_choice",
    "parse_business_type",
    "extract_hours",
    "extract_category_names",
    "extract_categories_from_price_file",
]

_HOURS_RE = re.compile(r"\b(\d{1,2}[:.]\d{2})\s*[-–]\s*(\d{1,2}[:.]\d{2})\b")
# Only allows a safe charset in stored category names, capped at 40 chars.
_CATEGORY_CHARS_RE = re.compile(r"^[A-Za-zก-๙0-9 ()/,&.'-]{1,40}$")


def parse_tone(text: str) -> str | None:
    """Map prospect's tone answer to a fixed tone menu key ('1'..'5').

    Returns ``None`` when the text carries no tone hint — the caller asks
    for an explicit menu pick; it never guesses.
    """
    import unicodedata

    t = unicodedata.normalize("NFC", (text or "").strip().lower())
    if not t:
        return None
    if re.fullmatch(r"[1-5]", t):
        return t
    hints = {
        "สุภาพ": "1",
        "polite": "1",
        "formal": "5",
        "เป็นทางการ": "5",
        "เป็นกันเอง": "2",
        "friendly": "2",
        "สั้น": "3",
        "กระชับ": "3",
        "concise": "3",
        "สดใส": "4",
        "cheerful": "4",
        "มีความสุข": "4",
    }
    for hint, key in hints.items():
        if hint in t:
            return key
    return None


def parse_task_choice(text: str) -> list[str]:
    """Map prospect's task answer to fixed task menu keys. Unknown tokens
    are ignored (they are stored nowhere); a task repeated once stays once.
    """
    import unicodedata

    t = unicodedata.normalize("NFC", (text or "").strip().lower())
    from .menus import TASK_HINTS

    hits: list[str] = []
    for key in TASK_MENU:
        key_lower = key.lower().replace("_", " ")
        if key_lower in t or key in t:
            hits.append(key)
            continue
        for hint in TASK_HINTS.get(key, ()):
            if hint in t and key not in hits:
                hits.append(key)
    return hits


def parse_business_type(text: str) -> str | None:
    """Map a business-type description to the fixed menu; ``None`` if the
    prospect does not clearly map (caller asks; never guessed)."""
    import unicodedata

    t = unicodedata.normalize("NFC", (text or "").strip().lower())
    table = {
        ("cafe", "กาแฟ", "คาเฟ่"): "cafe",
        ("restaurant", "ร้านอาหาร", "food"): "restaurant",
        ("retail", "ร้านค้า", "shop", "ขายของ"): "retail_shop",
        ("salon", "ร้านเสริมสวย", "ความงาม"): "salon",
        ("service", "บริการ", "บริษัท"): "services",
    }
    for hints, value in table.items():
        if any(h in t for h in hints):
            return value
    return None


def extract_hours(text: str) -> str | None:
    """Extract an opening-hours range ``HH:MM-HH:MM`` from text.

    Returns a normalized range string or ``None``. This is *data extraction*
    into a structured field — the text itself is never stored.
    """
    if not text:
        return None
    m = _HOURS_RE.search(text)
    if not m:
        return None
    start, end = m.group(1).replace(".", ":"), m.group(2).replace(".", ":")
    return f"{start}-{end}"


def extract_category_names(text: str, limit: int = 20) -> list[str]:
    """Extract category names from a menu/price listing into the fixed
    ``menu_categories`` structured field.

    Charset-whitelist + length cap keep this DATA-ONLY: ``, `` ` `` ``|``,
    JSON braces, markdown, newlines and other injection surfaces are
    stripped from stored values, and the number of categories is capped.
    Unknown/unparseable input returns ``[]`` — the caller then asks the
    prospect (never guessed, never stored as free text).
    """
    if not text:
        return []
    seen: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("•-–*#0123456789. ")
        # Split a line on separators into candidate category names.
        for candidate in re.split(r"[|;:,]", line):
            name = candidate.strip()
            if not name or len(name) > 40:
                continue
            if not _CATEGORY_CHARS_RE.match(name):
                continue
            if name not in seen:
                seen.append(name)
            if len(seen) >= limit:
                return seen
    return seen


def extract_categories_from_price_file(text: str, limit: int = 20) -> list[str]:
    """Ingest an uploaded menu/price file (e.g. ``name,price`` CSV lines) into
    the fixed ``menu_categories`` structured field.

    The left column of each line is the category NAME; the right column is a
    PRICE, which is never stored. Every candidate still goes through the same
    charset-whitelist as ``extract_category_names`` — nothing beyond the
    whitelist can ever reach the draft (fixed-menu rule preserved).
    """
    if not text:
        return []
    seen: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        name = line.split(",", 1)[0].strip().lstrip("•-–*#0123456789. ")
        if not name or len(name) > 40 or not _CATEGORY_CHARS_RE.match(name):
            continue
        if name not in seen:
            seen.append(name)
        if len(seen) >= limit:
            break
    return seen
