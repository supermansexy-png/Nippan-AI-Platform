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
Status: PARTIAL
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
Status: PARTIAL
Parked 2026-09-25: blocked - remote owner access not enabled; tracked by Issue #35 D-01.
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
- [ ] Remote owner loads /war-room/ → PENDING (auth mechanism ready, currently loopback_only — T-010 handles this)
- [~] Source head recorded → PARTIAL (git HEAD 73672d7; deployed e672a77)
Next: D-01 conditionally accepted pending T-010. Issue #35 checkbox conditional.

---

### T-BRIDGE-01 — Bridge Watcher v1 (external-session watcher)

Status: PARKED — UNVERIFIED (NOT DONE)
Parked 2026-09-25: Owner order "reset to protocol; stop all in-progress ad-hoc work"; bridge work stopped mid-flight and must not resume without Owner approval.
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
