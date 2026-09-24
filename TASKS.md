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

(none)

## REVIEW

(none)

## DONE

(none)
