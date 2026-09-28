"""Parse a customer's chat message into a ChangeRequest (T-079e rule 6).

The SAME rule T-079b/T-079c enforce: the message is parsed into FIXED-MENU
choices by the real onboarding parsers (``app/onboarding/signals.py``).
Text that maps nowhere stays in ``ChangeRequest.raw_text`` for the
refusal log only — it is persisted to no config, ever.
"""

from __future__ import annotations

import re

from ..onboarding.signals import extract_hours, parse_task_choice, parse_tone
from .request import ChangeRequest

__all__ = ["parse_chat_request"]


def parse_chat_request(
    *, tenant_id: str, bot_id: str, requested_by: str, text: str,
) -> ChangeRequest:
    req = ChangeRequest(tenant_id=tenant_id, bot_id=bot_id,
                        requested_by=requested_by, raw_text=text)
    if req.is_free_text_request():
        return req  # caller refuses via handle()
    tone_key = parse_tone(text)
    if tone_key:
        req.tone_menu_key = tone_key
    hours = extract_hours(text)
    if hours:
        req.hours_range = hours
    tasks = parse_task_choice(text)
    if tasks:
        req.task_keys = tuple(tasks)
    m = re.search(r"(\d+)\s*(?:messages|ข้อความ)", (text or "").lower())
    if m and ("quota" in text.lower() or "โควตา" in text):
        req.quota_field = "monthly_message_quota"
        req.quota_value = int(m.group(1))
    return req
