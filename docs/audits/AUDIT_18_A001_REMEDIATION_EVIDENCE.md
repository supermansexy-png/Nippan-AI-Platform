# Audit #18 — A-001 Remediation Evidence Package

## 0. Review target and evidence boundary

Repository: `supermansexy-png/Nippan-AI-Platform`

PR: `#24`

Finding: `A-001 — HIGH — Database privileges / runtime boundary`

Audited base SHA:

`1129bc562a238d338bf2761a49e4170588d52735`

Remediation code SHA covered by this package:

`18d8936fbcf29ccec22ab5718950540e87d061f3`

This document is an evidence-only addition after the remediation code SHA above. It does not change the remediation SQL, privilege tests, isolation tests, or CI workflow being reviewed. PR #24 must not be merged until Independent Auditor re-review completes. Builder self-approval is not permitted.

The package is deliberately inline: file contents, scope diff, database ACL query results, negative-control output, and CI evidence are reproduced below so the reviewer does not need to trust Builder summaries or external links alone.

---

## 1. Full content at remediation SHA `18d8936fbcf29ccec22ab5718950540e87d061f3`

### `migrations/20260922193829_phase2_a001_least_privilege.sql`

Blob SHA: `1c701de747f87fb91631c040420ec72a3d61d81e`

```sql
-- Audit #18 Finding A-001 remediation: least-privilege database role boundaries.
-- Baseline: PR #17 @ 1129bc562a238d338bf2761a49e4170588d52735
--
-- Control Plane owns identity/configuration mutation.
-- Data Plane runtime may mutate only conversation/runtime execution state,
-- telemetry, idempotency, usage and audit records required for execution.
-- Analytics remains read-only.
--
-- Existing tenant RLS policies remain unchanged. No role is granted BYPASSRLS.

-- Reset table privileges first so the broad grants from the Phase 2 foundation
-- cannot survive on any current public table.
revoke all on all tables in schema public
  from nippan_runtime, nippan_control_plane, nippan_analytics;

-- Runtime may read the control-plane state required to route and execute work.
grant select on
  public.tenants,
  public.applications,
  public.agents,
  public.channels,
  public.agent_channel_bindings,
  public.subjects,
  public.subject_identities,
  public.policy_versions,
  public.agent_config_versions,
  public.agent_activations
to nippan_runtime;

-- Conversation state and runtime/request telemetry are Data Plane-owned.
grant select, insert, update on
  public.conversations,
  public.requests,
  public.trace_spans,
  public.trace_span_links,
  public.ai_calls,
  public.tool_calls,
  public.retrieval_events,
  public.idempotency_records
to nippan_runtime;

-- Usage and audit ledgers are append-only at the role boundary as well as by
-- their existing database triggers.
grant select, insert on
  public.usage_events,
  public.audit_events
to nippan_runtime;

-- The Control Plane may inspect current platform/runtime state for dashboard
-- operations but may mutate only identity/configuration state plus the
-- idempotency/audit records needed for governed side effects.
grant select on all tables in schema public
to nippan_control_plane;

grant insert, update on
  public.tenants,
  public.workspaces,
  public.applications,
  public.agents,
  public.channels,
  public.agent_channel_bindings,
  public.subjects,
  public.subject_identities,
  public.policy_versions,
  public.agent_config_versions,
  public.agent_activations,
  public.idempotency_records
to nippan_control_plane;

grant insert on
  public.audit_events
to nippan_control_plane;

-- Analytics is strictly read-only.
grant select on all tables in schema public
to nippan_analytics;

```

### `tests/sql/phase2_privilege_boundaries.sql`

Blob SHA: `cbb6edd04a267a360b2a92d2e3387bb24f4fc43a`

```sql
\set ON_ERROR_STOP on

begin;

-- Audit #18 / A-001 privilege regression suite.
-- This test inspects PostgreSQL ACLs directly, so it does not require SET ROLE.
-- It also re-checks the existing RLS and non-BYPASSRLS boundaries.

do $$
declare
  missing_roles text;
  unsafe_roles text;
begin
  select string_agg(v.role_name, ', ' order by v.role_name)
    into missing_roles
  from (values
    ('nippan_runtime'),
    ('nippan_control_plane'),
    ('nippan_analytics')
  ) as v(role_name)
  left join pg_roles r on r.rolname = v.role_name
  where r.rolname is null;

  if missing_roles is not null then
    raise exception 'required roles missing: %', missing_roles;
  end if;

  select string_agg(r.rolname, ', ' order by r.rolname)
    into unsafe_roles
  from pg_roles r
  where r.rolname in ('nippan_runtime','nippan_control_plane','nippan_analytics')
    and (r.rolsuper or r.rolbypassrls);

  if unsafe_roles is not null then
    raise exception 'project role unexpectedly has superuser/BYPASSRLS: %', unsafe_roles;
  end if;
end $$;

create temporary table phase2_privilege_expectations (
  table_name text primary key,
  runtime_select boolean not null,
  runtime_insert boolean not null,
  runtime_update boolean not null,
  control_select boolean not null,
  control_insert boolean not null,
  control_update boolean not null,
  analytics_select boolean not null
);

insert into phase2_privilege_expectations values
  ('tenants',                true,  false, false, true, true,  true,  true),
  ('workspaces',             false, false, false, true, true,  true,  true),
  ('applications',           true,  false, false, true, true,  true,  true),
  ('agents',                 true,  false, false, true, true,  true,  true),
  ('channels',               true,  false, false, true, true,  true,  true),
  ('agent_channel_bindings', true,  false, false, true, true,  true,  true),
  ('subjects',               true,  false, false, true, true,  true,  true),
  ('subject_identities',     true,  false, false, true, true,  true,  true),
  ('conversations',          true,  true,  true,  true, false, false, true),
  ('policy_versions',        true,  false, false, true, true,  true,  true),
  ('agent_config_versions',  true,  false, false, true, true,  true,  true),
  ('agent_activations',      true,  false, false, true, true,  true,  true),
  ('requests',               true,  true,  true,  true, false, false, true),
  ('trace_spans',            true,  true,  true,  true, false, false, true),
  ('trace_span_links',       true,  true,  true,  true, false, false, true),
  ('ai_calls',               true,  true,  true,  true, false, false, true),
  ('tool_calls',             true,  true,  true,  true, false, false, true),
  ('retrieval_events',       true,  true,  true,  true, false, false, true),
  ('idempotency_records',    true,  true,  true,  true, true,  true,  true),
  ('usage_events',           true,  true,  false, true, false, false, true),
  ('audit_events',           true,  true,  false, true, true,  false, true);

do $$
declare
  e record;
  qualified_table text;
begin
  for e in select * from phase2_privilege_expectations order by table_name loop
    qualified_table := format('public.%I', e.table_name);

    if has_table_privilege('nippan_runtime', qualified_table, 'SELECT')
         is distinct from e.runtime_select then
      raise exception 'nippan_runtime SELECT mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_runtime', qualified_table, 'INSERT')
         is distinct from e.runtime_insert then
      raise exception 'nippan_runtime INSERT mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_runtime', qualified_table, 'UPDATE')
         is distinct from e.runtime_update then
      raise exception 'nippan_runtime UPDATE mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_runtime', qualified_table, 'DELETE') then
      raise exception 'nippan_runtime unexpectedly has DELETE on %', qualified_table;
    end if;

    if has_table_privilege('nippan_control_plane', qualified_table, 'SELECT')
         is distinct from e.control_select then
      raise exception 'nippan_control_plane SELECT mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_control_plane', qualified_table, 'INSERT')
         is distinct from e.control_insert then
      raise exception 'nippan_control_plane INSERT mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_control_plane', qualified_table, 'UPDATE')
         is distinct from e.control_update then
      raise exception 'nippan_control_plane UPDATE mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_control_plane', qualified_table, 'DELETE') then
      raise exception 'nippan_control_plane unexpectedly has DELETE on %', qualified_table;
    end if;

    if has_table_privilege('nippan_analytics', qualified_table, 'SELECT')
         is distinct from e.analytics_select then
      raise exception 'nippan_analytics SELECT mismatch on %', qualified_table;
    end if;
    if has_table_privilege('nippan_analytics', qualified_table, 'INSERT')
       or has_table_privilege('nippan_analytics', qualified_table, 'UPDATE')
       or has_table_privilege('nippan_analytics', qualified_table, 'DELETE') then
      raise exception 'nippan_analytics unexpectedly has mutation privilege on %', qualified_table;
    end if;
  end loop;
end $$;

-- A-001 must not weaken the tenant isolation boundary.
do $$
declare
  missing_rls text;
begin
  select string_agg(e.table_name, ', ' order by e.table_name)
    into missing_rls
  from phase2_privilege_expectations e
  left join pg_class c on c.relname = e.table_name
  left join pg_namespace n on n.oid = c.relnamespace and n.nspname = 'public'
  where c.oid is null or not c.relrowsecurity;

  if missing_rls is not null then
    raise exception 'RLS missing/disabled for: %', missing_rls;
  end if;
end $$;

rollback;

```

### `tests/sql/phase2_isolation_invariants.sql`

Blob SHA: `680edac0d9effb46218f8b7397412b278b464644`

```sql
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

```

### `.github/workflows/a001-db-privilege-regression.yml`

Blob SHA: `49444826a501dcdf96619fb2621e94ea1de0b4aa`

```yaml
name: A-001 DB privilege regression

on:
  push:
    branches:
      - audit/a001-least-privilege
  workflow_dispatch:

jobs:
  postgres-regression:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U postgres -d postgres"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10

    env:
      PGHOST: 127.0.0.1
      PGPORT: 5432
      PGUSER: postgres
      PGPASSWORD: postgres
      PGDATABASE: postgres

    steps:
      - uses: actions/checkout@v4

      - name: Prepare Supabase-compatible local roles/extensions
        run: |
          psql -v ON_ERROR_STOP=1 <<'SQL'
          create schema if not exists extensions;
          create extension if not exists pgcrypto with schema extensions;
          do $$
          begin
            if not exists (select 1 from pg_roles where rolname = 'anon') then
              create role anon nologin;
            end if;
            if not exists (select 1 from pg_roles where rolname = 'authenticated') then
              create role authenticated nologin;
            end if;
            if not exists (select 1 from pg_roles where rolname = 'service_role') then
              create role service_role nologin;
            end if;
          end
          $$;
          SQL

      - name: Apply Phase 2 migrations in order
        run: |
          set -euo pipefail
          for file in migrations/*.sql; do
            echo "APPLY $file"
            psql -v ON_ERROR_STOP=1 -f "$file"
          done

      - name: Run A-001 privilege regression
        run: |
          psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_privilege_boundaries.sql

      - name: Run Phase 2 isolation invariants
        run: |
          psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_isolation_invariants.sql

```

---

## 2. Scope proof — base `1129bc562a238d338bf2761a49e4170588d52735` to remediation SHA `18d8936fbcf29ccec22ab5718950540e87d061f3`

A temporary GitHub Actions evidence harness checked out full repository history and ran the requested commands. Harness run: `35780440820`. The harness branch was reset back to `18d8936fbcf29ccec22ab5718950540e87d061f3` after the run and is not part of PR #24.

### 2.1 Exact `git diff --stat`

Command:

```sh
git diff --stat 1129bc562a238d338bf2761a49e4170588d52735..18d8936fbcf29ccec22ab5718950540e87d061f3
```

Output:

```text
.github/workflows/a001-db-privilege-regression.yml |  70 ++++++++++
 .../20260922193829_phase2_a001_least_privilege.sql |  76 +++++++++++
 migrations/README.md                               |   6 +
 tests/sql/phase2_isolation_invariants.sql          |   5 +-
 tests/sql/phase2_privilege_boundaries.sql          | 142 +++++++++++++++++++++
 5 files changed, 298 insertions(+), 1 deletion(-)
```

### 2.2 Full unified diff

Command:

```sh
git diff --no-color 1129bc562a238d338bf2761a49e4170588d52735..18d8936fbcf29ccec22ab5718950540e87d061f3
```

Output:

```diff
diff --git a/.github/workflows/a001-db-privilege-regression.yml b/.github/workflows/a001-db-privilege-regression.yml
new file mode 100644
index 0000000..4944482
--- /dev/null
+++ b/.github/workflows/a001-db-privilege-regression.yml
@@ -0,0 +1,70 @@
+name: A-001 DB privilege regression
+
+on:
+  push:
+    branches:
+      - audit/a001-least-privilege
+  workflow_dispatch:
+
+jobs:
+  postgres-regression:
+    runs-on: ubuntu-latest
+    services:
+      postgres:
+        image: postgres:17
+        env:
+          POSTGRES_PASSWORD: postgres
+          POSTGRES_DB: postgres
+        ports:
+          - 5432:5432
+        options: >-
+          --health-cmd "pg_isready -U postgres -d postgres"
+          --health-interval 5s
+          --health-timeout 5s
+          --health-retries 10
+
+    env:
+      PGHOST: 127.0.0.1
+      PGPORT: 5432
+      PGUSER: postgres
+      PGPASSWORD: postgres
+      PGDATABASE: postgres
+
+    steps:
+      - uses: actions/checkout@v4
+
+      - name: Prepare Supabase-compatible local roles/extensions
+        run: |
+          psql -v ON_ERROR_STOP=1 <<'SQL'
+          create schema if not exists extensions;
+          create extension if not exists pgcrypto with schema extensions;
+          do $$
+          begin
+            if not exists (select 1 from pg_roles where rolname = 'anon') then
+              create role anon nologin;
+            end if;
+            if not exists (select 1 from pg_roles where rolname = 'authenticated') then
+              create role authenticated nologin;
+            end if;
+            if not exists (select 1 from pg_roles where rolname = 'service_role') then
+              create role service_role nologin;
+            end if;
+          end
+          $$;
+          SQL
+
+      - name: Apply Phase 2 migrations in order
+        run: |
+          set -euo pipefail
+          for file in migrations/*.sql; do
+            echo "APPLY $file"
+            psql -v ON_ERROR_STOP=1 -f "$file"
+          done
+
+      - name: Run A-001 privilege regression
+        run: |
+          psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_privilege_boundaries.sql
+
+      - name: Run Phase 2 isolation invariants
+        run: |
+          psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_isolation_invariants.sql
diff --git a/migrations/20260922193829_phase2_a001_least_privilege.sql b/migrations/20260922193829_phase2_a001_least_privilege.sql
new file mode 100644
index 0000000..1c701de
--- /dev/null
+++ b/migrations/20260922193829_phase2_a001_least_privilege.sql
@@ -0,0 +1,76 @@
+-- Audit #18 Finding A-001 remediation: least-privilege database role boundaries.
+-- Baseline: PR #17 @ 1129bc562a238d338bf2761a49e4170588d52735
+--
+-- Control Plane owns identity/configuration mutation.
+-- Data Plane runtime may mutate only conversation/runtime execution state,
+-- telemetry, idempotency, usage and audit records required for execution.
+-- Analytics remains read-only.
+--
+-- Existing tenant RLS policies remain unchanged. No role is granted BYPASSRLS.
+
+-- Reset table privileges first so the broad grants from the Phase 2 foundation
+-- cannot survive on any current public table.
+revoke all on all tables in schema public
+  from nippan_runtime, nippan_control_plane, nippan_analytics;
+
+-- Runtime may read the control-plane state required to route and execute work.
+grant select on
+  public.tenants,
+  public.applications,
+  public.agents,
+  public.channels,
+  public.agent_channel_bindings,
+  public.subjects,
+  public.subject_identities,
+  public.policy_versions,
+  public.agent_config_versions,
+  public.agent_activations
+to nippan_runtime;
+
+-- Conversation state and runtime/request telemetry are Data Plane-owned.
+grant select, insert, update on
+  public.conversations,
+  public.requests,
+  public.trace_spans,
+  public.trace_span_links,
+  public.ai_calls,
+  public.tool_calls,
+  public.retrieval_events,
+  public.idempotency_records
+to nippan_runtime;
+
+-- Usage and audit ledgers are append-only at the role boundary as well as by
+-- their existing database triggers.
+grant select, insert on
+  public.usage_events,
+  public.audit_events
+to nippan_runtime;
+
+-- The Control Plane may inspect current platform/runtime state for dashboard
+-- operations but may mutate only identity/configuration state plus the
+-- idempotency/audit records needed for governed side effects.
+grant select on all tables in schema public
+to nippan_control_plane;
+
+grant insert, update on
+  public.tenants,
+  public.workspaces,
+  public.applications,
+  public.agents,
+  public.channels,
+  public.agent_channel_bindings,
+  public.subjects,
+  public.subject_identities,
+  public.policy_versions,
+  public.agent_config_versions,
+  public.agent_activations,
+  public.idempotency_records
+to nippan_control_plane;
+
+grant insert on
+  public.audit_events
+to nippan_control_plane;
+
+-- Analytics is strictly read-only.
+grant select on all tables in schema public
+to nippan_analytics;
diff --git a/migrations/README.md b/migrations/README.md
index 573ceed..b20d709 100644
--- a/migrations/README.md
+++ b/migrations/README.md
@@ -13,8 +13,14 @@ Applied to Supabase `nippan-ai-platform`:
 - `20260922180029_phase2_request_trace_telemetry.sql`
 - `20260922180107_phase2_idempotency_usage_audit.sql`
 
+Pending independent remediation review before application:
+
+- `20260922193829_phase2_a001_least_privilege.sql` — Audit #18 Finding A-001; replaces broad runtime/control-plane table mutation grants with explicit least-privilege role boundaries.
+
 The first migration establishes identity, ownership, Agent/Channel binding, config/policy versioning, activation invariants and tenant RLS. The follow-up index migration addresses FK advisor findings. The telemetry migration adds request/span/model/tool/retrieval operational truth. The idempotency/usage/audit migration adds persistent side-effect dedupe, an immutable UsageEvent ledger and append-only audit events.
 
+The A-001 remediation migration is intentionally additive instead of rewriting an already-applied migration. It revokes current project-role table privileges and re-grants an explicit matrix: runtime can mutate conversation/runtime telemetry/idempotency and append usage/audit records; control plane owns identity/configuration mutation plus governed idempotency/audit writes; analytics remains read-only. Existing RLS policies are unchanged and all project roles remain non-`BYPASSRLS`.
+
 Apply DDL through the connected Supabase project and keep checked-in SQL aligned with applied migration history. Runtime access uses the non-owner, non-`BYPASSRLS` roles described in `docs/decisions/ADR-0007-supabase-schema-baseline.md`.
 
 Memory/embedding DDL remains deferred until benchmark fixtures choose an embedding model and vector dimension.
diff --git a/tests/sql/phase2_isolation_invariants.sql b/tests/sql/phase2_isolation_invariants.sql
index 3938a68..680edac 100644
--- a/tests/sql/phase2_isolation_invariants.sql
+++ b/tests/sql/phase2_isolation_invariants.sql
@@ -170,8 +170,11 @@ declare
   t text;
   visible_count bigint;
 begin
+  -- Only tables readable by nippan_runtime belong in this visibility check.
+  -- Control-plane-only tables such as workspaces are asserted separately by
+  -- tests/sql/phase2_privilege_boundaries.sql.
   foreach t in array array[
-    'tenants','workspaces','applications','agents','channels','agent_channel_bindings',
+    'tenants','applications','agents','channels','agent_channel_bindings',
     'subjects','subject_identities','conversations','policy_versions','agent_config_versions',
     'agent_activations','requests','trace_spans','trace_span_links','ai_calls','tool_calls',
     'retrieval_events','idempotency_records','usage_events','audit_events'
diff --git a/tests/sql/phase2_privilege_boundaries.sql b/tests/sql/phase2_privilege_boundaries.sql
new file mode 100644
index 0000000..cbb6edd
--- /dev/null
+++ b/tests/sql/phase2_privilege_boundaries.sql
@@ -0,0 +1,142 @@
+\set ON_ERROR_STOP on
+
+begin;
+
+-- Audit #18 / A-001 privilege regression suite.
+-- This test inspects PostgreSQL ACLs directly, so it does not require SET ROLE.
+-- It also re-checks the existing RLS and non-BYPASSRLS boundaries.
+
+do $$
+declare
+  missing_roles text;
+  unsafe_roles text;
+begin
+  select string_agg(v.role_name, ', ' order by v.role_name)
+    into missing_roles
+  from (values
+    ('nippan_runtime'),
+    ('nippan_control_plane'),
+    ('nippan_analytics')
+  ) as v(role_name)
+  left join pg_roles r on r.rolname = v.role_name
+  where r.rolname is null;
+
+  if missing_roles is not null then
+    raise exception 'required roles missing: %', missing_roles;
+  end if;
+
+  select string_agg(r.rolname, ', ' order by r.rolname)
+    into unsafe_roles
+  from pg_roles r
+  where r.rolname in ('nippan_runtime','nippan_control_plane','nippan_analytics')
+    and (r.rolsuper or r.rolbypassrls);
+
+  if unsafe_roles is not null then
+    raise exception 'project role unexpectedly has superuser/BYPASSRLS: %', unsafe_roles;
+  end if;
+end $$;
+
+create temporary table phase2_privilege_expectations (
+  table_name text primary key,
+  runtime_select boolean not null,
+  runtime_insert boolean not null,
+  runtime_update boolean not null,
+  control_select boolean not null,
+  control_insert boolean not null,
+  control_update boolean not null,
+  analytics_select boolean not null
+);
+
+insert into phase2_privilege_expectations values
+  ('tenants',                true,  false, false, true, true,  true,  true),
+  ('workspaces',             false, false, false, true, true,  true,  true),
+  ('applications',           true,  false, false, true, true,  true,  true),
+  ('agents',                 true,  false, false, true, true,  true,  true),
+  ('channels',               true,  false, false, true, true,  true,  true),
+  ('agent_channel_bindings', true,  false, false, true, true,  true,  true),
+  ('subjects',               true,  false, false, true, true,  true,  true),
+  ('subject_identities',     true,  false, false, true, true,  true,  true),
+  ('conversations',          true,  true,  true,  true, false, false, true),
+  ('policy_versions',        true,  false, false, true, true,  true,  true),
+  ('agent_config_versions',  true,  false, false, true, true,  true,  true),
+  ('agent_activations',      true,  false, false, true, true,  true,  true),
+  ('requests',               true,  true,  true,  true, false, false, true),
+  ('trace_spans',            true,  true,  true,  true, false, false, true),
+  ('trace_span_links',       true,  true,  true,  true, false, false, true),
+  ('ai_calls',               true,  true,  true,  true, false, false, true),
+  ('tool_calls',             true,  true,  true,  true, false, false, true),
+  ('retrieval_events',       true,  true,  true,  true, false, false, true),
+  ('idempotency_records',    true,  true,  true,  true, true,  true,  true),
+  ('usage_events',           true,  true,  false, true, false, false, true),
+  ('audit_events',           true,  true,  false, true, true,  false, true);
+
+do $$
+declare
+  e record;
+  qualified_table text;
+begin
+  for e in select * from phase2_privilege_expectations order by table_name loop
+    qualified_table := format('public.%I', e.table_name);
+
+    if has_table_privilege('nippan_runtime', qualified_table, 'SELECT')
+         is distinct from e.runtime_select then
+      raise exception 'nippan_runtime SELECT mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_runtime', qualified_table, 'INSERT')
+         is distinct from e.runtime_insert then
+      raise exception 'nippan_runtime INSERT mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_runtime', qualified_table, 'UPDATE')
+         is distinct from e.runtime_update then
+      raise exception 'nippan_runtime UPDATE mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_runtime', qualified_table, 'DELETE') then
+      raise exception 'nippan_runtime unexpectedly has DELETE on %', qualified_table;
+    end if;
+
+    if has_table_privilege('nippan_control_plane', qualified_table, 'SELECT')
+         is distinct from e.control_select then
+      raise exception 'nippan_control_plane SELECT mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_control_plane', qualified_table, 'INSERT')
+         is distinct from e.control_insert then
+      raise exception 'nippan_control_plane INSERT mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_control_plane', qualified_table, 'UPDATE')
+         is distinct from e.control_update then
+      raise exception 'nippan_control_plane UPDATE mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_control_plane', qualified_table, 'DELETE') then
+      raise exception 'nippan_control_plane unexpectedly has DELETE on %', qualified_table;
+    end if;
+
+    if has_table_privilege('nippan_analytics', qualified_table, 'SELECT')
+         is distinct from e.analytics_select then
+      raise exception 'nippan_analytics SELECT mismatch on %', qualified_table;
+    end if;
+    if has_table_privilege('nippan_analytics', qualified_table, 'INSERT')
+       or has_table_privilege('nippan_analytics', qualified_table, 'UPDATE')
+       or has_table_privilege('nippan_analytics', qualified_table, 'DELETE') then
+      raise exception 'nippan_analytics unexpectedly has mutation privilege on %', qualified_table;
+    end if;
+  end loop;
+end $$;
+
+-- A-001 must not weaken the tenant isolation boundary.
+do $$
+declare
+  missing_rls text;
+begin
+  select string_agg(e.table_name, ', ' order by e.table_name)
+    into missing_rls
+  from phase2_privilege_expectations e
+  left join pg_class c on c.relname = e.table_name
+  left join pg_namespace n on n.oid = c.relnamespace and n.nspname = 'public'
+  where c.oid is null or not c.relrowsecurity;
+
+  if missing_rls is not null then
+    raise exception 'RLS missing/disabled for: %', missing_rls;
+  end if;
+end $$;
+
+rollback;
```

GitHub Compare API independently reports `5` changed files, `298` insertions and `1` deletion across this same base/head pair.

---

## 3. Test-integrity proof for `phase2_isolation_invariants.sql`

Baseline blob SHA: `3938a689c2d4a6418b9d52411f1f8b11560a9388`

Head blob SHA: `680edac0d9effb46218f8b7397412b278b464644`

Exact file patch from the base/head comparison:

```diff
@@ -170,8 +170,11 @@ declare
   t text;
   visible_count bigint;
 begin
+  -- Only tables readable by nippan_runtime belong in this visibility check.
+  -- Control-plane-only tables such as workspaces are asserted separately by
+  -- tests/sql/phase2_privilege_boundaries.sql.
   foreach t in array array[
-    'tenants','workspaces','applications','agents','channels','agent_channel_bindings',
+    'tenants','applications','agents','channels','agent_channel_bindings',
     'subjects','subject_identities','conversations','policy_versions','agent_config_versions',
     'agent_activations','requests','trace_spans','trace_span_links','ai_calls','tool_calls',
     'retrieval_events','idempotency_records','usage_events','audit_events'
```

### Assertions retained / changed

- RLS-enabled guard over all 21 tenant-owned tables remains present; `workspaces` remains in `phase2_expected_tables`.
- Tenant-scoped visibility check remains present for every table that `nippan_runtime` is allowed to SELECT.
- Missing tenant context fail-closed assertion remains present.
- Usage ledger immutability assertion remains present.
- Usage dedupe assertion remains present.
- Persistent idempotency uniqueness assertion remains present.
- Conversation request Application + Channel constraint assertion remains present.
- Published config immutability assertion remains present.
- The only deletion in the isolation-suite diff is `workspaces` from the runtime SELECT visibility loop. That table is now intentionally unreadable by runtime and is asserted as `runtime_select=false` in `phase2_privilege_boundaries.sql`.

No isolation/security assertion block was deleted merely to make CI pass. The removed `workspaces` entry was a runtime-read expectation that became invalid when A-001 correctly removed runtime SELECT on `workspaces`; RLS coverage for `workspaces` is still tested, and the new privilege suite explicitly fails if runtime receives SELECT/INSERT/UPDATE/DELETE on that table.

---

## 4. Database privilege proof after applying migrations

Evidence source: ephemeral PostgreSQL 17 GitHub Actions run `35780158998`.

The temporary evidence harness commit was `335862746447e07baa0f81907d6b365570265ef5`. GitHub commit metadata proves:

- parent: `18d8936fbcf29ccec22ab5718950540e87d061f3`
- changed file in harness commit: `.github/workflows/a001-negative-control-evidence.yml`

Therefore all Phase 2/A-001 migration and test files executed by this harness came from remediation SHA `18d8936fbcf29ccec22ab5718950540e87d061f3`; the only harness-only change was the temporary workflow file. After evidence collection, the temporary branch ref was force-reset to `18d8936fbcf29ccec22ab5718950540e87d061f3`.

The database proof queries ran after applying every `migrations/*.sql` file and before introducing the negative-control grant.

### 4.1 Actual role/table grants

Query:

```sql
select grantee, table_schema, table_name, privilege_type, is_grantable
from information_schema.role_table_grants
where grantee in ('nippan_runtime','nippan_control_plane','nippan_analytics')
  and table_schema='public'
order by grantee, table_name, privilege_type;
```

Output:

```text
=== ROLE TABLE GRANTS ===
       grantee        | table_schema |       table_name       | privilege_type | is_grantable 
----------------------+--------------+------------------------+----------------+--------------
 nippan_analytics     | public       | agent_activations      | SELECT         | NO
 nippan_analytics     | public       | agent_channel_bindings | SELECT         | NO
 nippan_analytics     | public       | agent_config_versions  | SELECT         | NO
 nippan_analytics     | public       | agents                 | SELECT         | NO
 nippan_analytics     | public       | ai_calls               | SELECT         | NO
 nippan_analytics     | public       | applications           | SELECT         | NO
 nippan_analytics     | public       | audit_events           | SELECT         | NO
 nippan_analytics     | public       | channels               | SELECT         | NO
 nippan_analytics     | public       | conversations          | SELECT         | NO
 nippan_analytics     | public       | idempotency_records    | SELECT         | NO
 nippan_analytics     | public       | policy_versions        | SELECT         | NO
 nippan_analytics     | public       | requests               | SELECT         | NO
 nippan_analytics     | public       | retrieval_events       | SELECT         | NO
 nippan_analytics     | public       | subject_identities     | SELECT         | NO
 nippan_analytics     | public       | subjects               | SELECT         | NO
 nippan_analytics     | public       | tenants                | SELECT         | NO
 nippan_analytics     | public       | tool_calls             | SELECT         | NO
 nippan_analytics     | public       | trace_span_links       | SELECT         | NO
 nippan_analytics     | public       | trace_spans            | SELECT         | NO
 nippan_analytics     | public       | usage_events           | SELECT         | NO
 nippan_analytics     | public       | workspaces             | SELECT         | NO
 nippan_control_plane | public       | agent_activations      | INSERT         | NO
 nippan_control_plane | public       | agent_activations      | SELECT         | NO
 nippan_control_plane | public       | agent_activations      | UPDATE         | NO
 nippan_control_plane | public       | agent_channel_bindings | INSERT         | NO
 nippan_control_plane | public       | agent_channel_bindings | SELECT         | NO
 nippan_control_plane | public       | agent_channel_bindings | UPDATE         | NO
 nippan_control_plane | public       | agent_config_versions  | INSERT         | NO
 nippan_control_plane | public       | agent_config_versions  | SELECT         | NO
 nippan_control_plane | public       | agent_config_versions  | UPDATE         | NO
 nippan_control_plane | public       | agents                 | INSERT         | NO
 nippan_control_plane | public       | agents                 | SELECT         | NO
 nippan_control_plane | public       | agents                 | UPDATE         | NO
 nippan_control_plane | public       | ai_calls               | SELECT         | NO
 nippan_control_plane | public       | applications           | INSERT         | NO
 nippan_control_plane | public       | applications           | SELECT         | NO
 nippan_control_plane | public       | applications           | UPDATE         | NO
 nippan_control_plane | public       | audit_events           | INSERT         | NO
 nippan_control_plane | public       | audit_events           | SELECT         | NO
 nippan_control_plane | public       | channels               | INSERT         | NO
 nippan_control_plane | public       | channels               | SELECT         | NO
 nippan_control_plane | public       | channels               | UPDATE         | NO
 nippan_control_plane | public       | conversations          | SELECT         | NO
 nippan_control_plane | public       | idempotency_records    | INSERT         | NO
 nippan_control_plane | public       | idempotency_records    | SELECT         | NO
 nippan_control_plane | public       | idempotency_records    | UPDATE         | NO
 nippan_control_plane | public       | policy_versions        | INSERT         | NO
 nippan_control_plane | public       | policy_versions        | SELECT         | NO
 nippan_control_plane | public       | policy_versions        | UPDATE         | NO
 nippan_control_plane | public       | requests               | SELECT         | NO
 nippan_control_plane | public       | retrieval_events       | SELECT         | NO
 nippan_control_plane | public       | subject_identities     | INSERT         | NO
 nippan_control_plane | public       | subject_identities     | SELECT         | NO
 nippan_control_plane | public       | subject_identities     | UPDATE         | NO
 nippan_control_plane | public       | subjects               | INSERT         | NO
 nippan_control_plane | public       | subjects               | SELECT         | NO
 nippan_control_plane | public       | subjects               | UPDATE         | NO
 nippan_control_plane | public       | tenants                | INSERT         | NO
 nippan_control_plane | public       | tenants                | SELECT         | NO
 nippan_control_plane | public       | tenants                | UPDATE         | NO
 nippan_control_plane | public       | tool_calls             | SELECT         | NO
 nippan_control_plane | public       | trace_span_links       | SELECT         | NO
 nippan_control_plane | public       | trace_spans            | SELECT         | NO
 nippan_control_plane | public       | usage_events           | SELECT         | NO
 nippan_control_plane | public       | workspaces             | INSERT         | NO
 nippan_control_plane | public       | workspaces             | SELECT         | NO
 nippan_control_plane | public       | workspaces             | UPDATE         | NO
 nippan_runtime       | public       | agent_activations      | SELECT         | NO
 nippan_runtime       | public       | agent_channel_bindings | SELECT         | NO
 nippan_runtime       | public       | agent_config_versions  | SELECT         | NO
 nippan_runtime       | public       | agents                 | SELECT         | NO
 nippan_runtime       | public       | ai_calls               | INSERT         | NO
 nippan_runtime       | public       | ai_calls               | SELECT         | NO
 nippan_runtime       | public       | ai_calls               | UPDATE         | NO
 nippan_runtime       | public       | applications           | SELECT         | NO
 nippan_runtime       | public       | audit_events           | INSERT         | NO
 nippan_runtime       | public       | audit_events           | SELECT         | NO
 nippan_runtime       | public       | channels               | SELECT         | NO
 nippan_runtime       | public       | conversations          | INSERT         | NO
 nippan_runtime       | public       | conversations          | SELECT         | NO
 nippan_runtime       | public       | conversations          | UPDATE         | NO
 nippan_runtime       | public       | idempotency_records    | INSERT         | NO
 nippan_runtime       | public       | idempotency_records    | SELECT         | NO
 nippan_runtime       | public       | idempotency_records    | UPDATE         | NO
 nippan_runtime       | public       | policy_versions        | SELECT         | NO
 nippan_runtime       | public       | requests               | INSERT         | NO
 nippan_runtime       | public       | requests               | SELECT         | NO
 nippan_runtime       | public       | requests               | UPDATE         | NO
 nippan_runtime       | public       | retrieval_events       | INSERT         | NO
 nippan_runtime       | public       | retrieval_events       | SELECT         | NO
 nippan_runtime       | public       | retrieval_events       | UPDATE         | NO
 nippan_runtime       | public       | subject_identities     | SELECT         | NO
 nippan_runtime       | public       | subjects               | SELECT         | NO
 nippan_runtime       | public       | tenants                | SELECT         | NO
 nippan_runtime       | public       | tool_calls             | INSERT         | NO
 nippan_runtime       | public       | tool_calls             | SELECT         | NO
 nippan_runtime       | public       | tool_calls             | UPDATE         | NO
 nippan_runtime       | public       | trace_span_links       | INSERT         | NO
 nippan_runtime       | public       | trace_span_links       | SELECT         | NO
 nippan_runtime       | public       | trace_span_links       | UPDATE         | NO
 nippan_runtime       | public       | trace_spans            | INSERT         | NO
 nippan_runtime       | public       | trace_spans            | SELECT         | NO
 nippan_runtime       | public       | trace_spans            | UPDATE         | NO
 nippan_runtime       | public       | usage_events           | INSERT         | NO
 nippan_runtime       | public       | usage_events           | SELECT         | NO
(105 rows)
```

### 4.2 Actual role flags

Query:

```sql
select rolname, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb, rolcanlogin, rolinherit
from pg_roles
where rolname in ('nippan_runtime','nippan_control_plane','nippan_analytics')
order by rolname;
```

Output:

```text
=== ROLE FLAGS ===
       rolname        | rolsuper | rolbypassrls | rolcreaterole | rolcreatedb | rolcanlogin | rolinherit 
----------------------+----------+--------------+---------------+-------------+-------------+------------
 nippan_analytics     | f        | f            | f             | f           | f           | f
 nippan_control_plane | f        | f            | f             | f           | f           | f
 nippan_runtime       | f        | f            | f             | f           | f           | f
(3 rows)
```

This proves all three project roles have `rolsuper=false`, `rolbypassrls=false`, `rolcreaterole=false`, `rolcreatedb=false`, and `rolcanlogin=false`.

### 4.3 Actual `pg_default_acl`

Query:

```sql
select d.defaclrole::regrole as owner,
       coalesce(n.nspname,'<all schemas>') as schema_name,
       d.defaclobjtype,
       d.defaclacl
from pg_default_acl d
left join pg_namespace n on n.oid=d.defaclnamespace
order by 1,2,3;
```

Output:

```text
=== DEFAULT ACL ===
 owner | schema_name | defaclobjtype | defaclacl 
-------+-------------+---------------+-----------
(0 rows)
```

The ephemeral database had no custom default ACL rows after the migrations; in particular there was no default table-mutation grant to any project role.

### 4.4 Explicit SELECT/INSERT/UPDATE/DELETE matrix

Query:

```sql
with roles(role_name) as (
  values ('nippan_runtime'),('nippan_control_plane'),('nippan_analytics')
), tables(table_name) as (
  values
  ('tenants'),('workspaces'),('applications'),('agents'),('channels'),
  ('agent_channel_bindings'),('subjects'),('subject_identities'),('conversations'),
  ('policy_versions'),('agent_config_versions'),('agent_activations'),('requests'),
  ('trace_spans'),('trace_span_links'),('ai_calls'),('tool_calls'),('retrieval_events'),
  ('idempotency_records'),('usage_events'),('audit_events')
)
select role_name, table_name,
       has_table_privilege(role_name, 'public.'||table_name, 'SELECT') as sel,
       has_table_privilege(role_name, 'public.'||table_name, 'INSERT') as ins,
       has_table_privilege(role_name, 'public.'||table_name, 'UPDATE') as upd,
       has_table_privilege(role_name, 'public.'||table_name, 'DELETE') as del
from roles cross join tables
order by role_name, table_name;
```

Output:

```text
=== EXPLICIT PRIVILEGE MATRIX ===
      role_name       |       table_name       | sel | ins | upd | del 
----------------------+------------------------+-----+-----+-----+-----
 nippan_analytics     | agent_activations      | t   | f   | f   | f
 nippan_analytics     | agent_channel_bindings | t   | f   | f   | f
 nippan_analytics     | agent_config_versions  | t   | f   | f   | f
 nippan_analytics     | agents                 | t   | f   | f   | f
 nippan_analytics     | ai_calls               | t   | f   | f   | f
 nippan_analytics     | applications           | t   | f   | f   | f
 nippan_analytics     | audit_events           | t   | f   | f   | f
 nippan_analytics     | channels               | t   | f   | f   | f
 nippan_analytics     | conversations          | t   | f   | f   | f
 nippan_analytics     | idempotency_records    | t   | f   | f   | f
 nippan_analytics     | policy_versions        | t   | f   | f   | f
 nippan_analytics     | requests               | t   | f   | f   | f
 nippan_analytics     | retrieval_events       | t   | f   | f   | f
 nippan_analytics     | subject_identities     | t   | f   | f   | f
 nippan_analytics     | subjects               | t   | f   | f   | f
 nippan_analytics     | tenants                | t   | f   | f   | f
 nippan_analytics     | tool_calls             | t   | f   | f   | f
 nippan_analytics     | trace_span_links       | t   | f   | f   | f
 nippan_analytics     | trace_spans            | t   | f   | f   | f
 nippan_analytics     | usage_events           | t   | f   | f   | f
 nippan_analytics     | workspaces             | t   | f   | f   | f
 nippan_control_plane | agent_activations      | t   | t   | t   | f
 nippan_control_plane | agent_channel_bindings | t   | t   | t   | f
 nippan_control_plane | agent_config_versions  | t   | t   | t   | f
 nippan_control_plane | agents                 | t   | t   | t   | f
 nippan_control_plane | ai_calls               | t   | f   | f   | f
 nippan_control_plane | applications           | t   | t   | t   | f
 nippan_control_plane | audit_events           | t   | t   | f   | f
 nippan_control_plane | channels               | t   | t   | t   | f
 nippan_control_plane | conversations          | t   | f   | f   | f
 nippan_control_plane | idempotency_records    | t   | t   | t   | f
 nippan_control_plane | policy_versions        | t   | t   | t   | f
 nippan_control_plane | requests               | t   | f   | f   | f
 nippan_control_plane | retrieval_events       | t   | f   | f   | f
 nippan_control_plane | subject_identities     | t   | t   | t   | f
 nippan_control_plane | subjects               | t   | t   | t   | f
 nippan_control_plane | tenants                | t   | t   | t   | f
 nippan_control_plane | tool_calls             | t   | f   | f   | f
 nippan_control_plane | trace_span_links       | t   | f   | f   | f
 nippan_control_plane | trace_spans            | t   | f   | f   | f
 nippan_control_plane | usage_events           | t   | f   | f   | f
 nippan_control_plane | workspaces             | t   | t   | t   | f
 nippan_runtime       | agent_activations      | t   | f   | f   | f
 nippan_runtime       | agent_channel_bindings | t   | f   | f   | f
 nippan_runtime       | agent_config_versions  | t   | f   | f   | f
 nippan_runtime       | agents                 | t   | f   | f   | f
 nippan_runtime       | ai_calls               | t   | t   | t   | f
 nippan_runtime       | applications           | t   | f   | f   | f
 nippan_runtime       | audit_events           | t   | t   | f   | f
 nippan_runtime       | channels               | t   | f   | f   | f
 nippan_runtime       | conversations          | t   | t   | t   | f
 nippan_runtime       | idempotency_records    | t   | t   | t   | f
 nippan_runtime       | policy_versions        | t   | f   | f   | f
 nippan_runtime       | requests               | t   | t   | t   | f
 nippan_runtime       | retrieval_events       | t   | t   | t   | f
 nippan_runtime       | subject_identities     | t   | f   | f   | f
 nippan_runtime       | subjects               | t   | f   | f   | f
 nippan_runtime       | tenants                | t   | f   | f   | f
 nippan_runtime       | tool_calls             | t   | t   | t   | f
 nippan_runtime       | trace_span_links       | t   | t   | t   | f
 nippan_runtime       | trace_spans            | t   | t   | t   | f
 nippan_runtime       | usage_events           | t   | t   | f   | f
 nippan_runtime       | workspaces             | f   | f   | f   | f
(63 rows)
```

Interpretation directly from the matrix:

- `nippan_runtime` cannot INSERT/UPDATE/DELETE identity/config/control-plane tables; `workspaces` is not readable at all, and other control/config tables needed for execution are SELECT-only.
- `nippan_runtime` can mutate only `conversations`, request/trace/model/tool/retrieval telemetry, and `idempotency_records`; `usage_events` and `audit_events` are INSERT-only for mutation.
- `nippan_control_plane` has SELECT on all current tables, INSERT/UPDATE only on identity/configuration plus `idempotency_records`, INSERT-only on `audit_events`, and no DELETE privilege.
- `nippan_analytics` has SELECT only on every current table and no INSERT/UPDATE/DELETE privilege.
- None of the three roles has SUPERUSER or BYPASSRLS.

---

## 5. Negative control

The violating grant was introduced only inside an ephemeral PostgreSQL job on a temporary evidence branch; it was never committed to PR #24 or to any migration.

Temporary statement:

```sql
grant update on public.agent_config_versions to nippan_runtime;
```

The regression suite was then run with `ON_ERROR_STOP=1`. Actual output:

```text
REVOKE
REVOKE
REVOKE
GRANT
GRANT
REVOKE
REVOKE
REVOKE
REVOKE
GRANT
GRANT
REVOKE
GRANT
GRANT
REVOKE
REVOKE
REVOKE
REVOKE
GRANT
GRANT
GRANT
REVOKE
GRANT
GRANT
GRANT
GRANT
GRANT
GRANT
GRANT
echo "NEGATIVE_CONTROL_EXIT_CODE=$rc"
grep -F "nippan_runtime UPDATE mismatch on public.agent_config_versions" /tmp/a001-negative.log
echo "NEGATIVE_CONTROL_EXPECTED_FAILURE_CONFIRMED"
GRANT
psql:tests/sql/phase2_privilege_boundaries.sql:123: ERROR:  nippan_runtime UPDATE mismatch on public.agent_config_versions
NEGATIVE_CONTROL_EXIT_CODE=3
psql:tests/sql/phase2_privilege_boundaries.sql:123: ERROR:  nippan_runtime UPDATE mismatch on public.agent_config_versions
NEGATIVE_CONTROL_EXPECTED_FAILURE_CONFIRMED
REVOKE
 2026-09-22 20:25:34.628 UTC [86] ERROR:  nippan_runtime UPDATE mismatch on public.agent_config_versions
```

The expected failure was therefore observed with exit code `3` and the exact assertion:

`nippan_runtime UPDATE mismatch on public.agent_config_versions`

The temporary grant was revoked:

```sql
revoke update on public.agent_config_versions from nippan_runtime;
```

The same job then reran the clean suites. Job/step conclusions:

- Set up job: completed / success
- Initialize containers: completed / success
- Run actions/checkout@v4: completed / success
- Bind run to commit: completed / success
- Prepare Supabase-compatible local roles/extensions: completed / success
- Apply exact Phase 2 + A-001 migrations: completed / success
- Database privilege proof: completed / success
- Normal privilege regression must pass before negative control: completed / success
- Negative control must be detected: completed / success
- Clean-state privilege regression must pass: completed / success
- Clean-state isolation suite must pass: completed / success
- Post Run actions/checkout@v4: completed / success
- Stop containers: completed / success
- Complete job: completed / success

Result:

- normal privilege suite before negative control: PASS
- violating grant inserted ephemerally: privilege suite FAIL as expected
- violating grant revoked: PASS
- clean privilege suite after revoke: PASS
- clean isolation suite after revoke: PASS
- workflow job conclusion: SUCCESS

Temporary evidence branch was reset to `18d8936fbcf29ccec22ab5718950540e87d061f3` after evidence collection; the harness workflow/violating statement is not part of PR #24.

---

## 6. CI evidence — GitHub Actions run `35775485700`

GitHub run metadata:

- event: `push`
- run status: `completed`
- run conclusion: `success`
- run head branch: `audit/a001-least-privilege`
- run head SHA: `18d8936fbcf29ccec22ab5718950540e87d061f3`
- PR association: `#24`
- PR base SHA recorded by GitHub: `1129bc562a238d338bf2761a49e4170588d52735`
- PR head SHA recorded by GitHub: `18d8936fbcf29ccec22ab5718950540e87d061f3`
- head commit ID: `18d8936fbcf29ccec22ab5718950540e87d061f3`

For this push-triggered run, GitHub metadata binds the run to `18d8936fbcf29ccec22ab5718950540e87d061f3`. The original workflow did not separately print the literal `GITHUB_SHA` environment variable, so this package does not fabricate such a line. The checkout log independently proves the same commit was fetched and checked out:

```text
[command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +18d8936fbcf29ccec22ab5718950540e87d061f3:refs/remotes/origin/audit/a001-least-privilege
18d8936fbcf29ccec22ab5718950540e87d061f3
APPLY migrations/20260922174011_phase2_core_foundation.sql
APPLY migrations/20260922174227_phase2_core_fk_indexes.sql
APPLY migrations/20260922180029_phase2_request_trace_telemetry.sql
APPLY migrations/20260922180107_phase2_idempotency_usage_audit.sql
APPLY migrations/20260922193829_phase2_a001_least_privilege.sql
##[group]Run psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_privilege_boundaries.sql
psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_privilege_boundaries.sql
##[group]Run psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_isolation_invariants.sql
psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_isolation_invariants.sql
```

The temporary negative-control evidence run explicitly printed its own environment binding:

```text
GITHUB_EVENT_NAME=push
GITHUB_SHA=335862746447e07baa0f81907d6b365570265ef5
CHECKOUT_SHA=335862746447e07baa0f81907d6b365570265ef5
```

That temporary harness commit has parent `18d8936fbcf29ccec22ab5718950540e87d061f3`, establishing that its database test inputs were the audited remediation snapshot plus one harness-only workflow file.

### 6.1 Original job/step conclusions

- Set up job: completed / success
- Initialize containers: completed / success
- Run actions/checkout@v4: completed / success
- Prepare Supabase-compatible local roles/extensions: completed / success
- Apply Phase 2 migrations in order: completed / success
- Run A-001 privilege regression: completed / success
- Run Phase 2 isolation invariants: completed / success
- Post Run actions/checkout@v4: completed / success
- Stop containers: completed / success
- Complete job: completed / success

### 6.2 SQL commands executed by run `35775485700`

From the checked-in workflow and job log:

```sh
set -euo pipefail
for file in migrations/*.sql; do
  echo "APPLY $file"
  psql -v ON_ERROR_STOP=1 -f "$file"
done

psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_privilege_boundaries.sql
psql -v ON_ERROR_STOP=1 -f tests/sql/phase2_isolation_invariants.sql
```

Applied migration log includes:

```text
APPLY migrations/20260922174011_phase2_core_foundation.sql
APPLY migrations/20260922174227_phase2_core_fk_indexes.sql
APPLY migrations/20260922180029_phase2_request_trace_telemetry.sql
APPLY migrations/20260922180107_phase2_idempotency_usage_audit.sql
APPLY migrations/20260922193829_phase2_a001_least_privilege.sql
```

### 6.3 Failure masking check

Checked-in workflow source at remediation SHA contains:

- `continue-on-error` occurrences: `0`
- `|| true` occurrences: `0`
- migration loop uses `set -euo pipefail`
- all migration/test `psql` invocations use `-v ON_ERROR_STOP=1`

Therefore run `35775485700` does not contain a workflow-level mechanism that converts SQL test failure into success.

---

## 7. Evidence-source provenance

- Base SHA: `1129bc562a238d338bf2761a49e4170588d52735`
- Remediation SHA reviewed: `18d8936fbcf29ccec22ab5718950540e87d061f3`
- Original remediation CI run: `35775485700`
- Negative-control/database-proof run: `35780158998`
- Negative-control harness commit: `335862746447e07baa0f81907d6b365570265ef5`, parent `18d8936fbcf29ccec22ab5718950540e87d061f3`, harness-only file `.github/workflows/a001-negative-control-evidence.yml`
- Scope-proof run: `35780440820`
- Both temporary evidence branches were reset to `18d8936fbcf29ccec22ab5718950540e87d061f3` after evidence collection.
- No violating grant was committed to PR #24.
- No production credentials or production traffic were used by these PostgreSQL 17 evidence jobs.

## 8. Governance state

- PR #24: must remain open and unmerged pending Independent Auditor re-review.
- Builder self-approval: prohibited.
- This package supplies evidence only; it does not declare A-001 closed.
