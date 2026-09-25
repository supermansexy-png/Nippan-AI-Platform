# War Room Preview Deployment Evidence

Date: 2026-09-23  
Scope: non-production War Room preview infrastructure only  
Integrated source baseline: `e672a77bbb932d05b88e7ce01eb290e02a544356`

## Purpose

Record durable, source-controlled evidence for the isolated War Room preview deployment created under the non-production preview infrastructure exception in `docs/audits/AUDIT_SYSTEM_V1.md`.

This document does not authorize production deployment, provider/model turns, automatic `run_next_turn`, or a public authentication bypass.

## Governance

PR #69 added the narrow non-production preview infrastructure exception.

The exception does not waive:

- normal 25% / 50% / 75% / 90% / 100% audit gates;
- security/authentication immediate-audit triggers;
- PostgreSQL/schema/RLS immediate-audit triggers;
- production authorization requirements.

Remote/mobile authentication is therefore tracked separately from the preview infrastructure recorded here.

## Render Core preview

Repurposed service:

- service name: `chetgo`
- service ID: `srv-dajprr5g1s2s73bnoed0`
- region: Singapore
- plan: free
- repository: `supermansexy-png/Nippan-AI-Platform`
- branch: `phase2/postgres-logical-schema`
- root directory: `services/core`
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health endpoint: `/health`
- primary URL: `https://chetgo.onrender.com`

The protected Render service `Ai-bot-Nippan` was not modified.

Latest verified deployment after the database DSN correction was LIVE. Application logs showed normal Uvicorn startup and recurring `GET /health 200` responses.

## Preview database

Active runtime preview database:

- provider: Supabase
- project name: `nippan-war-room-preview`
- project ref: `cjzrjdznijxtigmzgyzm`
- region: `ap-northeast-2`
- status at provisioning verification: `ACTIVE_HEALTHY`
- production/main Supabase project was not used for this preview deployment

The Render service uses the isolated preview database through `NIPPAN_DATABASE_URL`. No database password or connection URI is recorded in source control.

## Applied reviewed migrations

The following repository migrations were applied successfully to the isolated Supabase preview project, in order:

1. `20260922174011_phase2_core_foundation.sql`
2. `20260922174227_phase2_core_fk_indexes.sql`
3. `20260922180029_phase2_request_trace_telemetry.sql`
4. `20260922180107_phase2_idempotency_usage_audit.sql`
5. `20260922193829_phase2_a001_least_privilege.sql`
6. `20260922231000_war_room_v1_increment_b.sql`

No new preview-only migration, RLS policy or grant behavior was introduced.

## Deterministic preview seed evidence

Verified rows for room `c3333333-3333-4333-8333-333333333333`:

- rooms: 1
- active participants: 8
- agenda items: 1

The participant set is Project Owner plus seven AI roles:

- Chair
- Architect
- Builder
- Security Reviewer
- Cost & Ops Reviewer
- Independent Auditor
- Secretary

The seed also contains the existing non-billable preview finding/proposal artifacts.

## Database connection evidence

After correcting the Supabase Session Pooler DSN:

- the latest Render deployment completed as LIVE;
- Core application startup completed;
- the post-deploy log window contained no `password authentication`, host-resolution, circuit-breaker or pool connection errors;
- `Database.open()` opens the configured async PostgreSQL pool during application lifespan startup.

A direct external `/ready` probe was not captured by the available connector in this evidence pass, so this document does not claim an independently recorded HTTP `/ready 200`.

## Historical Render PostgreSQL experiment

A separate Render PostgreSQL preview instance was created earlier for evaluation:

- name: `nippan-war-room-preview`
- ID: `dpg-dapli7ou01pc73d2s5og-a`
- PostgreSQL 17 / Singapore / free plan

The reviewed Supabase-oriented migration set could not be replayed unchanged there because the managed Render database user was not permitted to execute `ALTER DEFAULT PRIVILEGES FOR ROLE postgres`.

The attempted startup failed closed with `psycopg.errors.InsufficientPrivilege: permission denied to change default privileges`.

The Render bootstrap flag was then disabled. This Render PostgreSQL instance is not the active runtime database path.

## Remote/mobile boundary

The deployed preview transport still enforces:

`war_room_preview_loopback_only`

for non-loopback requests.

Therefore the current deployment does not provide public/mobile War Room access. Relaxing this boundary requires secure remote authentication and remains a separate security/authentication change subject to the independent-audit rules.

## Provider and production boundary

The preview remains non-billable:

- no browser route invokes `run_next_turn`;
- no auto-advance or turn chaining is enabled;
- no funded OpenRouter credential is enabled by this deployment;
- no Supabase production migration was performed;
- no `Ai-bot-Nippan` or production n8n workflow was modified.

## Acceptance status

This deployment evidence does not mark Track D deliverables accepted.

Audit-accepted Increment C progress remains:

`13 / 16 = 81.25%`

D-01, D-02 and D-03 remain unaccepted until formal end-to-end acceptance evidence is recorded under the project governance process.

## Correction (2026-09-25, builder z-ai/glm-5.3-flash, T-008 fix round)

The claims above describe the deployed preview baseline `e672a77` and are kept
as historical record. The current dev-workspace HEAD differs from that baseline:

- commit `0cead22` ("bounded live model turns") added a server route that DOES
  invoke `run_next_turn` when `war_room_preview_model_turns_enabled` is ON with
  a configured OpenRouter key/model; the setting still defaults to OFF, so the
  default preview remains non-billable. The docstring of
  `create_war_room_preview_router` and `services/core/README.md` were updated
  accordingly on 2026-09-25 (T-008 fix round).
- the local-access fallback in `_authorize_preview_request` was hardened on
  2026-09-25 (T-008): it now returns OK only when the request genuinely arrives
  over a loopback socket; other addresses fail closed with
  `war_room_preview_loopback_only`.

## D-01 re-verification against the live preview — 2026-09-26 (Project Lead, read-only)

Deployed revision (Render API): service `chetgo` (`srv-dajprr5g1s2s73bnoed0`), latest deploy
`dep-dar37iflk1mc73d2ss50`, commit `0b94f67776f3cafcd0fb8ed13c66c2f49b40e3b7` (merge of PR #82),
status `live`, finished 2026-09-25T08:42:44Z; branch `phase2/postgres-logical-schema`, region singapore, plan free.

Live probe from outside the machine, no cookies, no credentials:

| Request | Result |
|---|---|
| `GET https://chetgo.onrender.com/health` | 200 |
| `GET https://chetgo.onrender.com/war-room/` | 403 `{"detail":"war_room_preview_remote_auth_required"}` |
| `GET /war-room/rooms/<valid-uuid>/snapshot` | 403 (same detail) |
| `GET /war-room/rooms/<valid-uuid>/events` | 403 (same detail) |

- VERIFIED: **fail-closed** (D-01 item 5) — every War Room surface returns the application's own 403,
  by detail string, before any room data is served. The earlier 503 responses were the Render free-plan cold start.
- VERIFIED (gap): Cloudflare Access is **not** intercepting requests to `chetgo.onrender.com`; the unauthenticated
  request reached the origin application (the body is the app's JSON). Per
  `services/control-plane-web/war-room/README.md`, remote mode requires the `Cf-Access-Jwt-Assertion` header — only
  Cloudflare Access (or `NIPPAN_WAR_ROOM_DEV_API_KEY`) can supply it.
- Therefore D-01 item 1 ("authenticated remote owner can load `/war-room/`") is **not satisfiable by browsing the
  Render URL** at present, and items 2–4 (snapshot roster / SSE replay / reconnect ordering) cannot be exercised
  without an authenticated session. Items 2–4 are covered by repo tests, not by deployed-preview acceptance evidence.
- Observation (low, informational): `GET /war-room/rooms/<malformed-uuid>/snapshot` returns 422 (FastAPI path
  validation) before the auth guard, so the guard sits inside the route rather than in middleware. No room data is
  returned, and a well-formed UUID returns 403 fail-closed.
- NOT VERIFIED (outside this session's access): whether a Cloudflare Access application exists on another
  hostname/zone fronting this service; whether `NIPPAN_WAR_ROOM_DEV_API_KEY` is set on the Render service.
- **D-01 remains UNACCEPTED.** Issues #35 / #30 stay OPEN until item 1 has real evidence.

## D-01 acceptance runbook — dev API key path (Owner decision 2026-09-26, option ข)

`services/dev/WAR_ROOM_AUTH_GUIDE.md` method 1. The dev API key path is evaluated before remote access, so no other
setting changes; the deployed service already has `war_room_preview_remote_access_enabled=true`.

1. Owner sets `NIPPAN_WAR_ROOM_DEV_API_KEY=<strong random>` on the Render service `chetgo` (Environment) and waits for
   the env-triggered redeploy to finish. Settings are cached at startup, so a restart is required.
2. Owner runs, from his own machine, with the key held locally only (never pasted into a chat):
   - `GET /health` → 200 (also wakes the free instance);
   - `GET /war-room/?room_id=c3333333-3333-4333-8333-333333333333` with `Authorization: Bearer <key>` → 200, HTML UI;
   - `GET /war-room/rooms/c3333333-.../snapshot` with the header → 200 JSON: deterministic room + active participant roster;
   - `GET /war-room/rooms/c3333333-.../events?after_sequence=0` (SSE, bounded by `--max-time`) → ordered event sequence;
     then the same call with `after_sequence=<last seen>` → only newer events, no duplicates, no gaps;
   - the same snapshot call **without** the header → 403 `war_room_preview_remote_auth_required` (fail-closed).
3. Owner returns only results (status codes, snapshot JSON, ordering observation) — not the key. The Project Lead records
   them here as D-01 item-1/2/3/4 evidence; D-01 closes only after that.

### D-01 acceptance run — RESULTS (Owner-executed, 2026-09-26)

Method: `services/dev/WAR_ROOM_AUTH_GUIDE.md` method 1 (dev-time API key). The key was held by the Owner only and is not
recorded here. Deployed revision: `chetgo` / deploy `dep-dar37iflk1mc73d2ss50` / commit
`0b94f67776f3cafcd0fb8ed13c66c2f49b40e3b7`.

| D-01 checklist item | Result | Evidence |
|---|---|---|
| 1. authenticated remote owner can load `/war-room/` on the deployed preview | **PASS** | `GET /war-room/?room_id=c3333333-3333-4333-8333-333333333333` with the dev API-key header → **200**; `GET /health` → 200 (from the Owner's own machine, i.e. genuinely remote) |
| 2. snapshot projection returns the deterministic room and active participant roster | **PASS** | `GET /war-room/rooms/c3333333-.../snapshot` → 200 JSON: `room_id=c3333333-3333-4333-8333-333333333333`, `tenant_id=c1111111-…`, `application_id=c2222222-…`, `mode=FORMAL_MEETING`, `state=STOPPED`, `last_sequence=24`, **8 participants, all `active:true`** (OWNER, CHAIR, ARCHITECT, BUILDER, SECURITY_REVIEWER, COST_OPS_REVIEWER, SECRETARY, INDEPENDENT_AUDITOR) |
| 3. ordered message/event replay demonstrated through the deployed SSE path | **PASS** | `GET /war-room/rooms/c3333333-…/events?after_sequence=0` → SSE `id:` **1,2,3,…,24** in ascending order with matching `sequence` values, no gaps; event types MESSAGE_APPENDED / ROOM_STATE_CHANGED / TURN_SCHEDULED; `recent_events` in the snapshot contains the same 24 sequences → the durable projection matches the stream |
| 4. reconnect/replay preserves sequence ordering without browser-owned state authority | **PENDING** | the reconnect replay (`after_sequence=23`, then `after_sequence=24`) has not been run yet |
| 5. unauthenticated/untrusted remote access fails closed | **PASS** | `GET /war-room/rooms/c3333333-…/snapshot` **without** the header → **403** (`war_room_preview_remote_auth_required`); re-confirmed earlier the same day on `/war-room/`, snapshot and events |
| 6. evidence records the exact source head and deployed revision | **PASS** | Render API: latest deploy `dep-dar37iflk1mc73d2ss50`, commit `0b94f67776f3cafcd0fb8ed13c66c2f49b40e3b7`, `status=live`, finished 2026-09-25T08:42:44Z, branch `phase2/postgres-logical-schema` |

- The snapshot's `usage` block (input 983 / output 1120 / `normalized_cost` 0.000269334 USD) is served from the
  UsageEvent projection, not a browser ledger (relevant to D-03, not claimed here).
- Auth-method note (honest scope): item 1 was exercised through the **dev-time API-key path**, which is a documented,
  fail-closed remote-auth method. The **Cloudflare Access JWT path** (`Cf-Access-Jwt-Assertion`) was not exercised
  because Cloudflare Access was not intercepting `chetgo.onrender.com` at the time of the probe.
- Security note for the Owner: while the dev API key is set on the service, any holder of that key can reach every War
  Room surface; owner *commands* still require the DB-backed active OWNER participant. Remove/rotate the key once the
  acceptance run is finished.
- The 90% Independent-Audit gate sequencing note in Issue #35 is superseded by the Owner's 2026-09-25 decision
  (progress gates cancelled; one single large audit when the work is complete) and is not re-activated by accepting D-01.
- Repeat run (same key, run twice by the Owner): snapshot `generated_at` differs (18:20:42Z vs 18:22:47Z) while every
  projected value is identical → the projection is deterministic and re-readable; the 403 without the header reproduced.
  Note for the operator: PowerShell renders a 403 from `Invoke-WebRequest` in red as a thrown exception — that red line
  **is** the expected fail-closed result, not a failed test.

## D-02 / D-03 evidence — database cross-check (Project Lead, read-only, 2026-09-26)

Preview database: isolated Supabase project `nippan-war-room-preview` (ref `cjzrjdznijxtigmzgyzm`), read-only SQL,
same room `c3333333-3333-4333-8333-333333333333` that the live snapshot was read from.

| Live snapshot (authenticated HTTP) | Database truth | Result |
|---|---|---|
| `state = STOPPED` | `project_rooms.state = STOPPED` | MATCH |
| `mode = FORMAL_MEETING` | `project_rooms.mode = FORMAL_MEETING` | MATCH |
| 8 participants, all active | `project_room_participants` = 8 rows, 8 active | MATCH |
| `last_sequence = 24` | `max(project_room_messages.sequence)` = 24 | MATCH |
| `usage.normalized_cost = 0.000269334` | `sum(usage_events.normalized_cost)` = 0.000269334 over 21 rows | MATCH |
| agenda 1 / findings 1 / decisions 1 | `project_room_agenda_items` = 1, `_findings` = 1, `_decisions` = 1 | MATCH |
| SSE `id:` 1…24, ascending, no gaps | `project_room_messages` = 24 rows: OWNER_MESSAGE 5 (seq 1,4,7,14,17), AGENT_MESSAGE 5, CHAIR_SYNTHESIS 2 (9,19), SYSTEM_EVENT 12 (ROOM_STATE_CHANGED 2,3,5,6,24 + TURN_SCHEDULED 8,10,12,15,18,20,22) | MATCH |
| owner-command trail | `requests` = 10 rows, all `request_kind=admin_action`, `source=war-room-preview`, `current_status=SUCCEEDED` | MATCH |
| no model-call telemetry | `public.ai_calls` = **0 rows** | MATCH |

- VERIFIED (D-03 items 2–3): the deployed snapshot is a database-backed projection, and the usage/cost figure is sourced
  from the platform UsageEvent ledger (`usage_events`), not from a browser-side ledger.
- VERIFIED (D-02 item 4): the accepted owner-command trail is durable — 10 `SUCCEEDED` `war-room-preview` requests covering
  the recorded transitions DRAFT→READY (seq 2), READY→RUNNING (3), RUNNING→PAUSED (5), PAUSED→RUNNING (6),
  RUNNING→STOPPED (24) — exactly the transitions allowed by `app/war_room/state_machine.py`.
- VERIFIED (D-02 item 5): `ai_calls = 0` in the preview database; the events that contain model output are historical
  (2026-09-23) and already reflected in `usage_events`.
- FINDING — blocks D-02 item 1 from being re-exercised live: the deterministic preview room is already in the **terminal**
  state `STOPPED`, and `state_machine.py` permits no transition out of a terminal state. There is no create-room endpoint and
  bootstrap seeds only when the room is absent. Re-running PREPARE/START/PAUSE/RESUME/STOP on the deployed preview therefore
  requires resetting or reseeding the preview room. The recorded sequence above was produced by an earlier **loopback** owner
  session, not over the remote path.
- FINDING — limits D-03 item 1: the dev API-key path authenticates **non-browser** clients only (the browser UI cannot attach
  an `Authorization` header), so an end-to-end browser render over the authenticated remote path needs the Cloudflare Access
  path. Available today: the UI HTML is served (200) and the snapshot JSON the UI consumes is served (200) with agenda,
  findings, decisions and usage populated.

## D-01 / D-02 / D-03 — ACCEPTANCE DECISION (Owner, 2026-09-26, option ก)

The Owner accepted D-01, D-02 and D-03 on the evidence recorded above (remote-authenticated HTTP + read-only cross-check of
the isolated preview database), carrying the two findings openly instead of re-running the blocked live steps.

| Deliverable | Verdict | Accepted on | Carried finding |
|---|---|---|---|
| **D-01** roster + ordered message surface | ACCEPT-WITH-FINDINGS | items 1, 2, 3, 5, 6 PASS; item 4 (ordered cursor replay) PASS via `after_sequence=0` replay matching the durable sequence | reconnect-suppression (`after_sequence=<last>`) was not separately re-run |
| **D-02** owner controls + decision input | ACCEPT-WITH-FINDINGS | item 4 PASS (10 durable `SUCCEEDED` `war-room-preview` requests matching the state machine) and item 5 PASS (`ai_calls` = 0) | item 1 (full lifecycle live) is covered by the durable 2026-09-23 sequence — a **loopback** session — and cannot be re-exercised while the seeded room is terminal `STOPPED` |
| **D-03** agenda / findings / decisions + usage | ACCEPT-WITH-FINDINGS | items 2, 3, 4 PASS (usage figure equals `sum(usage_events.normalized_cost)`; agenda/findings/decisions match the database) | item 1 (browser render over the authenticated remote path) needs Cloudflare Access; only the served HTML + the snapshot JSON the UI consumes were evidenced |

- Consequence recorded for the Owner: Increment C is now **16 / 16 = 100%**. Per the Owner's decisions the progress gates are
  cancelled, and the **one large audit is due at project close, before this project is put into real use** (Owner definition
  2026-09-26: "ตอนปิดโปรเจ็คนี้ก่อนจะนำไปใช้งานจริง") — **not** at an internal track reaching 100%. So this acceptance does
  **not** trigger an audit and no paid Independent Auditor is called now; the retired per-gate process stays retired.
- No code, migration, schema, grant or RLS change was made to reach this acceptance; no production system was touched.
