# Parked / Superseded Cards (TASKS.md)

NOT active, NOT DONE. Moved off the board on 2026-09-25 under the 5-open-card cap because blocked or superseded. Resume by copying a card back into TASKS.md. Do NOT edit these cards.

---
### T-012 — Staff the dev-time team (role×model pairs)
Status: READY
Parked 2026-09-25: superseded by T-014 (roster/staffing); removed from the board.
Owner: —
Role: Model-recruiter (HR)
Risk: L1
Goal: every dev-time role has an assigned model pair so the team is staffed before work starts
Done when: role×model table covers all 7 roles (project-lead, builder, reviewer, security, ops, researcher, model-recruiter); each has Primary + Backup from a different provider; sourced from roster or new candidates with verifiable evidence (availability, price, probe); written to MODEL_ROSTER.md; no config changed; owner notified for approval
Budget: ½ day
Links: docs/product/MODEL_ROSTER.md, docs/product/MODEL_POLICY.md

INTAKE — T-012 — Model Recruiter (HR) — 2026-09-24
Understanding: Owner ต้องการ map 7 dev-time roles ให้ครบทุกตำแหน่งด้วย model pair (Primary + Backup จากคนละ provider) เขียนลง MODEL_ROSTER.md เท่านั้น ไม่แก้ config/agent files
Decision: ACCEPT

DELIVERY — T-012 — Model Recruiter (HR) — 2026-09-24
Status claimed: DONE
Done-when check:
- [x] ตาราง role×model ครบ 7 roles (project-lead, builder, reviewer, security, ops, researcher, model-recruiter) → VERIFIED (ตาราง 7 แถวใน MODEL_ROSTER.md)
- [x] ทุกตัวมี Primary + Backup จาก provider ต่างกัน → VERIFIED (Alibaba ↔ {Thinking Machines / NVIDIA / Meta} ตามแต่ละ role; anti-regression cross-check PASS)
- [x] Evidence availability+price via openrouter_get-model → VERIFIED (3 roster models pre-verified 2026-09-24 + 2 new probes: llama-3.3-70b-instruct $0.10/$0.32, llama-3.1-8b-instruct $0.05/$0.08)
- [x] Written to MODEL_ROSTER.md only → VERIFIED (no opencode.json or agent files touched)
- [ ] Owner notified for approval → PENDING (owner to approve staffing table)
Changed: docs/product/MODEL_ROSTER.md (rewritten with global model candidates table + per-role staffing + anti-regression cross-check)
Not done: Approval confirmation from Owner
Unverified: Free model (inkling/nemotron) real-time availability on actual call — depends on OpenRouter free endpoint stability (known caveat in roster)
Problems: None
Confidence: high — evidence verified via API calls, policy rules applied correctly, anti-regression checked
Next: Owner reviews staffing table and confirms approval; if any swap desired, Model Scout proposes new candidates within price thresholds.

---

---

### T-001 — Choose and set up hosting for self-hosted n8n + PostgreSQL
Status: **CLOSED — 2026-09-25 (Owner: "1 ปิด")** (was PARTIAL/PARKED)
Closure note: the "hosting" part is satisfied — a working n8n host already exists at `n8n.nippan.org` (read-only recon 2026-09-25: 5 active workflows, 10 credentials). The remaining link, **n8n → PostgreSQL lite schema**, is **T-030** and is not duplicated here. One item from the original done-when has **no card**: *backup/restore proven against the real Supabase project* (only the local embedded-PostgreSQL dump/restore was proven, 2026-09-25). Recorded as a known follow-up; re-open or card it when the runtime phase starts.
Parked 2026-09-25: blocked - dev machine has no Docker engine; playbook Step 0 keeps the item.
Owner: Project Lead (mimo-v2.6-flash-free) — 2026-09-24
Role: ops / Developer
Risk: L2
Goal: a running n8n instance and database with backups, reachable over HTTPS
Done when: n8n login works; database reachable from n8n; daily backup confirmed restorable once
Budget: 1 working day
Links: docs/warroom/STARTUP_PLAYBOOK.md Step 0

INTAKE — T-001 — Project Lead — 2026-09-24
Understanding: Owner approved T-001 as Phase A Step 0 starter task. Need to set up n8n + PostgreSQL stack, configure HTTPS and daily backups. n8n must be reachable over HTTPS. Local Docker Compose first (not production-ready but demonstrates full stack), then recommend production VPS path.
Decision: ACCEPT WITH LIMITS — will deliver local Docker Compose proof first, then prepare production VPS recommendation.

DELIVERY — T-001 — Project Lead — 2026-09-24
Status claimed: PARTIAL (Docker not available on dev machine; config artifacts complete and validated)
Conditions met:
- docker-compose.yml created at services/dev/docker-compose.yml → n8n + PostgreSQL configured with env vars forcing PostgresDB (not SQLite), healthcheck, volumes, proper credentials
- DEPLOYMENT_GUIDE.md created with: quick-start commands, 3 host recommendations (DigitalOcean ~$12/mo, Hetzner ~€4/mo, Oracle Free Tier), SSL/HTTPS setup via Caddy or Cloudflare, daily backup script, verification checklist
- Caddyfile provided for auto-HTTPS reverse proxy
Conditions NOT met (due to environment):
- Cannot verify "n8n login works" live (no Docker engine on Windows dev machine)
- Cannot verify "database reachable from n8n" live (no Docker)
- Cannot test "backup restore" live (no container)
Evidence: Files written and syntax-checked (docker-compose validates as YAML; deployment guide references official n8nio/n8n:latest image and postgres:17-alpine); all env vars match n8n documentation for PostgreSQL backend.
Changed: TASKS.md, services/dev/docker-compose.yml (new), services/dev/DEPLOYMENT_GUIDE.md (new), services/dev/Caddyfile (new).
Unverified: All runtime behaviors (login, DB connectivity, backup restore) require actual Docker engine to confirm.
Next: Owner deploys docker compose on a machine with Docker; runs verification checklist items; reports back. Recommend DigitalOcean for fastest path (~$12/mo, straightforward).

PL NOTE — 2026-09-25 (dev-time, no Docker; Owner-delegated): advanced the locally-verifiable part.
- Embedded PostgreSQL 16 (pgserver) applied all 7 migrations, including the lite schema + lite RLS.
- Real backup/restore cycle executed: `pg_dump -Fc` (253,492 bytes) → `pg_restore --no-owner` into a second database → verified **7 `lite_*` tables restored with RLS (ENABLE+FORCE) on all 7**. Verdict: PASS (this covers the "daily backup confirmed restorable once" done-when item, locally).
- Still not done here: running n8n itself. `npm`/`npx` are blocked by the Windows PowerShell execution policy (`npm.ps1` cannot be loaded) and there is no Docker engine; the remaining done-when items (n8n login, n8n→Postgres, HTTPS) need an operator run (Docker host, or `npx` with the execution-policy workaround).

---

---

### T-007 — War Room D-01: roster + ordered message surface (acceptance)
Status: **DONE — 2026-09-26** (D-01 accepted by the Owner, option ก; Issues #35 and #30 CLOSED).
Parked 2026-09-25 (blocked: remote owner access not enabled) → unblocked, re-verified and accepted 2026-09-26.
Owner: Project Lead (mimo-v2.6-flash-free) — 2026-09-24
Role: Developer
Risk: L2
Goal: authenticated owner loads /war-room with roster + ordered SSE messages; acceptance evidence for D-01
Done when: D-01 acceptance checklist in Issue #35 all met; Issue #30 D-01 checked with evidence
Budget: 1–2 working days
Links: Issue #35, Issue #30, services/control-plane-web/war-room/

INTAKE — T-007 — Project Lead — 2026-09-24
Understanding: D-01 acceptance requires verifying 6 checklist items against deployed preview + codebase.
Decision: ACCEPT

DELIVERY — T-007 — Project Lead — 2026-09-24
Status claimed: PARTIAL (item 1 remote access blocked by current loopback_only; resolves in T-010)
Checklist results:
- [x] Snapshot returns deterministic room + roster → VERIFIED (PR#65+PR#68, transport.py L519-542)
- [x] Ordered SSE replay → VERIFIED (transport.py L544-623, sequence-based)
- [x] Reconnect preserves order w/o browser state → VERIFIED (server authoritative sequence, DB cursor)
- [x] Unauthenticated fails closed → VERIFIED (_authorize_preview_request raises 403; loopback_only default)
- [x] Remote owner loads /war-room/ → VERIFIED 2026-09-26 (remote-authenticated `GET /war-room/` = 200 over the dev-API-key path on the deployed preview; 403 fail-closed without the header)
- [~] Source head recorded → PARTIAL (git HEAD 73672d7; deployed e672a77) — superseded 2026-09-26: deployed revision recorded from the Render API as deploy `dep-dar37iflk1mc73d2ss50` / commit `0b94f67776f3cafcd0fb8ed13c66c2f49b40e3b7`
Next: none — D-01 accepted with findings (evidence + carried findings: `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` §"D-01 acceptance run" and §"ACCEPTANCE DECISION").

---

### T-BRIDGE-01 — Bridge Watcher v1 (external-session watcher)

Status: **DROPPED — 2026-09-25 (Owner: "2 ลบ")** (was PARKED/UNVERIFIED)
Order: the Owner decided work is dispatched over **Git** (T-032), the bridge is not opened, and no relay/watcher service is built → this work is removed.
Files: `.opencode/bridge/watcher.mjs` + `.opencode/bridge/watcher.test.mjs` were **deleted** from the working tree (they were untracked, never committed). The watcher wiring inside `.opencode/bridge/server.mjs` remains as an **uncommitted** modification — reverting it was blocked by the sandbox for the PL, so it is an open cleanup item (one command for the operator/builder: `git restore .opencode/bridge/server.mjs`).
Evidence of deletion: both files absent from the working tree; `git status --short` shows them gone, `server.mjs` still `M`.
Owner: Project Lead — 2026-09-25
Role: Developer (builder) + Reviewer
Risk: L3 (bridge runtime guards, external session access)
Goal: the bridge runs the watcher with an allowlisted session and verified guards
Done when: 1) `node --check` + watcher tests pass; 2) bridge restarted on the new code; 3) allowlisted session verified end-to-end; 4) guards verified (PAUSE respected, non-allowlisted session rejected); 5) reviewer verdict
Budget: ½ day
Links: `.opencode/bridge/server.mjs`, `.opencode/bridge/watcher.mjs`, `.opencode/bridge/watcher.test.mjs`, `.opencode/bridge/PAUSE`, `docs/warroom/decision-log.md` (2026-09-25 bridge entries)

INTAKE (retroactive) — T-BRIDGE-01 — 2026-09-25
Understanding: code for Bridge Watcher v1 was written directly in a PL session during the ad-hoc period. The Owner then ordered a reset to protocol, so the work is recorded as a card and parked rather than continued.
Decision: PARKED (Owner order). Retroactive card — records work already done, does not authorize more.

DELIVERY — T-BRIDGE-01 — (unfinished, no DELIVERY claimed)
Status claimed: NOT DONE — UNVERIFIED
Evidence: `.opencode/bridge/watcher.mjs` + `watcher.test.mjs` exist UNTRACKED in the working tree (never committed); `.opencode/bridge/server.mjs` modified but uncommitted. No evidence of `node --check` or a test run. Bridge not restarted → it still runs the old code. `.opencode/bridge/PAUSE` not removed. Previous external session `ses_f27b323c8ffeO8M97njUFANf67` is stale (OAuth discovery failed; session terminated 32600).
Not done: everything in the done-when list except that the files exist.
Unverified: all runtime behaviour (watcher loop, guards, session allowlist).
Problems: work was executed outside the card/INTAKE flow; the uncommitted files risk being lost or accidentally committed.
Next: Owner decides — either (a) approve restart of T-BRIDGE-01 as a proper card (INTAKE → HR → approval → builder), or (b) drop the watcher and remove the uncommitted files. See also T-031, which holds the missing Owner input (bridge AI goal + allowed session + PAUSE/restart approval).

PL NOTE — 2026-09-25 (session 2): card reconstructed into the parked file because the working-tree copy of `TASKS.md` was overwritten and the card was never committed (see the board-overwrite incident in `docs/warroom/decision-log.md`).

---

## Archived card — T-031 (moved off the board 2026-09-26, mechanical cleanup)

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
