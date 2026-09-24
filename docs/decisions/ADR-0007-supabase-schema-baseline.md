# ADR-0007: Supabase Schema Baseline

Status: **ACCEPTED FOR PHASE 2 FOUNDATION**
Date: 2026-09-23

## Context

Phase 1 froze identity, tenancy, configuration, policy and telemetry contracts. Phase 2 needs an executable PostgreSQL baseline on the existing Supabase project `nippan-ai-platform`.

## Decisions

- Supabase migrations are the migration history authority and use `YYYYMMDDHHMMSS_description.sql` names.
- Lifecycle and environment values use `text` with explicit `CHECK` constraints in v1.
- IDs default to `extensions.gen_random_uuid()`; applications may supply UUIDv7 values.
- Config and policy JSON validation stays in application code and CI for v1. PostgreSQL verifies object shape and protects frozen versions from mutation.
- `nippan_runtime`, `nippan_control_plane` and `nippan_analytics` are `NOLOGIN`, non-owner, non-`BYPASSRLS` group roles.
- `service_role` is not a normal runtime database role because it can bypass RLS.
- Tables remain in `public` initially, but access by `anon`, `authenticated` and `service_role` is explicitly revoked.
- Embedding dimensions and vector indexing remain deferred until benchmarks choose a model.

## Consequences

- Runtime code must set `SET LOCAL app.tenant_id` inside every tenant-scoped transaction.
- Deployment work creates login identities separately and grants only the applicable group role.
- Future Data API exposure requires explicit grants and a review of matching RLS policies.

