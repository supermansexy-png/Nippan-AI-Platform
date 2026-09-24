# PostgreSQL + pgvector Logical Schema v1

Status: **DRAFT / PHASE 2 START**
Date: 2026-09-23

Depends on:
- `docs/data/IDENTITY_TENANCY_CONTRACT_V1.md`
- `docs/data/AGENT_POLICY_CONTRACT_V1.md`
- `docs/data/REQUEST_TRACE_USAGE_CONTRACT_V1.md`
- `docs/reviews/PHASE1_REVIEW_GATE_FINAL.md`

## Purpose

Translate the frozen Phase 1 contracts into a PostgreSQL logical schema and RLS design before writing executable migrations or runtime code.

This is the implementation handoff for reproducible SQL migrations, isolation tests, FastAPI Core data access, policy/config loading, request tracing and usage telemetry storage. It does not create production tables by itself.

## Scope

In scope:
- tenant/application ownership tables
- Agent activation and immutable config/policy version tables
- Channel, Subject and Conversation identity tables
- request/span/model/tool/retrieval telemetry tables
- immutable UsageEvent ledger
- persistent idempotency records
- audit event minimum
- pgvector memory/retrieval tables at logical level
- RLS execution model and testable isolation invariants

Out of scope:
- final pricing and invoice tables
- final dashboard UI
- production data migration from `supermansexy-png/Ai-Nippan`
- exact provider SDK integration
- exact retention durations
- exact control-plane RBAC beyond minimum operator identity references

## Design Principles

1. `tenant_id` is present on every tenant-owned operational table.
2. Application-owned records also carry `application_id`.
3. Tenant/Application consistency is enforced by database constraints, not application prose.
4. Runtime roles are non-owner roles with no `BYPASSRLS`.
5. Tenant context is set transaction-locally for each request and cannot leak across pooled connections.
6. RLS is defense in depth; application authorization and policy checks still run.
7. Published config and policy versions are immutable.
8. Usage events are append-only and deduplicated.
9. Side effects use atomic idempotency reservation.
10. Vector search always includes tenant and applicable application filters.

## Runtime Roles And Context

Minimum roles:
- migration owner role: owns schema and runs migrations only
- app runtime role: reads/writes tenant-protected runtime tables, does not own protected tables, no `BYPASSRLS`
- control-plane role: performs dashboard/config operations through application authorization, no superuser or `BYPASSRLS`
- read-only analytics role: restricted aggregate/reporting access where needed

Tenant context:
- runtime sets `app.tenant_id` with `SET LOCAL` inside a transaction
- application context may also set `app.application_id` for application-scoped operations
- request context may set `app.request_id` for audit defaults
- connection pool code must begin a transaction before tenant-scoped queries
- no tenant-scoped query should run when `current_setting('app.tenant_id', true)` is null

Recommended helpers:
- `current_tenant_id()` returns UUID from `current_setting('app.tenant_id', true)`
- optional `current_application_id()` returns UUID/null
- helper functions must not silently choose a tenant

RLS policy shape:
- tenant-owned tables filter `tenant_id = current_tenant_id()`
- application-owned tables additionally constrain `application_id` where the operation requires a specific application context
- platform-admin or cross-tenant operations require a separate audited path and are not part of normal runtime role access

`FORCE ROW LEVEL SECURITY` is required only where the selected ownership pattern would otherwise let a table owner bypass RLS. It is not a blanket requirement when runtime is a non-owner role.

## Core Ownership Tables

### tenants

Primary security, quota and future billing boundary.

Columns:
- `tenant_id` UUID primary key
- `slug` unique not null
- `display_name` not null
- `tenant_type` not null
- `status` not null
- `created_at` not null
- `updated_at` not null

Constraints:
- `slug` unique platform-wide
- status values match the identity contract lifecycle

### workspaces

Columns:
- `workspace_id` UUID primary key
- `tenant_id` not null references `tenants`
- `slug` not null
- `display_name` not null
- `status` not null
- `created_at` not null
- `updated_at` not null

Constraints:
- unique `(tenant_id, workspace_id)` for composite child FKs
- unique `(tenant_id, slug)`

### applications

Columns:
- `application_id` UUID primary key
- `tenant_id` not null
- `workspace_id` nullable
- `slug` not null
- `display_name` not null
- `application_type` not null
- `status` not null
- `environment_policy` JSONB not null default object
- `created_at` not null
- `updated_at` not null

Constraints:
- unique `(tenant_id, application_id)`
- unique `(tenant_id, slug)`
- `(tenant_id, workspace_id)` FK to `workspaces` when workspace is present

## Agent, Channel And Subject Tables

### agents

Columns:
- `agent_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `slug` not null
- `display_name` not null
- `role` not null
- `status` not null
- `created_at` not null
- `updated_at` not null

Constraints:
- unique `(tenant_id, application_id, agent_id)`
- unique `(tenant_id, application_id, slug)`
- composite FK `(tenant_id, application_id)` to `applications`

No active config pointer exists on this table.

### channels

Columns:
- `channel_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `channel_type` not null
- `display_name` not null
- `status` not null
- `external_ref` nullable
- `created_at` not null
- `updated_at` not null

Constraints:
- unique `(tenant_id, application_id, channel_id)`
- composite FK `(tenant_id, application_id)` to `applications`
- partial unique index on `(tenant_id, application_id, channel_type, external_ref)` where `external_ref is not null`

Secrets are stored as references outside this table, never as plaintext.

### agent_channel_bindings

Columns:
- `binding_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `agent_id` not null
- `channel_id` not null
- `environment` not null
- `routing_role` not null
- `priority` integer not null
- `enabled` boolean not null default true
- `created_at` not null
- `updated_at` not null

Constraints:
- composite FK `(tenant_id, application_id, agent_id)` to `agents`
- composite FK `(tenant_id, application_id, channel_id)` to `channels`
- partial unique index for one enabled default per `(tenant_id, application_id, channel_id, environment)` where `enabled` and `routing_role = 'default'`

### subjects

Columns:
- `subject_id` UUID primary key
- `tenant_id` not null
- `canonical_display_name` nullable
- `status` not null
- `created_at` not null
- `updated_at` not null

Constraints:
- unique `(tenant_id, subject_id)`

Subject is tenant-global. Application data access is not granted by `subject_id` alone.

### subject_identities

Columns:
- `subject_identity_id` UUID primary key
- `tenant_id` not null
- `subject_id` not null
- `channel_id` not null
- `provider` not null
- `external_subject_id` not null
- `verified_at` nullable
- `created_at` not null
- `updated_at` not null

Constraints:
- composite FK `(tenant_id, subject_id)` to `subjects`
- channel FK must preserve tenant scope
- unique `(tenant_id, channel_id, provider, external_subject_id)`

### conversations

Columns:
- `conversation_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `channel_id` not null
- `subject_id` nullable
- `primary_agent_id` nullable
- `external_thread_ref` nullable
- `parent_conversation_id` nullable
- `status` not null
- `started_at` not null
- `last_activity_at` not null
- `closed_at` nullable

Constraints:
- unique `(tenant_id, application_id, conversation_id)`
- composite FK `(tenant_id, application_id, channel_id)` to `channels`
- composite FK `(tenant_id, subject_id)` to `subjects` when subject is present
- composite FK `(tenant_id, application_id, primary_agent_id)` to `agents` when primary agent is present
- parent conversation remains in the same tenant/application

## Config And Policy Version Tables

### agent_config_versions

Columns:
- `config_version_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `agent_id` not null
- `version_number` integer not null
- `lifecycle_status` not null
- `environment` not null
- `config_document` JSONB not null
- `published_config_hash` nullable
- `policy_merge_version` not null
- `created_by` not null
- `created_at` not null
- `published_at` nullable
- `supersedes_version_id` nullable
- `change_note` not null

Constraints:
- composite FK `(tenant_id, application_id, agent_id)` to `agents`
- unique `(tenant_id, application_id, agent_id, environment, version_number)`
- `published_config_hash` is required for `PUBLISHED` and `SUPERSEDED`
- `published_at` is required for `PUBLISHED` and `SUPERSEDED`

Immutability:
- `PUBLISHED` and `SUPERSEDED` rows must not mutate semantically significant fields
- enforce with trigger logic in migrations and application-level publish flow

### policy_versions

Stores immutable versioned policy documents referenced by Agent Config.

Columns:
- `policy_version_id` UUID primary key
- `tenant_id` nullable for platform-shared policies
- `application_id` nullable
- `policy_type` not null
- `version_number` integer not null
- `lifecycle_status` not null
- `policy_document` JSONB not null
- `content_hash` not null
- `platform_shared` boolean not null default false
- `created_by` not null
- `created_at` not null
- `published_at` nullable
- `supersedes_policy_id` nullable

Constraints:
- tenant/application scope is required unless `platform_shared` is true
- published policy versions are immutable
- exact stable policy-family strategy remains a migration decision because v1 does not require a separate policy-family table

### agent_activations

Columns:
- `activation_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `agent_id` not null
- `environment` not null
- `config_version_id` not null
- `activated_at` not null
- `activated_by` not null

Constraints:
- unique `(tenant_id, application_id, agent_id, environment)`
- composite FK `(tenant_id, application_id, agent_id)` to `agents`
- FK to `agent_config_versions` enforces same tenant/application/agent/environment and published lifecycle

This table is the current pointer only. Activation history is stored in audit events.

## Request, Trace And Telemetry Tables

### requests

Columns:
- `request_id` UUID primary key
- `trace_id` text not null
- `tenant_id` not null
- `application_id` nullable
- `channel_id` nullable
- `agent_id` nullable
- `subject_id` nullable
- `conversation_id` nullable
- `environment` not null
- `request_kind` not null
- `source` not null
- `privacy_class` not null
- `current_status` not null
- `received_at` not null
- `completed_at` nullable
- `parent_request_id` nullable
- `idempotency_key` nullable

Constraints:
- trace ID format check: 32 lowercase hex, not all zero
- request-kind checks for required `application_id` and `channel_id`
- fake IDs are prevented by FKs when present
- model/tool execution paths require application attribution

### trace_spans

Columns:
- `span_row_id` UUID primary key
- `trace_id` not null
- `span_id` text not null
- `parent_span_id` nullable
- `request_id` not null
- `tenant_id` not null
- `span_type` not null
- `service` not null
- `operation` not null
- `started_at` not null
- `ended_at` nullable
- `duration_ms` nullable
- `status` not null
- `attempt` integer not null
- `error_code` nullable
- `metadata` JSONB not null default object

Constraints:
- unique `(trace_id, span_id)`
- span ID format check: 16 lowercase hex, not all zero
- FK `request_id` to `requests`

Trace links for async/causal relationships should use a separate `trace_span_links` table.

### ai_calls

Records model/provider calls with request/trace/span IDs, tenant/application/agent IDs, provider/model/purpose, timing, token counts, provider-reported cost, normalized cost, currency, success/error/fallback fields and structured-output flags.

Missing provider metrics remain null.

### tool_calls

Records MCP/tool calls with request/trace IDs, tenant/application/agent IDs, tool domain/name/version/operation, risk/privacy class, policy decision, approval reference, idempotency key, timing, attempt, success/error and approved fingerprints.

Do not store sensitive full arguments/results by default.

### retrieval_events

Records retrieval diagnostics without copying full retrieved content into logs: retrieval mode, query kind, candidate and selected counts, structured/keyword/vector hit counts, reranker and embedding metadata, context token estimate and latency.

## Idempotency And Usage

### idempotency_records

Columns:
- `idempotency_record_id` UUID primary key
- `tenant_id` not null
- `scope` not null
- `operation` not null
- `idempotency_key` not null
- `request_id` not null
- `state` not null
- `result_reference` nullable
- `request_fingerprint` nullable
- `created_at` not null
- `updated_at` not null
- `expires_at` not null

Constraints:
- unique `(tenant_id, scope, operation, idempotency_key)`
- state values: `IN_PROGRESS`, `SUCCEEDED`, `FAILED`, `EXPIRED`

Reservation is an atomic insert/upsert before side effect execution.

### usage_events

Columns:
- `usage_event_id` UUID primary key
- `occurred_at` not null
- `tenant_id` not null
- `application_id` not null
- `request_id` not null
- `agent_id` nullable
- `channel_id` nullable
- `subject_id` nullable
- `conversation_id` nullable
- `event_type` not null
- `quantity` numeric not null
- `unit` not null
- `dedupe_key` not null
- `source_type` not null
- `source_id` not null
- `provider` nullable
- `model` nullable
- `tool_domain` nullable
- `tool_name` nullable
- `provider_reported_cost` nullable
- `normalized_cost` nullable
- `currency` nullable
- `pricing_rate_version` nullable
- `metadata` JSONB not null default object

Constraints:
- unique `(tenant_id, dedupe_key)`
- FK to `requests`
- pricing rate version required when normalized cost is present

Accepted usage events are append-only. Corrections are modeled as compensating events, not edits.

## Audit Events

Minimum columns:
- `audit_event_id` UUID primary key
- `occurred_at` not null
- `tenant_id` not null
- `application_id` nullable
- `agent_id` nullable
- `config_version_id` nullable
- `actor_principal_id` not null
- `request_id` nullable
- `event_type` not null
- `before_hash` nullable
- `after_hash` nullable
- `metadata` JSONB not null default object

Must cover config publish/rollback, policy publish/change, activation change, enable/disable, quota/entitlement changes, tool permission changes and privacy/risk policy changes.

## Memory And pgvector Tables

### memory_items

Columns:
- `memory_item_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `subject_id` nullable
- `agent_id` nullable
- `conversation_id` nullable
- `memory_type` not null
- `privacy_class` not null
- `content_ref` nullable
- `structured_value` JSONB nullable
- `source_request_id` nullable
- `verification_status` not null
- `confidence` numeric nullable
- `expires_at` nullable
- `created_at` not null
- `updated_at` not null

Tenant/application filters are mandatory. Tenant-global Subject does not allow cross-Application retrieval.

### memory_embeddings

Columns:
- `memory_embedding_id` UUID primary key
- `tenant_id` not null
- `application_id` not null
- `memory_item_id` not null
- `embedding_model_version` not null
- `embedding` vector not null
- `created_at` not null

Vector dimensions and index strategy depend on the selected embedding model and benchmark results.

## Isolation Test Matrix

Executable tests should prove:

1. Tenant A cannot read Tenant B rows for every tenant-owned table.
2. Application A cannot bind to Agent/Channel from Application B.
3. Agent activation cannot point to another tenant/application/agent/environment.
4. Agent activation cannot point to a non-PUBLISHED config version.
5. Only one current activation exists per Agent + environment.
6. Only one enabled default binding exists per Channel + environment.
7. Conversation channel and primary agent remain in the same tenant/application.
8. SubjectIdentity uniqueness prevents duplicate provider identities in a channel.
9. Subject ID alone cannot retrieve memory from another Application.
10. Vector search refuses or returns no results without tenant/application filters.
11. UsageEvent dedupe prevents retry double-counting.
12. Idempotency reservation prevents duplicate side effects under concurrency.
13. Published config/policy rows cannot be mutated.
14. Runtime role cannot bypass RLS by omitting tenant context.
15. Pooled connections do not retain tenant context after transaction end.

## Migration Authoring Order

1. Create extensions, domains/enums and helper functions.
2. Create tenants/workspaces/applications.
3. Create agents/channels/bindings/subjects/conversations.
4. Create policy/config/activation tables and immutability triggers.
5. Create request/span/call telemetry tables.
6. Create idempotency and usage ledger tables.
7. Create audit tables.
8. Create memory/embedding tables and indexes.
9. Enable RLS policies.
10. Add isolation and invariant tests.

## Open Decisions Before Executable DDL

1. Choose migration tool and naming convention.
2. Decide enum vs checked text domains for lifecycle/status values.
3. Decide whether config/policy JSON gets database JSON Schema validation in v1 or validation stays in application/CI.
4. Define exact runtime role names for development/staging/production.
5. Choose UUIDv7 generation source for local tests and production runtime.
6. Pick initial embedding model/dimension only after benchmark fixtures exist.
7. Define retention class names and hooks before production telemetry storage.
8. Define minimum operator principal representation for `created_by`, `activated_by` and audit actor fields.

## Phase 2 Exit Criteria Contribution

This schema design supports Phase 2 by giving the Core Runtime Skeleton stable data contracts for config loading, policy resolution, request tracing, tool authorization context, usage/cost events and synthetic end-to-end request testing.

Phase 2 runtime work should not hard-code shortcuts that contradict this schema. If implementation discovers a contradiction, reopen the relevant frozen contract instead of silently changing semantics.
