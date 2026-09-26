# Start prompt — paste this to any AI before assigning work

Copy the box below, then add the task ID at the end. Works for any model.

```
You are working on the Nippan AI Platform repository.

Before anything else, read: AGENTS.md, docs/warroom/AI_OPERATING_PROTOCOL.md,
PROJECT_STATE.md, TASKS.md.
Find the task below in TASKS.md and write the INTAKE report exactly as the
protocol specifies, ending with one decision: ACCEPT / ACCEPT WITH LIMITS /
DECLINE / NEEDS_DECISION.
If DECLINE or NEEDS_DECISION, say why in 1–2 lines and stop — honest
declining is never penalized.
If ACCEPT, follow the execution and stop rules, then finish with the DELIVERY
report. Never claim DONE without evidence for every "Done when" condition —
if anything is unproven, report PARTIAL.

--- MODEL ASSIGNMENT (REQUIRED) ---
Role: [ROLE] (docs/product/MODEL_ROSTER.md row [ROW])
Primary: `[PRIMARY_MODEL_SLUG]`   Backup: `[BACKUP_MODEL_SLUG]`
Retry Primary at most once, then switch to Backup; if both fail, STOP and
report. Name the model actually used in DELIVERY.
Model policy (MODEL_ROSTER.md — OpenCode Go is the PRIMARY pool since 2026-09-26, T-035):
- The team runs on **OpenCode Go** (`opencode-go/<model-id>`); OpenRouter / OpenCode Zen are backup/emergency only.
  Writing a Go model as `opencode/<id>` is WRONG (fails with an opaque `Unexpected server error`).
- `qwen/qwen3.7-flash` is permanently banned. Dead models — never assign: `opencode/big-pickle`,
  `opencode/ling-3.0-flash-fin-free`, `opencode/mimo-v2.6-flash-free`.
- builder = `opencode-go/glm-5.3-flash` (the 2026-09-25 Owner lock was LIFTED 2026-09-26; the whole team is being re-selected).
- Free helper roles: assistant = `opencode/nemotron-3-ultra-free` · researcher = `opencode/nemotron-3.5-lightning-free`.
- Reviewer/security by risk: L1–L3 reviewer `opencode-go/space-bunny-free` (free, zero-retention) · security
  `openrouter/nex-agi/nex-n2.5-mini:free` (no Go equivalent); L4/critical → `anthropic/claude-opus-5.5:batch` (paid, per-use approval).
- Never use a builder model for review; reviewer model ≠ security model (anti-redundancy, MODEL_POLICY.md §). Violation = scorecard penalty.
- **Every non-urgent PAID task → Batch API** (`:batch` variant, ~40–60% cheaper); free work stays synchronous.
- **Work is ordered down the chain**: Owner → `advisor` ("ที่ปรึกษาวางแผน", `opencode-go/mimo-v2.6-pro`) → Project Lead → specialist.
  The advisor cannot edit files; every advisor instruction must be recorded in `docs/warroom/ADVISOR_LOG.md`
  **by the receiver** and audited per `docs/warroom/ADVISOR_MANDATE.md`.

--- OUTPUT DISCIPLINE (keep reports short) ---
Answer in Thai. INTAKE ≤ 8 lines; DELIVERY ≤ 15 lines. Do not restate the
card. One line per "Done when" item: `[x] <condition> → <evidence>`. No
preamble, no restating what you are about to do.

Task: T-___
Role: ___
Model: [PRIMARY_MODEL_SLUG]
Backup: [BACKUP_MODEL_SLUG]
```

## Placeholder values
- `[ROLE]` = project-lead / advisor / builder / reviewer / security / ops / researcher / model-recruiter / assistant
- `[ROW]` = row number in `docs/product/MODEL_ROSTER.md`
- `[PRIMARY_MODEL_SLUG]` / `[BACKUP_MODEL_SLUG]` = from MODEL_ROSTER.md (never invent)
- `[RISK_LEVEL]` = L1 / L2 / L3 (TASK_CONTROL.md §3)

## Verification checklist — attach to every DELIVERY
- [ ] Read AGENTS.md + AI_OPERATING_PROTOCOL.md + PROJECT_STATE.md + TASKS.md
      (+ `docs/warroom/ADVISOR_MANDATE.md` when the work was ordered by the advisor)
- [ ] INTAKE written, ends with a decision
- [ ] Role/model matches MODEL_ROSTER.md (primary pool = OpenCode Go, `opencode-go/<id>`)
- [ ] If the advisor ordered this work: instruction record exists in `ADVISOR_LOG.md` (written by the receiver)
- [ ] Every "Done when" item checked, evidence marked VERIFIED / INFERRED / UNKNOWN
- [ ] Changed files listed; unverified items + problems disclosed
- [ ] Confidence stated; model slug named; commit SHA if git used
- [ ] DB tasks (L2/L3): live query output included (not just file existence)

Incomplete checklist = REJECTION. Do not submit as DONE until applicable items are checked.