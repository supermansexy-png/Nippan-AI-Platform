# Request, Trace & Usage Telemetry Contract v1

Status: **REVIEW**
Issue: #9
Date: 2026-09-22

**Normativity:** This Markdown contract is normative for request/trace/usage semantics and invariants. `schemas/request-envelope-v1.schema.json` and `schemas/usage-event-v1.schema.json` are normative for the serialized structures they describe and must not conflict with this contract.

## Purpose

Create one correlation contract across Cloudflare Worker, FastAPI Core, OpenRouter/model calls, Nippan MCP, Cloudflare Queues, n8n, storage, and outbound channel delivery.

Primary operator goal:

> Given one request, the Dashboard can show where it went, what configuration/model/tool it used, what failed, how long it took, and what it cost.

## Core identifiers

Do not overload one ID for multiple jobs.

- request_id: one logical platform request
- trace_id: distributed execution trace
- span_id: one timed operation inside a trace
- event_id: external/provider event identity when available
- idempotency_key: deduplication and side-effect safety
- conversation_id: conversation thread
- job_id: background/queued job

Generate request_id at the first trusted ingress boundary. Prefer UUIDv7; UUIDv4 is acceptable.

For W3C/OpenTelemetry interoperability:
- `trace_id` is 16 bytes serialized as exactly 32 lowercase hexadecimal characters and must not be all zero
- `span_id` is 8 bytes serialized as exactly 16 lowercase hexadecimal characters and must not be all zero
- `request_id` remains the platform UUID and is not overloaded as trace/span identity

request_id stays unchanged across Worker -> Core -> model -> MCP -> reply.

## Request envelope

Always required:
- request_id
- trace_id
- tenant_id
- received_at
- environment
- request_kind
- source
- privacy_class
- status_at_emit

Scope requirements:
- `application_id` is required for conversation, tool_action, background_job, scheduled_job, ingestion, extraction and evaluation
- `application_id` may be null/absent only for explicitly platform/tenant-scoped admin_action or health_internal work
- `channel_id` is required for conversation and otherwise optional when the request did not originate from a Channel
- fake Application/Channel IDs are forbidden

Conditional:
- agent_id after routing
- subject_id
- conversation_id
- event_id
- parent_request_id
- idempotency_key

Provider/client correlation IDs are stored separately from authoritative platform IDs.

## Request kinds

Initial canonical values:
- conversation
- tool_action
- background_job
- scheduled_job
- admin_action
- ingestion
- extraction
- evaluation
- health_internal

## Request status

The request envelope carries `status_at_emit`, an immutable snapshot of status when that envelope is emitted. Mutable current request status belongs to the operational request-state record.

Canonical operational status:
- RECEIVED
- ACCEPTED
- RUNNING
- WAITING
- SUCCEEDED
- FAILED
- PARTIAL
- CANCELLED
- BLOCKED
- DEAD_LETTER

## Trace spans

Material operations create spans.

Canonical span types:
- edge.ingress
- edge.rate_limit
- core.route
- core.policy
- context.retrieve
- context.compile
- model.call
- reviewer.call
- tool.call
- queue.publish
- queue.consume
- n8n.workflow
- storage.read
- storage.write
- channel.reply
- approval.wait
- approval.resolve

Span fields:
- trace_id
- span_id
- parent_span_id nullable
- trace_links nullable for async/causal relationships
- request_id
- span_type
- service
- operation
- started_at
- ended_at
- duration_ms
- status
- attempt
- error_code
- minimal metadata

Rules:
- queued/async work may use trace links when a single synchronous parent would be misleading
- retries create distinct attempts/spans while preserving the logical request/trace where appropriate
- attempt numbering starts at 1 and is monotonic per retried operation

Full content is not a default trace field.

## Effective configuration trace

Every AI/tool execution records:
- agent_id
- effective_config_version_id
- effective_config_hash
- model policy reference
- tool policy reference when applicable
- memory policy reference when applicable
- risk/privacy policy references

Dashboard must answer:
"Which exact published configuration produced this execution?"

## Model call telemetry

Each model call records:
- ai_call_id
- request_id
- trace_id
- span_id
- tenant_id
- application_id
- agent_id
- provider
- model
- model tier/role
- purpose
- timestamps
- latency_ms
- time_to_first_token_ms when available
- input_tokens when available
- output_tokens when available
- cached_input_tokens when available
- reasoning_tokens when available
- provider_reported_cost when available
- normalized_cost when calculated by platform
- currency
- success
- error_code
- retry_count
- fallback source/reason
- structured_output_valid when applicable
- tool_call_requested when applicable

Purpose examples:
- main_response
- classifier
- decision_router
- context_compiler
- reviewer
- extractor
- vision
- embedding
- reranker
- coding
- evaluation

Missing provider metrics are null, never guessed.

## Tool call telemetry

Record:
- tool_call_id
- request_id
- trace_id
- tenant_id
- application_id
- agent_id
- tool_domain
- tool_name
- tool_version
- operation
- risk_class
- privacy_class
- policy_decision
- approval_id when applicable
- idempotency_key when applicable
- timestamps
- latency_ms
- attempt
- success
- error_code
- args_fingerprint nullable
- result_fingerprint nullable
- fingerprint_key_id nullable

Default audit stores privacy-approved fingerprints and operational metadata, not full sensitive arguments/results. Fingerprint rules are defined in Logging/privacy below.

## Retrieval telemetry

Record enough to debug retrieval without copying all retrieved memory into logs:
- retrieval_mode
- query_kind
- candidate_count
- selected_count
- structured_hits
- keyword_hits
- vector_hits
- reranker_used
- embedding_model_version
- retrieval_latency_ms
- context_token_estimate
- compiler_used
- compiler token counts when available

## Usage attribution

Every measurable unit must be attributable at minimum to:
- tenant_id
- application_id
- request_id

Where applicable:
- agent_id
- channel_id
- subject_id
- conversation_id
- model/provider
- tool
- storage domain

Usage event types may include:
- request
- ai_tokens
- ai_cost
- embedding_tokens
- tool_call
- storage_bytes
- queue_operation
- file_processing
- external_api_cost

### Immutable UsageEvent ledger

Every billable/measurable unit used for aggregation is represented by an immutable UsageEvent with at least:
- usage_event_id
- occurred_at
- tenant_id
- application_id
- request_id
- event_type
- quantity
- unit
- dedupe_key
- source_type and source_id/call reference

Where applicable:
- agent_id
- channel_id
- subject_id
- conversation_id
- provider
- model
- tool_domain/tool_name
- provider_reported_cost
- normalized_cost
- currency
- pricing_rate_version

Rules:
- `provider_reported_cost` and `normalized_cost` are distinct and never overwrite one another
- `pricing_rate_version` is required when normalized cost is calculated by platform pricing/rates
- UsageEvents are append-only/immutable after acceptance
- `tenant_id + dedupe_key` identifies the same measurable event for dedupe; retries/replays must not create duplicate billable units
- aggregates are derived/rebuildable from UsageEvents and are not the billing source of truth

This supports future billing without implementing billing now.

## Cost accounting

Keep separate:
- provider_reported_cost
- normalized_cost

Rules:
- provider-reported cost is never overwritten by an estimate
- currency is stored
- internal price/rate version is recorded when platform calculates cost
- immutable call/usage events are the basis for aggregation
- primary optimization metric remains cost per successful task

## Error taxonomy

Stable top-level categories:
- EDGE_AUTH_ERROR
- RATE_LIMITED
- ROUTING_ERROR
- POLICY_BLOCKED
- PRIVACY_BLOCKED
- CONTEXT_ERROR
- MODEL_TIMEOUT
- MODEL_RATE_LIMIT
- MODEL_PROVIDER_ERROR
- MODEL_OUTPUT_INVALID
- TOOL_VALIDATION_ERROR
- TOOL_PERMISSION_DENIED
- TOOL_TIMEOUT
- TOOL_EXECUTION_ERROR
- DATABASE_ERROR
- STORAGE_ERROR
- QUEUE_ERROR
- N8N_ERROR
- CHANNEL_DELIVERY_ERROR
- APPROVAL_TIMEOUT
- IDEMPOTENCY_CONFLICT
- INTERNAL_ERROR

Vendor-specific codes may be recorded separately.

## Retry and fallback

Each retry/fallback records:
- attempt
- reason
- previous target
- next target
- backoff/delay
- final outcome

Rules:
- retry never bypasses idempotency
- fallback never weakens privacy/policy constraints
- retries have hard maximums
- failed intermediate attempts remain visible even if final user request succeeds

## Idempotency

Idempotency is separate from request identity.

Persistent record:
- idempotency_key
- tenant_id
- scope
- operation
- request_id
- state
- result_reference
- request_fingerprint nullable when policy permits
- created_at
- updated_at
- expires_at

Semantics:
- uniqueness scope is `tenant_id + scope + operation + idempotency_key`
- reservation/check is atomic before executing a side effect
- canonical states are `IN_PROGRESS`, `SUCCEEDED`, `FAILED`, `EXPIRED`
- a duplicate while `IN_PROGRESS` must not execute the side effect again; wait/ack/conflict behavior is transport policy
- a duplicate after `SUCCEEDED` reuses or references the prior successful result where supported
- reuse of the same key for materially different operation/request identity is a conflict
- retry after `FAILED` is allowed only when operation policy says retry is safe; the same idempotency protection remains in force
- expiry removes dedupe guarantees only after the documented safe replay window
- provider `event_id` dedupe is ingress-event dedupe and is separate from side-effect `idempotency_key`

Side-effecting operations consult persistent idempotency state before execute/retry.

## Queue/background propagation

Queue envelope includes:
- job_id
- request_id
- trace_id
- parent_span_id
- tenant_id
- application_id
- agent_id when applicable
- job_type
- payload_ref or minimal payload
- attempt
- max_attempts
- idempotency_key
- created_at
- scheduled_at

## n8n propagation

Platform-triggered n8n workflows receive:
- request_id
- trace_id
- tenant_id
- application_id
- job/request context

n8n execution ID is stored as an external execution reference.

n8n execution history is diagnostic, not the platform source of truth.

## Logging/privacy

Production logs are metadata-first.

Content logging is opt-in by policy and environment.

Fingerprint/minimization rules:
- `SECRET_CREDENTIAL` values are never logged, hashed or included in telemetry fingerprints
- sensitive values are omitted/redacted by default
- plain unkeyed hashes are not treated as safe redaction for low-entropy PII/sensitive values
- where correlation/comparison is justified and privacy policy permits it, canonicalize the approved value and use HMAC-SHA-256 with a platform-managed rotating secret
- HMAC input is domain-separated by Tenant and fingerprint purpose; telemetry stores `fingerprint_key_id` for rotation/audit
- a separate per-Tenant HMAC key is not required in v1
- telemetry field collection is minimized by privacy class

Suggested modes:
- metadata_only
- redacted
- debug_safe_test

Normal trace debugging must not require copying full customer context into logs.

## Dashboard views enabled

### Request explorer
Shows:
Ingress -> Routing -> Context -> Model -> Tool -> Reply

For each request show:
- final/current status
- step durations
- model/tool/fallback
- error point
- cost
- effective config version

### Error view
Group errors by:
- category
- Application/Agent
- first/last occurrence
- failure rate
- sample request IDs

### Usage/cost view
Aggregate by:
- tenant
- application
- agent
- model
- purpose
- day/month
- successful task

### Approval view
Show:
- pending approval
- risk class
- requested action
- expiry
- originating request

## Source of truth

For v1:
- PostgreSQL ops/audit/usage = platform operational truth
- Cloudflare logs/traces = edge diagnostics
- OpenRouter activity/usage = model/provider corroboration
- n8n executions = workflow diagnostics

All share platform request/trace correlation.

## Invariants

1. Every production request has request_id and tenant_id; Application/Channel scope follows request-kind rules and fake IDs are forbidden.
2. Every material span belongs to one trace and request and uses the canonical W3C-compatible trace/span identifier format.
3. Every model/tool call is attributable to tenant/application/request.
4. Side-effect retry preserves idempotency protection.
5. Effective config version/hash is recorded for AI/tool execution.
6. Unknown provider cost is null, never fabricated.
7. High-level error categories remain stable across providers.
8. Normal trace debugging does not require sensitive payload content and SECRET_CREDENTIAL is never fingerprinted.
9. Async jobs preserve causal request/trace correlation using parent relationships and/or trace links.
10. Side-effect retries cannot bypass atomic idempotency protection.
11. Usage aggregates are rebuildable from immutable deduplicated UsageEvents.
12. Dashboard can locate the failing service from request_id without searching by customer message text.

## Non-goals

Not defined here:
- final observability vendor
- database DDL
- exact retention durations
- billing invoice logic
- final Dashboard visual design
- vendor-specific tracing SDK
