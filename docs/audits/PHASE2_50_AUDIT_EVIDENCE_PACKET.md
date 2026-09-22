# Phase 2 — 50% Catch-up Audit Evidence Packet

Status: READY FOR INDEPENDENT AUDIT
Date: 2026-09-23
Audit tracking: Issue #18
Target PR: #17
Branch: `phase2/postgres-logical-schema`

## Purpose

This packet is an index of repository evidence for the mandatory Phase 2 catch-up 50% Independent Audit.

It is not an audit result and must not be treated as PASS, PASS_WITH_FINDINGS or BLOCKED.

The independent Auditor must verify the referenced evidence directly.

## Progress baseline

Roadmap baseline:
- total currently enumerated Phase 2 deliverables: 19
- recorded complete: 11
- recorded pending: 8
- equal-weight progress: 57.9%
- highest crossed mandatory gate: 50%

The Audit System was introduced after Phase 2 had already crossed 50%, therefore a catch-up 50% audit is required before normal milestone advancement.

## Governance evidence

- `docs/audits/AUDIT_SYSTEM_V1.md`
- `docs/audits/AUDIT_REPORT_TEMPLATE.md`
- `AGENTS.md`
- `.ai/project.yaml`
- `ROADMAP.md`
- `PROJECT_STATE.md`

Auditor must verify:
- Builder cannot self-approve.
- BLOCKER findings halt milestone advancement.
- BLOCKER remediation requires independent re-audit.
- 100% gate must PASS before milestone DONE.
- Primary Independent Auditor is configured through project governance rather than application runtime code.

## Architecture / frozen-contract evidence

Architecture:
- `docs/architecture/FOUNDATION_V1.md`
- `docs/decisions/ADR-0001-runtime-topology.md`
- `docs/decisions/ADR-0002-control-plane-and-multitenancy.md`
- `docs/decisions/ADR-0003-model-routing.md`
- `docs/decisions/ADR-0004-data-memory-retrieval.md`
- `docs/decisions/ADR-0005-policy-tools-and-approval.md`
- `docs/decisions/ADR-0006-infrastructure-simplicity.md`
- `docs/decisions/ADR-0007-supabase-schema-baseline.md`

Frozen Phase 1 contracts:
- `docs/data/IDENTITY_TENANCY_CONTRACT_V1.md`
- `docs/data/AGENT_POLICY_CONTRACT_V1.md`
- `docs/data/REQUEST_TRACE_USAGE_CONTRACT_V1.md`
- `schemas/platform-identity-v1.schema.json`
- `schemas/agent-config-v1.schema.json`
- `schemas/request-envelope-v1.schema.json`
- `schemas/usage-event-v1.schema.json`
- `docs/reviews/PHASE1_REVIEW_GATE_FINAL.md`

Logical schema:
- `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md`

Auditor must compare executable migrations and Core code against these sources rather than accepting implementation summaries.

## Executable PostgreSQL evidence

Migrations in PR #17:
- `migrations/20260922174011_phase2_core_foundation.sql`
- `migrations/20260922174227_phase2_core_fk_indexes.sql`
- `migrations/20260922180029_phase2_request_trace_telemetry.sql`
- `migrations/20260922180107_phase2_idempotency_usage_audit.sql`

Claims requiring independent verification:
- identity/config baseline exists
- request/trace telemetry exists
- W3C-compatible trace/span identifier constraints exist
- AI/tool/retrieval telemetry exists
- persistent idempotency records exist
- UsageEvent ledger is deduplicated and append-only
- audit events are append-only
- tenant-owned tables have tenant-scoped RLS
- direct `anon`, `authenticated` and `service_role` table grants are revoked
- runtime/control-plane/analytics roles are tenant-scoped and non-`BYPASSRLS`
- cross-tenant/application/agent/config references are constrained where claimed

Auditor should specifically inspect:
- role ownership and privilege assumptions
- fail-closed behavior when `app.tenant_id` is missing
- composite foreign keys and scope consistency
- update/delete permissions versus trigger guards
- idempotency state transitions
- immutable published configuration behavior
- UsageEvent dedupe scope
- audit event mutation protection
- any path that could bypass RLS or deterministic authorization assumptions

## SQL verification evidence

Repeatable suite:
- `tests/sql/phase2_isolation_invariants.sql`
- `tests/README.md`

Recorded limitation:
- the full role-level suite has NOT been executed through the connected Supabase SQL API session because that principal cannot `SET ROLE nippan_runtime`
- the suite is intended for a CI/test database principal with role-impersonation permission

Recorded builder verification claims in PROJECT_STATE / PR:
- Supabase security advisor: no findings
- performance advisor: expected unused-index notices only on the empty database
- rollback checks passed for:
  - conversation request scope
  - all-zero trace ID rejection
  - UsageEvent dedupe
  - UsageEvent append-only behavior
  - idempotency reservation uniqueness

The Auditor must distinguish:
- evidence present in repository,
- external verification claims not reproducible from repository alone,
- and checks explicitly not yet executed.

Lack of execution of the known CI role-impersonation suite is a known pending Phase 2 deliverable and must not automatically be mislabeled as a defect; however any unsupported stronger isolation claim should be flagged.

## FastAPI Core evidence

Core package:
- `services/core/pyproject.toml`
- `services/core/README.md`
- `services/core/app/settings.py`
- `services/core/app/db.py`
- `services/core/app/config_repository.py`
- `services/core/app/main.py`
- `services/core/tests/test_health.py`

Recorded implemented scope:
- FastAPI package
- `/health`
- `/ready`
- async PostgreSQL connection pool
- transaction-local `app.tenant_id`
- optional transaction-local `app.application_id`
- optional transaction-local `app.request_id`
- active Agent config loader restricted to activation -> PUBLISHED config path
- initial health test

Explicitly not implemented yet:
- policy engine boundary
- request persistence/tracing service
- OpenRouter adapter interface
- deterministic context assembler interface
- MCP client/tool authorization interface
- synthetic end-to-end request
- production traffic

Auditor must not report these planned pending deliverables as defects merely because they are not yet implemented at the 50% gate.

## Security / protected-system boundary

Protected systems:
- `supermansexy-png/Ai-Nippan`
- existing production Personal Assistant / n8n workflows

Current phase does not authorize migration or rewrite of either system.

Auditor should verify PR #17 contains only Nippan-AI-Platform changes and no evidence of production cutover.

## Cost / complexity checks

Foundation requires:
- cost-efficient defaults
- minimal realtime path
- no infrastructure duplication without measured reason
- complexity only when justified by evidence

Explicitly deferred:
- Cloudflare AI Gateway
- Hyperdrive
- Durable Objects
- Analytics Engine
- Redis
- D1
- Vectorize
- Cloudflare Workflows
- dedicated vector database
- Kubernetes
- unnecessary microservices

Auditor should flag accidental adoption, duplicated capability or premature infrastructure.

## Documentation consistency checks

Compare:
- `README.md`
- `ROADMAP.md`
- `PROJECT_STATE.md`
- `.ai/project.yaml`
- `AGENTS.md`
- ADRs
- logical schema
- migrations
- Core README/code/tests

Look for:
- stale phase/status statements
- contradictions in ownership hierarchy
- unsupported verification claims
- a deliverable marked complete without acceptance evidence
- hidden scope changes
- model IDs incorrectly hard-coded into distributed runtime logic

## Required report output

Create a durable report under `docs/audits/` using `AUDIT_REPORT_TEMPLATE.md`.

Required fields:
- audit metadata
- progress calculation
- evidence inspected
- findings with severity
- outcome: PASS / PASS_WITH_FINDINGS / BLOCKED
- remediation
- re-audit requirement

A report is valid only if produced by an independent Auditor under `AUDIT_SYSTEM_V1.md`.

## Current audit execution status

Evidence packet: READY

Independent 50% Audit: PENDING

No PASS/PASS_WITH_FINDINGS/BLOCKED outcome has been claimed yet.
