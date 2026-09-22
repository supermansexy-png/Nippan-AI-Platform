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
- For the V1 **internal pilot**, prevention of `SECRET_CREDENTIAL` persistence is an **application-level pre-persistence classification/redaction policy**. Increment B does not propose a database content scanner. This is an explicitly accepted temporary pilot risk.
- Before War Room is enabled outside the internal pilot, pre-persistence classification/redaction enforcement for `SECRET_CREDENTIAL` content is mandatory and must be verified before storage is allowed.
- The **30-day retention period is a policy target only**, measured from `project_rooms.closed_at`. It is not an automatic TTL, database expiry, or current deletion guarantee.
- Until a retention worker is implemented, message bodies **may persist longer than 30 days**.
- Structured meeting artifacts, findings, decisions and action items may outlive message bodies.
- A future retention worker may redact `content_text` while preserving row identity, ordering, evidence references and request correlation.
- Runtime and Control Plane keep **no UPDATE/DELETE privilege** on `project_room_messages`. A future retention/redaction worker must use a **separate maintenance/retention role** with narrowly scoped privileges only for retention work, such as updating `content_text` and `content_redacted_at` on eligible rows.
- The maintenance/retention role is **not created in Increment B**. Its exact grants, RLS behavior and worker implementation require separate review before use.
- Each retention/redaction action should emit a corresponding append-only `audit_events` record through the maintenance workflow.
- No binary payloads are stored in these tables.

There is no automatic TTL/database expiry in Increment B. The future retention worker uses `project_rooms.closed_at` as the TTL anchor when determining whether a message body has passed the 30-day policy target.

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
- `audit_baseline_ref text` — nullable outside `AUDIT_REVIEW`; repository/PR/issue reference when present
- `audit_baseline_sha text` — nullable outside `AUDIT_REVIEW`; exactly 40 lowercase hexadecimal characters when present
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `started_at timestamptz`
- `closed_at timestamptz`

Constraints:

- named parent scope key: `project_rooms_scope_uniq UNIQUE (tenant_id, application_id, room_id)`
- exact application FK: child `(tenant_id, application_id)` -> `public.applications (tenant_id, application_id)`, backed by the existing parent `UNIQUE (tenant_id, application_id)`
- if `cost_budget` is non-null, `cost_currency` is non-null
- if state is `CLOSED` or `STOPPED`, `closed_at` is non-null
- if state is active, `closed_at` is null
- `started_at <= closed_at` when both are present
- an `AUDIT_REVIEW` room cannot enter `READY` without both `audit_baseline_ref` and `audit_baseline_sha`

Indexes:

- `(tenant_id, application_id, state, updated_at desc)`
- `(tenant_id, application_id, project_key, created_at desc)`

### 4.2 `public.project_room_participants`

Columns:

- `participant_id uuid primary key default extensions.gen_random_uuid()`
- `tenant_id uuid not null`
- `application_id uuid not null`
- `room_id uuid not null`
- `principal_type text not null` — canonical principal class: `HUMAN | AGENT | SYSTEM`
- `principal_id text not null` — stable canonical identifier within `principal_type`; 1..255 chars
- `agent_id uuid` — AGENT-specific reference only; it is **not** the separation-of-duties identity
- `participant_type text not null` — `HUMAN | AGENT | SYSTEM`
- `role text not null` — `OWNER | CHAIR | ARCHITECT | BUILDER | SECURITY_REVIEWER | COST_OPS_REVIEWER | INDEPENDENT_AUDITOR | SECRETARY`
- `display_name text not null` — 1..120 chars
- `model_policy_ref text` — reference only; not a model ID authority
- `active boolean not null default true`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Canonical identity rules:

- `principal_type + principal_id` is the authoritative principal identity for separation-of-duties across HUMAN, AGENT and SYSTEM participants.
- In V1, `principal_type` must equal `participant_type`.
- For `AGENT`, `agent_id` is required and provides the existing Agent/config relationship; `principal_id` remains the canonical identity used by the Builder/Auditor invariant.
- For non-`AGENT`, `agent_id` must be null.
- `principal_id` must be non-empty after trimming.

Constraints:

- named parent scope key: `project_room_participants_scope_uniq UNIQUE (tenant_id, application_id, room_id, participant_id)`
- duplicate identity/role guard: `UNIQUE (tenant_id, application_id, room_id, principal_type, principal_id, role)`
- exact room FK: child `(tenant_id, application_id, room_id)` -> `public.project_rooms (tenant_id, application_id, room_id)`, backed by `project_rooms_scope_uniq`
- exact agent FK: child `(tenant_id, application_id, agent_id)` -> `public.agents (tenant_id, application_id, agent_id)`, backed by the existing parent `UNIQUE (tenant_id, application_id, agent_id)`
- `AGENT` requires `agent_id is not null`
- non-`AGENT` requires `agent_id is null`
- one active `OWNER` per room via partial unique index
- one active `CHAIR` per room via partial unique index

Authoritative Builder/Auditor independence:

`app_private.validate_project_room_participant_independence()` is a DB trigger function executed `BEFORE INSERT OR UPDATE OF principal_type, principal_id, role, active, room_id, tenant_id, application_id` on `project_room_participants`.

When the incoming row is active and has role `BUILDER` or `INDEPENDENT_AUDITOR`, it rejects the write if another active row in the same `tenant_id + application_id + room_id` has the same `principal_type + principal_id` and the opposite role. This invariant applies equally to HUMAN, AGENT and SYSTEM principals. `agent_id` is not used as the authoritative separation-of-duties identity.

Authoritative `AUDIT_REVIEW` readiness:

- `app_private.assert_project_room_audit_readiness(tenant_id, application_id, room_id)` is a DB validation function.
- A `BEFORE UPDATE OF state` trigger on `project_rooms` calls it whenever an `AUDIT_REVIEW` room transitions into `READY`.
- The function requires **exactly one** active participant with role `INDEPENDENT_AUDITOR` in the same tenant/application/room.
- The function also verifies that no active principal is simultaneously represented as both `BUILDER` and `INDEPENDENT_AUDITOR`, using `principal_type + principal_id`.
- Participant INSERT/UPDATE operations that would invalidate an already READY-or-active `AUDIT_REVIEW` room call the same readiness assertion and reject the change. This prevents a valid READY room from being made invalid afterward.
- Service-layer validation may mirror these checks for user feedback, but **the database is authoritative**.

Indexes:

- `(tenant_id, application_id, room_id, active, role)`
- `(tenant_id, application_id, room_id, principal_type, principal_id)`
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

- named parent scope key: `project_room_agenda_items_scope_uniq UNIQUE (tenant_id, application_id, room_id, agenda_item_id)`
- unique `(tenant_id, application_id, room_id, sequence)`
- exact room FK: child `(tenant_id, application_id, room_id)` -> `public.project_rooms (tenant_id, application_id, room_id)`, backed by `project_rooms_scope_uniq`
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
- exact room FK: child `(tenant_id, application_id, room_id)` -> `public.project_rooms (tenant_id, application_id, room_id)`, backed by `project_rooms_scope_uniq`
- exact agenda FK: child `(tenant_id, application_id, room_id, agenda_item_id)` -> `public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)`, backed by `project_room_agenda_items_scope_uniq`
- exact participant FK: child `(tenant_id, application_id, room_id, participant_id)` -> `public.project_room_participants (tenant_id, application_id, room_id, participant_id)`, backed by `project_room_participants_scope_uniq`; nullable `participant_id` is allowed for system events
- exact request FK: child `(tenant_id, application_id, request_id)` -> `public.requests (tenant_id, application_id, request_id)`, backed by the existing parent `UNIQUE (tenant_id, application_id, request_id)`
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

- exact room FK: child `(tenant_id, application_id, room_id)` -> `public.project_rooms (tenant_id, application_id, room_id)`, backed by `project_rooms_scope_uniq`
- exact agenda FK: child `(tenant_id, application_id, room_id, agenda_item_id)` -> `public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)`, backed by `project_room_agenda_items_scope_uniq`
- exact raised-by participant FK: child `(tenant_id, application_id, room_id, raised_by_participant_id)` -> `public.project_room_participants (tenant_id, application_id, room_id, participant_id)`, backed by `project_room_participants_scope_uniq`
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
- `decision_type text not null` — `PROPOSAL | OWNER_DECISION | ADVISORY_AUDIT_OUTCOME`
- `proposed_by_participant_id uuid`
- `owner_principal_id text`
- `decision text not null` — 1..4000 chars
- `rationale text` — max 8000 chars
- `evidence_refs jsonb not null default '[]'::jsonb` — array of repository/request/content references
- `status text not null default 'PROPOSED'` — `PROPOSED | ACCEPTED | REJECTED | SUPERSEDED`
- `created_at timestamptz not null default now()`
- `decided_at timestamptz`

Constraints:

- exact room FK: child `(tenant_id, application_id, room_id)` -> `public.project_rooms (tenant_id, application_id, room_id)`, backed by `project_rooms_scope_uniq`
- exact agenda FK: child `(tenant_id, application_id, room_id, agenda_item_id)` -> `public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)`, backed by `project_room_agenda_items_scope_uniq`
- exact proposed-by participant FK: child `(tenant_id, application_id, room_id, proposed_by_participant_id)` -> `public.project_room_participants (tenant_id, application_id, room_id, participant_id)`, backed by `project_room_participants_scope_uniq`; nullable proposer remains allowed
- accepted/rejected requires owner principal and decided_at
- PROPOSED requires decided_at null
- an accepted/rejected `OWNER_DECISION` requires `owner_principal_id` to resolve to the active HUMAN participant with role `OWNER`; a Builder, Auditor or other AI participant cannot be the owner approver
- `ADVISORY_AUDIT_OUTCOME` requires `project_rooms.mode = AUDIT_REVIEW`, exactly one configured active Independent Auditor, `proposed_by_participant_id` referencing that Auditor, non-empty `evidence_refs`, and a non-null room `audit_baseline_sha`
- `ADVISORY_AUDIT_OUTCOME` requires status `PROPOSED` or `SUPERSEDED`, is never a formal audit report, and cannot set `owner_principal_id` or an accepted/rejected owner status
- `evidence_refs` must be a JSON array; references are metadata/pointers, not an instruction to store raw secrets or full sensitive payloads

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

- exact room FK: child `(tenant_id, application_id, room_id)` -> `public.project_rooms (tenant_id, application_id, room_id)`, backed by `project_rooms_scope_uniq`
- exact agenda FK: child `(tenant_id, application_id, room_id, agenda_item_id)` -> `public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)`, backed by `project_room_agenda_items_scope_uniq`
- DONE/CANCELLED requires completed_at

Index:

- `(tenant_id, application_id, room_id, status, created_at)`

### 4.8 Exact composite FK matrix

Every relationship below preserves the application-owned scope. **No War Room FK may reference only `room_id`, `agenda_item_id`, `participant_id`, or another entity id without the required `tenant_id + application_id` scope columns.**

| Child table / relationship | Child FK columns | Parent table / referenced columns | Parent key that makes reference valid |
|---|---|---|---|
| `project_rooms -> applications` | `(tenant_id, application_id)` | `applications (tenant_id, application_id)` | existing `UNIQUE (tenant_id, application_id)` |
| `project_room_participants -> project_rooms` | `(tenant_id, application_id, room_id)` | `project_rooms (tenant_id, application_id, room_id)` | `project_rooms_scope_uniq` |
| `project_room_participants -> agents` | `(tenant_id, application_id, agent_id)` | `agents (tenant_id, application_id, agent_id)` | existing `UNIQUE (tenant_id, application_id, agent_id)` |
| `project_room_agenda_items -> project_rooms` | `(tenant_id, application_id, room_id)` | `project_rooms (tenant_id, application_id, room_id)` | `project_rooms_scope_uniq` |
| `project_room_messages -> project_rooms` | `(tenant_id, application_id, room_id)` | `project_rooms (tenant_id, application_id, room_id)` | `project_rooms_scope_uniq` |
| `project_room_messages -> project_room_agenda_items` | `(tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items_scope_uniq` |
| `project_room_messages -> project_room_participants` | `(tenant_id, application_id, room_id, participant_id)` | `project_room_participants (tenant_id, application_id, room_id, participant_id)` | `project_room_participants_scope_uniq` |
| `project_room_messages -> requests` | `(tenant_id, application_id, request_id)` | `requests (tenant_id, application_id, request_id)` | existing `UNIQUE (tenant_id, application_id, request_id)` |
| `project_room_findings -> project_rooms` | `(tenant_id, application_id, room_id)` | `project_rooms (tenant_id, application_id, room_id)` | `project_rooms_scope_uniq` |
| `project_room_findings -> project_room_agenda_items` | `(tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items_scope_uniq` |
| `project_room_findings -> project_room_participants` | `(tenant_id, application_id, room_id, raised_by_participant_id)` | `project_room_participants (tenant_id, application_id, room_id, participant_id)` | `project_room_participants_scope_uniq` |
| `project_room_decisions -> project_rooms` | `(tenant_id, application_id, room_id)` | `project_rooms (tenant_id, application_id, room_id)` | `project_rooms_scope_uniq` |
| `project_room_decisions -> project_room_agenda_items` | `(tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items_scope_uniq` |
| `project_room_decisions -> project_room_participants` | `(tenant_id, application_id, room_id, proposed_by_participant_id)` | `project_room_participants (tenant_id, application_id, room_id, participant_id)` | `project_room_participants_scope_uniq` |
| `project_room_action_items -> project_rooms` | `(tenant_id, application_id, room_id)` | `project_rooms (tenant_id, application_id, room_id)` | `project_rooms_scope_uniq` |
| `project_room_action_items -> project_room_agenda_items` | `(tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id)` | `project_room_agenda_items_scope_uniq` |

The implementation migration, if later authorized, must use these exact scoped relationships or a stricter equivalent. Any relaxation to an entity-id-only FK requires a new design review.

### 4.9 Canonical mapping and prototype boundary

The seven authoritative War Room domain tables map to the proposal vocabulary as follows:

| Authoritative table | Domain group | Ownership rule |
|---|---|---|
| `project_rooms` | rooms / meetings | tenant + application scoped root |
| `project_room_participants` | participants | child of the scoped room |
| `project_room_agenda_items` | agenda items | child of the scoped room |
| `project_room_messages` | messages / transcript events | child of room, agenda and optional participant |
| `project_room_findings` | findings | child of room, agenda and raising participant |
| `project_room_decisions` | decisions / advisory outcomes | child of room and agenda |
| `project_room_action_items` | action items | child of room and agenda |

The four-table `apps/war-room/migrations/0001_war_room_sandbox.sql` prototype (`war_rooms`, `war_room_participants`, `war_room_messages`, `war_room_usage_events`) is not an alternate baseline. It is quarantined design output and must not be used to derive the Increment B migration, RLS policies, grants or permanent application interfaces.

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

### 5.1 Role context and behavior

Database roles are not inferred from a browser participant role. A participant marked `INDEPENDENT_AUDITOR` is an application/domain identity; it does not receive a database bypass role.

| Role | Tenant/application context | Allowed behavior | Explicit prohibition |
|---|---|---|---|
| `nippan_runtime` | Must set transaction-local `app.tenant_id` and `app.application_id`; missing either fails closed | Runtime reads and only the table mutations listed in the privilege matrix | No RLS bypass, participant configuration mutation, message/decision update or delete |
| `nippan_control_plane` | Trusted control-plane request context must set both scope keys | Room configuration, participant/agenda administration and owner decision operations within scope | No cross-scope access, message/decision update or delete, or formal audit approval |
| Configured Auditor principal | Uses the same runtime/control-plane database role as the executing service; identity is checked in domain constraints | May propose an advisory outcome only when Audit Review readiness requirements pass | No `BYPASSRLS`, no sole approval, no replacement of the formal repository audit |
| `nippan_analytics` | Read context must set both scope keys | Read-only scoped reporting | No INSERT, UPDATE, DELETE or state-changing function |
| Migration/admin role | Break-glass/deployment identity only; not available to application requests | Applies an independently authorized migration and verifies ACL/RLS state | Not granted to runtime, control plane, auditor or analytics; no use before the Audit #28 gate releases implementation |

All project roles are `NOLOGIN`, non-owner and non-`BYPASSRLS` group roles. `service_role`, `anon` and `authenticated` are not War Room runtime roles. `EXECUTE` on helper functions is revoked from `PUBLIC`; only the narrowly specified project roles or trigger owner may execute a function, and no helper function may widen row visibility or permissions.

## 6. Proposed privilege matrix

This is a design target for Independent Audit; no grants are applied yet.

| Table | Runtime SELECT | Runtime INSERT | Runtime UPDATE | Runtime DELETE | Control SELECT | Control INSERT | Control UPDATE | Control DELETE | Analytics SELECT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `project_rooms` | yes | yes | yes | no | yes | yes | yes | no | yes |
| `project_room_participants` | yes | no | no | no | yes | yes | yes | no | yes |
| `project_room_agenda_items` | yes | yes | yes | no | yes | yes | yes | no | yes |
| `project_room_messages` | yes | yes | no | no | yes | yes | no | no | yes |
| `project_room_findings` | yes | yes | yes | no | yes | yes | yes | no | yes |
| `project_room_decisions` | yes | yes | no | no | yes | yes | no | no | yes |
| `project_room_action_items` | yes | yes | yes | no | yes | yes | yes | no | yes |

Rationale:
- participants are Control Plane configuration, not runtime self-configuration.
- messages/decisions are append-only at the table privilege boundary.
- no project role receives DELETE.
- message redaction must be a separately audited controlled operation; V1 runtime and Control Plane receive no UPDATE/DELETE on messages.
- any future retention/redaction worker uses a separate maintenance/retention role with narrowly scoped column updates only for `content_text` / `content_redacted_at`, and emits `audit_events`; this role is not created in Increment B.

Function `EXECUTE` matrix:

| Function class | Runtime | Control Plane | Analytics | Migration/admin | PUBLIC |
|---|---:|---:|---:|---:|---:|
| `app_private.current_tenant_id()` / `current_application_id()` | yes | yes | yes | yes | no |
| RLS/read-only validation helpers | only where required by policy | only where required by policy | no | yes for verification only | no |
| participant independence trigger function | trigger-only | trigger-only | no | yes for verification only | no |
| Audit Review readiness trigger/function | trigger-only | no direct execution | no | yes for verification only | no |
| migration/admin helpers | no | no | no | explicit reviewed grant only | no |

`trigger-only` means the application role does not receive a callable state-changing function privilege; PostgreSQL invokes it through the owning trigger. Function ownership, `SECURITY DEFINER` use, and fixed `search_path` must be specified and reviewed in the future migration PR rather than assumed here.

## 7. State and integrity enforcement

Database should enforce only invariants that remain true regardless of service implementation.

Required DB-side protections:

1. tenant/application composite FKs on every relationship.
2. RLS tenant + application fail-closed policies.
3. no DELETE grant to project roles.
4. message/decision append-only role privileges.
5. V1 round_limit 1..2.
6. budget values non-negative/positive as applicable.
7. the same canonical principal `(principal_type, principal_id)` cannot be both active `BUILDER` and active `INDEPENDENT_AUDITOR` in one room.
8. `AUDIT_REVIEW` transition into `READY` is DB-authoritative: a room-state trigger calls `app_private.assert_project_room_audit_readiness(...)`, requiring exactly one active Independent Auditor and a valid Builder/Auditor separation-of-duties state.
9. participant writes must not be allowed to invalidate the same readiness invariant while an Audit Review room is READY or active.
10. room state timestamps remain coherent.

The full orchestration state machine stays in deterministic application code from Increment A. Database triggers should not duplicate the scheduler; the readiness and separation-of-duties triggers exist only to enforce security/integrity invariants that must remain authoritative at the database boundary.

### 7.1 Audit Review readiness minimum

Before an `ADVISORY_AUDIT_OUTCOME` can be created, the service and database readiness validator must require:

1. `project_rooms.mode = AUDIT_REVIEW` and the room is in an eligible active/summary state.
2. Exactly one active participant has role `INDEPENDENT_AUDITOR`; the canonical principal is not the active `BUILDER` principal.
3. `audit_baseline_ref` and a valid 40-character lowercase `audit_baseline_sha` identify the reviewed baseline.
4. At least one evidence reference exists through `evidence_refs` or an `EVIDENCE_REFERENCE` message with `evidence_kind` and `content_reference`; references must be privacy-approved.
5. Every finding has an explicit status and evidence references. Unresolved findings are allowed only when their unresolved state is explicitly included in the advisory artifact; they are not silently treated as resolved.
6. Decision state is explicit: proposals, owner decisions, rejected decisions and unresolved owner decisions are distinguishable. An advisory outcome cannot imply owner acceptance.
7. The outcome-producing execution has a platform `request_id` and trace correlation once runtime execution exists; the model output alone is not sufficient evidence.

Enforcement is layered: application validation provides feedback, the database readiness trigger protects the room/participant/baseline invariants, and the formal Independent Audit process remains the authority for a formal audit report. No War Room decision row or message may be interpreted as `PASS`, `FAIL` or a replacement audit report merely because its `decision_type` is `ADVISORY_AUDIT_OUTCOME`.

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

### 8.1 Telemetry ownership contract

- Every automatic War Room turn creates or references one platform `request_id`; `trace_id`, `span_id`, attempt and causal links follow the frozen request/trace contract.
- The model execution writes its provider/model/token/latency/result metadata to the existing `ai_calls` record and its immutable normalized accounting to the existing `usage_events` ledger.
- Operational/security events use existing append-only `audit_events`; War Room domain rows may store a correlation/reference, not a second audit ledger.
- War Room tables may keep local domain metadata such as `room_id`, `agenda_item_id`, `participant_id`, sequence, round, evidence references and budget snapshot/warning state. They must not become authoritative for provider cost, token accounting, trace identity or audit history.
- A provider retry creates a new `ai_calls` attempt while preserving the logical `request_id`/trace relationship; replay/dedupe must not create a second successful usage event for the same provider event.

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
12. Audit Review DB trigger rejects a READY transition unless exactly one active Independent Auditor exists.
13. Builder/Auditor separation tests cover canonical `principal_type + principal_id` identity for HUMAN, AGENT and SYSTEM principals, and reject the same principal holding both active roles in one room.
14. participant mutation after READY cannot invalidate the exactly-one-auditor or Builder/Auditor independence invariant.
15. room/agenda round limit >2 rejected.
16. duplicate room message sequence rejected.
17. message request reference cannot cross tenant/application.
18. War Room does not add alternative cost/token truth columns.
19. negative control: grant an intentionally forbidden War Room privilege in ephemeral CI and prove the privilege suite fails.
20. a non-auditor cannot insert an `ADVISORY_AUDIT_OUTCOME`.
21. an Independent Auditor cannot create an advisory outcome in `FREE_DISCUSSION` or `FORMAL_MEETING` mode.
22. an Audit Review cannot become ready without auditor identity, baseline/reference SHA, evidence references and explicit findings/decision state.
23. the same canonical principal cannot hold active `BUILDER` and `INDEPENDENT_AUDITOR` roles.
24. a missing or malformed baseline SHA rejects Audit Review readiness.
25. `PUBLIC`, `anon`, `authenticated` and analytics cannot execute state-changing helpers or migration/admin helpers.
26. an advisory outcome cannot create or mutate a formal `docs/audits/` report record.

Tests must run in PostgreSQL 17 ephemeral CI and must not use production credentials/data.

## 10. Migration rollout plan after explicit audit authorization

Audit #28 currently returned `PASS_WITH_FINDINGS`, but **migration creation remains NOT_AUTHORIZED**. The steps below begin only after the Independent Auditor re-reviews F-28-01 through F-28-06 and explicitly authorizes migration creation.

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

## 13. Audit #28 Remediation

Audited design head: `7ec9d3f0329c39e595d2cd3b47909eee487d71f1`  
Audit #28 initial verdict: `PASS_WITH_FINDINGS`  
Migration creation: `NOT_AUTHORIZED`

Remediation mapping:

- **F-28-01 — Composite FK completeness:** Sections 4.1–4.7 now spell out exact scoped child FK columns, referenced parent columns and the parent UNIQUE/constraint. Section 4.8 provides the complete relationship matrix and explicitly forbids entity-id-only War Room FKs.
- **F-28-02 — Redaction vs append-only:** Sections 3 and 6 preserve no UPDATE/DELETE for runtime/control-plane messages. A future retention worker must use a separate narrowly scoped maintenance/retention role, not created in Increment B, and should emit `audit_events` for redaction.
- **F-28-03 — Builder/Auditor independence:** Section 4.2 introduces non-null canonical `principal_type + principal_id` identity for HUMAN/AGENT/SYSTEM participants, keeps `agent_id` AGENT-specific, adds identity/role uniqueness, and changes the DB invariant to canonical-principal separation-of-duties.
- **F-28-04 — Independent Auditor readiness:** Sections 4.2 and 7 make the database authoritative through `app_private.assert_project_room_audit_readiness(...)` plus room-state/participant triggers. `AUDIT_REVIEW` cannot enter `READY` without exactly one active Independent Auditor and valid Builder/Auditor independence.
- **F-28-05 — SECRET_CREDENTIAL:** Section 3 explicitly defines this as application-level pre-persistence classification/redaction for the internal pilot, records the temporary pilot risk, and requires enforced classification/redaction before non-internal-pilot use. No DB content scanner is introduced.
- **F-28-06 — Retention wording:** Section 3 defines 30 days as a policy target only, states message bodies may remain longer until a worker exists, uses `project_rooms.closed_at` as the future TTL anchor, and explicitly states that Increment B provides no automatic TTL/database expiry.

No migration, Supabase application, implementation code, RLS policy shape, accepted privilege boundary, telemetry source-of-truth, negative-control plan, rollback strategy, or production boundary was changed by this remediation.

## 14. Gate

Current gate:

**AUDIT_28_REMEDIATION_READY_FOR_REVIEW**

Migration creation/application remains **BLOCKED / NOT_AUTHORIZED** until the Independent Auditor re-reviews F-28-01 through F-28-06 and explicitly releases the gate.
