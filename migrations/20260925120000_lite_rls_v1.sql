-- Lite RLS v1 — row level security for the Phase A lite_* tables
-- Mirrors app_private.current_tenant_id() from 20260922174011_phase2_core_foundation.sql
-- with a bot-scoped helper reading 'app.bot_id'.
-- Policies scope nippan_runtime (the only role granted on lite_* tables) to
-- tenant_id + bot_id, matching the lite schema scope chain: tenant → bot.

begin;

create or replace function app_private.current_bot_id() returns uuid
language sql stable security invoker set search_path = ''
as $$ select nullif(current_setting('app.bot_id', true), '')::uuid $$;

revoke all on function app_private.current_bot_id() from public, anon, authenticated;
grant execute on function app_private.current_bot_id()
  to nippan_runtime, nippan_control_plane, nippan_analytics;

alter table public.lite_tenants enable row level security;
alter table public.lite_tenants force row level security;
alter table public.lite_bots enable row level security;
alter table public.lite_bots force row level security;
alter table public.lite_channels enable row level security;
alter table public.lite_channels force row level security;
alter table public.lite_end_customers enable row level security;
alter table public.lite_end_customers force row level security;
alter table public.lite_conversations enable row level security;
alter table public.lite_conversations force row level security;
alter table public.lite_memory_summaries enable row level security;
alter table public.lite_memory_summaries force row level security;
alter table public.lite_usage_log enable row level security;
alter table public.lite_usage_log force row level security;

drop policy if exists lite_tenant_isolation on public.lite_tenants;
create policy lite_tenant_isolation on public.lite_tenants for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()))
  with check (tenant_id = (select app_private.current_tenant_id()));

drop policy if exists lite_tenant_bot_isolation on public.lite_bots;
create policy lite_tenant_bot_isolation on public.lite_bots for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()))
  with check (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()));

drop policy if exists lite_tenant_bot_isolation on public.lite_channels;
create policy lite_tenant_bot_isolation on public.lite_channels for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()))
  with check (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()));

drop policy if exists lite_tenant_bot_isolation on public.lite_end_customers;
create policy lite_tenant_bot_isolation on public.lite_end_customers for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()))
  with check (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()));

drop policy if exists lite_tenant_bot_isolation on public.lite_conversations;
create policy lite_tenant_bot_isolation on public.lite_conversations for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()))
  with check (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()));

drop policy if exists lite_tenant_bot_isolation on public.lite_memory_summaries;
create policy lite_tenant_bot_isolation on public.lite_memory_summaries for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()))
  with check (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()));

drop policy if exists lite_tenant_bot_isolation on public.lite_usage_log;
create policy lite_tenant_bot_isolation on public.lite_usage_log for all to nippan_runtime
  using (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()))
  with check (tenant_id = (select app_private.current_tenant_id()) and bot_id = (select app_private.current_bot_id()));

comment on function app_private.current_bot_id() is 'Bot-scoped helper mirroring current_tenant_id(); reads app.bot_id.';

commit;