begin;

alter table public.agent_config_versions
  add constraint agent_config_versions_scope_id_uniq
  unique (tenant_id, application_id, agent_id, config_version_id);

create table public.requests (
  request_id uuid primary key,
  trace_id text not null
    check (trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  tenant_id uuid not null,
  application_id uuid,
  channel_id uuid,
  agent_id uuid,
  subject_id uuid,
  conversation_id uuid,
  environment text not null
    check (environment in ('development','staging','production')),
  request_kind text not null
    check (request_kind in (
      'conversation','tool_action','background_job','scheduled_job',
      'admin_action','ingestion','extraction','evaluation','health_internal'
    )),
  source text not null
    check (length(btrim(source)) between 1 and 64),
  privacy_class text not null
    check (privacy_class in (
      'PUBLIC_LOW_RISK','INTERNAL','PII','FINANCIAL_CUSTOMER','SECRET_CREDENTIAL'
    )),
  current_status text not null
    check (current_status in (
      'RECEIVED','ACCEPTED','RUNNING','WAITING','SUCCEEDED','FAILED',
      'PARTIAL','CANCELLED','BLOCKED','DEAD_LETTER'
    )),
  received_at timestamptz not null,
  completed_at timestamptz,
  event_id text check (event_id is null or length(event_id) <= 255),
  external_correlation_id text
    check (external_correlation_id is null or length(external_correlation_id) <= 255),
  parent_request_id uuid,
  idempotency_key text
    check (idempotency_key is null or length(idempotency_key) <= 255),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  unique (tenant_id, request_id),
  unique (tenant_id, request_id, trace_id),
  unique (tenant_id, application_id, request_id),

  foreign key (tenant_id) references public.tenants (tenant_id),
  foreign key (tenant_id, application_id)
    references public.applications (tenant_id, application_id),
  foreign key (tenant_id, application_id, channel_id)
    references public.channels (tenant_id, application_id, channel_id),
  foreign key (tenant_id, application_id, agent_id)
    references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, subject_id)
    references public.subjects (tenant_id, subject_id),
  foreign key (tenant_id, application_id, conversation_id)
    references public.conversations (tenant_id, application_id, conversation_id),
  foreign key (tenant_id, parent_request_id)
    references public.requests (tenant_id, request_id),

  check (
    request_kind in ('admin_action','health_internal')
    or application_id is not null
  ),
  check (request_kind <> 'conversation' or channel_id is not null),
  check (channel_id is null or application_id is not null),
  check (agent_id is null or application_id is not null),
  check (conversation_id is null or application_id is not null),
  check (completed_at is null or completed_at >= received_at),
  check (
    (current_status in ('RECEIVED','ACCEPTED','RUNNING','WAITING') and completed_at is null)
    or
    (current_status in ('SUCCEEDED','FAILED','PARTIAL','CANCELLED','BLOCKED','DEAD_LETTER')
      and completed_at is not null)
  )
);

create unique index requests_ingress_event_uidx
  on public.requests (tenant_id, source, event_id)
  where event_id is not null;

create index requests_scope_received_idx
  on public.requests (tenant_id, application_id, received_at desc);

create index requests_trace_idx
  on public.requests (tenant_id, trace_id);

create index requests_status_idx
  on public.requests (tenant_id, current_status, received_at desc);

create index requests_parent_fk_idx
  on public.requests (tenant_id, parent_request_id)
  where parent_request_id is not null;

create index requests_channel_fk_idx
  on public.requests (tenant_id, application_id, channel_id)
  where channel_id is not null;

create index requests_agent_fk_idx
  on public.requests (tenant_id, application_id, agent_id)
  where agent_id is not null;

create index requests_subject_fk_idx
  on public.requests (tenant_id, subject_id)
  where subject_id is not null;

create index requests_conversation_fk_idx
  on public.requests (tenant_id, application_id, conversation_id)
  where conversation_id is not null;

create table public.trace_spans (
  span_row_id uuid primary key default extensions.gen_random_uuid(),
  trace_id text not null
    check (trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  span_id text not null
    check (span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  parent_span_id text
    check (parent_span_id is null or parent_span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  request_id uuid not null,
  tenant_id uuid not null,
  span_type text not null
    check (span_type in (
      'edge.ingress','edge.rate_limit','core.route','core.policy',
      'context.retrieve','context.compile','model.call','reviewer.call',
      'tool.call','queue.publish','queue.consume','n8n.workflow',
      'storage.read','storage.write','channel.reply',
      'approval.wait','approval.resolve'
    )),
  service text not null check (length(btrim(service)) between 1 and 100),
  operation text not null check (length(btrim(operation)) between 1 and 150),
  started_at timestamptz not null,
  ended_at timestamptz,
  duration_ms bigint check (duration_ms is null or duration_ms >= 0),
  status text not null check (length(btrim(status)) between 1 and 50),
  attempt integer not null default 1 check (attempt >= 1),
  error_code text,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),

  unique (trace_id, span_id),
  unique (tenant_id, request_id, trace_id, span_id),

  foreign key (tenant_id, request_id, trace_id)
    references public.requests (tenant_id, request_id, trace_id),
  foreign key (trace_id, parent_span_id)
    references public.trace_spans (trace_id, span_id)
    deferrable initially immediate,

  check (
    (ended_at is null and duration_ms is null)
    or
    (ended_at is not null and duration_ms is not null and ended_at >= started_at)
  )
);

create index trace_spans_request_started_idx
  on public.trace_spans (tenant_id, request_id, started_at);

create index trace_spans_type_idx
  on public.trace_spans (tenant_id, span_type, started_at desc);

create index trace_spans_parent_fk_idx
  on public.trace_spans (trace_id, parent_span_id)
  where parent_span_id is not null;

create table public.trace_span_links (
  trace_span_link_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  request_id uuid not null,
  trace_id text not null
    check (trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  span_id text not null
    check (span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  linked_trace_id text not null
    check (linked_trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  linked_span_id text
    check (linked_span_id is null or linked_span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  relationship text not null default 'causal'
    check (length(btrim(relationship)) between 1 and 50),
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now(),

  foreign key (tenant_id, request_id, trace_id, span_id)
    references public.trace_spans (tenant_id, request_id, trace_id, span_id)
);

create index trace_span_links_source_idx
  on public.trace_span_links (tenant_id, request_id, trace_id, span_id);

create index trace_span_links_target_idx
  on public.trace_span_links (linked_trace_id, linked_span_id);

create table public.ai_calls (
  ai_call_id uuid primary key default extensions.gen_random_uuid(),
  request_id uuid not null,
  trace_id text not null
    check (trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  span_id text not null
    check (span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  tenant_id uuid not null,
  application_id uuid not null,
  agent_id uuid not null,
  effective_config_version_id uuid not null,
  effective_config_hash text not null
    check (length(btrim(effective_config_hash)) between 1 and 128),
  policy_refs jsonb not null default '{}'::jsonb
    check (jsonb_typeof(policy_refs) = 'object'),
  provider text not null check (length(btrim(provider)) between 1 and 100),
  provider_call_id text,
  model text not null check (length(btrim(model)) between 1 and 200),
  model_tier text not null check (length(btrim(model_tier)) between 1 and 100),
  model_role text not null check (length(btrim(model_role)) between 1 and 100),
  purpose text not null check (length(btrim(purpose)) between 1 and 100),
  started_at timestamptz not null,
  ended_at timestamptz not null,
  latency_ms bigint not null check (latency_ms >= 0),
  time_to_first_token_ms bigint
    check (time_to_first_token_ms is null or time_to_first_token_ms >= 0),
  input_tokens bigint check (input_tokens is null or input_tokens >= 0),
  output_tokens bigint check (output_tokens is null or output_tokens >= 0),
  cached_input_tokens bigint
    check (cached_input_tokens is null or cached_input_tokens >= 0),
  reasoning_tokens bigint
    check (reasoning_tokens is null or reasoning_tokens >= 0),
  provider_reported_cost numeric check (provider_reported_cost is null or provider_reported_cost >= 0),
  normalized_cost numeric check (normalized_cost is null or normalized_cost >= 0),
  currency text check (currency is null or currency ~ '^[A-Z]{3}$'),
  pricing_rate_version text,
  success boolean not null,
  error_code text,
  retry_count integer not null default 0 check (retry_count >= 0),
  fallback_source text,
  fallback_reason text,
  structured_output_valid boolean,
  tool_call_requested boolean,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),

  foreign key (tenant_id, application_id, request_id)
    references public.requests (tenant_id, application_id, request_id),
  foreign key (tenant_id, application_id, agent_id)
    references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, agent_id, effective_config_version_id)
    references public.agent_config_versions
      (tenant_id, application_id, agent_id, config_version_id),
  foreign key (tenant_id, request_id, trace_id, span_id)
    references public.trace_spans (tenant_id, request_id, trace_id, span_id),

  check (ended_at >= started_at),
  check (
    (provider_reported_cost is null and normalized_cost is null)
    or currency is not null
  ),
  check (normalized_cost is null or length(btrim(pricing_rate_version)) > 0)
);

create index ai_calls_request_idx
  on public.ai_calls (tenant_id, application_id, request_id, started_at);

create index ai_calls_agent_idx
  on public.ai_calls (tenant_id, application_id, agent_id, started_at desc);

create index ai_calls_provider_model_idx
  on public.ai_calls (tenant_id, provider, model, started_at desc);

create index ai_calls_config_fk_idx
  on public.ai_calls (tenant_id, application_id, agent_id, effective_config_version_id);

create index ai_calls_span_fk_idx
  on public.ai_calls (tenant_id, request_id, trace_id, span_id);

create table public.tool_calls (
  tool_call_id uuid primary key default extensions.gen_random_uuid(),
  request_id uuid not null,
  trace_id text not null
    check (trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  span_id text not null
    check (span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  tenant_id uuid not null,
  application_id uuid not null,
  agent_id uuid not null,
  effective_config_version_id uuid not null,
  effective_config_hash text not null
    check (length(btrim(effective_config_hash)) between 1 and 128),
  policy_refs jsonb not null default '{}'::jsonb
    check (jsonb_typeof(policy_refs) = 'object'),
  tool_domain text not null check (length(btrim(tool_domain)) between 1 and 100),
  tool_name text not null check (length(btrim(tool_name)) between 1 and 150),
  tool_version text not null check (length(btrim(tool_version)) between 1 and 100),
  operation text not null check (length(btrim(operation)) between 1 and 150),
  risk_class text not null
    check (risk_class in ('READ','WRITE_LOW','WRITE_IMPORTANT','DESTRUCTIVE','FINANCIAL')),
  privacy_class text not null
    check (privacy_class in (
      'PUBLIC_LOW_RISK','INTERNAL','PII','FINANCIAL_CUSTOMER','SECRET_CREDENTIAL'
    )),
  policy_decision text not null
    check (length(btrim(policy_decision)) between 1 and 50),
  approval_id uuid,
  idempotency_key text
    check (idempotency_key is null or length(idempotency_key) <= 255),
  started_at timestamptz not null,
  ended_at timestamptz not null,
  latency_ms bigint not null check (latency_ms >= 0),
  attempt integer not null default 1 check (attempt >= 1),
  success boolean not null,
  error_code text,
  args_fingerprint text,
  result_fingerprint text,
  fingerprint_key_id text,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),

  foreign key (tenant_id, application_id, request_id)
    references public.requests (tenant_id, application_id, request_id),
  foreign key (tenant_id, application_id, agent_id)
    references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, agent_id, effective_config_version_id)
    references public.agent_config_versions
      (tenant_id, application_id, agent_id, config_version_id),
  foreign key (tenant_id, request_id, trace_id, span_id)
    references public.trace_spans (tenant_id, request_id, trace_id, span_id),

  check (ended_at >= started_at),
  check (
    (args_fingerprint is null and result_fingerprint is null)
    or length(btrim(fingerprint_key_id)) > 0
  ),
  check (
    privacy_class <> 'SECRET_CREDENTIAL'
    or (args_fingerprint is null and result_fingerprint is null and fingerprint_key_id is null)
  )
);

create index tool_calls_request_idx
  on public.tool_calls (tenant_id, application_id, request_id, started_at);

create index tool_calls_agent_idx
  on public.tool_calls (tenant_id, application_id, agent_id, started_at desc);

create index tool_calls_tool_idx
  on public.tool_calls (tenant_id, tool_domain, tool_name, operation, started_at desc);

create index tool_calls_config_fk_idx
  on public.tool_calls (tenant_id, application_id, agent_id, effective_config_version_id);

create index tool_calls_span_fk_idx
  on public.tool_calls (tenant_id, request_id, trace_id, span_id);

create table public.retrieval_events (
  retrieval_event_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  request_id uuid not null,
  trace_id text not null
    check (trace_id ~ '^(?!0{32}$)[0-9a-f]{32}$'),
  span_id text not null
    check (span_id ~ '^(?!0{16}$)[0-9a-f]{16}$'),
  agent_id uuid,
  retrieval_mode text not null
    check (length(btrim(retrieval_mode)) between 1 and 50),
  query_kind text not null
    check (length(btrim(query_kind)) between 1 and 100),
  candidate_count integer not null default 0 check (candidate_count >= 0),
  selected_count integer not null default 0 check (selected_count >= 0),
  structured_hits integer not null default 0 check (structured_hits >= 0),
  keyword_hits integer not null default 0 check (keyword_hits >= 0),
  vector_hits integer not null default 0 check (vector_hits >= 0),
  reranker_used boolean not null default false,
  embedding_model_version text,
  retrieval_latency_ms bigint not null check (retrieval_latency_ms >= 0),
  context_token_estimate bigint
    check (context_token_estimate is null or context_token_estimate >= 0),
  compiler_used boolean not null default false,
  compiler_input_tokens bigint
    check (compiler_input_tokens is null or compiler_input_tokens >= 0),
  compiler_output_tokens bigint
    check (compiler_output_tokens is null or compiler_output_tokens >= 0),
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  occurred_at timestamptz not null default now(),

  foreign key (tenant_id, application_id, request_id)
    references public.requests (tenant_id, application_id, request_id),
  foreign key (tenant_id, application_id, agent_id)
    references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, request_id, trace_id, span_id)
    references public.trace_spans (tenant_id, request_id, trace_id, span_id),

  check (selected_count <= candidate_count)
);

create index retrieval_events_request_idx
  on public.retrieval_events (tenant_id, application_id, request_id, occurred_at);

create index retrieval_events_agent_idx
  on public.retrieval_events (tenant_id, application_id, agent_id, occurred_at desc)
  where agent_id is not null;

create index retrieval_events_span_fk_idx
  on public.retrieval_events (tenant_id, request_id, trace_id, span_id);

revoke all on public.requests, public.trace_spans, public.trace_span_links,
  public.ai_calls, public.tool_calls, public.retrieval_events
  from public, anon, authenticated, service_role;

grant select, insert, update on public.requests, public.trace_spans,
  public.trace_span_links, public.ai_calls, public.tool_calls, public.retrieval_events
  to nippan_runtime, nippan_control_plane;

grant select on public.requests, public.trace_spans, public.trace_span_links,
  public.ai_calls, public.tool_calls, public.retrieval_events
  to nippan_analytics;

do $$
declare t text;
begin
  foreach t in array array[
    'requests','trace_spans','trace_span_links','ai_calls','tool_calls','retrieval_events'
  ] loop
    execute format('alter table public.%I enable row level security', t);
    execute format(
      'create policy tenant_isolation on public.%I for all to nippan_runtime, nippan_control_plane using (tenant_id = (select app_private.current_tenant_id())) with check (tenant_id = (select app_private.current_tenant_id()))',
      t
    );
    execute format(
      'create policy tenant_analytics_read on public.%I for select to nippan_analytics using (tenant_id = (select app_private.current_tenant_id()))',
      t
    );
  end loop;
end $$;

comment on table public.requests is
  'Mutable operational request state correlated by request_id and W3C trace_id.';
comment on table public.trace_spans is
  'Material execution spans; retries are distinct attempts/spans.';
comment on table public.trace_span_links is
  'Async/causal trace links when a strict synchronous parent tree is misleading.';
comment on table public.ai_calls is
  'Model/provider call telemetry with exact request, span and effective config attribution.';
comment on table public.tool_calls is
  'Tool/MCP execution telemetry; sensitive full arguments/results are not stored by default.';
comment on table public.retrieval_events is
  'Retrieval diagnostics without copying retrieved content into operational telemetry.';

commit;
