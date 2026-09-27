"""Onboarding assistant — conversation / URL / file → fixed-menu config.

Card T-079b. Contract: ``docs/product/ONBOARDING_FLOW.md`` (Cost controls),
``docs/product/CUSTOMER_FACING_RULES.md`` §3, ``docs/data/LITE_SCHEMA_V1.md``
(``bots.business_info``, ``tone``, ``enabled_tools``, quotas).

Non-negotiable rules, enforced structurally in code:

1. **Fixed-menu output only** — every produced value is a member of an
   enumerated menu defined in ``menus.py``. No free text is ever stored as
   an instruction or system prompt.
2. **No raw customer text as instructions** — what the prospect typed is
   *data* parsed into a menu choice (``signals.py``); the model prompt is
   rendered only from code constants (``assistant.SYSTEM_PROMPTS``).
3. **Cost bounds enforced** — page/file size caps, own-domain-only fetch,
   bounded page count (no full crawl) in ``ingest.py``.
4. **Ask only what is missing** — the driver never re-asks a filled field
   (``assistant.OnboardingSession.next_questions``).
5. **Honesty rule 2** — no prospect-facing text names a model or vendor;
   the module has no provider names and the LLM call is fully injectable.
"""
