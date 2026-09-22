# Migrations

Migration artifacts will be versioned here.

Existing production systems must be migrated incrementally with explicit rollback paths. No big-bang migration.

Phase 2 starts from `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md`.

Phase 2 executable migrations use the Supabase timestamp convention.

`20260922174011_phase2_core_foundation.sql` implements the identity, ownership, Agent/Channel binding, config/policy versioning, activation invariants and tenant RLS baseline. Follow-up migrations keep advisor findings explicit. Telemetry, usage, audit and memory migrations follow after this foundation is verified.

Apply migrations through the connected Supabase project and keep checked-in SQL identical to the applied migration. Runtime access uses the non-owner, non-`BYPASSRLS` group roles described in `docs/decisions/ADR-0007-supabase-schema-baseline.md`.

