# Data Architecture

Foundation v1 contracts:

- `IDENTITY_TENANCY_CONTRACT_V1.md` — Tenant/Application/Agent/Channel/Subject/Conversation ownership and isolation
- `AGENT_POLICY_CONTRACT_V1.md` — versioned Agent configuration and policy precedence
- `REQUEST_TRACE_USAGE_CONTRACT_V1.md` — request correlation, tracing, usage, cost and Dashboard observability

Machine-readable contracts live under `/schemas`.

## Current gate

These contracts are ACCEPTED / FROZEN V1.

Do not implement production PostgreSQL DDL until the logical schema/RLS design is reviewed against the frozen contracts.

Phase 2 PostgreSQL design:
- `POSTGRES_LOGICAL_SCHEMA_V1.md`

This design defines:
- source-of-truth ownership
- schemas/tables
- pgvector use
- tenant RLS
- retention/deletion
- idempotency
- usage/audit
- migrations
- backup/restore
