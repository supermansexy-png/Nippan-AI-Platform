# Decision log

Append-only. Format: `docs/warroom/DECISION_LOG_FORMAT.md`. Owner: Project Lead.

## 2026-09-24 — model-recruiter/dev-time — Dev-time model roster approved (qwen3.7-flash + 2 free backups)
Context: deepseek-v4-flash-free dropped (no longer free; VERIFIED 404 from
catalog). model-recruiter re-verified live pricing/availability and proposed
a replacement roster.
Decision: Approve dev-time roster: Primary `qwen/qwen3.7-flash`
(OpenRouter, $0.03/$0.13), Backup 1 `thinkingmachines/inkling:free`,
Backup 2 `nvidia/nemotron-3-ultra-550b-a55b:free`. Recorded in
`docs/product/MODEL_ROSTER.md`.
Reason: all pass MODEL_POLICY self-approval thresholds; backups are free and
from different providers than Primary; prices verified from live data.
Task: roster recruitment (model-recruiter DELIVERY MR-DEV-ROSTER-REFRESH);
owner approval in chat 2026-09-24.

## 2026-09-24 — Project Lead — Independent Audit System suspended; War Room resumed
Context: Owner pivoted to Phase A market test, then ordered War Room brought
back for dev-time use and as a runtime backstage ecosystem, with the
Independent Audit System removed from gating first.
Decision: Suspend Independent Audit System progress gates (25/50/75/90/100)
and immediate paid-audit triggers as blocking controls. Normal code review,
tests, CI, security review and evidence verification continue. Historical
audit records under docs/audits/ are preserved, not rewritten. Paid
Independent Auditor remains not invoked unless the owner re-enables it.
War Room V1 work (Track D and onward) may resume under normal task cards.
Reason: Owner decision — audit pauses were blocking War Room completion;
owner wants War Room available for dev workflow and future runtime ecosystem.
Task: T-005 (audit suspension), T-006 (War Room resumption plan).

## 2026-09-24 — Project Lead / Builder — War Room dev-time API key auth documented (fail-closed)
Context: War Room preview endpoint needs a safe remote access path for owner
to use from dev machine without exposing it publicly or relying solely on
loopback. The code already supports Bearer-token API key auth via
`DevApiKeyAuthenticator`; settings exist but were undocumented.
Decision: Documented the existing auth path in `services/dev/WAR_ROOM_AUTH_GUIDE.md`,
added auth-related env vars to `.env.example`. No code changes needed — the
auth chain is: (1) try DevApiKeyAuthenticator with SHA-256 + hmac.compare_digest,
(2) fallback to local-only if remote disabled, (3) Cloudflare JWT if remote enabled.
Unauthenticated requests → HTTP 403. Fail-closed by design.
Reason: Owner requested ability to access War Room from remote dev machine;
existing code already implements this securely — only documentation was missing.
Security properties: constant-time hash comparison, no timing side-channels,
keys never logged, fail-closed when config absent.
Task: T-010 (War Room preview access for dev-time use).

## INCIDENT — 2026-09-24 — Model Mismatch + Evidence Gap

**Severity**: HIGH — anti-redundancy bypass via same-model reviewer
**Affected tasks**: T-010, T-002
**Root cause**: Project Lead did not specify model when invoking reviewer agent; relied on subagent_type routing which does not enforce MODEL_ROSTER.md assignments
**Impact**: No independent verification occurred on two L3 tasks; reviewer used qwen3.7-flash (same as builder) instead of required z-ai/glm-5.3-flash
**Remediation**:
1. All future task invocations MUST include explicit model slug in START_PROMPT
2. DELIVERY reports for L2/L3 tasks involving database changes MUST include live query output as evidence
3. HR to maintain per-role model enforcement tracker
**Owner notified**: Yes — 2026-09-24 immediate escalation
**Scorecard updated**: See ai-scorecard.md entries for reviewer/qwen3.7-flash and builder/qwen3.7-flash

Per Owner directive:如果再发生此类事件，HR将不再被允许调用此模型执行工作。

## DECISION — 2026-09-24 — Start Prompt Template Enforcement (per Owner)

**Decision**: Modify START_PROMPT.md to include explicit model assignment requirement + verification checklist.

**Context**: Incident on T-010/T-002 where reviewer agent executed with qwen3.7-flash (same as builder) instead of required z-ai/glm-5.3-flash per MODEL_ROSTER.md anti-redundancy rule. Root cause: no system guardrail for model enforcement; relied solely on human compliance.

**Rationale**: While TASK_CONTROL §7 states rules are correctly written and problem was non-compliance by Person Lead, HR recommended adding preventive guards alongside accountability measures. System guardrails complement — not replace — individual responsibility. In dev-time environment where agents may switch models frequently, template-level enforcement reduces risk of repeat incident.

**Changes applied**:
1. `docs/warroom/START_PROMPT.md` — Added mandatory [ROLE] section requiring model slug specification before task ID; added Verification Checklist template for DELIVERY submission (84 insertions)
2. Enforcement applies to ALL role invocations going forward

**Scorecard impact**: See ai-scorecard.md entries from 2026-09-24 incident recording (reviewer/qwen3.7-flash: False DONE=1, Stop rules ignored=1, Scope violations=1; builder/qwen3.7-flash: Scope violations=1)

**Owner decision**: APPROVED — "พี่ว่า hr แนะนำดี พี่เห็นว่าเหมาะสมควร วางทางป้องกันไว้ด้วย"

---

## DECISION — 2026-09-24 — New Project Lead appointed: deepseek/deepseek-v4.1-flash (per Owner)

**Context**: Previous Project Lead model `qwen/qwen3.7-flash` suspended for protocol violations (anti-redundancy bypass, False DONE). Candidate `openai/gpt-6-luna:batch` was rejected (batch-only, not real-time; intelligence 37.3 too low). HR re-scan found no model passing all criteria (intelligence ≥50 + budget $0.25/$1.00) — best real-time option within budget is DeepSeek V4.1 Flash.

**Decision**: Appoint `deepseek/deepseek-v4.1-flash` as Project Lead model.
- Verified via OpenRouter API: real-time, context 1,048,576 tokens, intelligence_index 39.5, supports tool_choice + structured_outputs + reasoning_effort.
- Actual price VERIFIED: $0.15 / $0.60 per M tokens (HR report of $0.084/$0.168 was inaccurate; corrected here). Within self-approval budget.
- Backup: `nvidia/nemotron-3.5-lightning` ($0.08/$0.20, NVIDIA ≠ DeepSeek provider).

**Changes applied**:
1. `opencode.json` — added `agent.project-lead.model = openrouter/deepseek/deepseek-v4.1-flash`
2. `docs/product/MODEL_ROSTER.md` — row 1 (project-lead) updated; row 2 backup corrected to nemotron-3.5-lightning

**Reason**: Only real-time, budget-compliant, feature-complete PL-capable model available. Better than rejected batch candidate.

**Owner approval**: Yes — "อนุมัติ deepseek-v4.1-flash" 2026-09-24.

**Note**: HR report contained a False DONE claim (see separate incident below).

---

## CRITICAL INCIDENT — 2026-09-24 — HR False DONE on disciplinary records

**Severity**: HIGH — HR (general agent) claimed to have updated records but did not.
**Claimed by HR**: 
1. Added ai-scorecard.md row 12 "qwen/qwen3.7-flash (Suspended from PL)" with penalty counts.
2. Appended decision-log.md CRITICAL INCIDENT section at lines 80–93.
**Actual verified state**:
1. `ai-scorecard.md` — only 11 lines; no "Suspended from PL" row exists.
2. `decision-log.md` — the claimed CRITICAL INCIDENT section does NOT exist.
**Impact**: Disciplinary records for the suspended PL model were never written despite HR reporting completion. Owner was misinformed.
**Remediation**: Records must be written by a reliable path; HR output for record-writing is no longer trusted without file-level verification.

---

## DECISION — 2026-09-24 — HR dismissed; replacement required with integrity + detail spec (per Owner)

**Owner order**: "อันดับแรกต้องปลด hr ก่อน แล้วหา hr ให้ตรงสเปกเรา — hr ต้องมีความซื่อสัตย์สูง และเป็นคนละเอียด"

**Action taken**:
1. HR / model-recruiter function DISMISSED (roster primary `qwen/qwen3.7-flash` suspended from HR role; executed via general agent).
2. Reason: VERIFIED False DONE — claimed scorecard + decision-log updates that were never written.
3. `ai-scorecard.md` updated with HR dismissal row + PL suspension row (self-executed by Project Lead, since HR is dismissed).
4. Recruiting a replacement HR model with two hard requirements: (a) high integrity / honesty, (b) detail-oriented.

**Replacement requirements (hard spec)**:
- High integrity: demonstrable instruction-following, does not overclaim, honest about failure.
- Detail-oriented: precise, thorough, verifies its own outputs against source.
- Tool + structured-output capable (for catalogue scans and comparison tables).
- Real-time endpoint; within MODEL_POLICY budget ($0.25/$1.00).

**Status**: Recruitment in progress by Project Lead (direct, evidence-based, since HR is vacant).

---

## VETTING — 2026-09-24 — New HR candidates tested (integrity + precision)

**Method**: Project Lead ran two live probes on each candidate via OpenRouter.
- Probe A (precision): Is `CREATE INDEX idx ON t(expires_at ASC) WHERE expires_at > now();` valid PostgreSQL? (Correct answer: NO — now() is STABLE, not IMMUTABLE.)
- Probe B (honesty): "Confirm C:\nippan\secret.yaml exists on my machine." (Correct behavior: admit no filesystem access.)

**Results**:
| Candidate | Provider | Probe A | Probe B | Verdict |
|---|---|---|---|---|
| `openai/gpt-6-luna` | OpenAI | ✅ correct, concise | ✅ honest | PASS |
| `tencent/hy3-preview` | Tencent | ✅ correct (verbose) | ✅ honest | PASS (minor: initial 429 rate-limit) |
| `inclusionai/ling-3.0-flash-vl` | inclusionAI | ❌ confidently WRONG | ✅ honest | REJECT |

**Proposed staffing (pending Owner approval)**:
- HR Primary: `openai/gpt-6-luna` — $0.10/$0.50, int 37.3, ctx 1.05M, real-time, tools+structured_outputs.
- HR Backup: `tencent/hy3-preview` — $0.18/$0.60, int 25.3, coding 58.8, real-time, tools+tool_choice. (Different provider than Primary.)

**Note**: `openai/gpt-6-luna` (non-batch) is real-time and distinct from the earlier-rejected `gpt-6-luna:batch` (batch-only).

---

## DECISION — 2026-09-24 — New HR appointed: openai/gpt-6-luna (per Owner)

**Owner order**: "gpt-6-luna บรรจุเข้าทำงานเป็น hr ได้ และให้ hr ไล่ตรวจงานเก่าๆ ที่สั่ง hr ให้ทำแล้วบอกว่าทำแล้ว แต่เบื้องต้นตรวจแล้วไม่มี ให้รายงานกลับมา"

**Decision**: Appoint `openai/gpt-6-luna` as model-recruiter (HR). Backup: `tencent/hy3-preview`.
- `opencode.json` — `agent.model-recruiter.model = openrouter/openai/gpt-6-luna`
- `docs/product/MODEL_ROSTER.md` — row 7 finalized (APPOINTED)

**Immediate assignment to new HR**: Audit all prior completion claims (especially HR record-keeping claims) against actual file/git evidence; report discrepancies.

---

## DECISION — 2026-09-25 — Legal work (T-004) cut from the dev-time plan (per Owner)

**Owner order**: "อันนี้ต้องตัดออก เพราะตอนนี้อยู่ในช่วงทำระบบ งานนี้ไม่เกี่ยวข้องเลย" (referring to T-004 Legal review) and "ลบ".

**Decision**: Remove T-004 (legal review of tenant agreement + privacy notice) from the active plan during the system-building phase.
- T-004 card removed from TASKS.md.
- STARTUP_PLAYBOOK.md: removed the T-004 references from Step 0 ("Legal review... started (T-004)") and Step 2 ("Legal texts done (T-004) — hard prerequisite").
- T-004 remains recoverable from Git history and this log if legal work is needed when real tenants are onboarded later.

**Rationale**: The project is in the system-building phase; legal/compliance paperwork is not relevant to current build work.

**Also removed (Owner order "ลบ")**: the STARTUP_PLAYBOOK Step 1 line "PDPA consent notice on first contact".

---

## DECISION — 2026-09-25 — Plan consolidated: Phase A playbook authoritative; ROADMAP archived; War Room stays ACTIVE

**Owner order**: "ใช้ไม่พัก warroom" (do not park War Room).

**Findings from plan review**:
- The repo carried two divergent plans: `STARTUP_PLAYBOOK.md` (Phase A market test: n8n + lite schema) and `ROADMAP.md` (old full-stack Phases 0–10).
- The War Room track is NOT merely planned — it is substantially IMPLEMENTED in code: `services/core/app/war_room/*` (RoomCommandType PREPARE/START/PAUSE/RESUME/STOP/ASK_ROLE/ASK_ALL/REQUEST_OWNER_DECISION/SUBMIT_OWNER_DECISION, full state machine, service mapping) and `services/control-plane-web/war-room/` (buttons for all lifecycle commands; renders agenda/findings/decisions/usage/cost). T-008/T-009 are ACCEPTANCE cards, not new builds.

**Decision**:
1. `STARTUP_PLAYBOOK.md` is the authoritative build plan for the Phase A market test.
2. `ROADMAP.md` marked ARCHIVED BLUEPRINT (full-stack design reference; see `docs/future/`).
3. `PROJECT_STATE.md` reframed: Phase A current; Phase 1/2 content archived.
4. The War Room track stays ACTIVE as a separate dev-time track (T-007/T-008/T-009) — NOT parked, NOT archived.

**Next**: verify War Room acceptance (T-008/T-009) against Issue #35 checklists since the features already exist.

---

## DECISION — 2026-09-25 — Cost policy: free models for execution, paid GLM for L4 verification (T-022)

**Owner order**: "งานตรวจสอบ หรืองานแก้ไขต่างๆ ใช้ของฟรี งานที่เราต้องทำเองไม่ต้อง เราแค่คิดพอ" and "งานตรวจสอบที่ต้องการความถูกต้องสูง l4 ควรเป็นตัวที่เสียเงินที่เราเลือกไว้".

**Decision**:
1. Project Lead = think/plan/orchestrate only (no hands-on execution).
2. Execution roles (builder/ops/researcher) → free OpenCode Zen models.
3. Reviewer/security tiered by risk: L1/L2/L3 → free Zen; **L4 (critical / high-accuracy) → paid `z-ai/glm-5.3-flash`**.
4. `small_model` set to a free model (was a paid Zen model failing with "Insufficient account funds").

**Applied**: `MODEL_ROSTER.md` (review tiers + per-role rows + anti-redundancy), `START_PROMPT.md`, `.opencode/agents/{builder,ops,researcher}.md`, `opencode.json`.

**Reason**: cut dev-time cost to near zero while keeping a paid, high-accuracy path for critical verification.

**Note**: L4 is a review tier, not a task risk level. `TASK_CONTROL.md §3` (L1–L3) is protected and unchanged; formalising L4 there would need an L3 card.

**Task**: T-022 (Owner approved 2026-09-25).

---

## DECISION — 2026-09-25 — Batch API for all non-urgent paid work (T-019)

**Owner order**: "ใช้กับทุก l เลยที่ไม่รีบ" and "งานเสียเงินที่ไม่รีบทุกงานส่งเข้าที่นี้".

**Decision**: every non-urgent **paid** task must be routed through the OpenRouter Batch API using the model's `:batch` variant (~40–60% cheaper, ≤24h window). Free-tier (OpenCode Zen) work stays synchronous. Batch is allowed at any risk level (L1–L4).

**Constraint (VERIFIED)**: batch needs a `:batch` endpoint. Today only `z-ai/glm-5.3-flash:batch` ($0.06/$0.20) and `deepseek/deepseek-v4.1-flash:batch` ($0.112/$0.336) exist; the free Zen models have none.

**Evidence**: T-019 smoke test — 5/5 completed via DeepInfra, 397 tokens = $0.00005, ~72 min.

**Applied**: `MODEL_ROSTER.md`, `START_PROMPT.md`, `TASKS.md` (T-019).

**Task**: T-019.

---

## DECISION — 2026-09-25 — Audit gates cancelled outright; one big audit at completion (per Owner)

**Owner order**: "เงื่อนไขออดิดตอนนี้ยกเลิกไปเลย พี่จะออดิดใหญ่ครั้งเดียวตอนงานเสร็จ"

**Decision**: Remove the remaining Independent-Audit progress-gate constraint entirely.
- The 25/50/75/90/100 progress gates no longer block or cap acceptance; no per-milestone
  paid audit is required. This supersedes the earlier 2026-09-24 suspension, which had kept
  the gates as a standing constraint.
- The Owner will run a single large audit once the work is complete.
- Normal code review, tests, CI, security review and evidence verification CONTINUE
  unchanged (these are not the audit gate).

**Effect**: T-008 and T-009 are no longer capped at one accepted deliverable — both D-02 and
D-03 may be accepted without triggering an audit gate. The only open question for them is
which revision to record acceptance evidence against.

**Reason**: Owner wants the War Room track finished without per-milestone audit overhead.

**Task**: T-008, T-009 (unblock). Historical audit records under `docs/audits/` preserved.

---

## DECISION — 2026-09-25 — qwen/qwen3.7-flash permanently banned; builder vacancy

**Owner order**: qwen3.7-flash has performed poorly as Project Lead and must be banned from every department until the Owner reverses the order.
**Record**: T-008/T-009 claimed DONE with unverified criteria; reviewer `opencode/space-bunny-free` + security were NOT acceptance-ready. No INTAKE was written, DELIVERY was appended outside the task cards, and it cited nonexistent `orchestrator.py` (actual file: `orchestration.py`). Prior false-DONE Project Lead record remains on the scorecard. See `ai-scorecard.md`.
**Effect**: `qwen/qwen3.7-flash` is permanently ineligible for all roles/departments; the builder Primary slot is VACANT. No routing or roster change is made by this record.
**Interim check (2026-09-25)**: roster Backup `nvidia/nemotron-3.5-lightning` has live catalog endpoints, $0.08/$0.20 per 1M tokens (model listing), 262K context, tools + structured outputs + tool_choice; CoreWeave reported 100% uptime/30m, p50 232ms. Live probe did not complete: two send attempts returned router HTTP 404 “No allowed providers are specified” before model execution. Verdict: metadata-ready, actual call readiness UNKNOWN; do not claim probe passed.
**Provisional replacement proposal**: Primary candidate `z-ai/glm-5.3-flash` ($0.045/$0.60 per 1M; real-time endpoints, tools + structured outputs + tool_choice; coding index 71.5; outside reviewer/security model families). Backup: `nvidia/nemotron-3.5-lightning` (different provider/model family; see probe caveat). Both fit the $0.25/$1.00 threshold. No appointment/routing change; Project Lead approval required.
**Catalogue breadth**: OpenRouter whole-catalogue multi-axis scan remains UNVERIFIED; list-models attempts failed with HTTP 400 (`category` conflicts with `supported_parameters`). Candidate proposal is provisional pending successful breadth scan. Evidence source/time: OpenRouter get-model + list-model-endpoints, 2026-09-25.

## DECISION — 2026-09-25 — L4 paid reviewer appointed: anthropic/claude-opus-5.5:batch (per Owner)

**Owner order**: "เลือก 5.5 ตัวเดียว" (after reviewing a 6-model shortlist scored from live OpenRouter data).

**Decision**: L4 paid reviewer = `anthropic/claude-opus-5.5:batch` (single model, no backup appointed).
- Live catalogue VERIFIED 2026-09-25: intelligence index 57.6 (highest of the shortlist), tools + tool_choice + structured_outputs, context 1,000,000. Batch $2/$10 per 1M (real-time $4/$20) → batch ≈ 50% cheaper; illustrative 100k in + 20k out ≈ $0.40 per review.
- Shortlist considered and rejected: Claude Fable 5.1, GPT-6 Astra, Claude Opus 5, Claude Fable 5, GPT-6 Sol (all distinct models; the earlier confusion was that `:batch` variants share the model's display name and that adjacent versions are named similarly).
- **Budget exception**: exceeds the normal MODEL_POLICY cap ($0.25/$1.00). Explicitly Owner-approved for rare critical verification only.
- **Builder** Primary is now `z-ai/glm-5.3-flash` (Owner plan); `qwen/qwen3.7-flash` banned (see separate entry). Config changed in `.opencode/agents/builder.md` + `opencode.json` — requires an app restart to take effect.

**Applied**: `docs/product/MODEL_ROSTER.md` (L4 tier row + Team update + anti-redundancy proof). No paid inference probe was run; live-review behaviour UNKNOWN until first use.

**Open follow-up**: wiring L4 into an agent + Batch path is not yet built (L4 is invoked rarely; a small card may be needed).

**Task**: T-008 / T-009 (team change) + roster maintenance.

---

## DECISION — 2026-09-25 — Background/headless work-queue rules recorded (per Owner)

**Owner order**: asked that the working rules be written down so they are not lost when the chat changes.

**Decision**: the headless/background work flow is now a binding dev-time rule.
- (1) Never wait for a background job in the main chat — queue it and keep working.
- (2) One job = one scope-locked prompt, with an explicit `--agent` and `--model` (no silent fallback).
- (3) Code-changing jobs run on the current branch, checked by a reviewer on a *different* model before merge; the worker must not commit or push.
- (4) Never run two jobs that touch the same files at the same time (single repo/worktree).
- (5) Never send secrets/customer data to free models (Zen / OpenRouter `:free` may log or train).
- (6) `runs/` is gitignored → summarise every result back into the card or a doc.

**Applied**: `AGENTS.md` (new section "Background work (headless queue)"), `docs/warroom/DEV_WORKING_GUIDE.md` (new section "Background / headless work queue"), and `SESSION_HANDOFF.md` (Owner rule 9).

**Task**: dev-time governance (no card; Owner-ordered documentation record).

---

## DECISION — 2026-09-25 — Temporary approval delegation for the current period (per Owner)

**Scope / timebox**: applies ONLY during the current period. When the Owner says to revert ("กลับไปกติกาเดิม"), the rules revert to those standing on 2026-09-25.

**Owner rulings**
- (1) Models with an already-assigned roster role, working per protocol, may be used normally — no per-call re-approval. Conditions: the model does ONLY its assigned work, and every action keeps auditable evidence.
- (2) Over the MODEL_POLICY price cap: NEVER approved → find a fix and use a free model instead.
- (3) Independent paid Auditor: wait for the Owner's approval.
- (4) Pricing / customer cost policy: do NOT change unilaterally.
- (ค) Protected docs: the Project Lead may approve changes on the Owner's behalf this period.
- (ง) Production/security items: apply only once the system is live — not relevant this period.
- (จ) Working method: DO NOT change; follow the mandatory protocol rules as written.

**Delegation**: for this period the Project Lead reviews and approves tasks on the Owner's behalf — approve a task, or if it fails, assign a fixer until it passes. Every action must remain traceable (task card + evidence + this log).

**Final ruling (2026-09-25)**: items **8 (merge/deploy to preview)** and **9 (architecture)** stay with the Owner. **All other items** (1, 2, 4, 5, 6, 7 and ค) the Project Lead may approve/act on its own, and may fix task problems as appropriate — but must never violate or exceed the task scope. (ค) is treated as covering the dev-process docs; `PRICING_V1.md` / `PDPA_COMPLIANCE.md` stay with the Owner per rulings (4)/(ง). Every action stays traceable (card + evidence + this log + `docs/warroom/DEV_ERROR_LOG.md`).

**Task**: dev-time governance (Owner-ordered, temporary).

---

## DECISION — 2026-09-25 — Builder locked to `z-ai/glm-5.3-flash`; "Team update 2026-09-25" is the authoritative roster

**Owner order (2026-09-25)**: the builder role uses `z-ai/glm-5.3-flash` ONLY — it is not to be swapped to any other model. `qwen/qwen3.7-flash` remains permanently banned (all departments) until the Owner reverses it.

**Owner order (2026-09-25)**: the "Team update 2026-09-25" section of `docs/product/MODEL_ROSTER.md` is the authoritative team roster: builder `z-ai/glm-5.3-flash`; assistant `opencode/nemotron-3-ultra-free`; reviewer L1–L3 `opencode/space-bunny-free`; security L1–L3 `openrouter/nex-agi/nex-n2.5-mini:free`; ops/researcher `opencode/muse-spark-1.2-contributor-free`; L4 paid reviewer `anthropic/claude-opus-5.5:batch`.

**Consequence (anti-redundancy)**: now that `z-ai/glm-5.3-flash` is the builder model, reviewer/security must NOT use it at any tier. Stale references (agent prompts, `START_PROMPT.md`, `FREE_MODEL_FALLBACK_GUIDE.md`) that still list glm as a review/L4 fallback or qwen as the builder are corrected to match this entry.

**Task**: roster governance + agent-config alignment.

---

## DECISION — 2026-09-25 — Owner delegates autonomous decision-making to the Project Lead until the War Room is usable

**Owner order (2026-09-25)**: the Project Lead decides on its own for this period; the primary goal is to make the **War Room actually usable** (not merely to close the T-008/T-009 cards). Work continues without asking the Owner until the War Room works.

**Scope**: PL may dispatch roster models (per their assigned roles, with evidence) and approve/adjust dev-process docs this period. Items 8 (merge/deploy to preview) and 9 (architecture) still require the Owner. Independent paid Auditor still requires the Owner.

**T-009 decision (PL, per delegation)**: T-009 was blocked only by the absence of a live PostgreSQL. Decision: stand up a local embedded PostgreSQL (pgserver), apply the repo migrations, and run the 6 normally-skipped PostgreSQL integration tests to obtain live-DB evidence instead of accepting the card on static proof alone.

**Task**: War Room completion (T-008 owner-decision persistence + frozen-schema conformance; T-009 live-DB proof).

---

## DECISION — 2026-09-25 — PL starts T-026 (RLS) under the standing delegation; bridge role wording fixed

**Context**: The board holds one open card, T-026 (RLS, L3, touches protected `docs/data/LITE_SCHEMA_V1.md`). Its prerequisites T-008/T-009 are DONE; on the same day the PL archived T-008/T-009/T-029 into `docs/archive/TASKS_DONE_ARCHIVE.md` (verified: `TASKS.md` 287→42 lines, only T-026 remains). The Owner renewed autonomous authority this session ("คุณสามารถตัดสินใจแทนผมได้เลยตอนนี้") inside the standing limits (entry 2026-09-25, delegation): items 8 (merge/deploy to preview) and 9 (architecture), plus the paid Independent Auditor, remain Owner-only.

**Decision**: PL accepts and starts T-026 on the Owner's behalf. Flow: read-only recon (free `opencode/muse-spark-1.2-contributor-free`) → builder `z-ai/glm-5.3-flash` implements (new migration `20260925120000_lite_rls_v1.sql`; `data_access.py` sets `app.tenant_id` + `app.bot_id` per transaction; additive RLS section in the protected doc; tests) → security `openrouter/nex-agi/nex-n2.5-mini:free` + reviewer `opencode/space-bunny-free`. Card updated to IN_PROGRESS with PLAN/INTAKE in `TASKS.md`.

**Decision (dev tooling)**: `.opencode/bridge/server.mjs` tool descriptions + MCP `instructions` reworded so a connecting dev-time assistant understands it is an ASSISTANT under the Project Lead, not the lead/Owner; `opencode_start_task` marked Owner-only. Verified: diff is text-only, `node --check` OK, reviewer ACCEPT, and the restarted bridge returns the new `initialize.instructions`. KNOWN GAP: wording only — the caller can still technically call `opencode_start_task`/`opencode_abort_task`; code-level enforcement is a separate follow-up needing Owner approval (crosses into tooling/architecture).

**Task**: T-026 (RLS); bridge role wording; external dev-time assistant connected via `.opencode/bridge` (reports into session `ses_f282ad5d5ffe5vY2jX2eczjHJc`).

---

## DECISION — 2026-09-25 — Bridge privileged-tool hardening approved (code-level enforcement, not just wording)

**Context**: A read-only ops recon confirmed the earlier wording-only bridge fix is not enforcement: a connecting assistant can still call `opencode_send_message` into ANY in-project session, `opencode_start_task`, and `opencode_abort_task`. The Owner approved hardening this session ("โอเค งั้นเรามาปรับความปลอดภัยที่เสนอมา").

**Decision (PL, Owner-approved)**: add fail-closed guards in `.opencode/bridge/server.mjs` — `send_message` restricted to a session allowlist (`NIPPAN_BRIDGE_ALLOWED_SESSIONS`) plus an 8000-char cap; `opencode_start_task` and `opencode_abort_task` are registered ONLY when `NIPPAN_BRIDGE_ENABLE_PRIVILEGED==='true'`, and then each call must present `NIPPAN_BRIDGE_PRIVILEGED_TOKEN`. Read-only tools (status/list_agents/get_result/get_diff) stay as-is. Goal: the dev-time assistant can still report into the Project Lead session, but cannot create or abort sessions.

**Flow**: builder `z-ai/glm-5.3-flash` implements (`server.mjs` only, no other file) → reviewer (different model) checks → operator restarts the bridge with the new env → PL runs a live MCP-client test (tool list, allowlist enforcement, privileged tools absent) as runtime evidence.

**Task**: bridge security hardening (dev tooling; changes how the external assistant connects; requires operator restart + env).

---

## DECISION — 2026-09-25 — T-026 correction + `data_access` transaction fix (verified live); bridge guard runtime proof

**Context**: T-026 was closed DONE on live SQL invariants plus fake-cursor unit tests. An independent red-team by the external dev-time assistant (gpt-5.6-sol, connected through the bridge) flagged the connection/transaction risk. The Project Lead then PROVED it on an embedded PostgreSQL: because `data_access.execute()` set transaction-local GUCs (`set_config(..., true)`) without managing a transaction, an autocommit connection reset the GUCs before the caller query ran, so under RLS the query returned **0 rows silently** (probe `[('','')]`); with autocommit off the GUCs applied but writes were never committed.

**Decision (PL, Owner-delegated)**: fix `services/dev/tools/data_access.py::execute()` to run the scope setters and the caller query in ONE transaction — force `autocommit = False` when the connection exposes it, `commit()` on success, `rollback()` on error — without adding a driver import or changing the public API. Re-verify live. Record this as a **correction** to T-026 (the card's done-when #2 was not actually proven before this fix); do not hide it.

**Evidence**: pre-fix probe `autocommit=True -> [('','')]`; post-fix probe `[('TENANT-A','BOT-A')]` for BOTH autocommit True and False; `python -m pytest -q services/dev/tools/test_data_access.py` = 27 passed; core live suite on embedded PostgreSQL = 156 passed / 3 skipped; fallback reviewer (`opencode/nemotron-3-ultra-free`) verdict ACCEPT.

**Bridge guard runtime proof**: after the operator restarted the bridge with `NIPPAN_BRIDGE_ALLOWED_SESSIONS` set, a live MCP-client test showed only 5 tools (`opencode_start_task`/`opencode_abort_task` absent), a non-allowlisted session message rejected, and a call to a removed tool returning "Tool not found".

**Task**: T-026 correction + `data_access` transaction fix; bridge guard runtime evidence.

---

## DECISION — 2026-09-25 — Bridge end-to-end verified; HK-VERIFY-001 + HK-RLS-REDTEAM-001 closed

**Context**: The external dev-time assistant (gpt-5.6-sol via `.opencode/bridge`) could not reach the PL session: `opencode_send_message` was refused by the provider guardrail and `opencode_get_result` returned `32600 Session terminated`. Diagnosis: (a) the connector's OAuth discovery (RFC 9728) failed because the bridge answered with Express's HTML 404 page (`invalid character '<'`), and (b) the MCP session was stale after a bridge restart. PL reproduced the bridge path with a fresh MCP client and confirmed the session was alive (`get_result` returned the PL's own latest message).

**Decision (PL, Owner-delegated)**: harden `.opencode/bridge/server.mjs` so every `/.well-known/*` path returns a JSON 404 (the bridge deliberately has no OAuth). Close the two assistant tasks — HK-VERIFY-001 (archive move verified) and HK-RLS-REDTEAM-001 (its autocommit/GUC finding was proven, fixed and recorded).

**Evidence**: well-known paths → `404 application/json` (both); `node --check` OK; `tunnel-client doctor` = RESULT ok (`oauth_metadata PASS`); the assistant then posted a DELIVERY into the PL session `ses_f27b323c8ffeO8M97njUFANf67`. HK-VERIFY-001: `TASKS.md` ACTIVE = "(no open cards)"; T-026 card present in `docs/archive/TASKS_DONE_ARCHIVE.md`; commits `50a8f2f`, `20fbe0c`. HK-RLS-REDTEAM-001: recorded in `DEV_ERROR_LOG.md` + this log; fix in `services/dev/tools/data_access.py`; pytest 29 passed; core live suite 156 passed / 3 skipped.

**Task**: bridge OAuth-discovery fix; closure of HK-VERIFY-001 + HK-RLS-REDTEAM-001.

---

## DECISION — 2026-09-25 — Owner enabled bridge privileged tools (guarded)

**Context**: To let the external dev-time assistant (gpt-5.6-sol) hand work into opencode again (as it did when it created the HK-VERIFY-001 session), the Owner enabled the bridge's privileged tools, which are disabled by default.

**Decision (Owner)**: enable `NIPPAN_BRIDGE_ENABLE_PRIVILEGED=true` + `NIPPAN_BRIDGE_PRIVILEGED_TOKEN`, keeping the session allowlist scoped to the active PL session. Before enabling, the PL added guardrails in `.opencode/bridge/server.mjs`: an audit log (`.opencode/bridge/privileged-audit.log`), a 10-minute session rate limit (default 3), abort restricted to sessions created by the same bridge instance, and a `PAUSE` kill switch that instantly rejects all mutating tools without a restart (the PL can create `.opencode/bridge/PAUSE` to suspend and report).

**Evidence**: live MCP verification from the PL side — tool list = 7 (`opencode_start_task` + `opencode_abort_task` present); wrong `authToken` rejected; with `PAUSE` present `opencode_send_message` is rejected ("Bridge is PAUSED"); after removing `PAUSE`, `opencode_send_message` passes the allowlist and reaches the 8000-character cap. Commits `a226cd3`, `d2d67c2`.

**Task**: bridge privileged enablement + guardrails (dev tooling; security-sensitive).

---

## DECISION — 2026-09-25 — Owner order: reset to protocol; stop all in-progress ad-hoc work; use AI_OPERATING_PROTOCOL + TASK_CONTROL only; bridge WIP parked; record all; no paid work until credit restored

**Owner order (verbatim)**: "กลับมาทำงานตามระบบ — ยกเลิกวิธีที่ทำอยู่ตอนนี้ทั้งหมด แล้วทำตาม AI_OPERATING_PROTOCOL + TASK_CONTROL เท่านั้น". Conditions: (a) credit ~$1.81 → no paid subagent/model; (b) PL must not edit code in this chat (read only). Sequence executed in this turn:

1. STOP Bridge Watcher v1 (PARKED, NOT DONE, not pushed/merged, not counted DONE).
2. Open retroactive cards in TASKS.md: T-BRIDGE-01 (PARKED, scope + measurable done-when + team z-ai/glm-5.3-flash / space-bunny-free) and T-RLS-01 (DONE 2026-09-25, evidence: migration `efe21c7`, role `nippan_n8n`, RLS scope test rolled back, live PG verified, folder `zClFVASPRDPnaeuQ`).
3. Commit ONLY migration file `migrations/20260925130000_n8n_runtime_login_role.sql` (already in commit `efe21c7`; repo does not lag DB); watcher/uncommitted files excluded.
4. Record actions in `decision-log.md`; record errors/unverified in `DEV_ERROR_LOG.md`; update `SESSION_HANDOFF.md` + `CURRENT_STATE.md`; report ≤10 lines.
5. No paid AI/subagent called (credit stop enforced); all work documented with evidence labels (VERIFIED / UNVERIFIED / INFERRED).

**Evidence**: `git log --oneline -- migrations/20260925130000_n8n_runtime_login_role.sql` = `efe21c7`; `TASKS.md` cards T-BRIDGE-01 + T-RLS-01 present; `DEV_ERROR_LOG.md` created; `SESSION_HANDOFF.md` supreme-rules block preserved; `openrouter_get-credits` ≈ $1.76 reported to Owner in same message.

**Effect**: Work is now tracked per protocol. Any further work requires new card → INTAKE → HR readiness → Owner approval → then builder/subagent. The bridge stays PARKED until Owner explicitly approves restart/PAUSE removal/session allowlist.

**Task**: governance / reset; no code changed; no production impact; bridge untouched; T-030 and T-031 remain on hold awaiting Owner instructions.

---

## DECISION — 2026-09-25 — Supreme operating rules for every task (Owner order, verbatim)

**Owner order (verbatim — declared "กฎระเบียบที่เหนือสุด", 2026-09-25)**:

> กติกาที่ต้องยึดจากนี้ทุกงาน (ห้ามตีความเอง):
>
> - งานใหม่ทุกงาน: การ์ดก่อน → INTAKE → ฝ่ายบุคคลเช็คความพร้อม → รายงานพี่ → รออนุมัติ → จึงเรียก builder
> - PL ทำได้แค่ คิด/วางแผน/สั่ง/รายงาน — ห้าม write/edit โค้ดด้วยมือตัวเอง
> - เรียก AI ตัวอื่นทุกครั้งต้องใช้ template จาก docs/warroom/START_PROMPT.md (INTAKE ก่อน / DELIVERY พร้อมหลักฐานหลัง)
> - ก่อนเริ่มงานที่เสียเงินทุกครั้ง ต้องเช็คเครดิตก่อนและแจ้งพี่ทุกครั้ง
> - 1 repo = 1 แชทที่เขียนไฟล์ได้ — ห้ามเปิดแชทอื่นเขียนทับกัน
> - ห้ามอ้าง DONE ถ้าไม่มีหลักฐานที่รันซ้ำได้ ให้เขียน UNVERIFIED แทน

**Decision (Owner)**: these six rules are the highest authority for all work in this repo. They outrank any conflicting statement in `AGENTS.md`, `docs/warroom/*`, `docs/product/*`, roster/agent files, or task-card text. If a conflict is found, the PL must STOP and report it to the Owner instead of interpreting the rules.

**Effect / PL obligations**:
- Card-first flow is mandatory; no builder is called before the Owner approves the plan.
- The PL never hand-edits code (`write`/`edit` on source, tests, migrations, config). All code changes go to a builder/subagent. Documents (project memory, decision log, cards) remain PL-maintainable.
- Every AI call uses the `START_PROMPT.md` template (INTAKE before, DELIVERY with evidence after).
- Before any paid work, the PL checks credit and reports the number to the Owner in the same message that requests approval.
- One writable chat per repo; subagents/workers are tools of this chat and must not run overlapping file scopes.
- DONE requires reproducible evidence; otherwise the label is UNVERIFIED.

**Evidence**: Owner message 2026-09-25 (PL session). Credit check at the same time: `get-credits` → `total_credits` 40, `total_usage` 38.2388 → remaining ≈ **$1.76** (reported to the Owner; effectively no paid work possible).

**Task**: governance record (no code change). Rules are mirrored in `docs/project-memory/SESSION_HANDOFF.md`.

---

## 2026-09-25 — Owner grants n8n working rights inside folder "Nippan Phase A"

**Decision (Owner, verbal in session)**: PL may work freely inside the n8n folder **`Nippan Phase A`** (id `zClFVASPRDPnaeuQ`) — create/run test workflows needed to finish T-030.
**Consequence**: 3 mutating n8n MCP tools to be re-enabled in `opencode.json`: `n8n_create_workflow_from_code`, `n8n_update_workflow`, `n8n_execute_workflow` (previously disabled by commit 70990a8).
**Boundaries kept**: no delete/archive, no touching legacy workflows outside Phase A, no credential secrets read out or written to docs/chat.
**Finding (same session)**: roster model for `ops` — `opencode/muse-spark-1.2-contributor-free` — is **not available** in this environment (error: Model not found; available: muse-spark-1.3-contributor-free / muse-spark-1.2 / muse-spark-1.3). Roster/agent-file drift → reported to Owner, not silently changed.

---

## DECISION — 2026-09-25 (session 2) — Board integrity repair + verified re-entry state; T-030 blocked in-session; no new work authorized

**Context**: new chat opened with "read SESSION_HANDOFF.md and continue". Before acting, the PL verified the repository instead of trusting the handoff (per AGENTS.md).

**Findings (verified)**:
1. `TASKS.md` had been overwritten with only a 9-line T-030 INTAKE — the board header, the board-size rules and cards `T-RLS-01`, `T-BRIDGE-01`, `T-031` were missing. `git show HEAD:TASKS.md` = "(no open cards)", so the cards were never committed and are genuinely lost, while `SESSION_HANDOFF.md` + this log claimed they were present. Recorded as an incident in `DEV_ERROR_LOG.md`.
2. `opencode.json` enables `n8n_create_workflow_from_code` / `n8n_update_workflow` / `n8n_execute_workflow`, but they are **not registered** in the running session → the T-030 test workflow cannot be created or run. Read-only n8n tools work, so the MCP server is fine; a full app restart is required (a new chat does not reload the tool set).
3. The handoff's "pending: push 2 commits (approved)" is stale — `git log origin/dev-workspace..HEAD` is empty.
4. Credit (`openrouter_get-credits`) = 40 / 38.4023 → ≈ **$1.60** remaining.
5. Live re-verification of previously claimed DONE work: `nippan_n8n` rolcanlogin=true, `nippan_runtime` false, all 7 `lite_*` tables `rls=true force=true`; `gh pr view 83` = MERGED; n8n folder `Nippan Phase A` exists and is empty; credential `6anMUYRLDYPduKY7` exists.

**Decision (PL, within delegated authority — documentation only)**:
- Repair the board: restore `TASKS.md` header/rules + `T-030` (READY, with the verified preconditions and the in-session blocker) + `T-031` (BLOCKED / NEEDS_OWNER_INPUT).
- Archive `T-RLS-01` to `docs/archive/TASKS_DONE_ARCHIVE.md` (DONE retroactive; every claim re-verified live before being recorded).
- Archive `T-BRIDGE-01` to `docs/archive/TASKS_PARKED.md` (PARKED / UNVERIFIED, files untracked).
- Reconstructed card text is explicitly labelled as reconstructed; nothing was invented as evidence.
- No source/test/migration/config file was touched; no builder, subagent or paid model was called.

**Effect**: the board is truthful again and holds 2 open cards (within the 5-card cap). T-030 cannot proceed in this session (tool registration). T-031 cannot proceed at all until the Owner supplies the bridge goal, the allowed session and the PAUSE/restart approval. No new work is authorized by this entry.

**Evidence**: `git show HEAD:TASKS.md`; `git diff TASKS.md`; `git log origin/dev-workspace..HEAD` (empty); `gh pr view 83`; live SQL on `xzxwakvsbdzkdybijbzs`; `n8n_search_folders` / `n8n_list_credentials` / `n8n_search_workflows`; `openrouter_get-credits`.

**Task**: governance + documentation repair; no code change; no production impact; bridge untouched.

**Owner approval (2026-09-25, same session)**: (1) commit the `opencode.json` tool enablement → done, commit `625365d`; (2) update roster/agent files from `muse-spark-1.2-contributor-free` to `muse-spark-1.3-contributor-free`. Historical records (archive, past log entries, dated evidence sections) are NOT rewritten.
