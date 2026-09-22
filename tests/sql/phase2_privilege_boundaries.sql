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
