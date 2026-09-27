# Assistant: Onboarding

Kind: Onboarding assistant · Status: building (T-079b, Phase A Step 1) · Risk: L2

- Implementation: `services/core/app/onboarding/` (menu/signal/
  cost-bound/ingest/session modules + tests + runnable e2e proof script
  `scripts/run_onboarding_e2e.py`, run from the repo root)
- Inputs (any mix): plain conversation, website URL (via `web-fetch`
  bounded to the shop's OWN domain), uploaded menu/price file (via
  `file-reader`). No other MCP tool is touched.
- Output: fixed-menu config rows only, shaped to `bots.*` fields of
  `docs/data/LITE_SCHEMA_V1.md`: `tone` (fixed 5-tone list),
  `business_type`, `business_info` (opening hours `HH:MM-HH:MM`,
  whitelist-charset category names), `enabled_tools` (only tools from
  `docs/product/MCP_TOOLS_V1.md`), `fallback_contact` (ND-2),
  `monthly_message_quota` = 300, `monthly_push_quota` = 200 (defaults per
  PRICING_V1/LITE_SCHEMA; overridable by the platform, never by the
  prospect).
- Rule 2 structural guarantee: customer prose can only enter through
  `signals.py` parse/extract functions that return menu keys or
  structured fields (`ConfigDraft` has NO free-text instruction field —
  tests prove this by asserting the row shape). The one injected-model
  call, `classify_with_llm`, sends customer text ONLY as data; its
  system prompt is a fixed constant (`SYSTEM_PROMPTS`) and its answer
  must be an existing menu key — anything else raises
  `UnmappedInputError` and nothing is stored.
- Cost controls (enforced, real checks — ONBOARDING_FLOW.md "Cost
  controls"): per-page cap 200 KB, per-file cap 500 KB (oversize
  REJECTED), web fetch own-site-only via origin comparison (`DomainError`
  on any other host), bounded page count `MAX_PAGES = 5` per session —
  `FetchBudgetExhausted` refuses further fetches; no full site crawl.
- Ask-only-what-is-missing: `OnboardingSession.next_questions()` derives
  from `ConfigDraft.missing_fields()`; a filled field is never re-asked.
- Honesty rule 2 honored: the module names no model or vendor anywhere;
  no `api_key`/provider/slug is hardcoded (tests scan for these). The
  LLM is fully injectable (`LLMClient` protocol / stub) — the e2e script
  and all tests run with zero network calls and zero paid model calls.
- Unmapped/invalid input → REJECTED (`UnmappedInputError`), never
  guessed; injection-looking category names are stripped by the charset
  whitelist and if nothing valid remains the input is rejected.
- Known limits (Phase A): business_type/tone/task mapping is keyword
  hint-based, not semantic; PDF/image extraction (real `file-reader`)
  arrives in a later card — the interface (`FileReader.read_fn`) is
  already injectable for it; no persistence yet (produces the row;
  writing to `lite_bots` is a later step).
