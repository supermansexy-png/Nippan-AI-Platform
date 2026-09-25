\set ON_ERROR_STOP on

begin;

-- Lite RLS v1 isolation invariants (T-026).
-- Runs against an ephemeral PostgreSQL with all migrations applied, rolls back
-- every fixture. Asserts that the lite_* tables enforce tenant+bot isolation in
-- the database (RLS) and fail closed when the runtime scope GUCs are missing.
--
-- Scope GUCs: app.tenant_id and app.bot_id (see migrations/20260925120000_lite_rls_v1.sql).

-- 1. Structural: all seven lite_* tables must have RLS enabled AND forced.
do $$
declare
  missing text;
begin
  select string_agg(v.table_name, ', ' order by v.table_name)
    into missing
  from (values
    ('lite_tenants'),
    ('lite_bots'),
    ('lite_channels'),
    ('lite_end_customers'),
    ('lite_conversations'),
    ('lite_memory_summaries'),
    ('lite_usage_log')
  ) as v(table_name)
  left join pg_class c on c.relname = v.table_name
  left join pg_namespace n
    on n.oid = c.relnamespace
   and n.nspname = 'public'
  where c.oid is null or not c.relrowsecurity or not c.relforcerowsecurity;

  if missing is not null then
    raise exception 'Lite RLS missing or not forced for: %', missing;
  end if;
end
$$;

-- 2. Fixtures (admin/superuser context; rolled back at the end).
insert into public.lite_tenants (tenant_id, business_name, owner_contact) values
  ('a1111111-1111-4111-8111-111111111111','RLS CI A','owner-a@example.test'),
  ('b2222222-2222-4222-8222-222222222222','RLS CI B','owner-b@example.test');

insert into public.lite_bots (bot_id, tenant_id, bot_type) values
  ('a0000001-0000-4000-8000-000000000001','a1111111-1111-4111-8111-111111111111','chat'),
  ('a0000002-0000-4000-8000-000000000002','a1111111-1111-4111-8111-111111111111','chat'),
  ('b0000001-0000-4000-8000-000000000001','b2222222-2222-4222-8222-222222222222','chat');

insert into public.lite_end_customers (end_customer_id, tenant_id, bot_id, external_user_ref) values
  ('ec000001-0000-4000-8000-000000000001','a1111111-1111-4111-8111-111111111111','a0000001-0000-4000-8000-000000000001','user-a'),
  ('ec000002-0000-4000-8000-000000000002','b2222222-2222-4222-8222-222222222222','b0000001-0000-4000-8000-000000000001','user-b');

-- 3. Isolation: tenant A + bot A sees only its own row (tenant AND bot dimension).
set local role nippan_runtime;
select set_config('app.tenant_id','a1111111-1111-4111-8111-111111111111',true);
select set_config('app.bot_id','a0000001-0000-4000-8000-000000000001',true);

do $$
declare
  visible_count bigint;
begin
  select count(*) into visible_count from public.lite_end_customers;
  if visible_count <> 1 then
    raise exception 'scope A/A-bot expected 1 visible row, got %', visible_count;
  end if;

  select count(*) into visible_count
    from public.lite_end_customers
   where tenant_id = 'b2222222-2222-4222-8222-222222222222';
  if visible_count <> 0 then
    raise exception 'cross-tenant rows visible, got %', visible_count;
  end if;

  select count(*) into visible_count
    from public.lite_end_customers
   where bot_id = 'a0000002-0000-4000-8000-000000000002';
  if visible_count <> 0 then
    raise exception 'cross-bot rows visible within the tenant, got %', visible_count;
  end if;
end
$$;

-- 4. Fail closed: missing bot context hides everything.
select set_config('app.bot_id','',true);
do $$
declare
  visible_count bigint;
begin
  select count(*) into visible_count from public.lite_end_customers;
  if visible_count <> 0 then
    raise exception 'missing bot context did not fail closed, got %', visible_count;
  end if;
end
$$;

-- 5. Fail closed: missing tenant context hides everything.
select set_config('app.tenant_id','',true);
select set_config('app.bot_id','a0000001-0000-4000-8000-000000000001',true);
do $$
declare
  visible_count bigint;
begin
  select count(*) into visible_count from public.lite_end_customers;
  if visible_count <> 0 then
    raise exception 'missing tenant context did not fail closed, got %', visible_count;
  end if;
end
$$;

-- 6. WITH CHECK: in-scope insert succeeds; out-of-scope insert is rejected.
select set_config('app.tenant_id','a1111111-1111-4111-8111-111111111111',true);
select set_config('app.bot_id','a0000001-0000-4000-8000-000000000001',true);

insert into public.lite_end_customers (end_customer_id, tenant_id, bot_id, external_user_ref)
values (
  'ec000003-0000-4000-8000-000000000003',
  'a1111111-1111-4111-8111-111111111111',
  'a0000001-0000-4000-8000-000000000001',
  'in-scope'
);

do $$
begin
  begin
    insert into public.lite_end_customers (end_customer_id, tenant_id, bot_id, external_user_ref)
    values (
      'ec000004-0000-4000-8000-000000000004',
      'b2222222-2222-4222-8222-222222222222',
      'b0000001-0000-4000-8000-000000000001',
      'cross-tenant'
    );
    raise exception 'out-of-scope insert unexpectedly accepted (WITH CHECK not enforced)';
  exception when insufficient_privilege then
    null; -- RLS WITH CHECK violation (SQLSTATE 42501) — expected.
  end;
end
$$;

reset role;

rollback;
