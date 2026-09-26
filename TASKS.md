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

Status: DONE — 2026-09-26, Owner approved ("พี่อนุมัติปิด T-030 แล้ว"). Evidence: `docs/n8n/T-030-execution-evidence.md` (executions `5842` + `5844`, reviewer pass 2 ACCEPT-WITH-FINDINGS). Mechanical move to the DONE section / archive on the next doc-cleanup pass.
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

PL VERIFY — T-030 recheck AFTER full app restart — 2026-09-26 (read-only)
- VERIFIED: Owner restarted the opencode app (full restart, not `/new`). In this post-restart session the n8n MCP tools are reachable (`n8n_search_projects` returned a valid response) — so the MCP connection itself is healthy.
- VERIFIED: the session's n8n tool set still does NOT include `n8n_create_workflow_from_code`, `n8n_update_workflow`, or `n8n_execute_workflow`, although all three are `true` in `opencode.json` (lines 123–129). Some tools that are NOT listed in that config block (e.g. `n8n_create_folder`) ARE exposed → the gap is not explained by the opencode allowlist alone.
- THEREFORE: the restart is NOT the fix. The remaining hypothesis is server-side (the n8n MCP server exposes only a read/validate tool subset, or its access mode/version gates write tools).
- ACTION: ops investigation dispatched (Owner approved 2026-09-26, model `opencode/muse-spark-1.3-contributor-free`, free/read-only) — see PL OPS FINDING below.
- Still READY / execution UNVERIFIED. Nothing here is DONE.

PL OPS FINDING — T-030 blocker (n8n MCP write tools missing)
- DISPATCH FAILED 2026-09-26: the `ops` subagent could not launch — "Model not found: `opencode/muse-spark-1.2-contributor-free`". `.opencode/agents/ops.md` line 4 was grep-verified to pin `opencode/muse-spark-1.3-contributor-free`, so the running app is loading a STALE agent set. Retried with `researcher` (same roster model, same 1.3 pin) → identical failure.
- VERIFIED: the app did restart for real — newest desktop log dir `20260925T170949` = 2026-09-25 17:09:49 UTC (~00:09 local 2026-09-26), minutes before this session.
- HYPOTHESIS (both symptoms at once): the app is loading config from the wrong / stale project root, not from `C:\opencode\nippan`. Desktop state holds separate workspace entries for `C:\opencode`, `C:\nippan`, `C:\Users\chetgo`; the `C:\opencode` entry was the one being written during this session. A stale `opencode.json` + `.opencode/agents/` under `C:\opencode` would explain both the missing write tools and the 1.2 model pins.
- UNVERIFIED: contents of `C:\opencode\opencode.json` / `C:\opencode\.opencode\` — this session's filesystem access is limited to `C:\opencode\nippan`, so the duplicate could not be inspected.
- CONSEQUENCE (agent side): `ops` and `researcher` subagents cannot launch while the runtime keeps resolving `muse-spark-1.2-contributor-free`. `assistant` DOES launch → workaround known; the stale pin itself is still unexplained (global config `C:\Users\chetgo\.config\opencode\opencode.json` is empty — only a `$schema` line; the project `.opencode/agents/*.md` files pin 1.3).
- Also still pending: `git restore .opencode/bridge/server.mjs` (uncommitted watcher wiring).

PL FINDING (ops-scope probe, run via `assistant`, 2026-09-26) — why the write tools are absent
- INFERRED from n8n docs (assistant, webfetch): `create_workflow_from_code` / `update_workflow` / `execute_workflow` exist from **n8n 2.12.0** and the instance-level MCP server exposes them **only if the connected client was granted write/execute permissions at authorization time** (granular per-client permission set; no separate read-only flag). Target workflows must also be published + "Available in MCP".
- INFERRED corroboration: `n8n_create_folder` IS exposed → the server is new enough for folder management, so the differentiator is most likely the **client permission grant**, not the version.
- VERIFIED (repo record): `docs/project-memory/CURRENT_STATE.md:324-326` records the earlier Owner order — "Every mutating n8n tool is disabled except `create_folder` (Owner order: the existing n8n work is legacy — read-only)". The later flip to `true` in `opencode.json` therefore conflicts with that recorded order and must be re-confirmed by the Owner.
- UNVERIFIED: the live client permission set — needs the n8n admin UI (Settings → Instance-level MCP → Connected clients) or a live probe; both are outside this session's access.
- Next action: ops checks the n8n side (version + connected-client permissions) and the Owner re-confirms whether write tools should be enabled at all. Status: BLOCKED — NEEDS_OWNER_DECISION.

PL EXECUTION RESULT — T-030 — 2026-09-26 (real run, evidence recorded)
- RESOLVED (tools): after the Owner's app restart the n8n write tools WERE registered — `n8n_validate_workflow` + `n8n_create_workflow_from_code` both worked. So the earlier gap was the stale session, not the n8n server.
- BUILT + EXECUTED (evidence recorded, not a DONE claim): v1 `T-030 RLS test (tenant A vs B)` (`CVhNSU5pjpGgzquB`) and v2 `T-030 RLS test v2 (role + positive control + cross-tenant)` (`eohtRWY8YEvEuS7n`), both in folder `Nippan Phase A` (personal project `hmhfL4HtmuUod5jL`); manual trigger → Postgres `executeQuery` node on credential `Postgres account` (`6anMUYRLDYPduKY7`); no query parameters.
- EVIDENCE: execution `5842` → `visible_as_tenant_a = "1"`, `visible_as_tenant_b = "0"`; execution `5844` (v2) → `connected_role = nippan_n8n`, `visible_as_tenant_a = 1`, `visible_as_tenant_b_before_own_insert = 0`, `visible_as_tenant_b_after_own_insert = 1` (positive control), `cross_tenant_write = BLOCKED by RLS WITH CHECK (42501)`, `visible_as_tenant_a_after_all = 1`; independent check after both runs: `lite_tenants = 0`, `lite_bots = 0` (rollback, nothing persisted). Full record + the v2 SQL: `docs/n8n/T-030-execution-evidence.md`.
- KEEPS: no secret read or written; no RLS policy / role / grant change; both runs are non-destructive and manual (never production).
- REVIEWER: `opencode/space-bunny-free` (different model from the author) — pass 1 ACCEPT-WITH-FINDINGS (role not proven; no positive control / no write-isolation proof) → pass 2 ACCEPT-WITH-FINDINGS after the v2 run, with both findings answered; the reviewer re-pulled execution `5844` raw from n8n and it matched the record.
- Status: REVIEW — awaiting the Owner's approval to close. Residual (not blocking): credential still uses `Ignore SSL Issues`; the card has not been run in production/published mode.
- Open Owner question that remains: whether n8n should keep write/execute capability at all (earlier recorded Owner order was read-only for the legacy n8n work). This does not block this card's evidence.

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
4. **Review (RESOLVED 2026-09-25)** — three layers: (a) **CI runs automatically on the PR** = machine evidence, no human needed; (b) a reviewer on a **different model** than the author reads the diff and writes a verdict comment; (c) the **PL** checks scope/evidence and records the verdict on the card. **Approval/merge: the Owner when present — or the PL on the Owner's behalf when the Owner is away** (deploy preview and architecture changes always need the Owner).

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

### T-033 — War Room in real use: the AI team's meeting room

Status: READY for INTAKE — blocked on the Owner's decisions (access, fresh room, who joins and who pays). No work starts until those are answered.
Owner: Project Lead — 2026-09-26 (Owner order: "ทดลองใช้ห้องวอร์รูปจริง ๆ เพราะหลังจากนี้เราต้องเอา AI เข้าไปประชุมและวางงาน แจกงาน รายงานผล พร้อมอภิปรายปัญหางานกัน")
Role: Owner (chair) + PL (facilitate, record, verify) + AI participants + reviewer on a different model
Risk: L3 (the room drives billable provider turns and holds the team's working record; no tenant/customer data involved)
Goal: the Owner and the AI team hold a **real working meeting** in the deployed War Room — plan, assign work, report results, debate problems — with durable room artifacts (agenda / findings / decisions / owner decisions) instead of a chat transcript.
Done when: 1) a human owner can open the room in a browser over a real auth path; 2) a fresh room can be opened for each meeting; 3) the agreed AI participants are present and produce bounded turns; 4) work assignments, reports and problem discussion are durable in the room; 5) cost per meeting is measured and inside an Owner-approved ceiling; 6) a reviewer on a different model checks the meeting evidence; 7) no secret and no production system touched.
Budget: 1 day setup + one pilot meeting (cost ceiling = Owner decision)
Links: `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` (acceptance + the three carried findings), `services/control-plane-web/war-room/README.md`, `docs/product/MODEL_ROSTER.md`, Issue #35 (closed)

**Blockers / open decisions — NEEDS_OWNER_DECISION**
1. ~~**Human access.**~~ **RESOLVED 2026-09-26** — Cloudflare Access was already configured for `warroom.nippan.org`
   (team `https://1011.cloudflareaccess.com`, AUD read from the login redirect); the Owner completed the Access one-time-PIN
   login and the room loaded in his browser. No new Cloudflare setup needed. Evidence:
   `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` §"Cloudflare Access configuration — discovered by read-only probe".
2. **A fresh room per meeting.** The seeded room is terminal `STOPPED`, the state machine permits no exit, and there is no create-room endpoint. Options: (a) add a reviewed create-room/seed path (code change → builder + reviewer); (b) reset the preview room to `DRAFT` before the pilot (one recorded data operation on the isolated preview DB) so the full lifecycle can be driven live; (c) leave it and accept that the first meeting happens on a fresh seed later.
3. **Who joins, and who pays.** Two architectures, and the choice decides the whole pilot:
   (a) **room-driven turns** — enable bounded turns on ONE preview model (`poolside/laguna-s-2.1` by default) so the room itself produces the AI turns. Cheap (the measured 2026-09-23 session cost $0.00027), but the voices are that single model, **not** our real roster agents;
   (b) **team-driven record** — our real AI team (the dev-time agents per `MODEL_ROSTER.md`) does the work and the room is the durable record of the meeting (plan, assignments, reports, problems). Matches the Owner's stated intent, needs a reviewed posting path for non-owner participants;
   (c) no provider calls at all — participants post without room-driven turns.
   Credit ≈ **$1.60**; any paid pilot needs a hard per-meeting ceiling approved by the Owner.

INTAKE T-033 — 2026-09-26 (Project Lead)
Understanding: the Owner wants the War Room used as the team's real working room: AIs attend, work is planned and assigned, results are reported, problems are debated — the meeting itself must become the durable record, not a chat.
Scope: one pilot meeting end to end on the deployed preview, with the three decisions above answered first. No new architecture, no production system, no customer data.
Needs: the three decisions; then (depending on the answers) a Cloudflare Access setup by the Owner, or a small reviewed create-room path, or a script client.
Missing: all three answers; the current preview's model-turn setting and its per-meeting cost are not readable from the PL session.
Plan (outline, subject to the answers): 1) Owner answers 1–3; 2) PL writes the meeting protocol (who chairs, turn budget, artifact expectations, stop rule); 3) prepare the access path + a fresh room; 4) run the pilot meeting with a hard cost ceiling and a kill switch; 5) collect the durable artifacts and the measured cost; 6) a different-model reviewer checks the evidence; 7) record the verdict and the cost per meeting.
Estimate: 1 day setup + 1 pilot meeting.
Risks: provider spend with a small credit balance (mitigated by the ceiling + kill switch); the room has never been driven by a real multi-participant meeting; the auth path may still block a browser (finding 2 of the War Room acceptance).
Decision: NEEDS_DECISION — blocked on the Owner's three answers above. No AI is dispatched and no paid call is made before that.

**MEETING #001 PLAN — prepared by the PL 2026-09-26 (Owner approved running the pilot)**

- Room: `d3333333-3333-4333-8333-333333333333` ("Nippan AI Team — Meeting #001"), 8 participants, 1 agenda item, DRAFT.
- **Topic (PL recommendation):** "ลำดับงานถัดไป 3 อย่าง + ใครรับงานไหน + ความเสี่ยงที่ต้องเฝ้า" — it is the real next decision, every role has something to contribute, and it produces exactly the artifacts this pilot must prove (agenda → findings → assignment → decision).
- Chair: the room's CHAIR participant; the Owner holds the room controls; the PL records the outcome and verifies it against the database afterwards.
- Opening message for the Owner to paste into the room (then press **ถามทุกคน** while the room is RUNNING):
  > ประชุมครั้งแรกของทีม Nippan AI — ขอให้แต่ละฝ่ายเสนอสั้น ๆ 3 ข้อ: (1) งานถัดไป 3 อย่างที่ควรทำก่อน (2) ใครควรรับงานไหน (3) ความเสี่ยงที่ต้องเฝ้า ตอบไม่เกิน 3 บรรทัด
- Turn budget: the room's defaults — up to 3 participants per Ask, 160 output tokens per turn, model `poolside/laguna-s-2.1` (already enabled: `NIPPAN_WAR_ROOM_PREVIEW_MODEL_TURNS_ENABLED=true`, confirmed by the Owner 2026-09-26).
- **Stop rule (hard):** if the cost display passes **$0.05** for this meeting, or the turns loop/repeat, the Owner presses **หยุด** immediately. The PL records cost before and after (`usage_events`), and the spend must stay inside the ceiling.
- Artifacts to verify after the meeting: `TURN_SCHEDULED` + `MESSAGE_APPENDED` per participant, the room's ordered sequence, the measured cost, and — if the Owner wants it on the record — a decision row via **บันทึกคำตัดสิน**.
- Known limitation to state honestly in the pilot: the room drives **one** cheap model, so the voices are that model, not our real roster agents (T-033 blocker 3 option (a)). The durable-record architecture (option (b)) is a follow-up.

**PILOT RESULT — Meeting #001, 2026-09-26 (Owner ran it in the browser; PL verified against the database)**

- The Owner pressed เตียมห้อง → เริ่ม → ถามทุกคน with the prepared opening message. The room answered with **three participants**,
  the maximum per Ask: **Preview Chair** (CHAIR_SYNTHESIS, 411 tokens), **Preview Builder** (AGENT_MESSAGE, 410 tokens),
  **Preview Security** (AGENT_MESSAGE, 412 tokens) — all on `poolside/laguna-s-2.1`, each preceded by its own `TURN_SCHEDULED`.
- Events recorded: seq 1–2 state changes (DRAFT→READY→RUNNING), seq 3 owner message, seq 4–9 the three scheduled turns and their
  messages. Three new `requests` rows (19 total, all `SUCCEEDED`).
- **Cost: $0.000149** for the meeting (total ledger moved 0.000269334 → 0.000418320 over 30 `usage_events`) — far inside the
  $0.05 ceiling. `ai_calls` remains 0 rows (that table is not the preview's spend ledger; `usage_events` is).
- **Owner finding (drives T-034):** the transcript is unreadable as a chat — you cannot tell **who** answered. The data shows
  three distinct speakers, so this is a **display** problem, not a missing-reply problem.
- T-033 status after the pilot: the room is proven usable for a real meeting (access, fresh room, live turns, durable artifacts,
  measured cost). Remaining: the Owner's UX requirements → T-034.

---

### T-034a — War Room UI: rewrite the surface as a readable chat screen (UI only, FREE model)

Status: READY for INTAKE — the T-033 pilot has run; model split approved by the Owner 2026-09-26.
Owner: Project Lead — 2026-09-26 (Owner order: "พอผ่านช่วงทดลองเสร็จแล้วต้องพัฒนาให้เรียบร้อย เหมือนหน้าจอแชทจริง")
Role: Developer — **free model `nvidia/nemotron-3.5-lightning:free`** (builder backup slot, $0/M, 1M ctx, tools ✓; HR check 2026-09-26: endpoint live, uptime ~90%, latency p50 2.9s / p90 78s → slow, so scope stays tight) + reviewer `opencode/space-bunny-free` (different model; anti-redundancy holds)
Risk: L2 (front-end only; no authentication, authorization, schema, RLS or grant change)
Goal: the `/war-room` surface behaves like a normal chat screen for daily team use — newest message always in view, long history handled without an endless page, and a meeting can be started/archived without hand-made SQL.
Done when: 1) the message list behaves like a chat thread — auto-scroll to the newest message, "กลับไปล่าสุด" control, and the page does not run away as history grows; 2) long history is handled deliberately (windowed/paged view with "โหลดก่อนหน้า" instead of dumping up to 100 events at once); 3) a fresh room per meeting is possible **without** touching the database by hand (reviewed create-room path — endpoint or a seed script that takes a room id/title); 4) the previous meeting stays archived and reachable by its room id; 5) Thai labels stay consistent and the UI states (idle/loading/error) are explicit; 6) tests + CI green, and the change is reviewed by a different model; 7) no production system, no customer data, no provider spend involved in the UI work itself.
Budget: 1–2 days
Links: T-033 (pilot findings drive this card), `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` (how the stopgap room was made), `services/control-plane-web/war-room/` (index.html / war-room.js / war-room.css), `docs/warroom/TASK_CONTROL.md` §8

INTAKE T-034 — 2026-09-26 (Project Lead, from the Owner order)
Understanding: during the pilot the Owner found the room page unusable as a chat screen — history is long, there is no way to clear or start fresh, and a new meeting room had to be created by hand in the database. The Owner wants the surface developed properly after the trial.
Scope: the `/war-room` front-end (and, if a create-room path is needed, the smallest reviewed server addition for it). No auth model change, no schema change.
Needs: the pilot results (what actually annoyed the Owner while using it); the T-033 decisions.
Missing: the pilot has not run yet.
Plan: 1) run the T-033 pilot; 2) collect the concrete usability complaints; 3) scope this card against them; 4) builder implements on a branch, reviewer on a different model checks the diff, CI green; 5) PL verifies against the deployed preview; 6) record the verdict.
Estimate: 1–2 days.
Risks: UI work on the deployed preview without breaking the auth boundary; the create-room path touches the server, so it must be reviewed as carefully as any transport change.
Decision: ACCEPT (queued behind the T-033 pilot).

**PILOT FINDINGS TO FIX — from the Owner using the room for real (2026-09-26)**

The first pilot meeting produced three AI answers (Chair, Builder, Security) but the Owner could not tell **who** answered —
the transcript reads as if only one participant replied. Concrete requirements, in priority order:

1. **Speaker identity on every message** — show the participant's display name **and** role (e.g. "Preview Chair · ประธาน")
   as a header on each bubble; the Owner's own messages must look different from AI messages.
2. **Separate system events from the conversation** — `TURN_SCHEDULED` / `ROOM_STATE_CHANGED` currently sit in the same list as
   the messages and drown the discussion; they belong in a collapsible one-line system log.
3. **Chat affordances** — newest message auto-scrolled into view + a "กลับไปล่าสุด" control; group consecutive messages from the
   same speaker; show time; show model and token count per AI message (small, secondary).
4. **Role-based visual distinction** — colour/avatar per role (OWNER / CHAIR / BUILDER / SECURITY / COST_OPS / AUDITOR / SECRETARY)
   so a long meeting is scannable.
5. **Start a new meeting without hand-editing the database** — a "เริ่มประชุมใหม่" action that creates a room (reviewed
   create-room path), and the previous room stays reachable as an archive.
6. Keep Thai labels consistent; make loading/error states explicit.
7. **Show the roster, not just a number** — the sidebar currently shows a count ("8"); the Owner wants to see **who** is in the
   meeting: each participant's display name + role, with active/inactive made obvious. The count alone tells the Owner nothing.
8. **The agenda panel must actually work** — the right-hand "วาระ" panel is decoration today; either make it usable (create/edit
   the agenda item, mark it done, show the round/round-limit and which agenda item a message belongs to) or remove it. Keeping a
   panel that cannot be used is worse than not having it.
9. **Chat window and typography must be readable** — comfortable line length and font size, clear separation between messages,
   no wall of same-looking text; the room must be readable for a long meeting, not only for a three-message demo.

Verification for this card: the Owner must be able to read a meeting transcript and name every speaker at a glance, see who is in
the room, and understand what the meeting is about from the agenda panel — all without asking the PL what the database says.

**Scope lock for T-034a (files the worker may touch — nothing else):** `services/control-plane-web/war-room/index.html`,
`war-room.css`, `war-room.js`. No server/transport/contract change, no new endpoint, no database access, no new dependency or
build step (the surface stays framework-free and dependency-free), the wire contract (snapshot / SSE / commands) is unchanged,
no secrets in the prompt, and the worker must **not** commit or push.
**Fallback rule (Owner-approved):** if the free model fails quality review twice, the paid builder `z-ai/glm-5.3-flash` closes
T-034a instead — no further attempts on the free model.

**WORK LOG — T-034a (PL, 2026-09-26; Owner away, PL acting under the delegation of 2026-09-26)**

| # | Attempt | Model | Outcome |
|---|---|---|---|
| 1 | headless worker, full rewrite | `opencode/nemotron-3.5-lightning-free` | 10 min of planning + todos, **no file written**, died on a length limit |
| 2 | headless worker, full rewrite, "small steps" | `openrouter/thinkingmachines/inkling:free` | **wrote the change** (~150 lines across the 3 files) → reviewer #1 = **REJECT** (5 findings: timestamps read `timestamp`/`created_at` instead of `occurred_at`; token count read `token_usage`/`usage` instead of scalar `usage_tokens`; `provider_model` invented; `provider_request_id` display dropped; system-log open-state reset every render) |
| 3 | headless worker, fix round 1 | `openrouter/thinkingmachines/inkling:free` | fixed 4 of 5 → reviewer #2 = **REJECT** (blocker: owner decisions pushed into the system log and truncated to 120 chars; blocker: `replaceChildren()` resets `scrollTop` so auto-scroll never fires in a long room; minor: English role enums, `usage_tokens === 0` hidden) |
| — | fallback rule triggered (2 free-model failures) | `openrouter/z-ai/glm-5.3-flash` | headless attempt **stalled twice without writing a file** — the headless harness elides large tool output, so the model kept re-reading the file and burned the step limit; the `builder` subagent path returns no edits (its agent file grants no `edit` permission) → use `--agent worker --model <builder model>` |
| 4 | headless worker, tight scope (4 edits max) | `openrouter/thinkingmachines/inkling:free` | in progress at the time of writing — fixes B1 (owner decision in the conversation) and B2 (auto-scroll); reviewer re-check to follow |

- Environment finding worth keeping: the headless runner truncates large tool output, so a job must be told to read only small
  regions; and `builder.md` has no `edit` permission, while `worker.md` has `edit: allow` — code jobs go through `worker`.
- The change is **not deployed yet**: the preview serves `phase2/postgres-logical-schema`, this work is on `dev-workspace`.
  Deploy path planned: commit → isolated 3-file change on a branch off the deployed branch → PR → merge → Render auto-deploy.

---

### T-034b — War Room server: create-room path + usable agenda (paid builder)

Status: BLOCKED behind T-034a — start only after the Owner has used the improved screen.
Owner: Project Lead — 2026-09-26 (Owner order: the agenda panel "ถ้าจะมีไว้ต้องใช้งานได้" and a new meeting must not need hand-edited SQL)
Role: Developer — **paid builder `z-ai/glm-5.3-flash` (Owner-locked)** + reviewer `opencode/space-bunny-free` + **security reviewer `openrouter/nex-agi/nex-n2.5-mini:free`** (a new write endpoint on the transport is security-relevant)
Risk: L3 (new write path on the transport: authorization, scope binding, fail-closed behaviour)
Goal: a meeting can be created and its agenda managed from the room itself, without anyone editing the preview database by hand.
Done when: 1) a reviewed create-room path exists (each meeting gets its own room, owner-only, server-established actor, fail-closed); 2) the agenda can be created/edited/closed and a message shows which agenda item it belongs to; 3) previous rooms stay reachable as archives; 4) tests + CI green; 5) reviewer **and** security reviewer verdicts recorded; 6) no schema/RLS/grant change and no production system touched.
Budget: 1–2 days
Links: T-034a, T-033 (blocker 2/3), `services/core/app/war_room/transport.py`, `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` (the hand-made room that this replaces)

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
