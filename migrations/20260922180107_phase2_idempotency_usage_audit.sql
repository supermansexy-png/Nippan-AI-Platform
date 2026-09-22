begin;

create table public.idempotency_records (
  idempotency_record_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  scope text not null check (length(btrim(scope)) between 1 and 150),
  operation text not null check (length(btrim(operation)) between 1 and 150),
  idempotency_key text not null check (length(btrim(idempotency_key)) between 1 and 255),
  request_id uuid not null,
  state text not null
    check (state in ('IN_PROGRESS','SUCCEEDED','FAILED','EXPIRED')),
  result_reference text,
  request_fingerprint text,
  fingerprint_key_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  expires_at timestamptz not null,

  unique (tenant_id, scope, operation, idempotency_key),

  foreign key (tenant_id, request_id)
    references public.requests (tenant_id, request_id),

  check (expires_at > created_at),
  check (
    request_fingerprint is null
    or length(btrim(fingerprint_key_id)) > 0
  )
);

create index idempotency_records_request_idx
  on public.idempotency_records (tenant_id, request_id);

create index idempotency_records_state_expiry_idx
  on public.idempotency_records (tenant_id, state, expires_at);

create or replace function app_private.enforce_idempotency_transition()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  if old.tenant_id <> new.tenant_id
     or old.scope <> new.scope
     or old.operation <> new.operation
     or old.idempotency_key <> new.idempotency_key
     or old.request_id <> new.request_id
     or old.created_at <> new.created_at then
    raise exception 'idempotency identity fields are immutable' using errcode = '55000';
  end if;

  if old.state = 'SUCCEEDED' and new.state <> 'SUCCEEDED' then
    raise exception 'SUCCEEDED idempotency record cannot transition' using errcode = '55000';
  end if;

  if old.state = 'EXPIRED' and new.state <> 'EXPIRED' then
    raise exception 'EXPIRED idempotency record cannot transition' using errcode = '55000';
  end if;

  if old.state = 'IN_PROGRESS'
     and new.state not in ('IN_PROGRESS','SUCCEEDED','FAILED','EXPIRED') then
    raise exception 'invalid idempotency transition from IN_PROGRESS to %', new.state using errcode = '23514';
  end if;

  if old.state = 'FAILED'
     and new.state not in ('FAILED','IN_PROGRESS','SUCCEEDED','EXPIRED') then
    raise exception 'invalid idempotency transition from FAILED to %', new.state using errcode = '23514';
  end if;

  new.updated_at := now();
  return new;
end $$;

revoke all on function app_private.enforce_idempotency_transition()
  from public, anon, authenticated;

create trigger idempotency_records_transition_guard
before update on public.idempotency_records
for each row execute function app_private.enforce_idempotency_transition();

create table public.usage_events (
  usage_event_id uuid primary key,
  occurred_at timestamptz not null,
  tenant_id uuid not null,
  application_id uuid not null,
  request_id uuid not null,
  agent_id uuid,
  channel_id uuid,
  subject_id uuid,
  conversation_id uuid,
  event_type text not null
    check (event_type in (
      'request','ai_tokens','ai_cost','embedding_tokens','tool_call',
      'storage_bytes','queue_operation','file_processing','external_api_cost'
    )),
  quantity numeric not null check (quantity >= 0),
  unit text not null check (length(btrim(unit)) between 1 and 64),
  dedupe_key text not null check (length(btrim(dedupe_key)) between 1 and 255),
  source_type text not null
    check (source_type in (
      'request','ai_call','tool_call','storage','queue','file','external_api','other'
    )),
  source_id text not null check (length(btrim(source_id)) between 1 and 255),
  provider text,
  model text,
  tool_domain text,
  tool_name text,
  provider_reported_cost numeric
    check (provider_reported_cost is null or provider_reported_cost >= 0),
  normalized_cost numeric
    check (normalized_cost is null or normalized_cost >= 0),
  currency text check (currency is null or currency ~ '^[A-Z]{3}$'),
  pricing_rate_version text,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now(),

  unique (tenant_id, dedupe_key),

  foreign key (tenant_id, application_id, request_id)
    references public.requests (tenant_id, application_id, request_id),
  foreign key (tenant_id, application_id, agent_id)
    references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, channel_id)
    references public.channels (tenant_id, application_id, channel_id),
  foreign key (tenant_id, subject_id)
    references public.subjects (tenant_id, subject_id),
  foreign key (tenant_id, application_id, conversation_id)
    references public.conversations (tenant_id, application_id, conversation_id),

  check (
    (provider_reported_cost is null and normalized_cost is null)
    or currency is not null
  ),
  check (
    normalized_cost is null
    or length(btrim(pricing_rate_version)) > 0
  )
);

create index usage_events_scope_time_idx
  on public.usage_events (tenant_id, application_id, occurred_at desc);

create index usage_events_request_idx
  on public.usage_events (tenant_id, application_id, request_id);

create index usage_events_agent_idx
  on public.usage_events (tenant_id, application_id, agent_id, occurred_at desc)
  where agent_id is not null;

create index usage_events_channel_idx
  on public.usage_events (tenant_id, application_id, channel_id, occurred_at desc)
  where channel_id is not null;

create index usage_events_subject_idx
  on public.usage_events (tenant_id, subject_id, occurred_at desc)
  where subject_id is not null;

create index usage_events_conversation_idx
  on public.usage_events (tenant_id, application_id, conversation_id, occurred_at desc)
  where conversation_id is not null;

create or replace function app_private.reject_usage_event_mutation()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  raise exception 'usage_events is append-only' using errcode = '55000';
end $$;

revoke all on function app_private.reject_usage_event_mutation()
  from public, anon, authenticated;

create trigger usage_events_append_only
before update or delete on public.usage_events
for each row execute function app_private.reject_usage_event_mutation();

create table public.audit_events (
  audit_event_id uuid primary key default extensions.gen_random_uuid(),
  occurred_at timestamptz not null default now(),
  tenant_id uuid not null,
  application_id uuid,
  agent_id uuid,
  config_version_id uuid,
  actor_principal_id text not null
    check (length(btrim(actor_principal_id)) between 1 and 255),
  request_id uuid,
  event_type text not null
    check (length(btrim(event_type)) between 1 and 150),
  before_hash text,
  after_hash text,
  metadata jsonb not null default '{}'::jsonb
    check (jsonb_typeof(metadata) = 'object'),
  created_at timestamptz not null default now(),

  foreign key (tenant_id) references public.tenants (tenant_id),
  foreign key (tenant_id, application_id)
    references public.applications (tenant_id, application_id),
  foreign key (tenant_id, application_id, agent_id)
    references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, agent_id, config_version_id)
    references public.agent_config_versions
      (tenant_id, application_id, agent_id, config_version_id),
  foreign key (tenant_id, request_id)
    references public.requests (tenant_id, request_id),

  check (application_id is not null or agent_id is null),
  check (agent_id is not null or config_version_id is null)
);

create index audit_events_scope_time_idx
  on public.audit_events (tenant_id, application_id, occurred_at desc);

create index audit_events_agent_idx
  on public.audit_events (tenant_id, application_id, agent_id, occurred_at desc)
  where agent_id is not null;

create index audit_events_request_idx
  on public.audit_events (tenant_id, request_id)
  where request_id is not null;

create index audit_events_config_idx
  on public.audit_events (tenant_id, application_id, agent_id, config_version_id)
  where config_version_id is not null;

create or replace function app_private.reject_audit_event_mutation()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  raise exception 'audit_events is append-only' using errcode = '55000';
end $$;

revoke all on function app_private.reject_audit_event_mutation()
  from public, anon, authenticated;

create trigger audit_events_append_only
before update or delete on public.audit_events
for each row execute function app_private.reject_audit_event_mutation();

revoke all on public.idempotency_records, public.usage_events, public.audit_events
  from public, anon, authenticated, service_role;

grant select, insert, update on public.idempotency_records
  to nippan_runtime, nippan_control_plane;

grant select, insert on public.usage_events, public.audit_events
  to nippan_runtime, nippan_control_plane;

grant select on public.idempotency_records, public.usage_events, public.audit_events
  to nippan_analytics;

do $$
declare t text;
begin
  foreach t in array array[
    'idempotency_records','usage_events','audit_events'
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

comment on table public.idempotency_records is
  'Persistent atomic dedupe state for side-effect safety; uniqueness is tenant+scope+operation+key.';
comment on table public.usage_events is
  'Immutable deduplicated usage ledger; aggregates must be rebuildable from this table.';
comment on table public.audit_events is
  'Append-only operational/control-plane audit trail for configuration, policy and authorization changes.';

commit;
