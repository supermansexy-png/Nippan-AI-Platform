-- War Room V1 Increment B schema/RLS migration.
-- Approved design: docs/proposals/WAR_ROOM_V1_SCHEMA_RLS_DESIGN.md
-- Design head audited by Audit #28: fd692583c3177746a70882de668bbdfda65d523a
-- Audit #28 remediation re-review: PASS_WITH_FINDINGS, all F-28-01..F-28-06 CLOSED.
-- Migration creation authorized by Claude Opus 5 generation:
-- gen-1790117818-TRluF9U9ckz3Mt0mldo1
--
-- IMPORTANT: this file is for reviewed migration implementation only.
-- It is NOT authorization to apply Supabase production.

begin;

create table public.project_rooms (
  room_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  project_key text not null
    check (length(btrim(project_key)) between 1 and 120),
  title text not null
    check (length(btrim(title)) between 1 and 255),
  mode text not null
    check (mode in ('FREE_DISCUSSION','FORMAL_MEETING','AUDIT_REVIEW')),
  state text not null default 'DRAFT'
    check (state in (
      'DRAFT','READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION',
      'SUMMARIZING','CLOSED','STOPPED'
    )),
  created_by_principal_id text not null
    check (length(btrim(created_by_principal_id)) between 1 and 255),
  automatic_round_limit smallint not null default 2
    check (automatic_round_limit between 1 and 2),
  max_automatic_participants smallint not null default 5
    check (max_automatic_participants between 1 and 5),
  token_budget bigint not null check (token_budget > 0),
  cost_budget numeric check (cost_budget is null or cost_budget >= 0),
  cost_currency text check (
    cost_currency is null or cost_currency ~ '^[A-Z]{3}$'
  ),
  retention_days integer not null default 30
    check (retention_days between 1 and 3650),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  started_at timestamptz,
  closed_at timestamptz,

  constraint project_rooms_scope_uniq
    unique (tenant_id, application_id, room_id),

  foreign key (tenant_id, application_id)
    references public.applications (tenant_id, application_id),

  check (cost_budget is null or cost_currency is not null),
  check ((state in ('CLOSED','STOPPED')) = (closed_at is not null)),
  check (
    started_at is null
    or closed_at is null
    or started_at <= closed_at
  )
);

create index project_rooms_scope_state_idx
  on public.project_rooms
    (tenant_id, application_id, state, updated_at desc);

create index project_rooms_project_idx
  on public.project_rooms
    (tenant_id, application_id, project_key, created_at desc);


create table public.project_room_participants (
  participant_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  principal_type text not null
    check (principal_type in ('HUMAN','AGENT','SYSTEM')),
  principal_id text not null
    check (length(btrim(principal_id)) between 1 and 255),
  agent_id uuid,
  participant_type text not null
    check (participant_type in ('HUMAN','AGENT','SYSTEM')),
  role text not null
    check (role in (
      'OWNER','CHAIR','ARCHITECT','BUILDER','SECURITY_REVIEWER',
      'COST_OPS_REVIEWER','INDEPENDENT_AUDITOR','SECRETARY'
    )),
  display_name text not null
    check (length(btrim(display_name)) between 1 and 120),
  model_policy_ref text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint project_room_participants_scope_uniq
    unique (tenant_id, application_id, room_id, participant_id),

  constraint project_room_participants_identity_role_uniq
    unique (
      tenant_id, application_id, room_id,
      principal_type, principal_id, role
    ),

  foreign key (tenant_id, application_id, room_id)
    references public.project_rooms
      (tenant_id, application_id, room_id),

  foreign key (tenant_id, application_id, agent_id)
    references public.agents
      (tenant_id, application_id, agent_id),

  check (principal_type = participant_type),
  check (
    (participant_type = 'AGENT' and agent_id is not null)
    or
    (participant_type <> 'AGENT' and agent_id is null)
  )
);

create unique index project_room_participants_one_active_owner_uidx
  on public.project_room_participants
    (tenant_id, application_id, room_id)
  where active and role = 'OWNER';

create unique index project_room_participants_one_active_chair_uidx
  on public.project_room_participants
    (tenant_id, application_id, room_id)
  where active and role = 'CHAIR';

create index project_room_participants_role_idx
  on public.project_room_participants
    (tenant_id, application_id, room_id, active, role);

create index project_room_participants_principal_idx
  on public.project_room_participants
    (tenant_id, application_id, room_id, principal_type, principal_id);

create index project_room_participants_agent_idx
  on public.project_room_participants
    (tenant_id, application_id, agent_id)
  where agent_id is not null;


create table public.project_room_agenda_items (
  agenda_item_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  sequence integer not null check (sequence > 0),
  title text not null
    check (length(btrim(title)) between 1 and 255),
  objective text not null
    check (length(btrim(objective)) between 1 and 4000),
  status text not null default 'OPEN'
    check (status in (
      'OPEN','RUNNING','NEEDS_OWNER_DECISION','COMPLETE','CANCELLED'
    )),
  round_limit smallint not null default 2
    check (round_limit between 1 and 2),
  token_budget bigint not null check (token_budget > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,

  constraint project_room_agenda_items_scope_uniq
    unique (tenant_id, application_id, room_id, agenda_item_id),

  unique (tenant_id, application_id, room_id, sequence),

  foreign key (tenant_id, application_id, room_id)
    references public.project_rooms
      (tenant_id, application_id, room_id),

  check (
    (status in ('COMPLETE','CANCELLED')) = (completed_at is not null)
  )
);

create index project_room_agenda_items_sequence_idx
  on public.project_room_agenda_items
    (tenant_id, application_id, room_id, sequence);


create table public.project_room_messages (
  message_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  participant_id uuid,
  request_id uuid,
  message_type text not null
    check (message_type in (
      'OWNER_MESSAGE','AGENT_MESSAGE','CHAIR_PROMPT','CHAIR_SYNTHESIS',
      'EVIDENCE_REQUEST','EVIDENCE_REFERENCE','FINDING',
      'DECISION_PROPOSAL','OWNER_DECISION','ACTION_ITEM',
      'SYSTEM_EVENT','BUDGET_WARNING','ERROR'
    )),
  evidence_kind text
    check (
      evidence_kind is null
      or evidence_kind in (
        'VERIFIED_EVIDENCE','PROVIDED_CLAIM','INFERENCE','OPINION','UNKNOWN'
      )
    ),
  round_number smallint
    check (round_number is null or round_number between 1 and 2),
  sequence bigint not null check (sequence > 0),
  content_text text,
  content_reference text,
  content_redacted_at timestamptz,
  created_at timestamptz not null default now(),

  unique (tenant_id, application_id, room_id, message_id),
  unique (tenant_id, application_id, room_id, sequence),

  foreign key (tenant_id, application_id, room_id)
    references public.project_rooms
      (tenant_id, application_id, room_id),

  foreign key (tenant_id, application_id, room_id, agenda_item_id)
    references public.project_room_agenda_items
      (tenant_id, application_id, room_id, agenda_item_id),

  foreign key (tenant_id, application_id, room_id, participant_id)
    references public.project_room_participants
      (tenant_id, application_id, room_id, participant_id),

  foreign key (tenant_id, application_id, request_id)
    references public.requests
      (tenant_id, application_id, request_id),

  check (content_text is null or length(content_text) <= 32768),
  check (
    content_redacted_at is not null
    or nullif(btrim(content_text), '') is not null
    or nullif(btrim(content_reference), '') is not null
  )
);

create index project_room_messages_sequence_idx
  on public.project_room_messages
    (tenant_id, application_id, room_id, sequence);

create index project_room_messages_agenda_idx
  on public.project_room_messages
    (tenant_id, application_id, room_id, agenda_item_id, sequence);

create index project_room_messages_request_idx
  on public.project_room_messages
    (tenant_id, application_id, request_id)
  where request_id is not null;

create index project_room_messages_participant_idx
  on public.project_room_messages
    (tenant_id, application_id, room_id, participant_id, created_at)
  where participant_id is not null;


create table public.project_room_findings (
  finding_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  raised_by_participant_id uuid not null,
  severity text not null
    check (severity in ('BLOCKER','HIGH','MEDIUM','LOW','NOTE')),
  status text not null default 'OPEN'
    check (status in ('OPEN','ACKNOWLEDGED','RESOLVED','DISMISSED')),
  summary text not null
    check (length(btrim(summary)) between 1 and 4000),
  evidence_refs jsonb not null default '[]'::jsonb
    check (jsonb_typeof(evidence_refs) = 'array'),
  created_at timestamptz not null default now(),
  resolved_at timestamptz,

  foreign key (tenant_id, application_id, room_id)
    references public.project_rooms
      (tenant_id, application_id, room_id),

  foreign key (tenant_id, application_id, room_id, agenda_item_id)
    references public.project_room_agenda_items
      (tenant_id, application_id, room_id, agenda_item_id),

  foreign key (
    tenant_id, application_id, room_id, raised_by_participant_id
  )
    references public.project_room_participants
      (tenant_id, application_id, room_id, participant_id),

  check (
    status not in ('RESOLVED','DISMISSED')
    or resolved_at is not null
  )
);

create index project_room_findings_room_idx
  on public.project_room_findings
    (tenant_id, application_id, room_id, status, created_at desc);


create table public.project_room_decisions (
  decision_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  decision_type text not null
    check (decision_type in ('PROPOSAL','OWNER_DECISION')),
  proposed_by_participant_id uuid,
  owner_principal_id text,
  decision text not null
    check (length(btrim(decision)) between 1 and 4000),
  rationale text
    check (rationale is null or length(rationale) <= 8000),
  status text not null default 'PROPOSED'
    check (status in ('PROPOSED','ACCEPTED','REJECTED','SUPERSEDED')),
  created_at timestamptz not null default now(),
  decided_at timestamptz,

  foreign key (tenant_id, application_id, room_id)
    references public.project_rooms
      (tenant_id, application_id, room_id),

  foreign key (tenant_id, application_id, room_id, agenda_item_id)
    references public.project_room_agenda_items
      (tenant_id, application_id, room_id, agenda_item_id),

  foreign key (
    tenant_id, application_id, room_id, proposed_by_participant_id
  )
    references public.project_room_participants
      (tenant_id, application_id, room_id, participant_id),

  check (
    status not in ('ACCEPTED','REJECTED')
    or (
      owner_principal_id is not null
      and length(btrim(owner_principal_id)) > 0
      and decided_at is not null
    )
  ),
  check (status <> 'PROPOSED' or decided_at is null)
);

create index project_room_decisions_room_idx
  on public.project_room_decisions
    (tenant_id, application_id, room_id, created_at desc);


create table public.project_room_action_items (
  action_item_id uuid primary key default extensions.gen_random_uuid(),
  tenant_id uuid not null,
  application_id uuid not null,
  room_id uuid not null,
  agenda_item_id uuid not null,
  title text not null
    check (length(btrim(title)) between 1 and 500),
  owner_principal_id text,
  status text not null default 'OPEN'
    check (status in ('OPEN','IN_PROGRESS','DONE','CANCELLED')),
  linked_issue_or_pr text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,

  foreign key (tenant_id, application_id, room_id)
    references public.project_rooms
      (tenant_id, application_id, room_id),

  foreign key (tenant_id, application_id, room_id, agenda_item_id)
    references public.project_room_agenda_items
      (tenant_id, application_id, room_id, agenda_item_id),

  check (
    status not in ('DONE','CANCELLED')
    or completed_at is not null
  )
);

create index project_room_action_items_status_idx
  on public.project_room_action_items
    (tenant_id, application_id, room_id, status, created_at);


create or replace function app_private.validate_project_room_participant_independence()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
declare
  opposite_role text;
begin
  if not new.active
     or new.role not in ('BUILDER','INDEPENDENT_AUDITOR') then
    return new;
  end if;

  opposite_role := case new.role
    when 'BUILDER' then 'INDEPENDENT_AUDITOR'
    else 'BUILDER'
  end;

  if exists (
    select 1
    from public.project_room_participants p
    where p.tenant_id = new.tenant_id
      and p.application_id = new.application_id
      and p.room_id = new.room_id
      and p.active
      and p.role = opposite_role
      and p.principal_type = new.principal_type
      and p.principal_id = new.principal_id
      and p.participant_id <> new.participant_id
  ) then
    raise exception
      'principal %:% cannot be both BUILDER and INDEPENDENT_AUDITOR in one room',
      new.principal_type, new.principal_id
      using errcode = '23514';
  end if;

  return new;
end
$$;


create or replace function app_private.assert_project_room_audit_readiness(
  p_tenant_id uuid,
  p_application_id uuid,
  p_room_id uuid
)
returns void
language plpgsql
security invoker
set search_path = ''
as $$
declare
  auditor_count integer;
begin
  select count(*)
    into auditor_count
  from public.project_room_participants p
  where p.tenant_id = p_tenant_id
    and p.application_id = p_application_id
    and p.room_id = p_room_id
    and p.active
    and p.role = 'INDEPENDENT_AUDITOR';

  if auditor_count <> 1 then
    raise exception
      'AUDIT_REVIEW room requires exactly one active INDEPENDENT_AUDITOR; found %',
      auditor_count
      using errcode = '23514';
  end if;

  if exists (
    select 1
    from public.project_room_participants b
    join public.project_room_participants a
      on a.tenant_id = b.tenant_id
     and a.application_id = b.application_id
     and a.room_id = b.room_id
     and a.principal_type = b.principal_type
     and a.principal_id = b.principal_id
    where b.tenant_id = p_tenant_id
      and b.application_id = p_application_id
      and b.room_id = p_room_id
      and b.active
      and a.active
      and b.role = 'BUILDER'
      and a.role = 'INDEPENDENT_AUDITOR'
  ) then
    raise exception
      'AUDIT_REVIEW room violates Builder/Independent Auditor separation'
      using errcode = '23514';
  end if;
end
$$;


create or replace function app_private.enforce_project_room_ready_state()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  if new.mode = 'AUDIT_REVIEW'
     and new.state = 'READY'
     and (
       tg_op = 'INSERT'
       or old.state is distinct from new.state
       or old.mode is distinct from new.mode
     ) then
    perform app_private.assert_project_room_audit_readiness(
      new.tenant_id,
      new.application_id,
      new.room_id
    );
  end if;

  return new;
end
$$;


create or replace function app_private.enforce_project_room_participant_post_ready()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
declare
  v_mode text;
  v_state text;
begin
  if tg_op = 'UPDATE'
     and (
       old.tenant_id,
       old.application_id,
       old.room_id
     ) is distinct from (
       new.tenant_id,
       new.application_id,
       new.room_id
     ) then
    select r.mode, r.state
      into v_mode, v_state
    from public.project_rooms r
    where r.tenant_id = old.tenant_id
      and r.application_id = old.application_id
      and r.room_id = old.room_id;

    if v_mode = 'AUDIT_REVIEW'
       and v_state in (
         'READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION','SUMMARIZING'
       ) then
      perform app_private.assert_project_room_audit_readiness(
        old.tenant_id,
        old.application_id,
        old.room_id
      );
    end if;
  end if;

  select r.mode, r.state
    into v_mode, v_state
  from public.project_rooms r
  where r.tenant_id = new.tenant_id
    and r.application_id = new.application_id
    and r.room_id = new.room_id;

  if v_mode = 'AUDIT_REVIEW'
     and v_state in (
       'READY','RUNNING','PAUSED','NEEDS_OWNER_DECISION','SUMMARIZING'
     ) then
    perform app_private.assert_project_room_audit_readiness(
      new.tenant_id,
      new.application_id,
      new.room_id
    );
  end if;

  return new;
end
$$;


revoke all on function
  app_private.validate_project_room_participant_independence(),
  app_private.assert_project_room_audit_readiness(uuid, uuid, uuid),
  app_private.enforce_project_room_ready_state(),
  app_private.enforce_project_room_participant_post_ready()
from public, anon, authenticated, service_role;

grant execute on function
  app_private.validate_project_room_participant_independence(),
  app_private.assert_project_room_audit_readiness(uuid, uuid, uuid),
  app_private.enforce_project_room_ready_state(),
  app_private.enforce_project_room_participant_post_ready()
to nippan_runtime, nippan_control_plane;


create trigger project_room_participant_independence_guard
before insert or update of
  principal_type, principal_id, role, active, room_id, tenant_id, application_id
on public.project_room_participants
for each row
execute function app_private.validate_project_room_participant_independence();


create trigger project_room_ready_guard
before insert or update of state, mode
on public.project_rooms
for each row
execute function app_private.enforce_project_room_ready_state();


create trigger project_room_participant_ready_guard
after insert or update of
  principal_type, principal_id, role, active, room_id, tenant_id, application_id
on public.project_room_participants
for each row
execute function app_private.enforce_project_room_participant_post_ready();


revoke all on
  public.project_rooms,
  public.project_room_participants,
  public.project_room_agenda_items,
  public.project_room_messages,
  public.project_room_findings,
  public.project_room_decisions,
  public.project_room_action_items
from
  public, anon, authenticated, service_role,
  nippan_runtime, nippan_control_plane, nippan_analytics;


grant select, insert, update on
  public.project_rooms,
  public.project_room_agenda_items,
  public.project_room_findings,
  public.project_room_action_items
to nippan_runtime;

grant select on
  public.project_room_participants
to nippan_runtime;

grant select, insert on
  public.project_room_messages,
  public.project_room_decisions
to nippan_runtime;


grant select, insert, update on
  public.project_rooms,
  public.project_room_participants,
  public.project_room_agenda_items,
  public.project_room_findings,
  public.project_room_action_items
to nippan_control_plane;

grant select, insert on
  public.project_room_messages,
  public.project_room_decisions
to nippan_control_plane;


grant select on
  public.project_rooms,
  public.project_room_participants,
  public.project_room_agenda_items,
  public.project_room_messages,
  public.project_room_findings,
  public.project_room_decisions,
  public.project_room_action_items
to nippan_analytics;


do $$
declare
  t text;
begin
  foreach t in array array[
    'project_rooms',
    'project_room_participants',
    'project_room_agenda_items',
    'project_room_messages',
    'project_room_findings',
    'project_room_decisions',
    'project_room_action_items'
  ] loop
    execute format('alter table public.%I enable row level security', t);

    execute format(
      'create policy war_room_runtime_control_scope on public.%I
       for all to nippan_runtime, nippan_control_plane
       using (
         tenant_id = (select app_private.current_tenant_id())
         and application_id = (select app_private.current_application_id())
       )
       with check (
         tenant_id = (select app_private.current_tenant_id())
         and application_id = (select app_private.current_application_id())
       )',
      t
    );

    execute format(
      'create policy war_room_analytics_read on public.%I
       for select to nippan_analytics
       using (
         tenant_id = (select app_private.current_tenant_id())
         and application_id = (select app_private.current_application_id())
       )',
      t
    );
  end loop;
end
$$;


comment on table public.project_rooms is
  'War Room domain root; tenant/application scoped and budget-bounded.';
comment on table public.project_room_participants is
  'War Room participant membership with canonical principal identity and DB-enforced Builder/Auditor separation.';
comment on table public.project_room_agenda_items is
  'Bounded War Room agenda items with maximum two automatic rounds in V1.';
comment on table public.project_room_messages is
  'Append-only War Room messages; token/cost truth remains in existing AI/usage telemetry.';
comment on table public.project_room_findings is
  'War Room discussion findings; these do not replace formal independent audit records.';
comment on table public.project_room_decisions is
  'Append-only War Room decision records; owner decision audit trail remains in audit_events.';
comment on table public.project_room_action_items is
  'War Room action items linked to room and agenda scope.';

commit;
