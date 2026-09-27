# Tasks

Board rules: `docs/warroom/TASK_CONTROL.md`. Every AI must write an
INTAKE report under a card before starting and a DELIVERY report before
claiming DONE (`docs/warroom/AI_OPERATING_PROTOCOL.md`). Build order:
`docs/warroom/STARTUP_PLAYBOOK.md`.

Housekeeping (Owner order 2026-09-25): this board holds ONLY open cards.
The moment a card reaches DONE it is moved to `docs/archive/TASKS_DONE_ARCHIVE.md`.
Blocked / superseded cards live in `docs/archive/TASKS_PARKED.md`.

Completed work: docs/archive/TASKS_DONE_ARCHIVE.md

## ACTIVE

### Board size (Owner order 2026-09-25; cap raised 2026-09-26)
- DONE cards are archived immediately; the board holds only open cards.
- **Cap: 10 open cards** (Owner order 2026-09-26 — raised from 5; the board had already been running at 11 open cards before this change, so the old cap was not being enforced).
- Blocked / superseded cards live in `docs/archive/TASKS_PARKED.md`.
- Inside the cap, WIP is governed by `TASK_CONTROL.md` section 5 (max **10** IN_PROGRESS, 5 REVIEW — IN_PROGRESS raised from 3 by Owner order 2026-09-26, card T-046).

> **PARKED — moved off the board 2026-09-27 (Owner order) to `docs/archive/TASKS_PARKED.md`:** the pre-HOLD set (**T-032, T-033, T-071, T-072, T-073, T-074, T-075, T-076**) plus **T-078** (auto-card mechanism, parked for a different reason — see its card). They are **not done**; they resume only when the Owner orders "เดินต่อ". Full cards and their INTAKE/DELIVERY records live in the parked file — nothing was closed.

---

> T-030 (DONE 2026-09-26) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`.
> T-031 (DROPPED 2026-09-25) is archived in `docs/archive/TASKS_PARKED.md`.
> T-049 (DONE 2026-09-26, reviewer ACCEPT-WITH-FINDINGS) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md` (archived 2026-09-26 under card T-050, Owner-authorized).

> **T-034b (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: War Room create-room path + usable agenda delivered, reviewed, merged (PR #86) and deployed to the Render preview (live).

### T-050 — Whole-project study: convene an existing-role committee and return a detailed draft roadmap

Status: NEEDS_DECISION — Owner-ordered 2026-09-26 (verbatim order below); read-only study; deliverables are **DRAFT — NOT APPROVED** — waiting for the Owner to read the DRAFT roadmap (`docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md`)
Owner: Project Lead — 2026-09-26 (order relayed through the advisor `opencode-go/mimo-v2.6-pro`)
Role: Project Lead (chair + integrate; writes this card and the draft doc) + an existing-role study panel — researcher, builder (estimates only, no code), ops, security, model-recruiter — + reviewer `opencode-go/space-bunny-free` (≠ author) + security reviewer `opencode-go/kimi-k3` (≠ author ≠ reviewer)
Risk: L1 — read-only planning/study. No code, no runtime/production, no DB write, no deploy, no credential/auth-file inspection, no new infrastructure, no new paid spend.
Goal: every remaining piece of "this project" becomes visible in one place with a detailed, evidence-based, whole-repository roadmap from today's verified state through a first-customer pilot, onboarding/limited launch and a conditional later expansion — for the Owner to review and decide. **No implementation starts.**
Done when:
- [x] T-049 archived verbatim to `docs/archive/TASKS_DONE_ARCHIVE.md`; board recounted; next free id (T-050) verified absent before this card
- [x] this card exists before the study; the receiver's advisor instruction record is appended to `docs/warroom/ADVISOR_LOG.md`
- [x] committee findings/minutes recorded, including agreement, disagreement and missing evidence
- [x] a detailed draft roadmap exists (work packages, relative durations + assumptions, dependencies/critical path, risks, gates, verification evidence, resource/cost notes, Owner decisions); customer launch separated from internal tooling
- [x] a reviewer on a different model checks coverage/status/timeline claims; security separately checks the security/privacy gates
- [x] no implementation or listed pending item started
- [x] the meeting findings + the DRAFT roadmap are returned to the Owner; the card waits for the Owner's decision
Budget: read-only; the panel runs on the existing OpenCode Go subscription + free models only — **no new paid spend**; no paid L4 review requested.
Links: `docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md` (the deliverable, DRAFT — NOT APPROVED), `docs/warroom/ADVISOR_LOG.md` (T-050), `docs/warroom/STARTUP_PLAYBOOK.md`, `TASKS.md`, `docs/archive/`

**Owner order (verbatim):** "ผมว่านะอันนี้เอากลับไปปรึกษากับ pl และให้ตั้งคณะศึกษาโครงการนี้ขึ้นมา แล้วช่วยกันทำ โรดแมพ แบบละอียดพร้อมระบุช่วงเวลาให้ละเอียด พร้ัอมแผนงานอย่างละเอียดเลยนะ แล้วเอากลับมากางดูกันใหม่ ตอนนี้เหมือนจะ งง กันหมดทุกฝ่ายเลย แล้วรอเอาผลประชุมพร้อมโรดแมพกลับมา ที่บอกว่าโครงการนี้คือทั้งหมดของอันนี้นะ https://github.com/supermansexy-png/Nippan-AI-Platform"

INTAKE T-050 — 2026-09-26 (Project Lead) — ACCEPT (Owner-ordered; relayed by the advisor).
Understanding: the team is out of alignment about what "this project" is; the Owner wants one committee study that produces a detailed, time-phased, whole-repository roadmap plus meeting findings, returned for his review. Nothing is implemented.
Scope: read-only survey of the whole repo; existing roles only; minutes + a draft roadmap; reviewer + separate security check. Customer launch kept separate from internal tooling.
Needs: the existing dev roles (researcher, builder, ops, security, model-recruiter), the reviewer and security models, and the repo docs.
Missing: nothing that blocks the study; some hosting/backup facts are not provable read-only → reported as UNKNOWN.
Plan: (1) archive T-049 + this card + the record; (2) dispatch the panel read-only, each returning its contribution; (3) integrate minutes + draft roadmap; (4) reviewer + security checks; (5) return to the Owner.
Estimate: one planning session; within budget.
Risks: docs drifting from reality (mitigated by VERIFIED/INFERRED/UNKNOWN labelling + a reviewer); stale docs implying false status.
Decision: ACCEPT.

**COMMITTEE DELIVERABLE — T-050 (2026-09-26)**
- Deliverable: `docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md` (DRAFT — NOT APPROVED; 240+ บรรทัด; ครบ: minutes, disagreement, work packages, relative durations + assumptions, dependencies/critical path, gates G1–G6, validation evidence, cost/resource, Owner decisions, ASCII graph, conditional archived blueprint).
- Contributions received: researcher ✅ (3 overclaims corrected by the PL) · builder ✅ (effort INFERRED) · ops ⚠️ **partial 4/6** (sections "ops before launch" + "critical path" truncated — PL estimated from §7) · security ⚠️ **substitute** `opencode/nemotron-3-ultra-free` (pinned `opencode-go/kimi-k3` could not launch from the live session — retired `openrouter/nex-agi/nex-n2.5-mini:free` resolved instead; root cause **UNVERIFIED**) · model-recruiter ✅. **Committee not 100% complete — stated on the card and in the draft §3.**
- Nothing implemented: no code/runtime/DB/deploy change; only the T-049 archive move + this card + the draft doc + the append-only ADVISOR_LOG record. Preserved all unrelated working-tree changes.

**REVIEW T-050 — `opencode-go/space-bunny-free` (different model from the author `openrouter/deepseek/deepseek-v4.1-flash`) — 2026-09-26 — ACCEPTED (with 3 findings)**
- run: `ses_f2196ff00ffeyvGZ5XNBGNljTV` (complete). An earlier attempt `ses_f219ac052ffeKGJrAxyvzpshtc` was truncated mid-output and is **not** counted.
- Evidence nature: these are **Task-tool subagent outputs in the PL session**, recorded here on the card — there is **no persisted `runs/` directory** for them (the headless runner was not used), which a later auditor cannot independently re-open. Recorded as a verifiability limitation.
- A COVERAGE PASS-with-findings · B STATUS ACCURACY PASS-with-findings · C TIMELINE PASS-with-findings · D NOTHING STARTED PASS · E HONESTY PASS.
- Spot-check 6 claims against source: RLS FORCE/policies/roles, T-030 tenant isolation (A=1/B=0/42501), alert silent-skip `monitor_log.py:117-119`, no release pipeline, backup only local, price 299 / quota 600 — all confirmed, no status overclaim.
- Findings (all fixed on the draft by the PL): (1) the security stand-in was mislabelled "roster backup" — corrected to "study-time stand-in, not the current backup" (roster backup = `openrouter/qwen/qwen3.8-flash`); (2) the stated cause of the security launch failure was unverified — reworded to UNVERIFIED; (3) the critical path ordering contradicted the "prerequisites" column — corrected (P1.3 depends on P1.1+P0.1, parallel to P1.4).
- Advisor-mandate A1–A5 = **WITHIN-MANDATE-WITH-FINDINGS** (A1–A5 PASS; sole concern: the PL session itself bills OpenRouter, though the mandate said no new paid spend — no new paid call was made).
- Could not verify: live OpenRouter credit; whether the War Room agenda actually deployed.

**SECURITY / PRIVACY REVIEW T-050 — `opencode/nemotron-3-ultra-free` (SUBSTITUTE; ≠ author ≠ reviewer; pinned security model `opencode-go/kimi-k3` could not launch) — 2026-09-26 — PASS-WITH-FINDINGS**
- run: `ses_f219ab785ffekOkNXCsdlmruVY` (review) · `ses_f219ff1eeffe5sbKYjv58XDaAp` (security contribution) — same in-session evidence caveat as above.
- Gates G1–G6 correct and necessary; forbidden items (PDPA Layer 3, customer-facing rules) correctly stated; no gate wrongly marked done; security claims in §4/§5.4/§6 spot-verified (auth fail-closed, FORCE RLS, superuser/SECURITY DEFINER residual, agenda-write rate limit, backup untested, stale team config).
- **3 missing gates identified:** (a) a pre-live `CUSTOMER_FACING_RULES` auditor test of rules 1/2/5; (b) the PDPA Layer-2 retention period confirmed with a compliance advisor; (c) a real end-customer deletion path implemented and tested. Plus 10 residual risks to close before real onboarding.
- Limitation recorded: the appointed security model could not run, so this review used a substitute — **not** the appointed reviewer; treat as a provisional security pass.

> **T-051 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: War Room trial findings closed — finding 2 (participants-only seed) verified; finding 1 (Windows-start doc + `dev_server.py`) verified by a different-model reviewer (ACCEPTED; a live Windows run to a DB-backed state stays UNKNOWN).

> **T-064 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: the **Google** provider works end to end (live call proven); **Groq** was wired correctly and its key is valid, but the free tier caps it, so the Owner parked it ("ปิด"). **Open follow-up (Owner):** a cost exception for Google (no usable Gemini model fits `MODEL_POLICY`'s $0.25/$1.00 cap), then HR staffing. No commit was made for this card.

> **T-067 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: Google free-tier adopted as backup/task-scoped only (2 models; limits UNKNOWN); no pin change.

> **T-068 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. Reviewer `opencode/muse-spark-1.3-contributor-free` = ACCEPT. Two live runs verified (typo→L1/0/0, prod DB→L3/1/1). Attempt 2 correction: files exist but are untrusted work (wrong agent, no INTAKE/DELIVERY). Wording corrected in 3 files.

---

> **T-070 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: PL seat re-pinned to `opencode/nemotron-3-ultra-free` at all 3 pin locations + the scorecard row recorded; reviewer verified the diff.

### T-077 — Lite schema change: `lite_processed_events` + `bots.business_info` fallback contact (protected doc — L3)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (Owner order: ND-1 resolved 2026-09-27, **option (ข)** — a dedicated L3 card; `docs/warroom/decision-log.md` 2026-09-27)
Role: Project Lead (plan/verify) + builder (migration + schema-doc edits) + reviewer L1–L3 on a **different model** + security (tenant isolation / RLS on the new table)
Risk: **L3** — `docs/data/LITE_SCHEMA_V1.md` is a **protected document** (`TASK_CONTROL.md` §8); adding a table also means a real migration + RLS policy + grants
Goal: the de-duplication store for inbound platform events exists as `lite_processed_events`, is tenant/bot-scoped with FORCE RLS, and is documented in `LITE_SCHEMA_V1.md`; `bots.business_info` is required to carry a fallback contact for the over-quota message (ND-2)
Done when:
- [ ] `LITE_SCHEMA_V1.md` documents `processed_events` / `lite_processed_events` (purpose, columns, scope rule, TTL) and the `business_info` fallback-contact requirement — **spec edit written 2026-09-27; checkbox flips only when the different-model reviewer confirms it**
- [ ] migration creates `lite_processed_events` with `tenant_id` + `bot_id` + `channel_id`, unique key (`tenant_id`, `bot_id`, `platform_event_id`), `ENABLE` + `FORCE ROW LEVEL SECURITY`, policy `tenant_id = app_private.current_tenant_id() AND bot_id = app_private.current_bot_id()`, `nippan_runtime` grants (pattern: `migrations/20260925120000_lite_rls_v1.sql`)
- [ ] tests: cross-tenant read/write rejected (fail-closed); duplicate insert is a no-op (not an error, not a second answer)
- [ ] reviewer (different model) + security verdicts recorded
- [ ] `decision-log.md` entry recorded (L3 requirement)
- [ ] no production apply; no real customer data; migration committed under `migrations/`
Budget: 2h builder + 1h reviewer + 1h security (OpenCode Go pool / free; builder ≤ $2)
Links: ND-1 + ND-2 (`docs/architecture/MESSAGE_FLOW_V1.md` §1.3, §4.2; `docs/warroom/decision-log.md` 2026-09-27), `docs/data/LITE_SCHEMA_V1.md`, `migrations/20260925120000_lite_rls_v1.sql`, T-002 (created the other `lite_*` tables), T-026/T-RLS-01 (RLS), T-076 (foundation schema — a separate card)

INTAKE T-077 — pending

---

### T-004 — Legal review: tenant agreement + end-customer privacy notice (PARKED — hard gate for Step 2)

Status: **PARKED** — cut from the dev-time plan by the Owner on 2026-09-25 ("อันนี้ต้องตัดออก เพราะตอนนี้อยู่ในช่วงทำระบบ งานนี้ไม่เกี่ยวข้องเลย"); **reopened as a tracked card 2026-09-27** so it lives on the board, not only in git history
Owner: Project Owner — must engage a lawyer / PDPA compliance advisor (this is **not** an AI seat)
Role: legal — an external human professional
Risk: L3 (the tenant agreement and the privacy notice are what customers actually agree to)
Goal: the tenant agreement and the end-customer privacy notice have been reviewed by a lawyer before the platform serves any real customer
Done when:
- [ ] Tenant agreement reviewed by a lawyer — the data-controller (tenant) / data-processor (platform) split is stated per `PDPA_COMPLIANCE.md` Layer 1, and the bot-is-an-assistant / owner-is-responsible wording per `BUSINESS_OPERATIONS.md` §2
- [ ] End-customer privacy notice wording reviewed (the short notice the bot shows on first contact, `PDPA_COMPLIANCE.md` Layer 1)
- [ ] The reviewed texts (or a reference to them) are recorded with the reviewer's identity and date
- [ ] No AI closes this card on its own — it closes only on a real legal review
Budget: one-off legal fee (the Owner sets the amount). No AI/model spend.
Links: `docs/security/PDPA_COMPLIANCE.md`, `docs/product/BUSINESS_OPERATIONS.md` §2–§3, `docs/product/ONBOARDING_FLOW.md`, `docs/warroom/STARTUP_PLAYBOOK.md` (hard gate in Step 2), `docs/warroom/decision-log.md` 2026-09-25 ("Legal work (T-004) cut from the dev-time plan")
Note: opening the first-customer onboarding card (Step 2) is blocked until this card is DONE — see the hard gate in `STARTUP_PLAYBOOK.md`.

INTAKE T-004 — pending (PARKED; no AI work is started)

---

> **T-079 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: split into the six build cards **T-079a–T-079f** (different-model reviewer ACCEPTED the split); build order a→b→c→d, then e & f.

> **T-080 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: Phase A uses the log + LINE alert already designed in `MONITORING.md`; **no admin web page in Phase A** — a real dashboard stays a Phase B/C trigger (25+ tenants / digest >15 min / a second person).

---

### T-079a — `web-chat` channel adapter (front-of-house foundation)

Status: **DONE — 2026-09-28** (commits `24c85ba` + `6d5f220`; reviewer ACCEPTED-WITH-FINDINGS, both findings fixed and re-verified)
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder (adapter + tests) + reviewer L1–L3 on a **different model**
Risk: L2 (new customer-facing channel; pre-G1, no customer data yet)
Goal: a visitor's message sent from a web page reaches the core and a reply comes back — the channel that the storefront demo, the onboarding assistant and the Support agent all run on. No LINE dependency anywhere in it.
Design source: `docs/product/INTEGRATIONS.md` (channel-adapter contract + normalized inbound/outbound), `docs/product/adapters/line-oa.md` (the pattern to follow), `docs/product/MCP_TOOLS_V1.md` (`web-chat-channel`, Step 3), `docs/architecture/MESSAGE_FLOW_V1.md` §1/§7/§14
Done when (each provable by running):
- [x] adapter does the 4 adapter duties per `INTEGRATIONS.md` (authenticity, identity mapping, normalize, de-dup) and reports usage/errors to `usage-tracker` / `monitor-log`
- [x] inbound/outbound use the normalized format exactly (`tenant_id, bot_id, channel_id, end_customer_ref, message_id, content[], reply_handle`) — no platform field name leaks into the core
- [x] runnable proof: a local end-to-end run — post a message as a web visitor → the core answers → the reply returns; transcript saved
- [x] scope enforced: a request that cannot be mapped to `tenant_id` + `bot_id` is rejected (never guessed)
- [x] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer (Go pool / free; builder ≤ $2)
Links: `docs/product/INTEGRATIONS.md`, `docs/product/MCP_TOOLS_V1.md`, `docs/architecture/MESSAGE_FLOW_V1.md` §14, `docs/product/adapters/line-oa.md`
Depends on: nothing (foundation). Note: T-075 (n8n workflow stubs) is PARKED — this card does not wait for it.

---

### T-079b — Onboarding assistant: conversation / URL / file → fixed-menu config

Status: **DONE — 2026-09-28** (commit `72a3d1a`; reviewer pass 1 ACCEPTED-WITH-FINDINGS with one HIGH finding, fixed; pass 2 **ACCEPTED**)
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (processes a prospect's uploaded business data; no real customers yet)
Goal: the assistant reads what the prospect gives it (plain conversation / a website link / an uploaded menu-price file) and produces **fixed-menu config values** — never a raw prompt built from the customer's words.
Design source: `docs/product/ONBOARDING_FLOW.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots.business_info`, `tone`, `enabled_tools`, quotas), `docs/product/MCP_TOOLS_V1.md` (`web-fetch`, `file-reader`, `chat-bot-core`)
Done when (each provable by running):
- [x] run against a sample shop (one website URL + one sample menu/price file) and show the produced config rows
- [x] asks only for what is still missing; tone comes from the fixed list; output is fixed-menu values only (no raw customer text stored as instructions)
- [x] ingestion cost bounds applied (`ONBOARDING_FLOW.md` "Cost controls"): page/file size cap, own-site pages only, no full crawl
- [x] honesty rule 2 holds with the prospect (never names the model)
- [x] reviewer (different model) verdict recorded

RESULT — 2026-09-28: `services/core/app/onboarding/` (menus/signals/cost_bounds/ingest/config/assistant), 23 tests pass, e2e `run_onboarding_e2e.py` exits 0 with 8/8 checks true and no nulls. The HIGH pass-1 finding (file ingestion was asserted-only, categories hardcoded) was fixed by wiring the real `signals.extract_categories_from_price_file` entry point; pass-2 reviewer proved it empirically by editing a fixture line (`MUTCAT`) and observing the output change. Residual LOW: one nearly-tautological conjunct in `tone_from_fixed_list`.
Budget: 6h builder + 1h reviewer (builder ≤ $3)
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, T-079a
Depends on: T-079a (transport for the conversation).

---

### T-079c — Customer setup page (chat with the Onboarding assistant over web-chat)

Status: **DONE — 2026-09-28** (commit `f176410`; reviewer ACCEPTED-WITH-FINDINGS; security ACCEPTED-WITH-FINDINGS after 2 HIGH findings closed, final MED test-hygiene fixed) — **one item still open: the PDPA notice wording is NEEDS_OWNER_DECISION**
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model** + security (customer-facing surface)
Risk: L2 (customer-facing UI; no payments, no tenant data yet)
Goal: a real page where a prospect onboards by chatting — accepts the three input kinds (conversation / website link / uploaded file) and shows progress.
Design source: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md` item 5 ("Set up my bot"), `docs/product/CUSTOMER_FACING_RULES.md`
Done when (provable by running):
- [x] open the page locally and complete an onboarding conversation end to end; transcript + saved run artifacts
- [x] all three input kinds work on the page (typed answer, URL, file upload)
- [x] the page never shows a model/vendor name and shows the short PDPA notice where it collects anything
- [x] reviewer (different model) + security verdict recorded

RESULT — 2026-09-28: built in 3 parts after the first attempt died on `reason:"length"`. 294 tests pass, 9 skipped; e2e `run_onboarding_page_e2e.py` = 27 checks, all true, exit 0, driving the real app in-process. Security found 2 HIGH + 3 MEDIUM, all now closed: (1) tenant scope was a client header with no identity — now server-wired at mount, fail-closed with no scope, a gated dev escape that reports `UNVERIFIED`; (2) SSRF — 19/19 bypass attempts now rejected before any fetch (decimal/hex/octal/short IP forms, `metadata.google.internal`, private/loopback/link-local), fail-closed when resolution fails or returns empty/mixed, address pinning, redirect guard wired, and the own-site check no longer compares the submitted URL against itself; (3) `/website` with no fetcher is a clean 503, not a 500; (4) filenames sanitised; (5) body capped cumulatively (a chunked 1,000,001-byte body is cut at 999,424 and answered 413), store bounded with TTL.

**OPEN — NEEDS_OWNER_DECISION:** the short PDPA notice shown on the page is **newly drafted wording**, because `docs/security/PDPA_COMPLIANCE.md` defines the requirement but no exact sentence to copy. Customer-facing legal text is not the Project Lead's to invent. Options: (ก) the Owner supplies the exact wording; (ข) the Owner approves the current draft after reading it; (ค) a legal pass is added before any real customer uses the page. Until then the page is dev-time only.
Budget: 6h builder + 1h reviewer + 1h security
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md`, T-079a, T-079b
Depends on: T-079a, T-079b.

---

### T-079d — Confirmation summary + go-live gate

Status: **DONE — 2026-09-28** (commit `cacebbb`; reviewer ACCEPTED-WITH-FINDINGS, 4 findings fixed and re-verified)
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (the gate that decides when a bot becomes active — fail-closed matters)
Goal: before the bot goes live, show the extracted **fixed-menu** config + a short sample conversation ("your bot will say things like…"); the customer confirms or asks for changes; **only on confirmation does the bot become active**.
Design source: `docs/product/ONBOARDING_FLOW.md` steps 4–5, `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots.status`)
Done when (provable by running):
- [x] run through onboarding → the summary renders the extracted config + a sample conversation
- [x] if the customer edits or declines, the config changes and the bot **does not** go live (fail-closed)
- [x] on confirm, `bots.status` flips to active and the config rows are persisted — shown in the run
- [x] reviewer (different model) verdict recorded

RESULT — 2026-09-28: `app/onboarding/gate.py` + `gate_repo.py` + `summary.py`. The reviewer enumerated every path to `active` and found exactly one: an explicit `confirm()` on a draft with no missing fields. `edit()` and `decline()` both write `paused` immediately, and a row that does not exist reads as `paused` — so an edit after confirming never leaves a bot ACTIVE on a draft the customer never re-confirmed. Status values (`active`/`paused`) and the persisted column names were checked against `LITE_SCHEMA_V1.md` and match the real schema; nothing was invented. 306 tests pass, 9 skipped; all three e2e scripts exit 0 (`run_onboarding_gate_e2e.py` 14 checks, `run_onboarding_page_e2e.py` 27, `run_onboarding_e2e.py` 8). Reviewer's 4 findings fixed: a proof check that was a truthy string is now a real boolean comparison, a dead helper that could write `status` bypassing the gate was removed, an unused `build_draft(fill)` parameter was resolved, and `summary.py` gained dedicated unit tests.

KNOWN GAP (carried forward, not a blocker for this card): the gate is not yet wired to the page session — the real caller must bind an already-verified tenant scope, which happens with T-079e/T-079f.
Budget: 4h builder + 1h reviewer
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/data/LITE_SCHEMA_V1.md`, T-079c
Depends on: T-079c.

---

### T-079e — Later-edit path via Support agent (Owner decided (ก))

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079; Owner decision 2026-09-27: option (ก))
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (a live tenant's own config changes; fixed menus only)
Goal: an existing customer asks in chat to change their business info; the Support agent (`ROLES.md`) applies the change **within fixed menus only**, and flags anything that could raise cost to Cost Guard first.
Design source: `docs/warroom/ROLES.md` (Support agent), `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots`)
Done when (provable by running):
- [ ] a chat change request updates the config row and the change is logged — shown in the run
- [ ] only fixed-menu fields can change; an attempt to set free-form instructions is refused
- [ ] a change that could raise cost (e.g. quota) is flagged to Cost Guard, not applied silently
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer
Links: `docs/warroom/ROLES.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, T-079b
Depends on: T-079b.

---

### T-079f — Storefront page (public, one page: headline, live demo, price, one button)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079; `STOREFRONT.md`, playbook Step 3)
Role: Project Lead (plan) + builder + reviewer on a **different model**
Risk: L1–L2 (public marketing page + live demo bot; the demo must have its own daily cap)
Goal: a prospect understands the offer in under a minute and tries a real bot before paying.
Design source: `docs/product/STOREFRONT.md`
Done when (provable by running):
- [ ] the one page runs locally with all 6 sections of `STOREFRONT.md` (headline, live demo, what it does, price 299, one button, small print)
- [ ] the live demo bot answers over `web-chat` on the cheapest tier with a working daily cap — shown by a run that hits the cap and stops
- [ ] no model name anywhere on the page; the demo shows the same consent notice as tenant bots
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer
Links: `docs/product/STOREFRONT.md`, T-079a
Depends on: T-079a.

---

> **T-081 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: added the **Document–Card Gap Check** to `ADVISOR_MANDATE.md` §8 and `TASK_CONTROL.md` §9 item 7 — a product/architecture doc change with no backing card becomes a `NEEDS_DECISION` to the Owner, and the advisor must not create cards to close the gap; merged via PR #97.

> **T-082 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: headless zero-output root cause = model behaviour against opencode's default reasoning budget (`reason:"length"`, `output:0`, `reasoning:4096`) — not the brief, not the runner; short-term fix applied (`opencode-go/mimo-v2.6-flash`), long-term fix = card T-083.

### T-083 — Bound/disable model reasoning for headless jobs (`opencode.json`) — L2

Status: **DONE — 2026-09-28** (commit `6d5f220`; proven on a real T-079a-sized job ending `reason:"stop"` with `reasoning:0`; reviewer ACCEPTED-WITH-FINDINGS, 0 findings against the config)
Owner: Project Lead — 2026-09-27 (Owner order; long-term fix from T-082)
Role: Project Lead (plan) + builder (edit `opencode.json` and/or add a runner flag) + reviewer L1–L3 on a **different model**
Risk: L2 (dev-time agent/model config change)
Goal: headless builder jobs can run **a real, T-079a-sized task** on a roster model without the `reason:"length"` / zero-output failure — reasoning is bounded per model instead of relying on a temporary model swap.
Mechanism (VERIFIED from the opencode docs, 2026-09-27 — do not guess):
`opencode.json` → `provider.<providerId>.models.<modelId>.options` accepts `reasoningEffort` (e.g. `"low"` / `"minimal"` / `"none"`), and the same file supports **variants** (`models.<id>.variants.<name>` with the same option keys). Provider ids here are `opencode-go` / `opencode` / `openrouter`. Agent-level config overrides the global model options.
Design source: T-082 finding; opencode docs `/docs/models` ("Configure models", "Variants"); `opencode.json`; `scripts/headless_run.mjs`
Done when:
- [x] a reasoning cap (or off-switch) is applied for the failing models via `provider.<id>.models.<model>.options` (or a variant passed by the runner)
- [x] **proof must use a test job whose length and complexity are close to the real T-079a** — not a trivial one-liner — and it must end with `reason:"stop"` and real output (**`reason:"length"` = fail, even if some text was produced**)
- [x] if the cap still fails on a T-079a-sized job, apply the fallback **immediately without asking**: (a) split T-079a into smaller sub-jobs that are short enough, and/or (b) cut unnecessary reference files/context out of the brief
- [x] the temporary rule (headless default = `opencode-go/mimo-v2.6-flash`) is reverted or kept deliberately, and that choice is recorded in the decision-log
- [x] reviewer (different model) verdict recorded

RESULT — VERIFIED 2026-09-28:
- `opencode.json` got `provider.opencode-go.models.{glm-5.3-flash,kimi-k3,deepseek-v4.1-flash}.options.reasoningEffort = "low"` (21 lines, valid JSON, no other key touched).
- Proof job `runs/2026-09-27T16-27-03Z-t079a-cap-proof-glm` ran the **real T-079a brief** on `opencode-go/glm-5.3-flash` and ended `reason:"stop"` (was `reason:"length"`, `output:0`, `reasoning:4096`) with `reasoning:0`, `output:856`, 10 real files, 15 tests passing, e2e PASS. Fallback (split/shorten) therefore **not needed**.
- Reviewer `opencode/muse-spark-1.3-contributor-free` re-ran the tests and e2e independently: 15 passed / PASS; confirmed the `opencode.json` diff touches no other key.
- Temporary rule: **reverted** — headless builder default is back to the roster Primary `opencode-go/glm-5.3-flash`, which now works.
Budget: 2h builder + 1h reviewer + the cost of the verification jobs (Go pool / free)
Links: T-082, `scripts/headless_run.mjs`, `opencode.json`, `docs/warroom/decision-log.md` 2026-09-27, T-079a (the real task this must unblock)

INTAKE T-083 — closed 2026-09-28 (see RESULT above)

---

## REVIEW

(none)

## DONE

(completed cards moved to docs/archive/TASKS_DONE_ARCHIVE.md — T-RLS-01 added 2026-09-25)

- **T-030 — DONE 2026-09-26 (Owner approved).** n8n → Supabase as `nippan_n8n`: connection proven, RLS read isolation proven
  (tenant A = 1 / tenant B = 0), write isolation proven (cross-tenant INSERT rejected, RLS WITH CHECK 42501), positive control for
  tenant B, tables left empty (rollback). Workflows `CVhNSU5pjpGgzquB` + `eohtRWY8YEvEuS7n` in folder `Nippan Phase A`.
  Evidence + the exact SQL: `docs/n8n/T-030-execution-evidence.md`. Reviewer `opencode/space-bunny-free` (different model) pass 2.
  Owner scope condition (2026-09-26): n8n write/read is allowed **only inside the `Nippan Phase A` folder**. Carried residual:
  the credential still has `Ignore SSL Issues`; the card has never been run published/production.
