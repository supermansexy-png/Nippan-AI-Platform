# War Room Increment B Implementation Evidence

Status: **IMPLEMENTATION COMMITTED / APPLICATION NOT AUTHORIZED**

## Scope

- Implementation branch: `war-room/increment-b-schema-implementation`
- Audited design base: `72932d76c03e36ce209357f581282526ccf4a9ac`
- Migration: `migrations/20260923010000_war_room_increment_b_schema.sql`
- Migration blob SHA: `d41a08f86f2206f345c6e3eea823ef8a80885a1b`
- Test suite: `tests/sql/war_room_increment_b_invariants.sql`
- Prototype migration: absent from this branch and not used

This evidence describes a migration implementation and disposable-test design. It does not authorize Supabase application, database deployment, preview deployment or production deployment.

## Objects

The migration creates exactly seven War Room domain tables:

1. `project_rooms`
2. `project_room_participants`
3. `project_room_agenda_items`
4. `project_room_messages`
5. `project_room_findings`
6. `project_room_decisions`
7. `project_room_action_items`

All tenant-owned rows carry `tenant_id` and `application_id`. All War Room relationships use scoped composite foreign keys. Existing platform `requests` is referenced by `(tenant_id, application_id, request_id)`; trace and model telemetry remain owned by existing platform tables and are correlated through `request_id`.

## Functions and triggers

- `app_private.validate_project_room_participant_independence()`
- `app_private.assert_project_room_audit_readiness(uuid, uuid, uuid)`
- `app_private.validate_project_room_participant_readiness()`
- `app_private.validate_project_room_state_readiness()`
- `app_private.validate_project_room_decision()`

All are `SECURITY INVOKER`, use `SET search_path = ''`, and have `PUBLIC`, `anon` and `authenticated` EXECUTE revoked. Trigger-only functions are not exposed as application mutation APIs.

The migration does not use `SECURITY DEFINER`.

## RLS and grants

- RLS is enabled on all seven tables.
- The policy scope requires both `app.tenant_id` and `app.application_id`.
- Missing either context returns no rows and fails write checks.
- `FORCE ROW LEVEL SECURITY` is not used because the existing convention keeps the schema/migration owner separate from non-owner, non-BYPASSRLS project roles; this must be rechecked in the migration audit.
- Runtime, Control Plane and Analytics grants follow the audited matrix.
- No project role receives DELETE.
- Runtime cannot mutate participant configuration.
- Runtime and Control Plane cannot UPDATE/DELETE messages or decisions.
- Analytics is read-only.
- `service_role`, `anon` and `authenticated` receive no War Room access.

## Test suite

Run after applying all migrations to disposable PostgreSQL 17:

```text
psql -v ON_ERROR_STOP=1 -f tests/sql/war_room_increment_b_invariants.sql
```

The suite includes positive controls and negative controls for tenant/application isolation, missing context, scoped FK rejection, readiness, Builder/Auditor separation, advisory outcome rules, append-only privilege boundaries, role safety and helper EXECUTE exposure.

Static inventory before PostgreSQL execution: 41 expected-failure assertion markers and 11 positive-control markers. These are not reported as passed tests until PostgreSQL executes the suite.

This environment did not have `docker` or `psql`, so the suite was not executed locally in this contribution. The SQL was checked into the branch for ephemeral CI/local PostgreSQL execution; a passing result must be recorded by the Independent Auditor workflow before application authorization.

## Retention boundary

No automatic 30-day TTL or retention worker is created. Future redaction requires a separately reviewed maintenance role, narrowly scoped content updates, idempotent retry behavior and an append-only `audit_events` record for each redaction.

## Limitations requiring audit review

- PostgreSQL execution was not available on the current workstation.
- Migration apply/reapply, rollback/forward-fix and full ACL/RLS behavior remain unverified until disposable PostgreSQL CI runs.
- No Supabase or production credentials were used.
- Implementation commit and migration checksum must be filled after commit in the final handoff.
