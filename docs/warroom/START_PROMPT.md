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
Model policy — do NOT restate it, do NOT copy slugs from this box:
- Pins (Primary + Backup per role): take them from `docs/product/MODEL_ROSTER.md` § "Per-role staffing".
- Rules (tiers, retry/failover, anti-redundancy, Batch API, the `opencode-go/<id>` slug rule, the ban list):
  `docs/product/MODEL_POLICY.md`.
- **Work is ordered down the chain**: Owner → `advisor` ("ที่ปรึกษาวางแผน") → Project Lead → specialist.
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
- [ ] Read the `AGENTS.md` § "Session Start" list (the one authoritative list), plus the card in
      `TASKS.md` (+ `docs/warroom/ADVISOR_MANDATE.md` when the work was ordered by the advisor)
- [ ] INTAKE written, ends with a decision
- [ ] Role/model matches MODEL_ROSTER.md (primary pool = OpenCode Go, `opencode-go/<id>`)
- [ ] If the advisor ordered this work: instruction record exists in `ADVISOR_LOG.md` (written by the receiver)
- [ ] Every "Done when" item checked, evidence marked VERIFIED / INFERRED / UNKNOWN
- [ ] Changed files listed; unverified items + problems disclosed
- [ ] Confidence stated; model slug named; commit SHA if git used
- [ ] DB tasks (L2/L3): live query output included (not just file existence)

Incomplete checklist = REJECTION. Do not submit as DONE until applicable items are checked.