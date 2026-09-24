# Tests

The platform requires contract, routing, memory isolation, idempotency, failure/fallback, privacy, migration compatibility and benchmark tests.

## Phase 2 SQL isolation suite

`sql/phase2_isolation_invariants.sql` is a transaction-wrapped, rollback-only suite that:

- creates two synthetic tenants/applications
- inserts representative rows across every current tenant-owned table
- impersonates `nippan_runtime`
- verifies Tenant A sees only Tenant A rows
- verifies missing tenant context fails closed
- verifies UsageEvent append-only behavior and dedupe
- verifies persistent idempotency uniqueness
- verifies request scope constraints
- verifies published config immutability
- rolls back all fixtures

Run it only with a CI/test database principal that is permitted to `SET ROLE nippan_runtime`. The Supabase SQL API session used during Phase 2 verification is intentionally not permitted to impersonate that role, so the checked-in suite is the reproducible role-level test path.
