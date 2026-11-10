# Tasks

Board rules: `docs/warroom/TASK_CONTROL.md`. Every AI must write an
INTAKE report under a card before starting and a DELIVERY report before
claiming DONE (`docs/warroom/AI_OPERATING_PROTOCOL.md`). Build order:
`docs/warroom/STARTUP_PLAYBOOK.md`.

## READY

### T-001 — Choose and set up hosting for self-hosted n8n + PostgreSQL
Status: READY
Owner: —
Role: Developer
Risk: L2
Goal: a running n8n instance and database with backups, reachable over HTTPS
Done when: n8n login works; database reachable from n8n; daily backup confirmed restorable once
Budget: 1 working day
Links: docs/warroom/STARTUP_PLAYBOOK.md Step 0

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

## IN_PROGRESS

### T-005 — Prototype internal Colab Compute Console (branch-only)
Status: IN_PROGRESS
Owner: GPT-5.6 Sol — 2026-11-10
Role: Developer
Risk: L2
Goal: a branch-only internal MVP that controls a Colab runtime, loads a model sourced from Google Drive, and provides a test chat without touching protected production systems
Done when: runtime status and GPU are visible; a model source can be selected from Google Drive; Start/Load exposes reconnect/loading/ready states; test chat works against the loaded model; Hermes/Ollama/NAS extension points are documented; test evidence is captured
Budget: 1 working session for prototype + verification; stop if a runnable test environment is unavailable
Links: PROJECT_STATE.md, ROADMAP.md, docs/warroom/STARTUP_PLAYBOOK.md, docs/product/MODEL_POLICY.md
Scope: experimental internal developer tool only; no production deployment, no merge to main, no protected-document changes

INTAKE — T-005 — GPT-5.6 Sol — 2026-11-10
Understanding: build the smallest internal Compute Console on its own branch, not a Phase A customer-facing control plane.
Done when: satisfy every check in the card with runnable evidence before any DONE claim.
Needs: isolated branch, GitHub write access, runnable checkout/test environment, Colab auth/runtime access, and a Drive-hosted test model.
Missing: runnable checkout/test environment; MODEL_ROSTER is absent from main; Colab credentials/runtime are not exposed through this GitHub connector.
Plan: create/claim branch and card; implement only where testable; run checks after each step; hand L2 result to a different Auditor/owner.
Estimate/Risks: one working session; risks are Phase A scope creep, unverified Colab API behavior, and producing code that cannot be executed here.
Decision: ACCEPT WITH LIMITS — branch/task setup now; implementation verification is blocked until a runnable environment is available; owner already approved the branch/task route.

## REVIEW

(none)

## DONE

(none)
