begin;

create extension if not exists pgcrypto with schema extensions;
create schema if not exists app_private;
revoke all on schema app_private from public, anon, authenticated;

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'nippan_runtime') then
    create role nippan_runtime nologin nosuperuser nocreatedb nocreaterole noinherit nobypassrls;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'nippan_control_plane') then
    create role nippan_control_plane nologin nosuperuser nocreatedb nocreaterole noinherit nobypassrls;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'nippan_analytics') then
    create role nippan_analytics nologin nosuperuser nocreatedb nocreaterole noinherit nobypassrls;
  end if;
end
$$;

create or replace function app_private.current_tenant_id() returns uuid
language sql stable security invoker set search_path = ''
as $$ select nullif(current_setting('app.tenant_id', true), '')::uuid $$;

create or replace function app_private.current_application_id() returns uuid
language sql stable security invoker set search_path = ''
as $$ select nullif(current_setting('app.application_id', true), '')::uuid $$;

revoke all on function app_private.current_tenant_id() from public, anon, authenticated;
revoke all on function app_private.current_application_id() from public, anon, authenticated;
grant usage on schema app_private to nippan_runtime, nippan_control_plane, nippan_analytics;
grant execute on function app_private.current_tenant_id(), app_private.current_application_id()
  to nippan_runtime, nippan_control_plane, nippan_analytics;

create table public.tenants (
  tenant_id uuid primary key default extensions.gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  display_name text not null check (length(btrim(display_name)) > 0),
  tenant_type text not null check (tenant_type in ('internal','customer','partner','system')),
  status text not null default 'provisioning' check (status in ('provisioning','active','suspended','disabled','archived')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

create table public.workspaces (
  workspace_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null references public.tenants (tenant_id),
  slug text not null check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  display_name text not null check (length(btrim(display_name)) > 0),
  status text not null default 'active' check (status in ('active','disabled','archived')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (tenant_id, workspace_id), unique (tenant_id, slug)
);

create table public.applications (
  application_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null,
  workspace_id uuid, slug text not null check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  display_name text not null check (length(btrim(display_name)) > 0),
  application_type text not null check (length(btrim(application_type)) > 0),
  status text not null default 'active' check (status in ('provisioning','active','suspended','disabled','archived')),
  environment_policy jsonb not null default '{}'::jsonb check (jsonb_typeof(environment_policy) = 'object'),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (tenant_id, application_id), unique (tenant_id, slug),
  foreign key (tenant_id) references public.tenants (tenant_id),
  foreign key (tenant_id, workspace_id) references public.workspaces (tenant_id, workspace_id)
);

create table public.agents (
  agent_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null, application_id uuid not null,
  slug text not null check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  display_name text not null check (length(btrim(display_name)) > 0), role text not null check (length(btrim(role)) > 0),
  status text not null default 'active' check (status in ('active','disabled','archived')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (tenant_id, application_id, agent_id), unique (tenant_id, application_id, slug),
  foreign key (tenant_id, application_id) references public.applications (tenant_id, application_id)
);

create table public.channels (
  channel_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null, application_id uuid not null,
  channel_type text not null check (length(btrim(channel_type)) > 0),
  display_name text not null check (length(btrim(display_name)) > 0),
  status text not null default 'active' check (status in ('active','disabled','archived')), external_ref text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (tenant_id, application_id, channel_id), unique (tenant_id, channel_id),
  foreign key (tenant_id, application_id) references public.applications (tenant_id, application_id)
);
create unique index channels_external_ref_uidx on public.channels
  (tenant_id, application_id, channel_type, external_ref) where external_ref is not null;

create table public.agent_channel_bindings (
  binding_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null, application_id uuid not null,
  agent_id uuid not null, channel_id uuid not null,
  environment text not null check (environment in ('development','staging','production')),
  routing_role text not null check (routing_role in ('default','specialist','fallback','reviewer')),
  priority integer not null default 100 check (priority >= 0), enabled boolean not null default true,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  foreign key (tenant_id, application_id, agent_id) references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, channel_id) references public.channels (tenant_id, application_id, channel_id)
);
create unique index agent_channel_one_default_uidx on public.agent_channel_bindings
  (tenant_id, application_id, channel_id, environment) where enabled and routing_role = 'default';
create index agent_channel_agent_idx on public.agent_channel_bindings
  (tenant_id, application_id, agent_id, environment) where enabled;

create table public.subjects (
  subject_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null,
  canonical_display_name text, status text not null default 'active' check (status in ('active','disabled','merged','archived')),
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  unique (tenant_id, subject_id), foreign key (tenant_id) references public.tenants (tenant_id)
);

create table public.subject_identities (
  subject_identity_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null,
  subject_id uuid not null, channel_id uuid not null, provider text not null check (length(btrim(provider)) > 0),
  external_subject_id text not null check (length(btrim(external_subject_id)) > 0), verified_at timestamptz,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  foreign key (tenant_id, subject_id) references public.subjects (tenant_id, subject_id),
  foreign key (tenant_id, channel_id) references public.channels (tenant_id, channel_id),
  unique (tenant_id, channel_id, provider, external_subject_id)
);

create table public.conversations (
  conversation_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null, application_id uuid not null,
  channel_id uuid not null, subject_id uuid, primary_agent_id uuid, external_thread_ref text, parent_conversation_id uuid,
  status text not null default 'active' check (status in ('active','waiting','human_handoff','closed','archived')),
  started_at timestamptz not null default now(), last_activity_at timestamptz not null default now(), closed_at timestamptz,
  unique (tenant_id, application_id, conversation_id),
  foreign key (tenant_id, application_id, channel_id) references public.channels (tenant_id, application_id, channel_id),
  foreign key (tenant_id, subject_id) references public.subjects (tenant_id, subject_id),
  foreign key (tenant_id, application_id, primary_agent_id) references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, parent_conversation_id) references public.conversations (tenant_id, application_id, conversation_id),
  check ((status in ('closed','archived')) = (closed_at is not null))
);
create unique index conversations_external_thread_uidx on public.conversations
  (tenant_id, application_id, channel_id, external_thread_ref) where external_thread_ref is not null;

create table public.policy_versions (
  policy_version_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid, application_id uuid,
  policy_type text not null check (length(btrim(policy_type)) > 0), version_number integer not null check (version_number > 0),
  lifecycle_status text not null default 'DRAFT' check (lifecycle_status in ('DRAFT','TESTING','PUBLISHED','SUPERSEDED')),
  policy_document jsonb not null check (jsonb_typeof(policy_document) = 'object'),
  content_hash text not null check (content_hash ~ '^[0-9a-f]{64}$'), platform_shared boolean not null default false,
  created_by text not null check (length(btrim(created_by)) > 0), created_at timestamptz not null default now(),
  published_at timestamptz, supersedes_policy_id uuid references public.policy_versions (policy_version_id),
  check ((platform_shared and tenant_id is null and application_id is null) or
         (not platform_shared and tenant_id is not null and application_id is not null)),
  check ((lifecycle_status in ('PUBLISHED','SUPERSEDED')) = (published_at is not null)),
  foreign key (tenant_id, application_id) references public.applications (tenant_id, application_id)
);
create unique index policy_versions_scoped_uidx on public.policy_versions
  (tenant_id, application_id, policy_type, version_number) where not platform_shared;
create unique index policy_versions_shared_uidx on public.policy_versions
  (policy_type, version_number) where platform_shared;

create table public.agent_config_versions (
  config_version_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null,
  application_id uuid not null, agent_id uuid not null, version_number integer not null check (version_number > 0),
  lifecycle_status text not null default 'DRAFT' check (lifecycle_status in ('DRAFT','TESTING','PUBLISHED','SUPERSEDED')),
  environment text not null check (environment in ('development','staging','production')),
  config_document jsonb not null check (jsonb_typeof(config_document) = 'object'),
  published_config_hash text check (published_config_hash ~ '^[0-9a-f]{64}$'),
  policy_merge_version text not null check (length(btrim(policy_merge_version)) > 0),
  created_by text not null check (length(btrim(created_by)) > 0), created_at timestamptz not null default now(),
  published_at timestamptz, supersedes_version_id uuid references public.agent_config_versions (config_version_id),
  change_note text not null,
  unique (tenant_id, application_id, agent_id, environment, version_number),
  unique (tenant_id, application_id, agent_id, environment, config_version_id),
  foreign key (tenant_id, application_id, agent_id) references public.agents (tenant_id, application_id, agent_id),
  check ((lifecycle_status in ('PUBLISHED','SUPERSEDED') and published_at is not null and published_config_hash is not null) or
         (lifecycle_status in ('DRAFT','TESTING') and published_at is null and published_config_hash is null))
);

create table public.agent_activations (
  activation_id uuid primary key default extensions.gen_random_uuid(), tenant_id uuid not null,
  application_id uuid not null, agent_id uuid not null,
  environment text not null check (environment in ('development','staging','production')),
  config_version_id uuid not null, activated_at timestamptz not null default now(),
  activated_by text not null check (length(btrim(activated_by)) > 0),
  unique (tenant_id, application_id, agent_id, environment),
  foreign key (tenant_id, application_id, agent_id) references public.agents (tenant_id, application_id, agent_id),
  foreign key (tenant_id, application_id, agent_id, environment, config_version_id)
    references public.agent_config_versions (tenant_id, application_id, agent_id, environment, config_version_id)
);

create or replace function app_private.reject_frozen_version_update() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  if old.lifecycle_status in ('TESTING','PUBLISHED','SUPERSEDED') then
    raise exception 'version % is immutable in lifecycle state %', old.config_version_id, old.lifecycle_status using errcode = '55000';
  end if;
  return new;
end $$;

create or replace function app_private.reject_frozen_policy_update() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  if old.lifecycle_status in ('PUBLISHED','SUPERSEDED') then
    raise exception 'policy version % is immutable in lifecycle state %', old.policy_version_id, old.lifecycle_status using errcode = '55000';
  end if;
  return new;
end $$;

create or replace function app_private.validate_agent_activation() returns trigger
language plpgsql security invoker set search_path = '' as $$
begin
  if not exists (
    select 1 from public.agent_config_versions c
    where c.config_version_id = new.config_version_id and c.tenant_id = new.tenant_id
      and c.application_id = new.application_id and c.agent_id = new.agent_id
      and c.environment = new.environment and c.lifecycle_status = 'PUBLISHED'
  ) then
    raise exception 'activation requires a PUBLISHED config in the same tenant/application/agent/environment' using errcode = '23514';
  end if;
  return new;
end $$;

revoke all on function app_private.reject_frozen_version_update() from public, anon, authenticated;
revoke all on function app_private.reject_frozen_policy_update() from public, anon, authenticated;
revoke all on function app_private.validate_agent_activation() from public, anon, authenticated;
create trigger agent_config_versions_immutable before update or delete on public.agent_config_versions
  for each row execute function app_private.reject_frozen_version_update();
create trigger policy_versions_immutable before update or delete on public.policy_versions
  for each row execute function app_private.reject_frozen_policy_update();
create trigger agent_activations_validate before insert or update on public.agent_activations
  for each row execute function app_private.validate_agent_activation();

alter default privileges for role postgres in schema public revoke select, insert, update, delete on tables from anon, authenticated, service_role;
alter default privileges for role postgres in schema public revoke usage, select on sequences from anon, authenticated, service_role;
alter default privileges for role postgres in schema public revoke execute on functions from public, anon, authenticated, service_role;
revoke all on all tables in schema public from public, anon, authenticated, service_role;
grant select, insert, update on all tables in schema public to nippan_runtime, nippan_control_plane;
grant select on all tables in schema public to nippan_analytics;

do $$
declare t text;
begin
  foreach t in array array['tenants','workspaces','applications','agents','channels','agent_channel_bindings',
    'subjects','subject_identities','conversations','policy_versions','agent_config_versions','agent_activations'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('create policy tenant_isolation on public.%I for all to nippan_runtime, nippan_control_plane using (tenant_id = (select app_private.current_tenant_id())) with check (tenant_id = (select app_private.current_tenant_id()))', t);
    execute format('create policy tenant_analytics_read on public.%I for select to nippan_analytics using (tenant_id = (select app_private.current_tenant_id()))', t);
  end loop;
end $$;

drop policy tenant_isolation on public.policy_versions;
drop policy tenant_analytics_read on public.policy_versions;
create policy policy_versions_runtime_read on public.policy_versions for select to nippan_runtime
  using (platform_shared or tenant_id = (select app_private.current_tenant_id()));
create policy policy_versions_control on public.policy_versions for all to nippan_control_plane
  using (not platform_shared and tenant_id = (select app_private.current_tenant_id()))
  with check (not platform_shared and tenant_id = (select app_private.current_tenant_id()));
create policy policy_versions_analytics_read on public.policy_versions for select to nippan_analytics
  using (platform_shared or tenant_id = (select app_private.current_tenant_id()));

create index workspaces_tenant_idx on public.workspaces (tenant_id);
create index applications_tenant_idx on public.applications (tenant_id);
create index agents_scope_idx on public.agents (tenant_id, application_id);
create index channels_scope_idx on public.channels (tenant_id, application_id);
create index subjects_tenant_idx on public.subjects (tenant_id);
create index subject_identities_subject_idx on public.subject_identities (tenant_id, subject_id);
create index conversations_scope_activity_idx on public.conversations (tenant_id, application_id, last_activity_at desc);
create index agent_config_versions_lookup_idx on public.agent_config_versions (tenant_id, application_id, agent_id, environment, lifecycle_status);
create index policy_versions_lookup_idx on public.policy_versions (tenant_id, application_id, policy_type, lifecycle_status);

comment on schema app_private is 'Non-exposed helper functions for tenant-scoped runtime access.';
comment on role nippan_runtime is 'NOLOGIN tenant-scoped runtime group role; never grant BYPASSRLS.';
comment on role nippan_control_plane is 'NOLOGIN tenant-scoped control-plane group role; never grant BYPASSRLS.';
comment on role nippan_analytics is 'NOLOGIN tenant-scoped read-only analytics group role; never grant BYPASSRLS.';

commit;

