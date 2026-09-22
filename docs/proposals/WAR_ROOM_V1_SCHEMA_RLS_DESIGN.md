# War Room V1 — PostgreSQL Schema and Tenant-Isolation Design

Status: DESIGN FOR INDEPENDENT AUDIT — NOT AUTHORIZED FOR MIGRATION/APPLICATION
Date: 2026-09-23
Parent: #19
Increment: B / #21
Baseline: `bdde03e580e166ca43beb5f248024ffe269000f6`

## 1. Scope and hard boundary

This document converts the accepted War Room logical model into an exact PostgreSQL/RLS design.

It does **not** authorize:
- creation of a migration file,
- application to Supabase,
- production data changes,
- OpenRouter/model calls,
- realtime/UI work,
- write/destructive tool execution.

The design must receive the project's immediate Independent Audit for a major PostgreSQL/schema/RLS change before implementation proceeds.

## 2. Design principles

1. Every War Room row is tenant scoped.
2. Application-scoped rows use composite foreign keys so cross-tenant/application references fail at the database boundary.
3. Missing `app.tenant_id` fails closed under RLS.
4. Runtime owns mutable room execution state; Control Plane may create/configure rooms and record owner decisions.
5. Analytics is read-only.
6. War Room does not duplicate `requests`, traces, AI/tool telemetry, usage cost truth, or `audit_events`.
7. Model identity/config remains sourced from existing Agent/config records.
8. Room membership never implies tool permission.
9. Full chat content is retained in PostgreSQL only for the V1 internal pilot, subject to bounded retention; large artifacts/evidence use references.
10. Formal audit reports remain repository artifacts under `docs/audits/`; a War Room finding is not a formal audit verdict.

## 3. Retention/content decision

V1 decision:

- `project_room_messages.content_text`: allowed for internal pilot chat text up to 32 KiB per message.
- `content_reference`: optional external/durable reference for large evidence or documents.
- At least one of `content_text` or `content_reference` must be present for user/agent content messages.
- Secrets and `SECRET_CREDENTIAL` content are prohibited from message storage by application policy before persistence.
- Default room retention: 30 days after room closure for message bodies.
- Structured meeting artifacts, findings, decisions and action items may outlive message bodies.
- A later retention worker may redact `content_text` while preserving row identity, ordering, evidence references and request correlation.
- No binary payloads are stored in these tables.

The 30-day value is a V1 policy default, not a database TTL mechanism. Automatic deletion/redaction is outside Increment B migration scope.

## 4. Exact table design

### 4.1 `public.project_rooms`

Columns:

- `room_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `project_key text not null` — 1..120 chars
- `title text not null` — 1..255 chars
- `mode text not null` — `FREE_DISCUSSION | FORMAL_MEETING | AUDIT_REVIEW`
- `state text not null default 'DRAFT'` — `DRAFT | READY | RUNNING | PAUSED | NEEDS_OWNER_DECISION | SUMMARIZING | CLOSED | STOPPED`
- `created_by_principal_id text not null` — 1..255 chars
- `automatic_round_limit smallint not null default 2` — 1..2
- `max_automatic_participants smallint not null default 5` — 1..5
- `token_budget bigint not null` — > 0
- `cost_budget numeric` — null or >= 0
- `cost_currency text` — null or ISO-style `^[A-Z]{3}$`
- `retention_days integer not null default 30` — 1..3650
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `started_at timestamptz`
- `closed_at timestamptz`

Constraints:

- unique `(tenant_id, application_id, room_id)`
- FK `(tenant_id, application_id) -> applications`
- if `cost_budget` is non-null, `cost_currency` is non-null
- if state is `CLOSED` or `STOPPED`, `closed_at` is non-null
- if state is active, `closed_at` is null
- `started_at <= closed_at` when both are present

Indexes:

- `(tenant_id, application_id, state, updated_at desc)`
- `(tenant_id, application_id, project_key, created_at desc)`

### 4.2 `public.project_room_participants`

Columns:

- `participant_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `agent_id uuid` — required only for `AGENT`
- `participant_type text not null` — `HUMAN | AGENT | SYSTEM`
- `role text not null` — `OWNER | CHAIR | ARCHITECT | BUILDER | SECURITY_REVIEWER | COST_OPS_REVIEWER | INDEPENDENT_AUDITOR | SECRETARY`
- `display_name text not null` — 1..120 chars
- `model_policy_ref text` — reference only; not a model ID authority
- `active boolean not null default true`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Constraints:

- unique `(tenant_id, application_id, room_id, participant_id)`
- FK room scope -> `project_rooms`
- FK agent scope -> `agents`
- `AGENT` requires `agent_id is not null`
- non-`AGENT` requires `agent_id is null`
- one active `OWNER` per room via partial unique index
- one active `CHAIR` per room via partial unique index
- one active `INDEPENDENT_AUDITOR` per `AUDIT_REVIEW` room is enforced by room-readiness validation, because a partial unique index alone cannot require presence.
- no active Builder and Independent Auditor may share the same `agent_id` in the same room.

Database invariant proposal:

`app_private.validate_project_room_participant_independence()` checks inserts/updates involving `BUILDER` or `INDEPENDENT_AUDITOR` and rejects a same-room role conflict on the same `agent_id`.

A separate readiness validator checks that an `AUDIT_REVIEW` room has exactly one active Independent Auditor before transition to `READY`.

Indexes:

- `(tenant_id, application_id, room_id, active, role)`
- `(tenant_id, application_id, agent_id)` where `agent_id is not null`

### 4.3 `public.project_room_agenda_items`

Columns:

- `agenda_item_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `sequence integer not null` — > 0
- `title text not null` — 1..255 chars
- `objective text not null` — 1..4000 chars
- `status text not null default 'OPEN'` — `OPEN | RUNNING | NEEDS_OWNER_DECISION | COMPLETE | CANCELLED`
- `round_limit smallint not null default 2` — 1..2
- `token_budget bigint not null` — > 0
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `completed_at timestamptz`

Constraints:

- unique `(tenant_id, application_id, room_id, agenda_item_id)`
- unique `(tenant_id, application_id, room_id, sequence)`
- FK room scope -> `project_rooms`
- completed/cancelled requires `completed_at`; other states require null

Index:

- `(tenant_id, application_id, room_id, sequence)`

### 4.4 `public.project_room_messages`

Columns:

- `message_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `agenda_item_id uuid not null`
- `participant_id uuid` — nullable for system events
- `request_id uuid` — required for any AI-generated turn once execution is implemented
- `message_type text not null`
- `evidence_kind text`
- `round_number smallint` — null for owner/system messages, otherwise 1..2
- `sequence bigint not null` — monotonic within room
- `content_text text`
- `content_reference text`
- `content_redacted_at timestamptz`
- `created_at timestamptz not null default now()`

Allowed `message_type` values:
`OWNER_MESSAGE, AGENT_MESSAGE, CHAIR_PROMPT, CHAIR_SYNTHESIS, EVIDENCE_REQUEST, EVIDENCE_REFERENCE, FINDING, DECISION_PROPOSAL, OWNER_DECISION, ACTION_ITEM, SYSTEM_EVENT, BUDGET_WARNING, ERROR`.

Allowed `evidence_kind` values when present:
`VERIFIED_EVIDENCE, PROVIDED_CLAIM, INFERENCE, OPINION, UNKNOWN`.

Constraints:

- unique `(tenant_id, application_id, room_id, message_id)`
- unique `(tenant_id, application_id, room_id, sequence)`
- FK room scope -> `project_rooms`
- FK agenda scope -> `project_room_agenda_items`
- FK participant scope -> `project_room_participants`
- FK request scope -> `requests (tenant_id, application_id, request_id)`
- `round_number` null or 1..2
- content body/reference rule:
  - normal content messages require non-empty `content_text` or `content_reference`
  - redacted historical messages may have both null only when `content_redacted_at is not null`
- `length(content_text) <= 32768`
- an `AGENT_MESSAGE` or `CHAIR_SYNTHESIS` produced by automatic execution must have `request_id`; this is enforced by application/service contract because legacy/import/manual artifacts may not have an execution request.

Indexes:

- `(tenant_id, application_id, room_id, sequence)`
- `(tenant_id, application_id, agenda_item_id, sequence)`
- `(tenant_id, application_id, request_id)` where request_id is not null
- `(tenant_id, application_id, participant_id, created_at)` where participant_id is not null

No token/cost columns are stored here. Actual model usage/cost remains in `ai_calls` and `usage_events`, correlated through `request_id`.

### 4.5 `public.project_room_findings`

Columns:

- `finding_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `agenda_item_id uuid not null`
- `raised_by_participant_id uuid not null`
- `severity text not null` — `BLOCKER | HIGH | MEDIUM | LOW | NOTE`
- `status text not null default 'OPEN'` — `OPEN | ACKNOWLEDGED | RESOLVED | DISMISSED`
- `summary text not null` — 1..4000 chars
- `evidence_refs jsonb not null default '[]'::jsonb` — array only
- `created_at timestamptz not null default now()`
- `resolved_at timestamptz`

Constraints:

- scoped FKs to room, agenda and participant
- `evidence_refs` must be JSON array
- resolved/dismissed requires `resolved_at`

Important:
A row in this table is a War Room discussion finding. It does not satisfy or replace `AUDIT_SYSTEM_V1.md` formal audit records.

### 4.6 `public.project_room_decisions`

Columns:

- `decision_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `agenda_item_id uuid not null`
- `decision_type text not null` — `PROPOSAL | OWNER_DECISION`
- `proposed_by_participant_id uuid`
- `owner_principal_id text`
- `decision text not null` — 1..4000 chars
- `rationale text` — max 8000 chars
- `status text not null default 'PROPOSED'` — `PROPOSED | ACCEPTED | REJECTED | SUPERSEDED`
- `created_at timestamptz not null default now()`
- `decided_at timestamptz`

Constraints:

- scoped FKs to room/agenda/participant
- accepted/rejected requires owner principal and decided_at
- PROPOSED requires decided_at null

Owner decision events should additionally emit an append-only `audit_events` row through the future service layer; this table is the domain record, while `audit_events` is the operational audit trail.

### 4.7 `public.project_room_action_items`

Columns:

- `action_item_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `agenda_item_id uuid not null`
- `title text not null` — 1..500 chars
- `owner_principal_id text`
- `status text not null default 'OPEN'` — `OPEN | IN_PROGRESS | DONE | CANCELLED`
- `linked_issue_or_pr text`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `completed_at timestamptz`

Constraints:

- scoped FKs to room/agenda
- DONE/CANCELLED requires completed_at

Index:

- `(tenant_id, application_id, room_id, status, created_at)`

## 5. RLS design

All seven tables enable RLS.

Common runtime/control-plane tenant policy shape:

```sql
using (
  tenant_id = (select app_private.current_tenant_id())
  and application_id = (select app_private.current_application_id())
)
with check (
  tenant_id = (select app_private.current_tenant_id())
  and application_id = (select app_private.current_application_id())
)
```

Analytics read policy uses the same tenant + application predicate for SELECT.

Reason for application scoping:
War Room is a Control Plane application feature and every room is application-owned. Using both session keys reduces accidental cross-application access inside one tenant.

Missing either tenant or application context therefore returns zero rows.

## 6. Proposed privilege matrix

This is a design target for Independent Audit; no grants are applied yet.

| Table | Runtime SELECT | Runtime INSERT | Runtime UPDATE | Runtime DELETE | Control SELECT | Control INSERT | Control UPDATE | Control DELETE | Analytics |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| project_rooms | yes | yes | yes | no | yes | yes | yes | no | SELECT only |
| project_room_participants | yes | no | no | no | yes | yes | yes | no | SELECT only |
| project_room_agenda_items | yes | yes | yes | no | yes | yes | yes | no | SELECT only |
| project_room_messages | yes | yes | no | no | yes | yes | no | no | SELECT only |
| project_room_findings | yes | yes | yes | no | yes | yes | yes | no | SELECT only |
| project_room_decisions | yes | yes | no | no | yes | yes | no | no | SELECT only |
| project_room_action_items | yes | yes | yes | no | yes | yes | yes | no | SELECT only |

Rationale:
- participants are Control Plane configuration, not runtime self-configuration.
- messages/decisions are append-only at the table privilege boundary.
- no project role receives DELETE.
- message redaction must be a separately audited controlled operation if later required; V1 runtime does not receive UPDATE solely to implement retention.

## 7. State and integrity enforcement

Database should enforce only invariants that remain true regardless of service implementation.

Required DB-side protections:

1. tenant/application composite FKs on every relationship.
2. RLS tenant + application fail-closed policies.
3. no DELETE grant to project roles.
4. message/decision append-only role privileges.
5. V1 round_limit 1..2.
6. budget values non-negative/positive as applicable.
7. independent-auditor agent identity cannot equal Builder agent identity in one room.
8. Audit Review readiness requires exactly one active Independent Auditor.
9. room state timestamps remain coherent.

The full orchestration state machine stays in deterministic application code from Increment A. Database triggers should not duplicate the scheduler.

## 8. Existing platform records reused

War Room does not create replacements for:

- `requests` — every future automatic AI turn gets its own request.
- `trace_spans` / `trace_span_links` — execution topology.
- `ai_calls` — provider/model/token/cost telemetry.
- `tool_calls` — tool execution evidence.
- `retrieval_events` — evidence retrieval diagnostics.
- `usage_events` — immutable usage/cost source of truth.
- `audit_events` — append-only operational/control-plane audit trail.
- `agent_config_versions` / `agent_activations` — model/config authority.

War Room rows hold domain state plus references only.

## 9. Isolation/invariant test plan

A future migration PR must add a dedicated SQL suite and extend the existing global table guards.

Required tests:

1. RLS enabled on all seven War Room tables.
2. Runtime with tenant A/application A sees only A/A rows.
3. Same tenant but different application is invisible.
4. Different tenant is invisible.
5. missing tenant context sees zero rows.
6. missing application context sees zero rows.
7. cross-tenant/application FK insertion fails.
8. runtime cannot mutate participant configuration.
9. runtime cannot UPDATE/DELETE messages or decisions.
10. analytics cannot INSERT/UPDATE/DELETE.
11. all project roles remain non-superuser/non-BYPASSRLS.
12. Audit Review rejects missing Independent Auditor at READY transition.
13. Audit Review rejects Builder/Auditor sharing one `agent_id`.
14. room/agenda round limit >2 rejected.
15. duplicate room message sequence rejected.
16. message request reference cannot cross tenant/application.
17. War Room does not add alternative cost/token truth columns.
18. negative control: grant an intentionally forbidden War Room privilege in ephemeral CI and prove the privilege suite fails.

Tests must run in PostgreSQL 17 ephemeral CI and must not use production credentials/data.

## 10. Migration rollout plan after audit PASS

Only after Independent Audit approval:

1. create additive migration on a new reviewed branch.
2. create seven tables, indexes, constraints and helper validators.
3. revoke public/anon/authenticated/service_role direct access.
4. grant exact project-role matrix.
5. enable RLS and create tenant+application policies.
6. extend `phase2_privilege_boundaries.sql`.
7. add `war_room_isolation_invariants.sql`.
8. run PostgreSQL 17 CI including a negative control.
9. require independent GitHub approval.
10. merge.
11. apply controlled Supabase migration.
12. post-deploy verify ACL/RLS/BYPASSRLS and Security Advisor.

## 11. Rollback plan

Before any production room data exists:
- rollback may drop the seven War Room tables in reverse FK order plus War Room-specific helper functions/policies/indexes.

After any room data exists:
- do **not** destructive-drop as routine rollback.
- disable War Room application entrypoints.
- revoke runtime mutation grants first.
- preserve tables for forensic/export access.
- perform corrective forward migration.
- destructive removal requires explicit owner decision and separate backup/export evidence.

Rollback order for pre-data development only:

1. `project_room_action_items`
2. `project_room_decisions`
3. `project_room_findings`
4. `project_room_messages`
5. `project_room_agenda_items`
6. `project_room_participants`
7. `project_rooms`
8. War Room-only validation helper functions

## 12. Independent Audit questions

Auditor must explicitly answer:

1. Does tenant + application RLS fail closed?
2. Can any composite FK permit cross-scope references?
3. Is the role privilege split least-privilege and compatible with A-001?
4. Are append-only message/decision semantics sufficient for V1?
5. Does the schema accidentally duplicate usage/cost/audit truth?
6. Is Builder/Auditor independence enforceable with the proposed validator?
7. Is the retention/content strategy acceptable for the internal pilot?
8. Is the rollback strategy safe before and after data exists?
9. Are any fields missing that would force an unsafe schema change during Increment C?
10. Is it safe to authorize creation of the actual migration and isolation suite?

## 13. Gate

Current gate:

**DESIGN_READY_FOR_INDEPENDENT_AUDIT**

Migration/application remains **BLOCKED** until the Independent Auditor returns PASS or PASS_WITH_FINDINGS with no blocking schema/RLS finding.
