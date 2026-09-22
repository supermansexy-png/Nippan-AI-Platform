begin;

-- War Room V1 Increment B, derived from the audited design head 72932d7.
-- This migration is for disposable/local/ephemeral PostgreSQL only until the
-- required implementation audit authorizes controlled application.
-- It intentionally does not reference the quarantined prototype migration.

create table public.project_rooms (
  room_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  project_key text not null check (length(btrim(project_key)) between 1 and 120),
  title text not null check (length(btrim(title)) between 1 and 255),
  mode text not null check (mode in ('FREE_DISCUSSION','FORMAL_MEETING','AUDIT_REVIEW')),
  state text not null default 'DRAFT'
    check (state in ('DRAFT','READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION','SUMMARIZING','CLOSED','STOPPED')),
  created_by_principal_id text not null check (length(btrim(created_by_principal_id)) between 1 and 255),
  automatic_round_limit smallint not null default 2 check (automatic_round_limit between 1 and 2),
  max_automatic_participants smallint not null default 5 check (max_automatic_participants between 1 and 5),
  token_budget bigint not null check (token_budget > 0),
  cost_budget numeric check (cost_budget is null or cost_budget >= 0),
  cost_currency text check (cost_currency is null or cost_currency ~ '^[A-Z]{3}$'),
  retention_days integer not null default 30 check (retention_days between 1 and 3650),
  audit_baseline_ref text,
  audit_baseline_sha text check (audit_baseline_sha is null or audit_baseline_sha ~ '^[0-9a-f]{40}$'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  started_at timestamptz,
  closed_at timestamptz,
  unique (tenant_id, application_id, room_id),
  foreign key (tenant_id, application_id) references public.applications (tenant_id, application_id),
  check ((cost_budget is null) or cost_currency is not null),
  check ((state in ('CLOSED','STOPPED')) = (closed_at is not null)),
  check (started_at is null or closed_at is null or started_at <= closed_at),
  check (mode <> 'AUDIT_REVIEW' or state not in ('READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION','SUMMARIZING') or (audit_baseline_ref is not null and audit_baseline_sha is not null))
);

create table public.project_room_participants (
  participant_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  principal_type text not null check (principal_type in ('HUMAN','AGENT','SYSTEM')),
  principal_id text not null check (length(btrim(principal_id)) between 1 and 255),
  agent_id uuid,
  participant_type text not null check (participant_type in ('HUMAN','AGENT','SYSTEM')),
  role text not null check (role in ('OWNER','CHAIR','ARCHITECT','BUILDER','SECURITY_REVIEWER','COST_OPS_REVIEWER','INDEPENDENT_AUDITOR','SECRETARY')),
  display_name text not null check (length(btrim(display_name)) between 1 and 120),
  model_policy_ref text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, application_id, room_id, participant_id),
  unique (tenant_id, application_id, room_id, principal_type, principal_id, role),
  foreign key (tenant_id, application_id, room_id) references public.project_rooms (tenant_id, application_id, room_id),
  foreign key (tenant_id, application_id, agent_id) references public.agents (tenant_id, application_id, agent_id),
  check (principal_type = participant_type),
  check ((participant_type = 'AGENT') = (agent_id is not null))
);

create unique index project_room_one_owner_uidx on public.project_room_participants (tenant_id, application_id, room_id) where active and role = 'OWNER';
create unique index project_room_one_chair_uidx on public.project_room_participants (tenant_id, application_id, room_id) where active and role = 'CHAIR';

create table public.project_room_agenda_items (
  agenda_item_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  sequence integer not null check (sequence > 0),
  title text not null check (length(btrim(title)) between 1 and 255),
  objective text not null check (length(btrim(objective)) between 1 and 4000),
  status text not null default 'OPEN' check (status in ('OPEN','RUNNING','NEEDS_OWNER_DECISION','COMPLETE','CANCELLED')),
  round_limit smallint not null default 2 check (round_limit between 1 and 2),
  token_budget bigint not null check (token_budget > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (tenant_id, application_id, room_id, agenda_item_id),
  unique (tenant_id, application_id, room_id, sequence),
  foreign key (tenant_id, application_id, room_id) references public.project_rooms (tenant_id, application_id, room_id),
  check ((status in ('COMPLETE','CANCELLED')) = (completed_at is not null))
);

create table public.project_room_messages (
  message_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  participant_id uuid,
  request_id uuid,
  message_type text not null check (message_type in ('OWNER_MESSAGE','AGENT_MESSAGE','CHAIR_PROMPT','CHAIR_SYNTHESIS','EVIDENCE_REQUEST','EVIDENCE_REFERENCE','FINDING','DECISION_PROPOSAL','OWNER_DECISION','ACTION_ITEM','SYSTEM_EVENT','BUDGET_WARNING','ERROR')),
  evidence_kind text check (evidence_kind is null or evidence_kind in ('VERIFIED_EVIDENCE','PROVIDED_CLAIM','INFERENCE','OPINION','UNKNOWN')),
  round_number smallint check (round_number is null or round_number between 1 and 2),
  sequence bigint not null,
  content_text text,
  content_reference text,
  content_redacted_at timestamptz,
  created_at timestamptz not null default now(),
  unique (tenant_id, application_id, room_id, message_id),
  unique (tenant_id, application_id, room_id, sequence),
  foreign key (tenant_id, application_id, room_id) references public.project_rooms (tenant_id, application_id, room_id),
  foreign key (tenant_id, application_id, room_id, agenda_item_id) references public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id),
  foreign key (tenant_id, application_id, room_id, participant_id) references public.project_room_participants (tenant_id, application_id, room_id, participant_id),
  foreign key (tenant_id, application_id, request_id) references public.requests (tenant_id, application_id, request_id),
  check (content_text is not null or content_reference is not null or content_redacted_at is not null),
  check (content_text is null or length(content_text) <= 32768),
  check (participant_id is not null or message_type in ('OWNER_MESSAGE','SYSTEM_EVENT','BUDGET_WARNING','ERROR')),
  check ((message_type in ('OWNER_MESSAGE','SYSTEM_EVENT','BUDGET_WARNING','ERROR') and round_number is null) or (message_type not in ('OWNER_MESSAGE','SYSTEM_EVENT','BUDGET_WARNING','ERROR') and round_number is not null)),
  check (message_type not in ('AGENT_MESSAGE','CHAIR_SYNTHESIS') or request_id is not null)
);

create table public.project_room_findings (
  finding_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  raised_by_participant_id uuid not null,
  severity text not null check (severity in ('BLOCKER','HIGH','MEDIUM','LOW','NOTE')),
  status text not null default 'OPEN' check (status in ('OPEN','ACKNOWLEDGED','RESOLVED','DISMISSED')),
  summary text not null check (length(btrim(summary)) between 1 and 4000),
  evidence_refs jsonb not null default '[]'::jsonb check (jsonb_typeof(evidence_refs) = 'array'),
  created_at timestamptz not null default now(),
  resolved_at timestamptz,
  foreign key (tenant_id, application_id, room_id) references public.project_rooms (tenant_id, application_id, room_id),
  foreign key (tenant_id, application_id, room_id, agenda_item_id) references public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id),
  foreign key (tenant_id, application_id, room_id, raised_by_participant_id) references public.project_room_participants (tenant_id, application_id, room_id, participant_id),
  check ((status in ('RESOLVED','DISMISSED')) = (resolved_at is not null))
);

create table public.project_room_decisions (
  decision_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  decision_type text not null check (decision_type in ('PROPOSAL','OWNER_DECISION','ADVISORY_AUDIT_OUTCOME')),
  proposed_by_participant_id uuid,
  owner_principal_id text,
  decision_text text not null check (length(btrim(decision_text)) between 1 and 4000),
  rationale text check (rationale is null or length(rationale) <= 8000),
  evidence_refs jsonb not null default '[]'::jsonb check (jsonb_typeof(evidence_refs) = 'array'),
  status text not null default 'PROPOSED' check (status in ('PROPOSED','ACCEPTED','REJECTED','SUPERSEDED')),
  created_at timestamptz not null default now(),
  decided_at timestamptz,
  foreign key (tenant_id, application_id, room_id) references public.project_rooms (tenant_id, application_id, room_id),
  foreign key (tenant_id, application_id, room_id, agenda_item_id) references public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id),
  foreign key (tenant_id, application_id, room_id, proposed_by_participant_id) references public.project_room_participants (tenant_id, application_id, room_id, participant_id),
  check ((status in ('ACCEPTED','REJECTED')) = (owner_principal_id is not null and decided_at is not null)),
  check (status <> 'PROPOSED' or decided_at is null),
  check (decision_type <> 'ADVISORY_AUDIT_OUTCOME' or (owner_principal_id is null and status in ('PROPOSED','SUPERSEDED')))
);

create table public.project_room_action_items (
  action_item_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  title text not null check (length(btrim(title)) between 1 and 500),
  owner_principal_id text,
  status text not null default 'OPEN' check (status in ('OPEN','IN_PROGRESS','DONE','CANCELLED')),
  linked_issue_or_pr text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,
  foreign key (tenant_id, application_id, room_id) references public.project_rooms (tenant_id, application_id, room_id),
  foreign key (tenant_id, application_id, room_id, agenda_item_id) references public.project_room_agenda_items (tenant_id, application_id, room_id, agenda_item_id),
  check ((status in ('DONE','CANCELLED')) = (completed_at is not null))
);

create index project_rooms_scope_state_idx on public.project_rooms (tenant_id, application_id, state, updated_at desc);
create index project_room_participants_scope_idx on public.project_room_participants (tenant_id, application_id, room_id, active, role);
create index project_room_agenda_scope_idx on public.project_room_agenda_items (tenant_id, application_id, room_id, sequence);
create index project_room_messages_scope_idx on public.project_room_messages (tenant_id, application_id, room_id, sequence);
create index project_room_messages_request_idx on public.project_room_messages (tenant_id, application_id, request_id) where request_id is not null;
create index project_room_findings_scope_idx on public.project_room_findings (tenant_id, application_id, room_id, status, created_at);
create index project_room_decisions_scope_idx on public.project_room_decisions (tenant_id, application_id, room_id, status, created_at);
create index project_room_action_items_scope_idx on public.project_room_action_items (tenant_id, application_id, room_id, status, created_at);

create or replace function app_private.validate_project_room_participant_independence()
returns trigger language plpgsql security invoker set search_path = '' as $$
begin
  if new.active and new.role in ('BUILDER','INDEPENDENT_AUDITOR')
     and exists (
       select 1 from public.project_room_participants other
       where other.tenant_id = new.tenant_id
         and other.application_id = new.application_id
         and other.room_id = new.room_id
         and other.active
         and other.principal_type = new.principal_type
         and other.principal_id = new.principal_id
         and other.role <> new.role
         and other.role in ('BUILDER','INDEPENDENT_AUDITOR')
         and other.participant_id <> new.participant_id
     ) then
    raise exception 'Builder and Independent Auditor must be distinct canonical principals' using errcode = '23514';
  end if;
  return new;
end $$;

create or replace function app_private.assert_project_room_audit_readiness(
  p_tenant_id uuid, p_application_id uuid, p_room_id uuid
) returns void language plpgsql security invoker set search_path = '' as $$
declare
  room_row public.project_rooms%rowtype;
  auditor_count integer;
begin
  select * into room_row from public.project_rooms
  where tenant_id = p_tenant_id and application_id = p_application_id and room_id = p_room_id;
  if not found then raise exception 'War Room does not exist' using errcode = '23503'; end if;
  if room_row.mode <> 'AUDIT_REVIEW' then raise exception 'Audit readiness requires AUDIT_REVIEW mode' using errcode = '23514'; end if;
  if room_row.audit_baseline_ref is null or room_row.audit_baseline_sha is null then
    raise exception 'Audit readiness requires baseline reference and SHA' using errcode = '23514';
  end if;
  select count(*) into auditor_count from public.project_room_participants
  where tenant_id = p_tenant_id and application_id = p_application_id and room_id = p_room_id
    and active and role = 'INDEPENDENT_AUDITOR';
  if auditor_count <> 1 then raise exception 'Audit Review requires exactly one active Independent Auditor' using errcode = '23514'; end if;
  if exists (
    select 1 from public.project_room_participants builder
    join public.project_room_participants auditor on auditor.tenant_id = builder.tenant_id
      and auditor.application_id = builder.application_id and auditor.room_id = builder.room_id
      and auditor.principal_type = builder.principal_type and auditor.principal_id = builder.principal_id
    where builder.tenant_id = p_tenant_id and builder.application_id = p_application_id and builder.room_id = p_room_id
      and builder.active and builder.role = 'BUILDER' and auditor.active and auditor.role = 'INDEPENDENT_AUDITOR'
  ) then raise exception 'Builder and Independent Auditor must be distinct canonical principals' using errcode = '23514'; end if;
  if not exists (
    select 1 from public.project_room_participants owner
    where owner.tenant_id = p_tenant_id and owner.application_id = p_application_id and owner.room_id = p_room_id
      and owner.active and owner.participant_type = 'HUMAN' and owner.role = 'OWNER'
  ) then raise exception 'Audit Review requires an active HUMAN OWNER' using errcode = '23514'; end if;
end $$;

create or replace function app_private.validate_project_room_participant_readiness()
returns trigger language plpgsql security invoker set search_path = '' as $$
declare room_id_value uuid; tenant_id_value uuid; application_id_value uuid; room_state text; room_mode text;
begin
  tenant_id_value := coalesce(new.tenant_id, old.tenant_id);
  application_id_value := coalesce(new.application_id, old.application_id);
  room_id_value := coalesce(new.room_id, old.room_id);
  select state, mode into room_state, room_mode from public.project_rooms
    where tenant_id = tenant_id_value and application_id = application_id_value and room_id = room_id_value;
  if room_mode = 'AUDIT_REVIEW' and room_state in ('READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION','SUMMARIZING') then
    perform app_private.assert_project_room_audit_readiness(tenant_id_value, application_id_value, room_id_value);
  end if;
  if tg_op = 'DELETE' then return old; end if;
  return new;
end $$;

create or replace function app_private.validate_project_room_state_readiness()
returns trigger language plpgsql security invoker set search_path = '' as $$
begin
  if new.mode = 'AUDIT_REVIEW' and new.state in ('READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION','SUMMARIZING') then
    perform app_private.assert_project_room_audit_readiness(new.tenant_id, new.application_id, new.room_id);
  end if;
  return new;
end $$;

create or replace function app_private.validate_project_room_decision()
returns trigger language plpgsql security invoker set search_path = '' as $$
declare room_row public.project_rooms%rowtype; proposed_role text; proposed_principal_type text; proposed_principal_id text;
begin
  select * into room_row from public.project_rooms where tenant_id = new.tenant_id and application_id = new.application_id and room_id = new.room_id;
  if not found then raise exception 'Decision room does not exist' using errcode = '23503'; end if;
  if new.decision_type = 'ADVISORY_AUDIT_OUTCOME' then
    if room_row.mode <> 'AUDIT_REVIEW' then raise exception 'Advisory audit outcome requires AUDIT_REVIEW mode' using errcode = '23514'; end if;
    perform app_private.assert_project_room_audit_readiness(new.tenant_id, new.application_id, new.room_id);
    if jsonb_array_length(new.evidence_refs) = 0 then raise exception 'Advisory audit outcome requires evidence references' using errcode = '23514'; end if;
    select role, principal_type, principal_id into proposed_role, proposed_principal_type, proposed_principal_id
      from public.project_room_participants where participant_id = new.proposed_by_participant_id
        and tenant_id = new.tenant_id and application_id = new.application_id and room_id = new.room_id and active;
    if new.proposed_by_participant_id is null or proposed_role is distinct from 'INDEPENDENT_AUDITOR' then raise exception 'Only the configured Independent Auditor may create an advisory audit outcome' using errcode = '42501'; end if;
    if new.owner_principal_id is not null or new.status not in ('PROPOSED','SUPERSEDED') then raise exception 'Advisory audit outcome cannot be an owner approval' using errcode = '23514'; end if;
  elsif new.decision_type = 'OWNER_DECISION' and new.status in ('ACCEPTED','REJECTED') then
    if not exists (select 1 from public.project_room_participants where tenant_id = new.tenant_id and application_id = new.application_id and room_id = new.room_id and active and participant_type = 'HUMAN' and role = 'OWNER' and principal_type = 'HUMAN' and principal_id = new.owner_principal_id) then
      raise exception 'Owner decision requires an active HUMAN OWNER principal' using errcode = '42501';
    end if;
    if new.proposed_by_participant_id is not null and exists (select 1 from public.project_room_participants builder where builder.participant_id = new.proposed_by_participant_id and builder.role = 'BUILDER' and builder.principal_type = 'HUMAN' and builder.principal_id = new.owner_principal_id) then
      raise exception 'Builder cannot self-approve' using errcode = '42501';
    end if;
  end if;
  return new;
end $$;

revoke all on function app_private.validate_project_room_participant_independence() from public, anon, authenticated;
revoke all on function app_private.assert_project_room_audit_readiness(uuid, uuid, uuid) from public, anon, authenticated;
revoke all on function app_private.validate_project_room_participant_readiness() from public, anon, authenticated;
revoke all on function app_private.validate_project_room_state_readiness() from public, anon, authenticated;
revoke all on function app_private.validate_project_room_decision() from public, anon, authenticated;

create trigger project_room_participant_independence
before insert or update of principal_type, principal_id, role, active, room_id, tenant_id, application_id
on public.project_room_participants for each row execute function app_private.validate_project_room_participant_independence();
create constraint trigger project_room_participant_readiness
after insert or update or delete on public.project_room_participants
deferrable initially immediate for each row execute function app_private.validate_project_room_participant_readiness();
create trigger project_room_state_readiness
before update of state on public.project_rooms for each row execute function app_private.validate_project_room_state_readiness();
create trigger project_room_decision_guard
before insert or update on public.project_room_decisions for each row execute function app_private.validate_project_room_decision();

do $$ declare t text; begin
  foreach t in array array['project_rooms','project_room_participants','project_room_agenda_items','project_room_messages','project_room_findings','project_room_decisions','project_room_action_items'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on public.%I from public, anon, authenticated, service_role, nippan_runtime, nippan_control_plane, nippan_analytics', t);
    execute format('create policy project_scope on public.%I for all to nippan_runtime, nippan_control_plane using (tenant_id = (select app_private.current_tenant_id()) and application_id = (select app_private.current_application_id())) with check (tenant_id = (select app_private.current_tenant_id()) and application_id = (select app_private.current_application_id()))', t);
    execute format('create policy project_analytics_read on public.%I for select to nippan_analytics using (tenant_id = (select app_private.current_tenant_id()) and application_id = (select app_private.current_application_id()))', t);
  end loop;
end $$;

grant select, insert, update on public.project_rooms to nippan_runtime, nippan_control_plane;
grant select on public.project_room_participants to nippan_runtime;
grant select, insert, update on public.project_room_participants to nippan_control_plane;
grant select, insert, update on public.project_room_agenda_items to nippan_runtime, nippan_control_plane;
grant select, insert on public.project_room_messages to nippan_runtime, nippan_control_plane;
grant select, insert, update on public.project_room_findings to nippan_runtime, nippan_control_plane;
grant select, insert on public.project_room_decisions to nippan_runtime, nippan_control_plane;
grant select, insert, update on public.project_room_action_items to nippan_runtime, nippan_control_plane;
grant select on public.project_rooms, public.project_room_participants, public.project_room_agenda_items, public.project_room_messages, public.project_room_findings, public.project_room_decisions, public.project_room_action_items to nippan_analytics;

commit;
