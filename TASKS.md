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

### T-031 — Bridge assistant (DROPPED — superseded by the Git work channel)

Status: DROPPED — Owner decision 2026-09-25: work is dispatched over **Git**, not over the bridge; the bridge is not opened and no message-relay/watcher service is built. Card kept here as the record; **to be moved to `docs/archive/TASKS_PARKED.md` on the next doc-cleanup pass** (mechanical move, delegated — not done in the main chat).
Owner: Project Lead — 2026-09-25
Role: external dev-time assistant (via `.opencode/bridge`) + PL + reviewer on a different model
Risk: L3 (bridge runtime guards, external access into the dev machine)
Goal: use the bridge assistant as an **on-demand specialist that is slotted into specific tasks** — never as permanent staff, never as a decision-maker, never the Owner's or PL's substitute
Done when: 1) the tier model below is recorded and the Owner's role definition is on the card; 2) the bridge is reachable end-to-end with the allowlist set (evidence: a real message round-trip); 3) at least one **Tier 1** red-team has been run on a real critical item and its findings are recorded with a verdict; 4) a reviewer on a different model checks that evidence; 5) no secret was held by the bridge assistant
Budget: ½ day for the first Tier-1 use
Links: `.opencode/bridge/server.mjs` (guards), `docs/warroom/decision-log.md` (bridge entries 2026-09-25), `docs/archive/TASKS_PARKED.md` (T-BRIDGE-01), `docs/warroom/DEV_ERROR_LOG.md`

**Tier model (Owner-approved 2026-09-25 — help escalates by task level, on demand)**

| Tier | What the bridge assistant does | Gate |
|---|---|---|
| **1 — red-team / reviewer (default, read-only)** | independent check of critical work (RLS/tenant isolation, bridge guard, secret handling); second opinion on a plan before we build | none — this is the default use |
| **2 — design advisor** | review designs (n8n workflow, lite schema, migration plan) before implementation | PL assigns; scope-locked prompt |
| **3 — author (write)** | draft code/docs instead of the paid builder | PL assigns **+ a different model checks the output** + must not hold any secret |
| **4 — privileged tooling** (`opencode_start_task`/`abort_task`) | dispatching work into opencode | Owner enables `NIPPAN_BRIDGE_ENABLE_PRIVILEGED=true` + token; **not part of this card** |

**Hard boundaries (from the bridge's own instructions, verified in `server.mjs`)**: the caller is a dev-time ASSISTANT reporting to the PL — NOT the PL and NOT the Owner · do not create tasks, do not command other agents, do not approve or close work, do not change architecture · messages capped at 8000 chars.

INTAKE T-031 — 2026-09-25 (session 2)
Understanding: the Owner wants the bridge assistant slotted into work **by tier on demand**, not hired as a permanent team member. The original card text was lost from the working tree before it was committed (see the board-overwrite incident in `decision-log.md`); this version is written from the Owner's decision this session.
Scope: use the bridge assistant as Tier 1 first (read-only red-team), on one real critical item, with evidence. Nothing else.
Done when: see card.
Needs: `.opencode/bridge` running with `NIPPAN_BRIDGE_ALLOWED_SESSIONS` set to the session we allow.
Missing: 1) the **allowlist session id** (rule decided below — the value is captured when the chat is opened); 2) whether `watcher.mjs` is wanted at all (untested, untracked).
Plan: 1) Owner opens the fixed bridge-assistant chat and captures its session id; 2) operator sets the env var and restarts the bridge; 3) PL runs the round-trip test; 4) PL scope-locks a Tier-1 red-team on T-030's RLS test plan; 5) findings recorded + reviewer verdict.
Estimate: ½ day for the first use.
Risks: external access into the dev machine (mitigated by the allowlist, the PAUSE kill switch, and privileged tools being off by default); the allowlist must be re-set after every restart — easy to forget (treat a missing allowlist as a blocker, not as "open").
Decision: ACCEPT (Owner approved the tiered on-demand role 2026-09-25).

**ALLOWLIST RULE — Owner decision 2026-09-25 (option ข)**
The bridge talks to **one fixed chat**, never to "whichever PL chat happens to be open". The Owner opens a dedicated chat titled **"ผู้ช่วยสะพาน" (bridge assistant)** and keeps it open; `NIPPAN_BRIDGE_ALLOWED_SESSIONS` = that chat's session id. A PL chat is never allowlisted, so opening/closing PL chats does not change the setting.

**RUNBOOK — first activation (operator = Owner)**
1. Owner opens the dedicated "ผู้ช่วยสะพาน" chat, leaves it open, and notes its session id (`ses_...`).
2. Operator sets `NIPPAN_BRIDGE_ALLOWED_SESSIONS=<ses_...>` (fail-closed: unset ⇒ every message rejected — expected, not a bug).
3. Operator restarts the bridge so the env var takes effect.
4. PL runs the **round-trip test**: bridge assistant → `opencode_send_message` → reply read via `opencode_get_result`; evidence recorded on this card.
5. First Tier-1 use: scope-locked red-team of the **T-030 RLS test plan**, before the workflow is built.
**Notes**: `PAUSE` must stay absent (`Test-Path .opencode/bridge/PAUSE` = False) for this to work · the env var must be re-set after any bridge restart · privileged tools stay OFF (Tier 4 is not part of this card).
**Capture note (UNVERIFIED)**: the PL could not read opencode's session store from the sandbox (the command was refused by permission), so the session id is captured by the Owner when the chat is opened — or from the bridge watcher log once T-BRIDGE-01 is settled.

**PL VERIFY — bridge guards (read-only, `server.mjs`, 2026-09-25 session 2)**
- VERIFIED: `NIPPAN_BRIDGE_ALLOWED_SESSIONS` empty → `opencode_send_message` **rejects all** ("disabled") → fail-closed.
- VERIFIED: a session id not in the allowlist is rejected.
- VERIFIED: privileged tools are **OFF by default**; enabling needs `NIPPAN_BRIDGE_ENABLE_PRIVILEGED=true` **and** the shared token; rate limit 3 sessions/10 min; every privileged call is appended to an audit log.
- VERIFIED: `PAUSE` is a **kill switch you create to pause** (absence = running). `Test-Path .opencode/bridge/PAUSE` = **False** → the bridge is currently **not** paused. The earlier handoff claim "PAUSE not removed" was muddled — corrected here.
- VERIFIED: `PAUSE` was never committed (`git ls-files .opencode/bridge` → only `server.mjs`), so there is no history of who touched it; `watcher.mjs` + `watcher.test.mjs` are also untracked.
- UNVERIFIED: `watcher.mjs` behaviour (never run, no `node --check`, no test result) — that is T-BRIDGE-01, still parked.

---

### T-032 — Dispatch work over Git (issue → branch → draft PR → CI → review → merge)

Status: READY for INTAKE — needs the Owner's decision on repo settings + the external side's settings (see Blockers)
Owner: Project Lead — 2026-09-25
Role: PL (dispatch + verify) + external assistant (author, on `codex/*` branches) + reviewer on a different model + Owner (approval)
Risk: L3 (external party writes into our repository)
Goal: the external assistant receives work through Git (not through the bridge), does it on its own branch, and lands it only through review — so work keeps moving when the Owner is not in a chat
Done when: 1) safe settings confirmed on both sides; 2) `dev-workspace` protected against direct/force pushes (or an equivalent rule agreed); 3) the issue↔card convention is written; 4) **pilot A (read-only)** proves the assistant can find our queued work by itself; 5) **pilot B (write)** lands one real change as a PR with CI evidence, checked by a different-model reviewer; 6) no secret ever reaches git; 7) PL/Owner approval recorded before merge
Budget: ½ day for pilot A, ½ day for pilot B
Links: `TASKS.md` (cards = source of truth), GitHub Issues (queue), `.github/workflows/` (CI), `docs/warroom/decision-log.md` (2026-09-25 git-channel decision)

**Hard rules (no exceptions)**: the external assistant works only on branches it creates (`codex/*`) · **never merge its own PR** · never push directly to `dev-workspace` or `phase2/postgres-logical-schema` · never force-push · **never put secrets in git** (history is permanent — work touching credentials runs on our machine only) · author ≠ checker: a different model reviews every non-trivial change · merge and any preview deploy still need the Owner (or the PL when the Owner is away, except deploy/architecture).

**Blockers / open questions**
1. Repo settings: **OPEN** — protection on `dev-workspace` not decided yet (checked: `dev-workspace` protected = **false**; `phase2/postgres-logical-schema` = **true**). Owner decision pending.
2. External side settings: **OPEN** — Owner has not yet confirmed the four values (Draft PR = ON · auto-merge = **OFF** · branch prefix `codex/` · no force-push).
3. **Trigger = the Owner (RESOLVED 2026-09-25)** — "พี่เอง": the Owner starts each round; the assistant does not auto-start from a queue. Pilot A therefore tests only whether it can *find* queued work **once started**.
4. **Review (RESOLVED 2026-09-25)** — three layers: (a) **CI runs automatically on the PR** = machine evidence, no human needed; (b) a reviewer on a **different model** than the author reads the diff and writes a verdict comment; (c) the **PL** checks scope/evidence and records the verdict on the card. **Merge stays with the Owner.**

**Review checklist for the assistant's PRs (7 points)** — 1) in scope vs the card? 2) only the expected files touched? 3) tests added / CI green? 4) **no secrets, tokens, DSNs or customer data anywhere in the diff?** 5) evidence attached (CI run + what was run and what was expected)? 6) claims match the diff (no "done" without proof)? 7) author ≠ checker confirmed.

INTAKE T-032 — 2026-09-25 (session 2)
Understanding: Owner decision — "ยึดแนวทาง git"; the bridge is not opened and no relay/watcher service is built. Git becomes the work channel because it is an asynchronous queue: the external assistant reads our queued work, does it on a branch, and CI + review provide the evidence, so work does not stall when nobody is answering a chat.
Scope: set-up + two pilots on this repo. Nothing else.
Needs: repo settings change (Owner), external-side settings (Owner), CI already exists.
Missing: the four answers above.
Plan: 1) Owner answers 1-4; 2) PL writes the issue↔card convention; 3) pilot A (read-only) — assistant finds queued work itself, evidence recorded; 4) pilot B (write) — one real PR with CI + different-model review; 5) verdict recorded in the decision log.
Estimate: 1 day total.
Risks: an external party writing into the repo (mitigated by branch rules + review + no secrets); auto-merge must stay off; `dev-workspace` is currently unprotected.
Decision: ACCEPT (Owner chose the Git channel 2026-09-25).

---

## REVIEW

(none)

## DONE

(completed cards moved to docs/archive/TASKS_DONE_ARCHIVE.md — T-RLS-01 added 2026-09-25)
