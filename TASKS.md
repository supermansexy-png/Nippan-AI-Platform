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

### Board size (Owner order 2026-09-25)
- DONE cards are archived immediately; the board holds only open cards.
- **Cap: 5 open cards** (Owner confirmed 2026-09-25).
- Blocked / superseded cards live in `docs/archive/TASKS_PARKED.md`.
- Inside the cap, WIP is governed by `TASK_CONTROL.md` section 5 (max 3 IN_PROGRESS, 5 REVIEW).

---

### T-030 — Postgres credential / RLS read-write test in n8n

Status: READY — NOT DONE (no connection + RLS proof yet)
Owner: Project Lead — 2026-09-25
Role: Developer (builder) + Reviewer
Risk: L2
Goal: n8n connects to Supabase as `nippan_n8n` and reads/writes `lite_*` under RLS, scoped by tenant + bot
Done when: 1) n8n credential configured and connection test PASS; 2) tenant-A scope sees its own row, tenant-B scope sees 0; 3) insert + read inside a transaction, then rollback; 4) reviewer verdict on the evidence
Budget: ½ day
Links: docs/n8n/T-030-credential-plan.md, docs/n8n/T-030-execution-evidence.md, migration `efe21c7`, n8n folder `Nippan Phase A` (`zClFVASPRDPnaeuQ`)

INTAKE T-030 — 2026-09-25 (strict protocol)
Card: T-030 (READY) — Postgres credential / RLS test
Goal: สร้าง Postgres credential ใน n8n (user nippan_n8n) + ทดสอบ read/write ผ่าน RLS
Scope: n8n workspace + Supabase project xzxw... ; ไม่แตะ Ai-bot-Nippan ; ไม่เปลี่ยน RLS policy (live จาก T-026)
Blocker: พี่ต้องตั้งรหัสผ่าน `nippan_n8n` ก่อน (SESSION_HANDOFF) — รออนุมัติ/ดำเนิน
Evidence needed: (1) n8n credential config (2) connection test result (3) RLS tenant scope verify (A visible / B hidden)
Team: PL (me) + builder z-ai/glm-5.3-flash (Owner-locked) + reviewer space-bunny-free (L1-L3, คนละโมเดล) + HR muse-spark/space-bunny
Cost: builder paid (approved); ไม่มี paid subagent/worker จนพี่อนุมัติชัด; batch ไม่จำเป็น (ไม่ใช่ audit)
Rules applied: PL ไม่แก้โค้ดเอง · INTAKE ก่อน · HR ก่อน · reviewer คนละโมเดล · หลักฐานต้องมี · ไม่อ้าง DONE ถ้ารันซ้ำไม่ได้

PL VERIFY — T-030 — 2026-09-25 (session 2, read-only, no code touched)
- VERIFIED: n8n folder `Nippan Phase A` (`zClFVASPRDPnaeuQ`) exists and is EMPTY (0 workflows) → the test workflow has not been created yet.
- VERIFIED: credential `6anMUYRLDYPduKY7` ("Postgres account", type `postgres`) exists in the personal project `hmhfL4HtmuUod5jL`. Secret values not read.
- VERIFIED (live DB, Supabase `xzxwakvsbdzkdybijbzs`): roles `nippan_n8n` (rolcanlogin=true), `nippan_runtime`, `nippan_analytics`, `nippan_control_plane`; all 7 `lite_*` tables `rls=true force=true`.
- BLOCKED (in-session, not Owner): `n8n_create_workflow_from_code` / `n8n_update_workflow` / `n8n_execute_workflow` are set `true` in `opencode.json` but are NOT registered in the running opencode session → this session cannot create or run the test workflow. Requires a full app restart (a new chat is not enough).
- Blocker from the original INTAKE (Owner sets `nippan_n8n` password) is CLEARED: the pooler connection already succeeded from the n8n UI (see `docs/n8n/T-030-credential-plan.md` §3c).
- Status remains READY / execution UNVERIFIED. Nothing here is DONE.

---

### T-031 — Bridge AI: goal / allowed session / PAUSE removal / restart

Status: BLOCKED — NEEDS_OWNER_INPUT (INTAKE incomplete, no work may start)
Owner: Project Lead — 2026-09-25
Role: unassigned (no builder may be called until the Owner input exists)
Risk: L3 (touches bridge runtime guards + external session access)
Goal: Owner defines what the bridge AI is for and which session is allowed, then PAUSE is removed and the bridge restarted under review
Done when: 1) Owner-provided goal recorded; 2) allowed external session id recorded; 3) PAUSE removal + restart approved and executed; 4) bridge verified running the new code; 5) reviewer verdict
Budget: —
Links: docs/warroom/decision-log.md (2026-09-25 bridge entries), docs/archive/TASKS_PARKED.md (T-BRIDGE-01), `.opencode/bridge/`

INTAKE (partial) T-031 — 2026-09-25
The original card text was lost from the working tree before it was committed (see the board-overwrite incident in `docs/warroom/decision-log.md`). This card is reconstructed from `SESSION_HANDOFF.md` + `decision-log.md`; treat the done-when list as PL-proposed until the Owner confirms it.
Missing from Owner (all three, before any builder is called): (1) the bridge AI's goal, (2) which external session is allowlisted, (3) explicit approval to remove `.opencode/bridge/PAUSE` and restart the bridge.

---

## REVIEW

(none)

## DONE

(completed cards moved to docs/archive/TASKS_DONE_ARCHIVE.md — T-RLS-01 added 2026-09-25)
