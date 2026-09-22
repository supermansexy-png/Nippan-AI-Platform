# Migrations

Migration artifacts are versioned here.

Existing production systems must be migrated incrementally with explicit rollback paths. No big-bang migration.

Phase 2 executable migrations use the Supabase timestamp convention.

Applied to Supabase `nippan-ai-platform`:

- `20260922174011_phase2_core_foundation.sql`
- `20260922174227_phase2_core_fk_indexes.sql`
- `20260922180029_phase2_request_trace_telemetry.sql`
- `20260922180107_phase2_idempotency_usage_audit.sql`

Pending independent remediation review before application:

- `20260922193829_phase2_a001_least_privilege.sql` — Audit #18 Finding A-001; replaces broad runtime/control-plane table mutation grants with explicit least-privilege role boundaries.

The first migration establishes identity, ownership, Agent/Channel binding, config/policy versioning, activation invariants and tenant RLS. The follow-up index migration addresses FK advisor findings. The telemetry migration adds request/span/model/tool/retrieval operational truth. The idempotency/usage/audit migration adds persistent side-effect dedupe, an immutable UsageEvent ledger and append-only audit events.

The A-001 remediation migration is intentionally additive instead of rewriting an already-applied migration. It revokes current project-role table privileges and re-grants an explicit matrix: runtime can mutate conversation/runtime telemetry/idempotency and append usage/audit records; control plane owns identity/configuration mutation plus governed idempotency/audit writes; analytics remains read-only. Existing RLS policies are unchanged and all project roles remain non-`BYPASSRLS`.

Apply DDL through the connected Supabase project and keep checked-in SQL aligned with applied migration history. Runtime access uses the non-owner, non-`BYPASSRLS` roles described in `docs/decisions/ADR-0007-supabase-schema-baseline.md`.

Memory/embedding DDL remains deferred until benchmark fixtures choose an embedding model and vector dimension.
