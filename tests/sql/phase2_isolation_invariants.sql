\set ON_ERROR_STOP on

begin;

-- This suite is destructive only inside this transaction. It must end in ROLLBACK.
-- Run as a CI/test database principal that is allowed to SET ROLE nippan_runtime.
-- Production data is never required.

create temporary table phase2_expected_tables (table_name text primary key);
insert into phase2_expected_tables (table_name) values
  ('tenants'),('workspaces'),('applications'),('agents'),('channels'),
  ('agent_channel_bindings'),('subjects'),('subject_identities'),('conversations'),
  ('policy_versions'),('agent_config_versions'),('agent_activations'),
  ('requests'),('trace_spans'),('trace_span_links'),('ai_calls'),('tool_calls'),
  ('retrieval_events'),('idempotency_records'),('usage_events'),('audit_events');

-- Guard: every tenant-owned table in this suite must have RLS enabled.
do $$
declare missing text;
begin
  select string_agg(e.table_name, ', ' order by e.table_name)
    into missing
  from phase2_expected_tables e
  left join pg_class c on c.relname = e.table_name
  left join pg_namespace n on n.oid = c.relnamespace and n.nspname = 'public'
  where c.oid is null or not c.relrowsecurity;

  if missing is not null then
    raise exception 'RLS missing/disabled for: %', missing;
  end if;
end $$;

insert into public.tenants (tenant_id, slug, display_name, tenant_type, status)
values
  ('11111111-1111-4111-8111-111111111111','phase2-ci-a','Phase2 CI A','internal','active'),
  ('22222222-2222-4222-8222-222222222222','phase2-ci-b','Phase2 CI B','internal','active');

insert into public.workspaces (workspace_id, tenant_id, slug, display_name, status)
values
  ('11111111-1111-4111-8111-111111111101','11111111-1111-4111-8111-111111111111','ws-a','WS A','active'),
  ('22222222-2222-4222-8222-222222222202','22222222-2222-4222-8222-222222222222','ws-b','WS B','active');

insert into public.applications (application_id, tenant_id, workspace_id, slug, display_name, application_type, status)
values
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','11111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111101','app-a','App A','test','active'),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','22222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222202','app-b','App B','test','active');

insert into public.agents (agent_id, tenant_id, application_id, slug, display_name, role, status)
values
  ('a1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','agent-a','Agent A','test','active'),
  ('a2222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','agent-b','Agent B','test','active');

insert into public.channels (channel_id, tenant_id, application_id, channel_type, display_name, status)
values
  ('c1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','test','Channel A','active'),
  ('c2222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','test','Channel B','active');

insert into public.agent_channel_bindings (
  binding_id, tenant_id, application_id, agent_id, channel_id, environment, routing_role, priority, enabled
) values
  ('b1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','a1111111-1111-4111-8111-111111111111','c1111111-1111-4111-8111-111111111111','development','default',100,true),
  ('b2222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','a2222222-2222-4222-8222-222222222222','c2222222-2222-4222-8222-222222222222','development','default',100,true);

insert into public.subjects (subject_id, tenant_id, canonical_display_name, status)
values
  ('d1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','Subject A','active'),
  ('d2222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','Subject B','active');

insert into public.subject_identities (
  subject_identity_id, tenant_id, subject_id, channel_id, provider, external_subject_id
) values
  ('e1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','d1111111-1111-4111-8111-111111111111','c1111111-1111-4111-8111-111111111111','test','subject-a'),
  ('e2222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','d2222222-2222-4222-8222-222222222222','c2222222-2222-4222-8222-222222222222','test','subject-b');

insert into public.conversations (
  conversation_id, tenant_id, application_id, channel_id, subject_id, primary_agent_id, status
) values
  ('f1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','c1111111-1111-4111-8111-111111111111','d1111111-1111-4111-8111-111111111111','a1111111-1111-4111-8111-111111111111','active'),
  ('f2222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','c2222222-2222-4222-8222-222222222222','d2222222-2222-4222-8222-222222222222','a2222222-2222-4222-8222-222222222222','active');

insert into public.policy_versions (
  policy_version_id, tenant_id, application_id, policy_type, version_number, lifecycle_status,
  policy_document, content_hash, platform_shared, created_by, published_at
) values
  ('01111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','test',1,'PUBLISHED','{}',repeat('a',64),false,'ci',now()),
  ('02222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','test',1,'PUBLISHED','{}',repeat('b',64),false,'ci',now());

insert into public.agent_config_versions (
  config_version_id, tenant_id, application_id, agent_id, version_number, lifecycle_status,
  environment, config_document, published_config_hash, policy_merge_version,
  created_by, published_at, change_note
) values
  ('03111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','a1111111-1111-4111-8111-111111111111',1,'PUBLISHED','development','{}',repeat('c',64),'v1','ci',now(),'ci'),
  ('03222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','a2222222-2222-4222-8222-222222222222',1,'PUBLISHED','development','{}',repeat('d',64),'v1','ci',now(),'ci');

insert into public.agent_activations (
  activation_id, tenant_id, application_id, agent_id, environment, config_version_id, activated_by
) values
  ('04111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','a1111111-1111-4111-8111-111111111111','development','03111111-1111-4111-8111-111111111111','ci'),
  ('04222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','a2222222-2222-4222-8222-222222222222','development','03222222-2222-4222-8222-222222222222','ci');

insert into public.requests (
  request_id, trace_id, tenant_id, application_id, channel_id, agent_id, subject_id, conversation_id,
  environment, request_kind, source, privacy_class, current_status, received_at
) values
  ('05111111-1111-4111-8111-111111111111','11111111111111111111111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','c1111111-1111-4111-8111-111111111111','a1111111-1111-4111-8111-111111111111','d1111111-1111-4111-8111-111111111111','f1111111-1111-4111-8111-111111111111','development','conversation','ci','INTERNAL','RUNNING',now()),
  ('05222222-2222-4222-8222-222222222222','22222222222222222222222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','c2222222-2222-4222-8222-222222222222','a2222222-2222-4222-8222-222222222222','d2222222-2222-4222-8222-222222222222','f2222222-2222-4222-8222-222222222222','development','conversation','ci','INTERNAL','RUNNING',now());

insert into public.trace_spans (
  span_row_id, trace_id, span_id, request_id, tenant_id, span_type, service, operation,
  started_at, status, attempt
) values
  ('06111111-1111-4111-8111-111111111111','11111111111111111111111111111111','1111111111111111','05111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','core.route','core','route',now(),'RUNNING',1),
  ('06222222-2222-4222-8222-222222222222','22222222222222222222222222222222','2222222222222222','05222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','core.route','core','route',now(),'RUNNING',1);

insert into public.trace_span_links (
  trace_span_link_id, tenant_id, request_id, trace_id, span_id, linked_trace_id, relationship
) values
  ('07111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','05111111-1111-4111-8111-111111111111','11111111111111111111111111111111','1111111111111111','33333333333333333333333333333333','causal'),
  ('07222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','05222222-2222-4222-8222-222222222222','22222222222222222222222222222222','2222222222222222','44444444444444444444444444444444','causal');

insert into public.ai_calls (
  ai_call_id, request_id, trace_id, span_id, tenant_id, application_id, agent_id,
  effective_config_version_id, effective_config_hash, provider, model, model_tier, model_role,
  purpose, started_at, ended_at, latency_ms, success
) values
  ('08111111-1111-4111-8111-111111111111','05111111-1111-4111-8111-111111111111','11111111111111111111111111111111','1111111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','a1111111-1111-4111-8111-111111111111','03111111-1111-4111-8111-111111111111','hash-a','test','model-a','small','worker','main_response',now(),now(),0,true),
  ('08222222-2222-4222-8222-222222222222','05222222-2222-4222-8222-222222222222','22222222222222222222222222222222','2222222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','a2222222-2222-4222-8222-222222222222','03222222-2222-4222-8222-222222222222','hash-b','test','model-b','small','worker','main_response',now(),now(),0,true);

insert into public.tool_calls (
  tool_call_id, request_id, trace_id, span_id, tenant_id, application_id, agent_id,
  effective_config_version_id, effective_config_hash, tool_domain, tool_name, tool_version,
  operation, risk_class, privacy_class, policy_decision, started_at, ended_at, latency_ms, success
) values
  ('09111111-1111-4111-8111-111111111111','05111111-1111-4111-8111-111111111111','11111111111111111111111111111111','1111111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','a1111111-1111-4111-8111-111111111111','03111111-1111-4111-8111-111111111111','hash-a','test','tool-a','1','read','READ','INTERNAL','ALLOW',now(),now(),0,true),
  ('09222222-2222-4222-8222-222222222222','05222222-2222-4222-8222-222222222222','22222222222222222222222222222222','2222222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','a2222222-2222-4222-8222-222222222222','03222222-2222-4222-8222-222222222222','hash-b','test','tool-b','1','read','READ','INTERNAL','ALLOW',now(),now(),0,true);

insert into public.retrieval_events (
  retrieval_event_id, tenant_id, application_id, request_id, trace_id, span_id, agent_id,
  retrieval_mode, query_kind, candidate_count, selected_count, retrieval_latency_ms
) values
  ('10111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','05111111-1111-4111-8111-111111111111','11111111111111111111111111111111','1111111111111111','a1111111-1111-4111-8111-111111111111','structured_only','ci',1,1,0),
  ('10222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','05222222-2222-4222-8222-222222222222','22222222222222222222222222222222','2222222222222222','a2222222-2222-4222-8222-222222222222','structured_only','ci',1,1,0);

insert into public.idempotency_records (
  idempotency_record_id, tenant_id, scope, operation, idempotency_key, request_id, state, expires_at
) values
  ('11111111-aaaa-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','ci','op','key-a','05111111-1111-4111-8111-111111111111','IN_PROGRESS',now()+interval '1 hour'),
  ('22222222-bbbb-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','ci','op','key-b','05222222-2222-4222-8222-222222222222','IN_PROGRESS',now()+interval '1 hour');

insert into public.usage_events (
  usage_event_id, occurred_at, tenant_id, application_id, request_id, agent_id, channel_id,
  subject_id, conversation_id, event_type, quantity, unit, dedupe_key, source_type, source_id
) values
  ('12111111-1111-4111-8111-111111111111',now(),'11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','05111111-1111-4111-8111-111111111111','a1111111-1111-4111-8111-111111111111','c1111111-1111-4111-8111-111111111111','d1111111-1111-4111-8111-111111111111','f1111111-1111-4111-8111-111111111111','request',1,'request','usage-a','request','05111111-1111-4111-8111-111111111111'),
  ('12222222-2222-4222-8222-222222222222',now(),'22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','05222222-2222-4222-8222-222222222222','a2222222-2222-4222-8222-222222222222','c2222222-2222-4222-8222-222222222222','d2222222-2222-4222-8222-222222222222','f2222222-2222-4222-8222-222222222222','request',1,'request','usage-b','request','05222222-2222-4222-8222-222222222222');

insert into public.audit_events (
  audit_event_id, tenant_id, application_id, agent_id, config_version_id,
  actor_principal_id, request_id, event_type
) values
  ('13111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','a1111111-1111-4111-8111-111111111111','03111111-1111-4111-8111-111111111111','ci','05111111-1111-4111-8111-111111111111','config.publish'),
  ('13222222-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2','a2222222-2222-4222-8222-222222222222','03222222-2222-4222-8222-222222222222','ci','05222222-2222-4222-8222-222222222222','config.publish');

set local role nippan_runtime;
select set_config('app.tenant_id','11111111-1111-4111-8111-111111111111',true);

do $$
declare
  t text;
  visible_count bigint;
begin
  -- Only tables readable by nippan_runtime belong in this visibility check.
  -- Control-plane-only tables such as workspaces are asserted separately by
  -- tests/sql/phase2_privilege_boundaries.sql.
  foreach t in array array[
    'tenants','applications','agents','channels','agent_channel_bindings',
    'subjects','subject_identities','conversations','policy_versions','agent_config_versions',
    'agent_activations','requests','trace_spans','trace_span_links','ai_calls','tool_calls',
    'retrieval_events','idempotency_records','usage_events','audit_events'
  ] loop
    execute format('select count(*) from public.%I', t) into visible_count;
    if visible_count <> 1 then
      raise exception 'tenant isolation failed for %, expected 1 visible row, got %', t, visible_count;
    end if;
  end loop;
end $$;

-- Missing tenant context must fail closed (zero visible tenant rows).
select set_config('app.tenant_id','',true);

do $$
declare visible_count bigint;
begin
  select count(*) into visible_count from public.requests;
  if visible_count <> 0 then
    raise exception 'missing tenant context did not fail closed';
  end if;
end $$;

reset role;

-- Immutable usage ledger.
do $$
begin
  begin
    update public.usage_events
      set quantity = 2
      where usage_event_id = '12111111-1111-4111-8111-111111111111';
    raise exception 'usage event mutation unexpectedly succeeded';
  exception when sqlstate '55000' then
    null;
  end;
end $$;

-- Dedupe: one measurable event per tenant + dedupe key.
do $$
begin
  begin
    insert into public.usage_events (
      usage_event_id, occurred_at, tenant_id, application_id, request_id,
      event_type, quantity, unit, dedupe_key, source_type, source_id
    ) values (
      '14111111-1111-4111-8111-111111111111',now(),
      '11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '05111111-1111-4111-8111-111111111111','request',1,'request','usage-a','request','dup'
    );
    raise exception 'usage dedupe unexpectedly accepted duplicate';
  exception when unique_violation then
    null;
  end;
end $$;

-- Persistent idempotency uniqueness.
do $$
begin
  begin
    insert into public.idempotency_records (
      idempotency_record_id, tenant_id, scope, operation, idempotency_key,
      request_id, state, expires_at
    ) values (
      '15111111-1111-4111-8111-111111111111',
      '11111111-1111-4111-8111-111111111111','ci','op','key-a',
      '05111111-1111-4111-8111-111111111111','IN_PROGRESS',now()+interval '1 hour'
    );
    raise exception 'idempotency duplicate unexpectedly accepted';
  exception when unique_violation then
    null;
  end;
end $$;

-- Conversation requests require Application + Channel.
do $$
begin
  begin
    insert into public.requests (
      request_id, trace_id, tenant_id, environment, request_kind,
      source, privacy_class, current_status, received_at
    ) values (
      '16111111-1111-4111-8111-111111111111',
      '55555555555555555555555555555555',
      '11111111-1111-4111-8111-111111111111',
      'development','conversation','ci','INTERNAL','RUNNING',now()
    );
    raise exception 'invalid conversation request unexpectedly accepted';
  exception when check_violation then
    null;
  end;
end $$;

-- Published config is immutable.
do $$
begin
  begin
    update public.agent_config_versions
      set change_note = 'mutated'
      where config_version_id = '03111111-1111-4111-8111-111111111111';
    raise exception 'published config mutation unexpectedly accepted';
  exception when sqlstate '55000' then
    null;
  end;
end $$;

rollback;
