\set ON_ERROR_STOP on

-- War Room Increment B disposable PostgreSQL suite.
-- Apply all migrations first, then run this file as a PostgreSQL test principal
-- able to SET ROLE nippan_runtime/nippan_control_plane/nippan_analytics.
-- It must never run against production or a Supabase project.

begin;

create temporary table wr_ids (key text primary key, value uuid not null);
insert into wr_ids values
  ('tenant_a','31111111-1111-4111-8111-111111111111'),
  ('tenant_b','32222222-2222-4222-8222-222222222222'),
  ('app_a','3aaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1'),
  ('app_a2','3aaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2'),
  ('app_b','3bbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2'),
  ('agent_a','3a111111-1111-4111-8111-111111111111'),
  ('agent_b','3b222222-2222-4222-8222-222222222222'),
  ('room_a','3c111111-1111-4111-8111-111111111111'),
  ('room_b','3c222222-2222-4222-8222-222222222222'),
  ('agenda_a','3d111111-1111-4111-8111-111111111111'),
  ('request_a','3e111111-1111-4111-8111-111111111111'),
  ('request_b','3e222222-2222-4222-8222-222222222222');

insert into public.tenants (tenant_id, slug, display_name, tenant_type, status)
select value, key, key, 'internal', 'active' from wr_ids where key in ('tenant_a','tenant_b');
insert into public.applications (application_id, tenant_id, slug, display_name, application_type, status)
select (select value from wr_ids where key = 'app_a'), (select value from wr_ids where key = 'tenant_a'), 'war-a', 'War A', 'internal_tool', 'active'
union all select (select value from wr_ids where key = 'app_b'), (select value from wr_ids where key = 'tenant_b'), 'war-b', 'War B', 'internal_tool', 'active';
insert into public.applications (application_id, tenant_id, slug, display_name, application_type, status)
values ((select value from wr_ids where key = 'app_a2'), (select value from wr_ids where key = 'tenant_a'), 'war-a2', 'War A2', 'internal_tool', 'active');
insert into public.agents (agent_id, tenant_id, application_id, slug, display_name, role, status)
select (select value from wr_ids where key='agent_a'), (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), 'agent-a', 'Agent A', 'builder', 'active'
union all select (select value from wr_ids where key='agent_b'), (select value from wr_ids where key='tenant_b'), (select value from wr_ids where key='app_b'), 'agent-b', 'Agent B', 'builder', 'active';
insert into public.requests (request_id, trace_id, tenant_id, application_id, environment, request_kind, source, privacy_class, current_status, received_at)
select (select value from wr_ids where key='request_a'), repeat('a',32), (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), 'development', 'evaluation', 'war-room-test', 'INTERNAL', 'RUNNING', now()
union all select (select value from wr_ids where key='request_b'), repeat('b',32), (select value from wr_ids where key='tenant_b'), (select value from wr_ids where key='app_b'), 'development', 'evaluation', 'war-room-test', 'INTERNAL', 'RUNNING', now();

insert into public.project_rooms (room_id, tenant_id, application_id, project_key, title, mode, token_budget, audit_baseline_ref, audit_baseline_sha)
select (select value from wr_ids where key='room_a'), (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), 'audit-a', 'Audit A', 'AUDIT_REVIEW', 1000, 'PR-27', repeat('a',40)
union all select (select value from wr_ids where key='room_b'), (select value from wr_ids where key='tenant_b'), (select value from wr_ids where key='app_b'), 'audit-b', 'Audit B', 'AUDIT_REVIEW', 1000, 'PR-27', repeat('b',40);
insert into public.project_room_agenda_items (agenda_item_id, tenant_id, application_id, room_id, sequence, title, objective, token_budget)
select (select value from wr_ids where key='agenda_a'), (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), (select value from wr_ids where key='room_a'), 1, 'Evidence', 'Review evidence', 500;
insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name, agent_id)
select (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), (select value from wr_ids where key='room_a'), 'HUMAN', 'owner-a', 'HUMAN', 'OWNER', 'Owner A', null
union all select (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), (select value from wr_ids where key='room_a'), 'AGENT', 'auditor-a', 'AGENT', 'INDEPENDENT_AUDITOR', 'Auditor A', (select value from wr_ids where key='agent_a');

-- Positive readiness path.
update public.project_rooms set state = 'READY' where room_id = (select value from wr_ids where key='room_a');
insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, proposed_by_participant_id, decision_text, evidence_refs)
select (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), (select value from wr_ids where key='room_a'), (select value from wr_ids where key='agenda_a'), 'ADVISORY_AUDIT_OUTCOME', participant_id, 'Advisory evidence is sufficient', '[{"ref":"docs/evidence.md"}]'::jsonb
from public.project_room_participants where room_id = (select value from wr_ids where key='room_a') and role = 'INDEPENDENT_AUDITOR';

-- Positive message and deterministic sequence.
insert into public.project_room_messages (tenant_id, application_id, room_id, agenda_item_id, participant_id, request_id, message_type, evidence_kind, round_number, sequence, content_text)
select (select value from wr_ids where key='tenant_a'), (select value from wr_ids where key='app_a'), (select value from wr_ids where key='room_a'), (select value from wr_ids where key='agenda_a'), participant_id, (select value from wr_ids where key='request_a'), 'AGENT_MESSAGE', 'VERIFIED_EVIDENCE', 1, 1, 'Evidence';

-- RLS positive and fail-closed controls.
set local role nippan_runtime;
select set_config('app.tenant_id',(select value::text from wr_ids where key='tenant_a'),true);
select set_config('app.application_id',(select value::text from wr_ids where key='app_a'),true);
do $$ declare n bigint; begin select count(*) into n from public.project_rooms; if n <> 1 then raise exception 'positive RLS scope failed'; end if; end $$;
select set_config('app.application_id','',true);
do $$ declare n bigint; begin select count(*) into n from public.project_rooms; if n <> 0 then raise exception 'missing application context did not fail closed'; end if; end $$;
select set_config('app.tenant_id','',true);
select set_config('app.application_id',(select value::text from wr_ids where key='app_a'),true);
do $$ declare n bigint; begin select count(*) into n from public.project_rooms; if n <> 0 then raise exception 'missing tenant context did not fail closed'; end if; end $$;
select set_config('app.tenant_id',(select value::text from wr_ids where key='tenant_b'),true);
do $$ declare n bigint; begin select count(*) into n from public.project_rooms; if n <> 0 then raise exception 'wrong tenant was visible'; end if; end $$;
select set_config('app.tenant_id',(select value::text from wr_ids where key='tenant_a'),true);
select set_config('app.application_id',(select value::text from wr_ids where key='app_a2'),true);
do $$ declare n bigint; begin select count(*) into n from public.project_rooms; if n <> 0 then raise exception 'wrong application was visible'; end if; end $$;
reset role;

-- Privilege negative controls.
do $$ begin
  if has_table_privilege('nippan_runtime','public.project_room_participants','INSERT') then raise exception 'runtime can mutate participants'; end if;
  if has_table_privilege('nippan_runtime','public.project_room_messages','UPDATE') or has_table_privilege('nippan_runtime','public.project_room_messages','DELETE') then raise exception 'runtime can mutate/delete messages'; end if;
  if has_table_privilege('nippan_control_plane','public.project_room_decisions','UPDATE') or has_table_privilege('nippan_control_plane','public.project_room_decisions','DELETE') then raise exception 'control plane can mutate/delete decisions'; end if;
  if has_table_privilege('nippan_analytics','public.project_rooms','INSERT') or has_table_privilege('nippan_analytics','public.project_rooms','UPDATE') or has_table_privilege('nippan_analytics','public.project_rooms','DELETE') then raise exception 'analytics has mutation privilege'; end if;
  if (select rolsuper or rolbypassrls from pg_roles where rolname='nippan_runtime') or (select rolsuper or rolbypassrls from pg_roles where rolname='nippan_control_plane') or (select rolsuper or rolbypassrls from pg_roles where rolname='nippan_analytics') then raise exception 'project role bypasses security'; end if;
end $$;

-- Constraint negative controls.
do $$ begin
  begin insert into public.project_room_messages (tenant_id, application_id, room_id, agenda_item_id, message_type, sequence, content_text) values ((select value from wr_ids where key='tenant_b'),(select value from wr_ids where key='app_b'),(select value from wr_ids where key='room_a'),(select value from wr_ids where key='agenda_a'),'OWNER_MESSAGE',2,'cross scope'); raise exception 'cross scope message accepted'; exception when foreign_key_violation then null; end;
  begin insert into public.project_room_messages (tenant_id, application_id, room_id, agenda_item_id, message_type, sequence, content_text) values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a2'),(select value from wr_ids where key='room_a'),(select value from wr_ids where key='agenda_a'),'OWNER_MESSAGE',2,'cross application'); raise exception 'cross application message accepted'; exception when foreign_key_violation then null; end;
  begin insert into public.project_room_messages (tenant_id, application_id, room_id, agenda_item_id, message_type, sequence, content_text) values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),(select value from wr_ids where key='room_a'),(select value from wr_ids where key='agenda_a'),'OWNER_MESSAGE',1,'duplicate'); raise exception 'duplicate sequence accepted'; exception when unique_violation then null; end;
  begin insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, automatic_round_limit, token_budget, audit_baseline_ref, audit_baseline_sha) values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'bad-round','Bad','FORMAL_MEETING',3,1); raise exception 'round >2 accepted'; exception when check_violation then null; end;
  begin insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget, audit_baseline_ref, audit_baseline_sha) values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'bad-sha','Bad','AUDIT_REVIEW',1,'PR-27','BAD'); raise exception 'bad SHA accepted'; exception when check_violation then null; end;
end $$;

do $$ declare missing text; begin
  select string_agg(v.table_name, ', ' order by v.table_name) into missing
  from (values ('project_rooms'),('project_room_participants'),('project_room_agenda_items'),('project_room_messages'),('project_room_findings'),('project_room_decisions'),('project_room_action_items')) v(table_name)
  left join pg_class c on c.relname=v.table_name
  left join pg_namespace n on n.oid=c.relnamespace and n.nspname='public'
  where c.oid is null or not c.relrowsecurity;
  if missing is not null then raise exception 'War Room RLS missing: %', missing; end if;
end $$;

do $$ declare unsafe text; begin
  select string_agg(p.proname, ', ') into unsafe
  from pg_proc p join pg_namespace n on n.oid=p.pronamespace
  where n.nspname='app_private' and p.proname in ('validate_project_room_participant_independence','assert_project_room_audit_readiness','validate_project_room_participant_readiness','validate_project_room_state_readiness','validate_project_room_decision')
    and p.prosecdef;
  if unsafe is not null then raise exception 'War Room helper unexpectedly SECURITY DEFINER: %', unsafe; end if;
end $$;

-- Audit readiness negative controls.
do $$ declare bad_room uuid; begin
  insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'missing-auditor','Missing Auditor','AUDIT_REVIEW',100)
    returning room_id into bad_room;
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','owner-missing','HUMAN','OWNER','Owner');
  begin update public.project_rooms set state='READY' where room_id=bad_room; raise exception 'Audit Review without Auditor accepted'; exception when sqlstate '23514' then null; end;
end $$;

do $$ declare bad_room uuid; begin
  insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget, audit_baseline_ref, audit_baseline_sha)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'two-auditors','Two Auditors','AUDIT_REVIEW',100,'PR-27',repeat('c',40)) returning room_id into bad_room;
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','owner-two','HUMAN','OWNER','Owner'),
           ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','auditor-two-a','HUMAN','INDEPENDENT_AUDITOR','Auditor A'),
           ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','auditor-two-b','HUMAN','INDEPENDENT_AUDITOR','Auditor B');
  begin update public.project_rooms set state='READY' where room_id=bad_room; raise exception 'Audit Review with two Auditors accepted'; exception when sqlstate '23514' then null; end;
end $$;

do $$ declare bad_room uuid; begin
  insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget, audit_baseline_ref, audit_baseline_sha)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'shared-principal','Shared Principal','AUDIT_REVIEW',100,'PR-27',repeat('d',40)) returning room_id into bad_room;
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','owner-shared','HUMAN','OWNER','Owner'),
           ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','shared','HUMAN','BUILDER','Builder');
  begin
    insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
      values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),bad_room,'HUMAN','shared','HUMAN','INDEPENDENT_AUDITOR','Auditor');
    raise exception 'Builder/Auditor shared principal accepted';
  exception when sqlstate '23514' then null; end;
end $$;

do $$ begin
  begin update public.project_room_participants set active=false where room_id=(select value from wr_ids where key='room_a') and role='INDEPENDENT_AUDITOR'; raise exception 'Ready room invalidation accepted'; exception when sqlstate '23514' then null; end;
end $$;

do $$ begin
  begin
    insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, decision_text, evidence_refs)
      values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),(select value from wr_ids where key='room_a'),(select value from wr_ids where key='agenda_a'),'ADVISORY_AUDIT_OUTCOME','Missing evidence','[]'::jsonb);
    raise exception 'Advisory outcome without Auditor/evidence accepted';
  exception when sqlstate '42501' then null; end;
end $$;

do $$ declare free_room uuid; agenda uuid; auditor uuid; begin
  insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'free-outcome','Free','FREE_DISCUSSION',100) returning room_id into free_room;
  insert into public.project_room_agenda_items (tenant_id, application_id, room_id, sequence, title, objective, token_budget)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),free_room,1,'Free','Discuss',50) returning agenda_item_id into agenda;
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),free_room,'HUMAN','owner-free','HUMAN','OWNER','Owner');
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),free_room,'HUMAN','auditor-free','HUMAN','INDEPENDENT_AUDITOR','Auditor') returning participant_id into auditor;
  begin
    insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, proposed_by_participant_id, decision_text, evidence_refs)
      values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),free_room,agenda,'ADVISORY_AUDIT_OUTCOME',auditor,'Wrong mode','[{"ref":"e"}]');
    raise exception 'Outcome in Free Discussion accepted';
  exception when sqlstate '23514' then null; end;
end $$;

-- Non-auditor and non-Audit-Review outcome controls.
do $$ declare builder_id uuid; begin
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),(select value from wr_ids where key='room_a'),'HUMAN','builder-a','HUMAN','BUILDER','Builder') returning participant_id into builder_id;
  begin
    insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, proposed_by_participant_id, decision_text, evidence_refs)
      values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),(select value from wr_ids where key='room_a'),(select value from wr_ids where key='agenda_a'),'ADVISORY_AUDIT_OUTCOME',builder_id,'Builder outcome','[{"ref":"e"}]');
    raise exception 'Non-auditor outcome accepted';
  exception when sqlstate '42501' then null; end;
end $$;

do $$ declare formal_room uuid; formal_agenda uuid; formal_auditor uuid; begin
  insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'formal-outcome','Formal','FORMAL_MEETING',100) returning room_id into formal_room;
  insert into public.project_room_agenda_items (tenant_id, application_id, room_id, sequence, title, objective, token_budget)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),formal_room,1,'Formal','Discuss',50) returning agenda_item_id into formal_agenda;
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),formal_room,'HUMAN','owner-formal','HUMAN','OWNER','Owner');
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),formal_room,'HUMAN','auditor-formal','HUMAN','INDEPENDENT_AUDITOR','Auditor') returning participant_id into formal_auditor;
  begin
    insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, proposed_by_participant_id, decision_text, evidence_refs)
      values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),formal_room,formal_agenda,'ADVISORY_AUDIT_OUTCOME',formal_auditor,'Wrong mode','[{"ref":"e"}]');
    raise exception 'Formal meeting outcome accepted';
  exception when sqlstate '23514' then null; end;
end $$;

-- Owner approval controls: non-HUMAN and Builder self-approval are rejected.
do $$ declare builder_id uuid; agenda uuid; room_id uuid; begin
  insert into public.project_room_agenda_items (tenant_id, application_id, room_id, sequence, title, objective, token_budget)
    values ((select value from wr_ids where key='tenant_b'),(select value from wr_ids where key='app_b'),(select value from wr_ids where key='room_b'),1,'Owner','Approve',50) returning agenda_item_id into agenda;
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_b'),(select value from wr_ids where key='app_b'),(select value from wr_ids where key='room_b'),'HUMAN','builder-owner','HUMAN','OWNER','Owner');
  insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name)
    values ((select value from wr_ids where key='tenant_b'),(select value from wr_ids where key='app_b'),(select value from wr_ids where key='room_b'),'HUMAN','builder-owner','HUMAN','BUILDER','Builder') returning participant_id into builder_id;
  begin
    insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, proposed_by_participant_id, owner_principal_id, decision_text, evidence_refs, status, decided_at)
      values ((select value from wr_ids where key='tenant_b'),(select value from wr_ids where key='app_b'),(select value from wr_ids where key='room_b'),agenda,'OWNER_DECISION',builder_id,'builder-owner','Self approve','[]'::jsonb,'ACCEPTED',now());
    raise exception 'Builder self-approval accepted';
  exception when sqlstate '42501' then null; end;
  begin
    insert into public.project_room_decisions (tenant_id, application_id, room_id, agenda_item_id, decision_type, proposed_by_participant_id, owner_principal_id, decision_text, evidence_refs, status, decided_at)
      values ((select value from wr_ids where key='tenant_b'),(select value from wr_ids where key='app_b'),(select value from wr_ids where key='room_b'),agenda,'OWNER_DECISION',builder_id,'auditor-agent','Non-human owner','[]'::jsonb,'ACCEPTED',now());
    raise exception 'Non-human owner approval accepted';
  exception when sqlstate '42501' then null; end;
end $$;

-- Analytics is read-only at the actual privilege boundary.
set local role nippan_analytics;
do $$ begin
  begin insert into public.project_rooms (tenant_id, application_id, project_key, title, mode, token_budget) values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),'analytics-write','Bad','FORMAL_MEETING',10); raise exception 'analytics INSERT succeeded'; exception when insufficient_privilege then null; end;
  begin update public.project_rooms set title='Bad' where room_id=(select value from wr_ids where key='room_a'); raise exception 'analytics UPDATE succeeded'; exception when insufficient_privilege then null; end;
  begin delete from public.project_rooms where room_id=(select value from wr_ids where key='room_a'); raise exception 'analytics DELETE succeeded'; exception when insufficient_privilege then null; end;
end $$;
reset role;

-- Function privilege negative controls: helper mutations are never public or analytics-callable.
do $$ begin
  if exists (
    select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
    cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
    where n.nspname='app_private' and p.proname='validate_project_room_decision' and a.grantee=0 and a.privilege_type='EXECUTE'
  ) then raise exception 'PUBLIC can execute decision helper'; end if;
  if has_function_privilege('anon','app_private.validate_project_room_decision()','EXECUTE') then raise exception 'anon can execute decision helper'; end if;
  if has_function_privilege('authenticated','app_private.validate_project_room_decision()','EXECUTE') then raise exception 'authenticated can execute decision helper'; end if;
  if has_function_privilege('nippan_analytics','app_private.validate_project_room_decision()','EXECUTE') then raise exception 'analytics can execute decision helper'; end if;
end $$;

-- Runtime privilege-level enforcement, not just application convention.
set local role nippan_runtime;
select set_config('app.tenant_id',(select value::text from wr_ids where key='tenant_a'),true);
select set_config('app.application_id',(select value::text from wr_ids where key='app_a'),true);
do $$ begin
  begin update public.project_room_messages set content_text='mutated' where sequence=1; raise exception 'runtime message UPDATE succeeded'; exception when insufficient_privilege then null; end;
  begin delete from public.project_room_messages where sequence=1; raise exception 'runtime message DELETE succeeded'; exception when insufficient_privilege then null; end;
  begin update public.project_room_decisions set decision_text='mutated'; raise exception 'runtime decision UPDATE succeeded'; exception when insufficient_privilege then null; end;
  begin delete from public.project_room_decisions; raise exception 'runtime decision DELETE succeeded'; exception when insufficient_privilege then null; end;
  begin insert into public.project_room_participants (tenant_id, application_id, room_id, principal_type, principal_id, participant_type, role, display_name) values ((select value from wr_ids where key='tenant_a'),(select value from wr_ids where key='app_a'),(select value from wr_ids where key='room_a'),'HUMAN','bad-runtime','HUMAN','BUILDER','Bad'); raise exception 'runtime participant INSERT succeeded'; exception when insufficient_privilege then null; end;
end $$;
reset role;

-- Positive owner approval and advisory rows remain domain rows, not formal audit records.
do $$ begin
  if not has_table_privilege('nippan_control_plane','public.project_room_decisions','INSERT') then raise exception 'control plane cannot insert decisions'; end if;
  if not has_table_privilege('nippan_runtime','public.project_room_messages','INSERT') then raise exception 'runtime cannot insert messages'; end if;
end $$;

rollback;
