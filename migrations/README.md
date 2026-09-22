# Migrations

Migration artifacts will be versioned here.

Existing production systems must be migrated incrementally with explicit rollback paths. No big-bang migration.

Phase 2 starts from `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md`.

No executable PostgreSQL DDL should be added until the logical schema/RLS design is reviewed against the frozen Phase 1 contracts.
