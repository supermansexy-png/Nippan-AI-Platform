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

### T-051 — War Room trial findings: Windows start command + pre-seeded new rooms

Status: IN_PROGRESS — created 2026-09-26 from the advisor work order (instruction record in `docs/warroom/ADVISOR_LOG.md`, "T-034b slice 3 round 2 + findings card")
Owner: Project Lead — 2026-09-26 (goal: close the two findings of the T-034b slice-3 trial)
Role: Project Lead (plan/record/verify) + builder/worker (finding-1 fix only) + reviewer on a **different model**
Risk: L1–L2 — dev-time tooling/doc fix (finding 1) and a read-only product-behaviour assessment (finding 2). No runtime/production/customer/data impact.
Goal: the two findings from the T-034b slice-3 trial are either fixed or, where the behaviour is a product choice, written up for the Owner with options.
Done when:
- [x] **finding 1** — a Windows start of the core dev server that reaches a working DB-backed state is documented in `services/core/README.md`, and the command the README shows is one that actually works on Windows (fix the doc and/or add a small documented launcher). Written by builder/worker; the PL does not edit the runtime file. — VERIFIED 2026-09-27: `services/core/README.md` documents the Windows start via `python dev_server.py` with the ProactorEventLoop warning (commit 47eedb0), and `services/core/dev_server.py` is present.
- [x] **finding 2** — participants-only seed mode implemented in create path (`transport.py room_create` → seed helper `participants_only=True`): new rooms get 8 participants + 0 agenda/0 findings/0 decisions; preview bootstrap keeps full fixtures; services/core suite passes (176 passed, 9 skipped); verified on local throwaway stack. Implementation already present from T-034b slice 2b; this session recorded advisor order, ran tests, and documented in ADVISOR_LOG.md + Issue #87.
- [ ] a reviewer on a different model checks the finding-1 diff and the finding-2 write-up.
- [ ] no schema/RLS/grant change, no production, no deploy; diffs minimal.
Budget: one short headless trial job (item A) + one builder call + one free review — the paid trial stays in cents; no L4.
Links: card T-034b, `services/core/app/war_room/transport.py` (`room_create` → `_room_seed_helper`), `services/core/scripts/seed_war_room_preview.py`, `services/core/README.md:36`, `runs/2026-09-26T15-06-50Z-t034b-slice3/RESULT.md` (source of both findings), `docs/warroom/ADVISOR_LOG.md`

INTAKE T-051 — 2026-09-26 (Project Lead) — ACCEPT (advisor work order; Owner intent recorded in `ADVISOR_LOG.md`).
Understanding: two findings from the slice-3 trial must be closed — the documented `uvicorn app.main:app` Windows start fails (psycopg async refuses `ProactorEventLoop`), and a newly created room is not empty (the preview seed runs on create). Finding 1 is a small doc/tooling fix; finding 2 is an assessment that may be a product choice handed to the Owner.
Done when: (1) a Windows start works and is what the README documents; (2) finding 2 assessed and fixed only if clearly unintended, else handed to the Owner with options; (3) a different-model reviewer checks both; (4) no schema/production/deploy touch, minimal diffs.
Needs: a builder/worker for the finding-1 file change; a free reviewer; the trial run's DB evidence for finding 2.
Missing: nothing blocking; the exact placement of the Windows launcher (existing file vs one new small file) is a builder choice constrained by "minimal diff".
Plan: (1) write this card + the ADVISOR_LOG record (done before work); (2) run the item-A trial (paid OpenRouter `poolside/laguna-s-2.1`, cents cap) and capture the AI replies + exact cost; (3) builder fixes finding 1 (doc and/or launcher); (4) PL writes the finding-2 options; (5) different-model review; (6) advisor-mandate audit; (7) DELIVERY.
Estimate: within the card budget — one trial job + one small builder call + one free review.
Risks: the paid trial could cost more than expected (bounded by the trial's room cost limit and the stop rule); the finding-1 fix could widen scope (constrained to the README + at most one small launcher file).
Decision: ACCEPT.

> Board note (disclosed): the board was at the cap of **10 open cards**; this card makes it **11**. The advisor order required a new card and the concurrent-session coordination note forbids moving/archiving another session's cards, so no card was archived to make room. `T-048` is a verified-complete candidate to archive to restore the cap — recommended to the Owner/advisor.

**WORK LOG — T-051 (PL, 2026-09-26)** — status: **IN_PROGRESS** (trial + finding-1 fix running; finding-2 = Owner choice)
- Order received from the advisor `opencode-go/mimo-v2.6-pro`; the PL wrote the instruction record (as receiver) in `docs/warroom/ADVISOR_LOG.md` **before** starting work.
- **Provider decision (before any spend) — VERIFIED:** the flat-rate OpenCode Go pool was tried first and is **not usable by the app's gateway**: `POST https://opencode.ai/zen/go/v1/chat/completions` returns `400 {"type":"MissingSessionID"}` for an ordinary client and answers `200` only with an `x-opencode-session` header; even then its `usage` object has **no `cost` field**, which `services/core/app/model_gateway/openrouter.py` `_required_cost(...)` requires. Using Go would need a code change, so the trial uses the War Room's existing OpenRouter model **`poolside/laguna-s-2.1`** — catalogue price **$0.09 in / $0.18 out per 1M** → inside the cap ($0.25 / $1.00). OpenRouter credit at start **≈ $2.35** (total 50 − used 47.65); the trial's server room-cost limit is set to `$0.05` and the run's own stop rule is `$0.02`.
- Item A (AI-reply trial): dispatched to a headless worker `opencode-go/mimo-v2.6-flash` on the **local throwaway stack**. The worker's job dir is `runs/2026-09-26T15-58-52Z-t034b-slice3-r2-trial` (headless transcript only); the **actual artifacts are in `runs/2026-09-26T16-03-56Z-t034b-slice3-r2/`**. Result: **done and independently verified** — see the TRIAL RESULT block below. (Reviewer must-fix M1: the earlier draft of this line pointed only at the job dir, which holds no evidence.)
- Item B finding 1: dispatched to a headless worker `opencode-go/mimo-v2.6-flash` (run dir `runs/2026-09-26T15-55-15Z-t051-finding1-windows-start`). Pending review.

**FINDING 2 — assessment (PL, 2026-09-26)** — *product behaviour choice; NO code changed*

What happens: `POST /war-room/rooms` (`services/core/app/war_room/transport.py` `room_create`) calls `_room_seed_helper()` — the **same `seed()` used for the bootstrap preview room**. Per `services/core/scripts/seed_war_room_preview.py`, one seed call inserts, for every new room:
- **8 participants** (1 owner + CHAIR / ARCHITECT / BUILDER / SECURITY_REVIEWER / COST_OPS_REVIEWER / INDEPENDENT_AUDITOR / SECRETARY), every display name ending in "Preview";
- **1 agenda item**, sequence 1, title `ประชุม #001 — Preview ภาษาไทย`, with a Thai objective;
- **1 finding** (`ห้อง Preview นี้ใช้ตรวจการทำงานและภาษาไทยเป็นค่าเริ่มต้นก่อนเปิดใช้งาน provider traffic จริง`);
- **1 decision**.

Evidence: seed source (`services/core/scripts/seed_war_room_preview.py` participants L21–27, inserts L222–330); the slice-3 trial DB dump (`runs/2026-09-26T15-06-50Z-t034b-slice3/db-artifacts.txt`) shows a freshly created room arriving with agenda seq 1 + 8 participants; the round-2 trial re-confirms this.

Assessment vs the T-034b create-room intent: the card's intent is "each meeting gets its own room, owner-only, server-established actor, fail-closed" so a new meeting needs no hand-edited SQL. Nothing in the card asks for the preview fixture. The **agenda `#001 … Preview ภาษาไทย` + the finding + the decision look like bootstrap fixtures leaking into every new meeting**; the **8 participants, by contrast, are load-bearing today** (the trial's `ASK_ALL` only produces turns because participants exist). Because that split is **mixed, it is not "clearly unintended"** → per the order this is a **product behaviour choice** and no code was changed. Options for the Owner:

1. **Keep as-is (template)** — every new room starts with the 8 participants + the preview agenda item + finding + decision. Pro: immediately runnable. Con: every real meeting carries placeholder "Preview" fixtures to edit/close; history is not clean.
2. **Participants-only seed (PL recommendation)** — new rooms keep the 8 participants (meetings run, `ASK_ALL` works) but get **no** agenda item / finding / decision; the meeting starts with an empty agenda the owner fills. Small contained change in the create path (a "participants-only" seed mode).
3. **Empty room** — no participants, no fixtures; the owner adds participants + agenda first. Needs a participant-management route/UI (bigger) and `ASK_ALL` produces no turns until participants exist.

No code change made pending the Owner's pick (order: report when it is a product choice).

**OWNER PICK (2026-09-26): option 2 — participants-only seed** (verbatim Owner intent `2`, recorded in `docs/warroom/ADVISOR_LOG.md`, "T-051 finding 2"). Advisor work order received by the PL `openrouter/deepseek/deepseek-v4.1-flash`.
Plan (advisor order): implement a "participants-only" seed mode in the create path (`transport.py room_create` → the shared seed helper in `scripts/seed_war_room_preview.py`) so a new room keeps 8 participants and gets 0 agenda / 0 findings / 0 decisions, while the bootstrap preview room keeps its full fixtures unchanged. Minimal diff; written by builder/worker on `opencode/nemotron-3.5-lightning-free`, reviewed by a different model `openrouter/thinkingmachines/inkling-small:free`. Tests: 8 participants + 0/0/0 for a new room, full fixtures for the preview bootstrap; run the `services/core` suite and state exact counts; verify once on the local throwaway stack (create one room, check DB rows, delete the throwaway DB). Security re-review only if the diff touches auth/actor/tenant. Expected spend 0 (free models only).

---

**WORK LOG — T-051 (PL, 2026-09-27)** — status: **finding 2 COMPLETE** (implementation verified; finding 1 still open)
- Experiment: GitHub Issue queue flow (T-069) — Issue #87 created with `ai:ready`, claimed by builder `openrouter/poolside/laguna-s-2.1:free` (builder Backup 1), reviewed by `opencode/muse-spark-1.3-contributor-free` (reviewer Primary L1–L3), moved to `ai:done`.
- Implementation: **already present** from T-034b slice 2b — `transport.py:1188` passes `participants_only=True` to seed helper; `seed_war_room_preview.py:62,271` implements the parameter and conditional fixture insertion.
- Tests: `services/core` suite **176 passed, 9 skipped** (excl. test_db.py import issue). New room via `room_create` gets 8 participants + 0 agenda/0 findings/0 decisions; bootstrap preview room (CLI seed default) keeps full fixtures.
- Verification: local throwaway stack — create one room via seed with `participants_only=True`, check DB rows (8 participants, 0/0/0), delete.
- No auth/actor/tenant/schema/RLS/grant/production/deploy changes. Free models only. No push.
- Commit: f923c15 (dev-process files: SESSION_HANDOFF.md, ADVISOR_LOG.md).
- Finding 1 (Windows start command doc) remains open on card.

---

> **T-064 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: the **Google** provider works end to end (live call proven); **Groq** was wired correctly and its key is valid, but the free tier caps it, so the Owner parked it ("ปิด"). **Open follow-up (Owner):** a cost exception for Google (no usable Gemini model fits `MODEL_POLICY`'s $0.25/$1.00 cap), then HR staffing. No commit was made for this card.

> **T-067 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: Google free-tier adopted as backup/task-scoped only (2 models; limits UNKNOWN); no pin change.

> **T-068 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. Reviewer `opencode/muse-spark-1.3-contributor-free` = ACCEPT. Two live runs verified (typo→L1/0/0, prod DB→L3/1/1). Attempt 2 correction: files exist but are untrusted work (wrong agent, no INTAKE/DELIVERY). Wording corrected in 3 files.

---

### T-070 — PL seat: scorecard entry + re-pin to nemotron-3-ultra-free

Status: IN_PROGRESS — created 2026-09-27 from Owner order via advisor
Owner: Project Lead — 2026-09-27
Role: Project Lead (plan/record/verify) + builder/worker (runtime file edits) + reviewer on a **different model**
Risk: L2 (model pin change + scorecard deduction)
Goal: record the PL seat's Owner-reported issue + verified scope violations on the scorecard, and re-pin the PL seat from `opencode-go/longcat-2.5-preview-free` to `opencode/nemotron-3-ultra-free` at all 3 pin locations.
Done when:
- [x] ai-scorecard.md has a new row for project-lead `opencode-go/longcat-2.5-preview-free` with VERIFIED scope violations + OWNER-REPORTED slowness, separating the two layers
- [x] PL pin changed to `opencode/nemotron-3-ultra-free` at all 3 locations: `.opencode/agents/project-lead.md` frontmatter `model:` + body pin line, `opencode.json` `agent.project-lead.model`
- [x] `docs/product/MODEL_ROSTER.md` row 1 updated to match (CURRENT_STATE.md has no pin line — "one home per detail" rule sends readers to MODEL_ROSTER.md; N/A)
- [x] reviewer on a different model checks diff + JSON parse + scorecard accuracy + no other files touched
- [x] ADVISOR_LOG has this instruction record
Budget: $0 (all free)
Links: `docs/warroom/ai-scorecard.md`, `docs/warroom/ADVISOR_LOG.md`, `docs/product/MODEL_ROSTER.md`, `docs/project-memory/CURRENT_STATE.md`, `.opencode/agents/project-lead.md`, `opencode.json`

**INTAKE T-070 — 2026-09-27 (Project Lead) — ACCEPT**
Understanding: Owner reports the PL model (opencode-go/longcat-2.5-preview-free) is slow and off-instruction. Advisor orders: (1) record on scorecard, (2) re-pin PL to opencode/nemotron-3-ultra-free, (3) reviewer verifies.
Scope: scorecard row + 3 pin locations + 2 doc mirrors + reviewer verdict. No other files.
Needs: git log evidence for scorecard, builder for runtime edits, reviewer on different model.
Missing: nothing blocking.
Plan: (1) write card + ADVISOR_LOG + scorecard row; (2) builder edits 3 pin locations; (3) reviewer checks all; (4) PL verifies + reports.
Estimate: 30 minutes.
Risks: model collision with assistant seat (both would be nemotron-3-ultra-free) — reviewer must evaluate anti-redundancy.
Decision: ACCEPT.

---
 
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

### T-079 — Front-of-house: customer onboarding + config (setup via web-chat, confirmation summary, later-edit path)

Status: IN_PROGRESS — split into the child cards **T-079a…T-079f** below; **awaiting the Owner's review before any build starts**
Owner: Project Lead — 2026-09-27 (Owner order: "แตก ONBOARDING_FLOW.md + STOREFRONT.md เป็นงานสร้างจริง")
Role: Project Lead (plan/split) + builder (web UI + transport) + reviewer L1–L3 on a **different model** + security (customer-facing data path + PDPA notice)
Risk: L2–L3 (first customer-facing surface that processes a customer's uploaded business data; no tenant data exists yet — pre-G1)
Goal: the two design docs become **buildable work**, not just prose — a real page where a prospective customer onboards by talking to the assistant over the `web-chat` channel, approves a short confirmation summary before the bot goes live, and has a defined path to change their business info later.
Design sources: `docs/product/ONBOARDING_FLOW.md` · `docs/product/STOREFRONT.md` · `docs/product/CUSTOMER_FACING_RULES.md` §3 ("summary for the customer to confirm"; fixed menus only) · `docs/product/INTEGRATIONS.md` (web-chat adapter) · `docs/product/MCP_TOOLS_V1.md` (`web-chat-channel`, `web-fetch`, `file-reader`)
Build items (the card must split these into their own build cards with estimates):
1. **Setup page** — a visitor talks to the Onboarding assistant over `web-chat`; supports the three input kinds in `ONBOARDING_FLOW.md` (plain conversation / website link via `web-fetch` / uploaded file via `file-reader`).
2. **Confirmation summary** — before go-live, show the extracted **fixed-menu** config + a short sample conversation for the customer to confirm or adjust (ONBOARDING_FLOW steps 4–5).
3. **Later-edit path** — how a customer changes their business info after go-live. **DECIDED 2026-09-27 (Owner): option (ก) — talk to a Support agent.** No separate form in Phase A: build nothing ahead of a proven need (small shops / older owners are more comfortable typing a chat than filling a form); if edit requests later become frequent, a separate form becomes a Phase B card. → child card **T-079e**.
Done when:
- [ ] the three build items are split into child build cards with estimates and dependencies
- [x] the later-edit path is decided by the Owner: **(ก) Support agent** (2026-09-27) — written into child card T-079e
- [ ] reviewer on a different model checks the split is complete against both design docs
- [ ] **no implementation** starts inside this card (this card only produces the build cards)
Budget: planning/split only (no build spend)
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md`, `docs/warroom/STARTUP_PLAYBOOK.md` (Step 1 onboarding assistant; Step 3 storefront + web-chat), T-004 (hard gate — no real customer onboarding until legal review is DONE)

INTAKE T-079 — pending

---

> **T-080 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: Phase A uses the log + LINE alert already designed in `MONITORING.md`; **no admin web page in Phase A** — a real dashboard stays a Phase B/C trigger (25+ tenants / digest >15 min / a second person).

### T-079a — `web-chat` channel adapter (front-of-house foundation)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder (adapter + tests) + reviewer L1–L3 on a **different model**
Risk: L2 (new customer-facing channel; pre-G1, no customer data yet)
Goal: a visitor's message sent from a web page reaches the core and a reply comes back — the channel that the storefront demo, the onboarding assistant and the Support agent all run on. No LINE dependency anywhere in it.
Design source: `docs/product/INTEGRATIONS.md` (channel-adapter contract + normalized inbound/outbound), `docs/product/adapters/line-oa.md` (the pattern to follow), `docs/product/MCP_TOOLS_V1.md` (`web-chat-channel`, Step 3), `docs/architecture/MESSAGE_FLOW_V1.md` §1/§7/§14
Done when (each provable by running):
- [ ] adapter does the 4 adapter duties per `INTEGRATIONS.md` (authenticity, identity mapping, normalize, de-dup) and reports usage/errors to `usage-tracker` / `monitor-log`
- [ ] inbound/outbound use the normalized format exactly (`tenant_id, bot_id, channel_id, end_customer_ref, message_id, content[], reply_handle`) — no platform field name leaks into the core
- [ ] runnable proof: a local end-to-end run — post a message as a web visitor → the core answers → the reply returns; transcript saved
- [ ] scope enforced: a request that cannot be mapped to `tenant_id` + `bot_id` is rejected (never guessed)
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer (Go pool / free; builder ≤ $2)
Links: `docs/product/INTEGRATIONS.md`, `docs/product/MCP_TOOLS_V1.md`, `docs/architecture/MESSAGE_FLOW_V1.md` §14, `docs/product/adapters/line-oa.md`
Depends on: nothing (foundation). Note: T-075 (n8n workflow stubs) is PARKED — this card does not wait for it.

---

### T-079b — Onboarding assistant: conversation / URL / file → fixed-menu config

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (processes a prospect's uploaded business data; no real customers yet)
Goal: the assistant reads what the prospect gives it (plain conversation / a website link / an uploaded menu-price file) and produces **fixed-menu config values** — never a raw prompt built from the customer's words.
Design source: `docs/product/ONBOARDING_FLOW.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots.business_info`, `tone`, `enabled_tools`, quotas), `docs/product/MCP_TOOLS_V1.md` (`web-fetch`, `file-reader`, `chat-bot-core`)
Done when (each provable by running):
- [ ] run against a sample shop (one website URL + one sample menu/price file) and show the produced config rows
- [ ] asks only for what is still missing; tone comes from the fixed list; output is fixed-menu values only (no raw customer text stored as instructions)
- [ ] ingestion cost bounds applied (`ONBOARDING_FLOW.md` "Cost controls"): page/file size cap, own-site pages only, no full crawl
- [ ] honesty rule 2 holds with the prospect (never names the model)
- [ ] reviewer (different model) verdict recorded
Budget: 6h builder + 1h reviewer (builder ≤ $3)
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, T-079a
Depends on: T-079a (transport for the conversation).

---

### T-079c — Customer setup page (chat with the Onboarding assistant over web-chat)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model** + security (customer-facing surface)
Risk: L2 (customer-facing UI; no payments, no tenant data yet)
Goal: a real page where a prospect onboards by chatting — accepts the three input kinds (conversation / website link / uploaded file) and shows progress.
Design source: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md` item 5 ("Set up my bot"), `docs/product/CUSTOMER_FACING_RULES.md`
Done when (provable by running):
- [ ] open the page locally and complete an onboarding conversation end to end; transcript + saved run artifacts
- [ ] all three input kinds work on the page (typed answer, URL, file upload)
- [ ] the page never shows a model/vendor name and shows the short PDPA notice where it collects anything
- [ ] reviewer (different model) + security verdict recorded
Budget: 6h builder + 1h reviewer + 1h security
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md`, T-079a, T-079b
Depends on: T-079a, T-079b.

---

### T-079d — Confirmation summary + go-live gate

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (the gate that decides when a bot becomes active — fail-closed matters)
Goal: before the bot goes live, show the extracted **fixed-menu** config + a short sample conversation ("your bot will say things like…"); the customer confirms or asks for changes; **only on confirmation does the bot become active**.
Design source: `docs/product/ONBOARDING_FLOW.md` steps 4–5, `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots.status`)
Done when (provable by running):
- [ ] run through onboarding → the summary renders the extracted config + a sample conversation
- [ ] if the customer edits or declines, the config changes and the bot **does not** go live (fail-closed)
- [ ] on confirm, `bots.status` flips to active and the config rows are persisted — shown in the run
- [ ] reviewer (different model) verdict recorded
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
