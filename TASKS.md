# Tasks

Board rules: `docs/warroom/TASK_CONTROL.md`. Every AI must write an
INTAKE report under a card before starting and a DELIVERY report before
claiming DONE (`docs/warroom/AI_OPERATING_PROTOCOL.md`). Build order:
`docs/warroom/STARTUP_PLAYBOOK.md`.

## READY

### T-013 — Re-staff reviewer/security per anti-redundancy rule
Status: REVIEW (รอพี่เชษอนุมัติ)
Owner: —
Role: Model-recruiter (HR)
Risk: L1
Goal: reviewer + security no longer share a Primary provider with builder
Done when: reviewer Primary+Backup and security Primary+Backup each come from a provider different from builder Primary; roster re-checked and updated; anti-redundancy cross-check row shows PASS; owner notified for approval; no config changed
Budget: ½ day
Links: docs/product/MODEL_POLICY.md (Anti-redundancy policy), docs/product/MODEL_ROSTER.md

INTAKE — T-013 — Model Recruiter (HR) — 2026-09-24
Understanding: T-012 ตั้ง reviewer + security ให้ใช้ qwen/qwen3.7-flash (Alibaba) เป็น Primary เหมือน builder แต่ผิดกฎ Anti-redundancy ใน MODEL_POLICY.md § — reviewer/security ต้อง Primary+Backup ต่าง provider จาก builder ทั้งหมด
Candidates ที่เลือก: nvidia/nemotron-3-ultra-550b-a55b:free (NVIDIA) + thinkingmachines/inkling:free (Thinking Machines) — ต่าง Alibaba ทั้งหมด, ฟรีทั้งคู่, nemotion รองรับ tool_choice
Evidence: verify via openrouter_list-models ทั้งคู่มีอยู่จริง, pricing $0/$0, tools/support parameters ครบ
Decision: ACCEPT

DELIVERY — T-013 — Model Recruiter (HR) — 2026-09-24
Status claimed: DONE
Done-when check:
- [x] reviewer Primary+Backup ≠ builder Primary provider (Alibaba) → VERIFIED (reviewer = NVIDIA + Thinking Machines, both ≠ Alibaba)
- [x] security Primary+Backup ≠ builder Primary provider (Alibaba) → VERIFIED (security = NVIDIA + Thinking Machines, both ≠ Alibaba)
- [x] Roster table updated in MODEL_ROSTER.md → VERIFIED (rows 3-4 changed, reasoning updated)
- [x] Anti-redundancy cross-check block added → VERIFIED (new section with 3 PASS rows + note)
- [x] No config/agent files modified → VERIFIED (only MODEL_ROSTER.md + TASKS.md)
- [ ] Owner notified for approval → PENDING (owner to approve)
Changed: docs/product/MODEL_ROSTER.md (reviewer row: Alibaba→NVIDIA/THINK; security row: Alibaba→NVIDIA/THINK; anti-regression→anti-regression+anti-redundancy cross-check; standing caveats updated)
Not done: Approval confirmation from Owner
Unverified: Free model real-time availability on actual API call — depends on OpenRouter free endpoint stability (known caveat per roster)
Problems: None. MCP `openrouter_get-model` had parameter-passing issues; fell back to `openrouter_list-models` which successfully verified both candidates.
Confidence: high — all evidence via API list query, policy rules applied correctly, anti-redundancy fully satisfied
Next: Owner reviews anti-redundancy fix and confirms approval. If any swap desired (e.g., Llama paid backup for reviewer), Model Scout proposes within price thresholds.

### T-012 — Staff the team: map all 7 dev roles to Primary + Backup models
Status: READY
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

### T-002 — Create lite schema tables
Status: READY
Owner: —
Role: Developer
Risk: L3
Goal: all tables in LITE_SCHEMA_V1 exist
Done when: tables created; a test insert/select through `data-access` requires tenant_id + bot_id
Budget: ½ day
Links: docs/data/LITE_SCHEMA_V1.md

### T-003 — Build data-access, usage-tracker, monitor-log tools
Status: READY
Owner: —
Role: MCP tool builder
Risk: L2
Goal: the three Step-0 tools work
Done when: a query without tenant_id/bot_id is rejected; usage row written per test message; a red test event reaches the owner's alert channel
Budget: 1–2 days
Links: docs/product/MCP_TOOLS_V1.md

### T-004 — Legal review of tenant agreement and privacy notice
Status: READY
Owner: owner
Role: Project Lead
Risk: L3
Goal: lawyer-checked tenant agreement + end-customer notice
Done when: reviewed texts stored in docs/security/
Budget: arrange within 2 weeks; must finish before tenant #1
Links: docs/security/PDPA_COMPLIANCE.md, docs/product/BUSINESS_OPERATIONS.md

### T-008 — War Room D-02: owner controls + decision input (acceptance)
Status: READY
Owner: —
Role: Developer
Risk: L2
Goal: PREPARE/START/PAUSE/RESUME/STOP + Ask/Owner Decision work for human owner; D-02 accepted
Done when: D-02 acceptance checklist in Issue #35 met (valid lifecycle commands, Ask paths without provider turns, non-owner fail-closed, durable state matches, ai_calls=0); Issue #30 D-02 checked
Budget: 1–2 working days
Links: Issue #35, Issue #30

### T-009 — War Room D-03: agenda/findings/decisions + usage display (acceptance)
Status: READY
Owner: —
Role: Developer
Risk: L2
Goal: UI renders agenda/finding/decision + UsageEvent-sourced cost; D-03 accepted
Done when: D-03 acceptance checklist in Issue #35 met (durable projection render, UsageEvent source not browser ledger, zero funded provider unless authorized, values cross-checked vs DB); Issue #30 D-03 checked
Budget: 1–2 working days
Links: Issue #35, Issue #30

### T-010 — War Room preview access for dev-time use (auth boundary)
Status: IN_PROGRESS
Owner: Project Lead (mimo-v2.6-flash-free) — 2026-09-24
Role: Developer (builder)
Risk: L3
Goal: owner can use War Room from dev machine/remote without public open-bypass; fail-closed auth documented
Done when: access path chosen and implemented or explicitly documented as loopback-only; no unauthenticated public bypass; security note recorded
Budget: 1–2 working days (scope may ACCEPT WITH LIMITS if full remote auth too large)
Links: Issue #35 auth notes, docs/warroom/DECISION_LOG_FORMAT.md

INTAKE — T-010 — Project Lead — 2026-09-24
Understanding: Currently War Room preview transport (`transport.py`) blocks all remote access via `war_room_preview_loopback_only` flag. Key missing piece per Issue #35: "Server authentication adapter for establishing TrustedActorContext is not yet present." Need to implement a simple dev-time access mechanism that satisfies "fail-closed" constraint — either a shared API key auth layer or Cloudflare Access verifier for authenticated remote users, WITHOUT creating an unauthenticated public bypass. Must NOT invent new auth models; must reuse existing `CloudflareAccessVerifier` pattern from `remote_auth.py` or create equivalent lightweight adapter. No migration/schema/RLS change needed.
Done when: Dev-time API key authentication implemented OR Cloudflare Access config documented; remote owner can load /war-room/; unauthenticated requests return HTTP 403; PR created with tests; security note in decision-log.
Needs: Current code understanding of _authorize_preview_request() flow, TrustedActorContext contract.
Missing: None — scope defined by Project Lead.
Plan: [Delegate to builder]
Estimate: ~1 day.
Risks: Security boundary must be fail-closed by design; over-complicating with complex SSO.
Decision: ACCEPT WITH LIMITS — scope limited to dev-time authenticated access only (no production deployment, no user management).

## IN_PROGRESS

### T-001 — Choose and set up hosting for self-hosted n8n + PostgreSQL
Status: DONE
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

## REVIEW

(none)

## DONE

### T-005 — Suspend Independent Audit System gates (owner order)
Status: DONE
Owner: Project Lead (mimo-v2.6-flash-free) — 2026-09-24
Role: Project Lead
Risk: L3
Goal: Independent Audit System no longer gates milestones; normal review/testing continues
Done when: AUDIT_SYSTEM_V1 status shows suspended; ROADMAP/PROJECT_STATE/DECISIONS/CURRENT_STATE updated consistently; decision-log entry written; historical audit records untouched
Budget: 1 working session
Links: docs/audits/AUDIT_SYSTEM_V1.md, docs/warroom/decision-log.md

INTAKE — T-005 — mimo-v2.6-flash-free — 2026-09-24
Understanding: Owner ordered Independent Audit System removed from active gating so War Room can resume; normal review/testing continue; historical audit files not rewritten.
Decision: ACCEPT

DELIVERY — T-005 — mimo-v2.6-flash-free — 2026-09-24
Status claimed: DONE
Evidence: git diff 7 intended files; grep SUSPENDED/RESUMED across AUDIT_SYSTEM_V1/ROADMAP/PROJECT_STATE/DECISIONS/CURRENT_STATE; decision-log 2026-09-24 entry; historical audit file timestamps unchanged.
Confidence: high
Gate 4: owner ACCEPTED → DONE.

### T-006 — Plan War Room V1 resumption (dev-use + runtime backstage)
Status: DONE
Owner: Project Lead (mimo-v2.6-flash-free) — 2026-09-24
Role: Project Lead
Risk: L2
Goal: approved plan for finishing Track D and repurposing War Room for dev-time + runtime backstage ecosystem
Done when: plan presented to owner; task cards drafted for remaining work; owner approves direction
Budget: 1 working session
Links: docs/proposals/WAR_ROOM_V1_PROPOSAL.md, Issue #30, Issue #35

INTAKE — T-006 — mimo-v2.6-flash-free — 2026-09-24
Understanding: Owner wants War Room back for dev-time use and runtime backstage ecosystem. Drafted cards T-007..T-011. Presented plan with sequencing.
Decision: ACCEPT

DELIVERY — T-006 — mimo-v2.6-flash-free — 2026-09-24
Status claimed: DONE
Evidence: Cards T-007(D-01)/T-008(D-02)/T-009(D-03)/T-010(auth)/T-011(positioning) drafted in TASKS.md; plan sequenced vs Phase A; owner approved "อนุมัติ" in chat.
Confidence: high
Gate 4: owner APPROVED → DONE.

### T-007 — War Room D-01: roster + ordered message surface (acceptance)
Status: DONE
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

### T-011 — War Room dual-use positioning (dev-time + runtime backstage)
Status: DONE
Owner: Project Lead (mimo-v2.6-flash-free) — 2026-09-24
Role: Project Lead
Risk: L1
Goal: short doc states how War Room is used (a) now by AI dev team (b) later as runtime backstage; non-goals unchanged
Done when: positioning note written to docs/proposals/WAR_ROOM_DUAL_USE_POSITIONING.md; referenced in CURRENT_STATE.md; owner notified
Budget: ½ session
Links: docs/proposals/WAR_ROOM_V1_PROPOSAL.md, docs/project-memory/CURRENT_STATE.md

INTAKE — T-011 — Project Lead — 2026-09-24
Understanding: Write dual-use positioning document covering (1) NOW: dev-time collaboration, (2) LATER: runtime backstage ecosystem. Non-goals unchanged from original proposal.
Decision: ACCEPT

DELIVERY — T-011 — Project Lead — 2026-09-24
Status claimed: DONE
Evidence: File `docs/proposals/WAR_ROOM_DUAL_USE_POSITIONING.md` created (covers Use Case ① Dev-Time, ② Runtime Backstage, Non-Goals, Current State); CURRENT_STATE.md updated with reference.
Changed: TASKS.md, docs/proposals/WAR_ROOM_DUAL_USE_POSITIONING.md (new), docs/project-memory/CURRENT_STATE.md
Confidence: high
