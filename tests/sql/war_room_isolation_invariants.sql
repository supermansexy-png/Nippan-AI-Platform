\set ON_ERROR_STOP on

begin;

-- War Room V1 Increment B isolation/invariant suite.
-- Runs only against ephemeral PostgreSQL 17 CI data and rolls back all fixtures.

do $$
declare
  missing text;
begin
  select string_agg(v.table_name, ', ' order by v.table_name)
    into missing
  from (values
    ('project_rooms'),
    ('project_room_participants'),
    ('project_room_agenda_items'),
    ('project_room_messages'),
    ('project_room_findings'),
    ('project_room_decisions'),
    ('project_room_action_items')
  ) as v(table_name)
  left join pg_class c on c.relname = v.table_name
  left join pg_namespace n
    on n.oid = c.relnamespace
   and n.nspname = 'public'
  where c.oid is null or not c.relrowsecurity;

  if missing is not null then
    raise exception 'War Room RLS missing/disabled for: %', missing;
  end if;
end
$$;


insert into public.tenants (
  tenant_id, slug, display_name, tenant_type, status
) values
  ('11111111-1111-4111-8111-111111111111','war-ci-a','War CI A','internal','active'),
  ('22222222-2222-4222-8222-222222222222','war-ci-b','War CI B','internal','active');

insert into public.applications (
  application_id, tenant_id, slug, display_name, application_type, status
) values
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','11111111-1111-4111-8111-111111111111','war-app-a1','War App A1','test','active'),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','11111111-1111-4111-8111-111111111111','war-app-a2','War App A2','test','active'),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','22222222-2222-4222-8222-222222222222','war-app-b1','War App B1','test','active');

insert into public.agents (
  agent_id, tenant_id, application_id, slug, display_name, role, status
) values
  ('a1111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','builder-a1','Builder A1','builder','active'),
  ('a1111111-1111-4111-8111-111111111112','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','auditor-a1','Auditor A1','auditor','active'),
  ('a1111111-1111-4111-8111-111111111122','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','agent-a2','Agent A2','test','active'),
  ('a2222222-2222-4222-8222-222222222211','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','agent-b1','Agent B1','test','active');

insert into public.requests (
  request_id, trace_id, tenant_id, application_id,
  environment, request_kind, source, privacy_class,
  current_status, received_at
) values
  ('90111111-1111-4111-8111-111111111111','11111111111111111111111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','development','admin_action','war-ci','INTERNAL','RUNNING',now()),
  ('90222222-2222-4222-8222-222222222222','22222222222222222222222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','development','admin_action','war-ci','INTERNAL','RUNNING',now()),
  ('90333333-3333-4333-8333-333333333333','33333333333333333333333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','development','admin_action','war-ci','INTERNAL','RUNNING',now());


insert into public.project_rooms (
  room_id, tenant_id, application_id, project_key, title, mode, state,
  created_by_principal_id, token_budget
) values
  ('10111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','scope-a1','Scope A1','FORMAL_MEETING','DRAFT','ci',1000),
  ('10222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','scope-a2','Scope A2','FORMAL_MEETING','DRAFT','ci',1000),
  ('20333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','scope-b1','Scope B1','FORMAL_MEETING','DRAFT','ci',1000);

insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, participant_type, role, display_name
) values
  ('30111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10111111-1111-4111-8111-111111111111','HUMAN','owner-a1','HUMAN','OWNER','Owner A1'),
  ('30222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','10222222-2222-4222-8222-222222222222','HUMAN','owner-a2','HUMAN','OWNER','Owner A2'),
  ('30333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','20333333-3333-4333-8333-333333333333','HUMAN','owner-b1','HUMAN','OWNER','Owner B1');

insert into public.project_room_agenda_items (
  agenda_item_id, tenant_id, application_id, room_id,
  sequence, title, objective, token_budget
) values
  ('40111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10111111-1111-4111-8111-111111111111',1,'Agenda A1','Test A1',500),
  ('40222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','10222222-2222-4222-8222-222222222222',1,'Agenda A2','Test A2',500),
  ('40333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','20333333-3333-4333-8333-333333333333',1,'Agenda B1','Test B1',500);

insert into public.project_room_messages (
  message_id, tenant_id, application_id, room_id, agenda_item_id,
  request_id, message_type, sequence, content_text
) values
  ('50111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10111111-1111-4111-8111-111111111111','40111111-1111-4111-8111-111111111111','90111111-1111-4111-8111-111111111111','SYSTEM_EVENT',1,'A1'),
  ('50222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','10222222-2222-4222-8222-222222222222','40222222-2222-4222-8222-222222222222','90222222-2222-4222-8222-222222222222','SYSTEM_EVENT',1,'A2'),
  ('50333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','20333333-3333-4333-8333-333333333333','40333333-3333-4333-8333-333333333333','90333333-3333-4333-8333-333333333333','SYSTEM_EVENT',1,'B1');

insert into public.project_room_findings (
  finding_id, tenant_id, application_id, room_id, agenda_item_id,
  raised_by_participant_id, severity, summary
) values
  ('60111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10111111-1111-4111-8111-111111111111','40111111-1111-4111-8111-111111111111','30111111-1111-4111-8111-111111111111','NOTE','A1 finding'),
  ('60222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','10222222-2222-4222-8222-222222222222','40222222-2222-4222-8222-222222222222','30222222-2222-4222-8222-222222222222','NOTE','A2 finding'),
  ('60333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','20333333-3333-4333-8333-333333333333','40333333-3333-4333-8333-333333333333','30333333-3333-4333-8333-333333333333','NOTE','B1 finding');

insert into public.project_room_decisions (
  decision_id, tenant_id, application_id, room_id, agenda_item_id,
  proposed_by_participant_id, decision_type, decision, status
) values
  ('70111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10111111-1111-4111-8111-111111111111','40111111-1111-4111-8111-111111111111','30111111-1111-4111-8111-111111111111','PROPOSAL','A1 decision','PROPOSED'),
  ('70222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','10222222-2222-4222-8222-222222222222','40222222-2222-4222-8222-222222222222','30222222-2222-4222-8222-222222222222','PROPOSAL','A2 decision','PROPOSED'),
  ('70333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','20333333-3333-4333-8333-333333333333','40333333-3333-4333-8333-333333333333','30333333-3333-4333-8333-333333333333','PROPOSAL','B1 decision','PROPOSED');

insert into public.project_room_action_items (
  action_item_id, tenant_id, application_id, room_id, agenda_item_id, title
) values
  ('80111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10111111-1111-4111-8111-111111111111','40111111-1111-4111-8111-111111111111','A1 action'),
  ('80222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2','10222222-2222-4222-8222-222222222222','40222222-2222-4222-8222-222222222222','A2 action'),
  ('80333333-3333-4333-8333-333333333333','22222222-2222-4222-8222-222222222222','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb1','20333333-3333-4333-8333-333333333333','40333333-3333-4333-8333-333333333333','B1 action');


-- Tenant A / Application A1 may see only its own row in all seven tables.
set local role nippan_runtime;
select set_config('app.tenant_id','11111111-1111-4111-8111-111111111111',true);
select set_config('app.application_id','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',true);

do $$
declare
  t text;
  visible_count bigint;
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
    execute format('select count(*) from public.%I', t)
      into visible_count;
    if visible_count <> 1 then
      raise exception
        'tenant/application isolation failed for %, expected 1 visible row, got %',
        t, visible_count;
    end if;
  end loop;
end
$$;

-- Missing tenant context fails closed across all seven tables.
select set_config('app.tenant_id','',true);

do $$
declare
  t text;
  visible_count bigint;
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
    execute format('select count(*) from public.%I', t)
      into visible_count;
    if visible_count <> 0 then
      raise exception 'missing tenant context did not fail closed for %', t;
    end if;
  end loop;
end
$$;

-- Missing application context fails closed across all seven tables.
select set_config('app.tenant_id','11111111-1111-4111-8111-111111111111',true);
select set_config('app.application_id','',true);

do $$
declare
  t text;
  visible_count bigint;
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
    execute format('select count(*) from public.%I', t)
      into visible_count;
    if visible_count <> 0 then
      raise exception 'missing application context did not fail closed for %', t;
    end if;
  end loop;
end
$$;

reset role;


-- Cross-application room FK within the same tenant must fail.
do $$
begin
  begin
    insert into public.project_room_agenda_items (
      agenda_item_id, tenant_id, application_id, room_id,
      sequence, title, objective, token_budget
    ) values (
      '41111111-1111-4111-8111-111111111111',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10222222-2222-4222-8222-222222222222',
      99, 'bad', 'bad', 100
    );
    raise exception 'cross-application room FK unexpectedly accepted';
  exception when foreign_key_violation then
    null;
  end;
end
$$;

-- Scoped request FK must reject a request from another application.
do $$
begin
  begin
    insert into public.project_room_messages (
      message_id, tenant_id, application_id, room_id, agenda_item_id,
      request_id, message_type, sequence, content_text
    ) values (
      '51111111-1111-4111-8111-111111111111',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10111111-1111-4111-8111-111111111111',
      '40111111-1111-4111-8111-111111111111',
      '90222222-2222-4222-8222-222222222222',
      'SYSTEM_EVENT', 99, 'bad request scope'
    );
    raise exception 'cross-application request FK unexpectedly accepted';
  exception when foreign_key_violation then
    null;
  end;
end
$$;

-- Duplicate message sequence in a room must fail.
do $$
begin
  begin
    insert into public.project_room_messages (
      message_id, tenant_id, application_id, room_id, agenda_item_id,
      message_type, sequence, content_text
    ) values (
      '51222222-2222-4222-8222-222222222222',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10111111-1111-4111-8111-111111111111',
      '40111111-1111-4111-8111-111111111111',
      'SYSTEM_EVENT', 1, 'duplicate'
    );
    raise exception 'duplicate message sequence unexpectedly accepted';
  exception when unique_violation then
    null;
  end;
end
$$;

-- V1 bounded rounds: room and agenda values above 2 must fail.
do $$
begin
  begin
    update public.project_rooms
      set automatic_round_limit = 3
      where room_id = '10111111-1111-4111-8111-111111111111';
    raise exception 'room round limit above 2 unexpectedly accepted';
  exception when check_violation then
    null;
  end;

  begin
    update public.project_room_agenda_items
      set round_limit = 3
      where agenda_item_id = '40111111-1111-4111-8111-111111111111';
    raise exception 'agenda round limit above 2 unexpectedly accepted';
  exception when check_violation then
    null;
  end;
end
$$;


-- Runtime cannot mutate participant configuration or append-only rows.
set local role nippan_runtime;
select set_config('app.tenant_id','11111111-1111-4111-8111-111111111111',true);
select set_config('app.application_id','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',true);

do $$
begin
  begin
    insert into public.project_room_participants (
      participant_id, tenant_id, application_id, room_id,
      principal_type, principal_id, participant_type, role, display_name
    ) values (
      '31111111-1111-4111-8111-111111111111',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10111111-1111-4111-8111-111111111111',
      'HUMAN','runtime-insert','HUMAN','SECRETARY','Runtime'
    );
    raise exception 'runtime participant INSERT unexpectedly succeeded';
  exception when insufficient_privilege then
    null;
  end;

  begin
    update public.project_room_messages
      set content_text = 'mutated'
      where message_id = '50111111-1111-4111-8111-111111111111';
    raise exception 'runtime message UPDATE unexpectedly succeeded';
  exception when insufficient_privilege then
    null;
  end;

  begin
    delete from public.project_room_messages
      where message_id = '50111111-1111-4111-8111-111111111111';
    raise exception 'runtime message DELETE unexpectedly succeeded';
  exception when insufficient_privilege then
    null;
  end;

  begin
    update public.project_room_decisions
      set decision = 'mutated'
      where decision_id = '70111111-1111-4111-8111-111111111111';
    raise exception 'runtime decision UPDATE unexpectedly succeeded';
  exception when insufficient_privilege then
    null;
  end;

  begin
    delete from public.project_room_decisions
      where decision_id = '70111111-1111-4111-8111-111111111111';
    raise exception 'runtime decision DELETE unexpectedly succeeded';
  exception when insufficient_privilege then
    null;
  end;
end
$$;

reset role;


-- Analytics is SELECT-only.
set local role nippan_analytics;
select set_config('app.tenant_id','11111111-1111-4111-8111-111111111111',true);
select set_config('app.application_id','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',true);

do $$
begin
  begin
    insert into public.project_rooms (
      room_id, tenant_id, application_id, project_key, title, mode,
      created_by_principal_id, token_budget
    ) values (
      '11112222-3333-4444-8555-666677778888',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      'analytics-write','Analytics Write','FORMAL_MEETING','ci',100
    );
    raise exception 'analytics INSERT unexpectedly succeeded';
  exception when insufficient_privilege then
    null;
  end;
end
$$;

reset role;


-- Audit readiness: zero auditors cannot transition to READY.
insert into public.project_rooms (
  room_id, tenant_id, application_id, project_key, title, mode, state,
  created_by_principal_id, token_budget
) values (
  '10444444-4444-4444-8444-444444444444',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  'audit-zero','Audit Zero','AUDIT_REVIEW','DRAFT','ci',1000
);

do $$
begin
  begin
    update public.project_rooms
      set state = 'READY'
      where room_id = '10444444-4444-4444-8444-444444444444';
    raise exception 'AUDIT_REVIEW with zero auditors unexpectedly reached READY';
  exception when check_violation then
    null;
  end;
end
$$;


-- Audit readiness: two auditors cannot transition to READY.
insert into public.project_rooms (
  room_id, tenant_id, application_id, project_key, title, mode, state,
  created_by_principal_id, token_budget
) values (
  '10555555-5555-4555-8555-555555555555',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  'audit-two','Audit Two','AUDIT_REVIEW','DRAFT','ci',1000
);

insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, participant_type, role, display_name
) values
  ('35111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10555555-5555-4555-8555-555555555555','HUMAN','auditor-one','HUMAN','INDEPENDENT_AUDITOR','Auditor One'),
  ('35222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10555555-5555-4555-8555-555555555555','HUMAN','auditor-two','HUMAN','INDEPENDENT_AUDITOR','Auditor Two');

do $$
begin
  begin
    update public.project_rooms
      set state = 'READY'
      where room_id = '10555555-5555-4555-8555-555555555555';
    raise exception 'AUDIT_REVIEW with two auditors unexpectedly reached READY';
  exception when check_violation then
    null;
  end;
end
$$;


-- Builder/Auditor conflict must use canonical principal identity for HUMAN.
insert into public.project_rooms (
  room_id, tenant_id, application_id, project_key, title, mode, state,
  created_by_principal_id, token_budget
) values (
  '10666666-6666-4666-8666-666666666666',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  'audit-conflict','Audit Conflict','AUDIT_REVIEW','DRAFT','ci',1000
);

insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, participant_type, role, display_name
) values (
  '36111111-1111-4111-8111-111111111111',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  '10666666-6666-4666-8666-666666666666',
  'HUMAN','same-human','HUMAN','BUILDER','Human Builder'
);

do $$
begin
  begin
    insert into public.project_room_participants (
      participant_id, tenant_id, application_id, room_id,
      principal_type, principal_id, participant_type, role, display_name
    ) values (
      '36222222-2222-4222-8222-222222222222',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10666666-6666-4666-8666-666666666666',
      'HUMAN','same-human','HUMAN','INDEPENDENT_AUDITOR','Human Auditor'
    );
    raise exception 'HUMAN Builder/Auditor conflict unexpectedly accepted';
  exception when check_violation then
    null;
  end;
end
$$;

delete from public.project_room_participants
where participant_id = '36111111-1111-4111-8111-111111111111';


-- AGENT canonical principal conflict.
insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, agent_id, participant_type, role, display_name
) values (
  '36333333-3333-4333-8333-333333333333',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  '10666666-6666-4666-8666-666666666666',
  'AGENT','agent-principal-a1',
  'a1111111-1111-4111-8111-111111111111',
  'AGENT','BUILDER','Agent Builder'
);

do $$
begin
  begin
    insert into public.project_room_participants (
      participant_id, tenant_id, application_id, room_id,
      principal_type, principal_id, agent_id, participant_type, role, display_name
    ) values (
      '36444444-4444-4444-8444-444444444444',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10666666-6666-4666-8666-666666666666',
      'AGENT','agent-principal-a1',
      'a1111111-1111-4111-8111-111111111111',
      'AGENT','INDEPENDENT_AUDITOR','Agent Auditor'
    );
    raise exception 'AGENT Builder/Auditor conflict unexpectedly accepted';
  exception when check_violation then
    null;
  end;
end
$$;

delete from public.project_room_participants
where participant_id = '36333333-3333-4333-8333-333333333333';


-- SYSTEM canonical principal conflict.
insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, participant_type, role, display_name
) values (
  '36555555-5555-4555-8555-555555555555',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  '10666666-6666-4666-8666-666666666666',
  'SYSTEM','same-system','SYSTEM','BUILDER','System Builder'
);

do $$
begin
  begin
    insert into public.project_room_participants (
      participant_id, tenant_id, application_id, room_id,
      principal_type, principal_id, participant_type, role, display_name
    ) values (
      '36666666-6666-4666-8666-666666666666',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10666666-6666-4666-8666-666666666666',
      'SYSTEM','same-system','SYSTEM','INDEPENDENT_AUDITOR','System Auditor'
    );
    raise exception 'SYSTEM Builder/Auditor conflict unexpectedly accepted';
  exception when check_violation then
    null;
  end;
end
$$;

delete from public.project_room_participants
where participant_id = '36555555-5555-4555-8555-555555555555';


-- Valid Audit Review can enter READY with exactly one independent auditor.
insert into public.project_rooms (
  room_id, tenant_id, application_id, project_key, title, mode, state,
  created_by_principal_id, token_budget
) values (
  '10777777-7777-4777-8777-777777777777',
  '11111111-1111-4111-8111-111111111111',
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
  'audit-valid','Audit Valid','AUDIT_REVIEW','DRAFT','ci',1000
);

insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, participant_type, role, display_name
) values
  ('37111111-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10777777-7777-4777-8777-777777777777','HUMAN','builder-valid','HUMAN','BUILDER','Builder Valid'),
  ('37222222-2222-4222-8222-222222222222','11111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1','10777777-7777-4777-8777-777777777777','HUMAN','auditor-valid','HUMAN','INDEPENDENT_AUDITOR','Auditor Valid');

update public.project_rooms
set state = 'READY'
where room_id = '10777777-7777-4777-8777-777777777777';


-- Participant mutation after READY cannot invalidate exactly-one auditor.
do $$
begin
  begin
    update public.project_room_participants
      set active = false
      where participant_id = '37222222-2222-4222-8222-222222222222';
    raise exception 'READY audit room unexpectedly allowed auditor deactivation';
  exception when check_violation then
    null;
  end;
end
$$;

-- Adding a second auditor after READY must also fail and roll back the insert.
do $$
begin
  begin
    insert into public.project_room_participants (
      participant_id, tenant_id, application_id, room_id,
      principal_type, principal_id, participant_type, role, display_name
    ) values (
      '37333333-3333-4333-8333-333333333333',
      '11111111-1111-4111-8111-111111111111',
      'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1',
      '10777777-7777-4777-8777-777777777777',
      'HUMAN','auditor-second','HUMAN','INDEPENDENT_AUDITOR','Auditor Second'
    );
    raise exception 'READY audit room unexpectedly allowed second auditor';
  exception when check_violation then
    null;
  end;
end
$$;


rollback;
