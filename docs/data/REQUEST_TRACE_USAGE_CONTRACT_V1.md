# Request, Trace & Usage Telemetry Contract v1

Status: **REVIEW**
Issue: #9
Date: 2026-09-22

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

request_id stays unchanged across Worker -> Core -> model -> MCP -> reply.

## Request envelope

Required when known:
- request_id
- trace_id
- tenant_id
- application_id
- channel_id
- received_at
- environment
- request_kind
- source
- privacy_class
- status

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
- parent_span_id
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
- args_hash
- result_hash when applicable

Default audit stores hashes and operational metadata, not full sensitive arguments/results.

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
- request_id
- operation
- state
- result_reference
- created_at
- expires_at

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

1. Every production request has request_id and tenant_id.
2. Every material span belongs to one trace and request.
3. Every model/tool call is attributable to tenant/application/request.
4. Side-effect retry preserves idempotency protection.
5. Effective config version/hash is recorded for AI/tool execution.
6. Unknown provider cost is null, never fabricated.
7. High-level error categories remain stable across providers.
8. Normal trace debugging does not require sensitive payload content.
9. Async jobs preserve parent request/trace correlation.
10. Dashboard can locate the failing service from request_id without searching by customer message text.

## Non-goals

Not defined here:
- final observability vendor
- database DDL
- exact retention durations
- billing invoice logic
- final Dashboard visual design
- vendor-specific tracing SDK
