# Data Architecture

Foundation v1 contracts:

- `IDENTITY_TENANCY_CONTRACT_V1.md` — Tenant/Application/Agent/Channel/Subject/Conversation ownership and isolation
- `AGENT_POLICY_CONTRACT_V1.md` — versioned Agent configuration and policy precedence
- `REQUEST_TRACE_USAGE_CONTRACT_V1.md` — request correlation, tracing, usage, cost and Dashboard observability

Machine-readable contracts live under `/schemas`.

## Current gate

These contracts are in REVIEW.

Do not implement production PostgreSQL DDL until the identity and policy contracts receive independent review and blocking issues are resolved.

The future PostgreSQL design will define:
- source-of-truth ownership
- schemas/tables
- pgvector use
- tenant RLS
- retention/deletion
- idempotency
- usage/audit
- migrations
- backup/restore
