-- Lite Schema v1 — Phase A n8n workflow data layer
-- Simpler tables for n8n sub-workflows; no DB-level RLS (isolation at workflow level).
-- Coexists with Phase 2 core tables which use UUID+RLS+application layer.
-- Scope chain: tenant → bot → channel → end customer → conversation
-- Every table carrying customer data has BOTH tenant_id AND bot_id as FKs.

begin;

-- ── tenants ──────────────────────────────────────────────
-- Businesses renting bots (Phase A simple view)
create table if not exists public.lite_tenants (
  tenant_id           uuid primary key default gen_random_uuid(),
  business_name       text not null,
  owner_contact       text not null,
  signup_date         date not null default current_date,
  status              text not null default 'active' check (status in ('active', 'paused', 'cancelled')),
  consent_accepted_at timestamptz
);

comment on table public.lite_tenants is 'Businesses renting bots — Phase A simple view. Consent tracked for PDPA.';

-- ── bots ─────────────────────────────────────────────────
-- One row per bot; config produced by Onboarding
create table if not exists public.lite_bots (
  bot_id                uuid primary key default gen_random_uuid(),
  tenant_id             uuid not null references public.lite_tenants(tenant_id),
  bot_type              text not null,                        -- chat / secretary / ...
  tone                  text,                                -- fixed-menu value
  business_info         jsonb not null default '{}'::jsonb,  -- structured fields
  enabled_tools         jsonb not null default '[]'::jsonb,  -- list of MCP tool names
  monthly_message_quota int not null default 500,
  monthly_push_quota    int not null default 200,
  status                text not null default 'active' check (status in ('active', 'paused'))
);

comment on table public.lite_bots is 'Bot configurations; one row per bot. Quotas from PRICING_V1.md.';

create index if not exists idx_lite_bots_tenant on public.lite_bots(tenant_id);
create index if not exists idx_lite_bots_status   on public.lite_bots(status);

-- ── channels ─────────────────────────────────────────────
-- Where a bot is reachable
create table if not exists public.lite_channels (
  channel_id      uuid primary key default gen_random_uuid(),
  tenant_id       uuid not null references public.lite_tenants(tenant_id),
  bot_id          uuid not null references public.lite_bots(bot_id),
  channel_type    text not null,            -- line_oa / web_chat / ...
  credential_ref  text                      -- reference to secret in n8n — NEVER the token
);

comment on table public.lite_channels is 'Where a bot is reachable. credential_ref points to n8n secrets.';

create index if not exists idx_lite_channels_bot      on public.lite_channels(bot_id);
create index if not exists idx_lite_channels_tenant   on public.lite_channels(tenant_id);

-- ── end_customers ────────────────────────────────────────
-- The tenant''s own customers
create table if not exists public.lite_end_customers (
  end_customer_id     uuid primary key default gen_random_uuid(),
  tenant_id           uuid not null references public.lite_tenants(tenant_id),
  bot_id              uuid not null references public.lite_bots(bot_id),
  channel_id          uuid references public.lite_channels(channel_id),
  external_user_ref   text,                 -- LINE userId — scoped to tenant only
  consent_notice_shown_at timestamptz,      -- PDPA Layer 1 notice timestamp
  last_active_at      timestamptz default now()
);

comment on table public.lite_end_customers is 'Tenant''s end-customers. consent_notice_shown_at for PDPA compliance.';

create index if not exists idx_lite_end_cust_tenant     on public.lite_end_customers(tenant_id);
create index if not exists idx_lite_end_cust_bot        on public.lite_end_customers(bot_id);
create index if not exists idx_lite_end_cust_last_active on public.lite_end_customers(last_active_at desc);

-- ── conversations ────────────────────────────────────────
-- Recent turns (memory layers 1–2)
create table if not exists public.lite_conversations (
  tenant_id         uuid not null references public.lite_tenants(tenant_id),
  bot_id            uuid not null references public.lite_bots(bot_id),
  end_customer_id   uuid not null references public.lite_end_customers(end_customer_id),
  role              text not null check (role in ('user', 'bot')),
  message           text not null,
  created_at        timestamptz not null default now(),
  primary key (tenant_id, bot_id, end_customer_id, created_at, role)
);

comment on table public.lite_conversations is 'Recent conversation turns. Partitioned by tenant+bot+customer+time.';

create index if not exists idx_lite_conv_customer   on public.lite_conversations(end_customer_id, created_at desc);
create index if not exists idx_lite_conv_tenant_bot on public.lite_conversations(tenant_id, bot_id, created_at desc);

-- ── memory_summaries ─────────────────────────────────────
-- Long-term memory (layer 3) — keyword-searchable facts
create table if not exists public.lite_memory_summaries (
  tenant_id         uuid not null references public.lite_tenants(tenant_id),
  bot_id            uuid not null references public.lite_bots(bot_id),
  end_customer_id   uuid not null references public.lite_end_customers(end_customer_id),
  summary           text not null,
  created_at        timestamptz not null default now(),
  expires_at        timestamptz not null,       -- mandatory retention deadline
  primary key (tenant_id, bot_id, end_customer_id, created_at)
);

comment on table public.lite_memory_summaries is 'Long-term memory facts. expires_at MANDATORY — daily job deletes expired rows.';

create index if not exists idx_lite_mem_cust    on public.lite_memory_summaries(end_customer_id);
create index if not exists idx_lite_mem_expire  on public.lite_memory_summaries(expires_at asc) where expires_at > now();

-- ── usage_log ────────────────────────────────────────────
-- Owned by Cost Guard — reply/push counts, model tokens, cost
create table if not exists public.lite_usage_log (
  tenant_id           uuid not null references public.lite_tenants(tenant_id),
  bot_id              uuid not null references public.lite_bots(bot_id),
  date                date not null default current_date,
  reply_count         int not null default 0,
  push_count          int not null default 0,
  model_tokens        int not null default 0,
  estimated_cost_thb  numeric(12, 4) not null default 0.0000,
  primary key (tenant_id, bot_id, date)
);

comment on table public.lite_usage_log is 'Usage metrics owned by Cost Guard. Enforces monthly push quota.';

create index if not exists idx_lite_usage_bot    on public.lite_usage_log(bot_id);
create index if not exists idx_lite_usage_date   on public.lite_usage_log(date desc);

-- Grant nippan_runtime role select/insert/update on all lite tables (for n8n workflow access)
grant select, insert, update, delete on all tables in schema public to nippan_runtime;

commit;
