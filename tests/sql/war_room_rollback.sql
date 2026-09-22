\set ON_ERROR_STOP on

-- Ephemeral CI rollback-path test for War Room V1 Increment B.
-- This is NOT a production rollback authorization.
-- It is intentionally destructive only inside the disposable CI database.

drop table public.project_room_action_items;
drop table public.project_room_decisions;
drop table public.project_room_findings;
drop table public.project_room_messages;
drop table public.project_room_agenda_items;
drop table public.project_room_participants;
drop table public.project_rooms;

drop function app_private.enforce_project_room_participant_post_ready();
drop function app_private.enforce_project_room_ready_state();
drop function app_private.validate_project_room_participant_independence();
drop function app_private.assert_project_room_audit_readiness(uuid, uuid, uuid);

do $$
declare
  surviving_tables text;
  surviving_functions text;
begin
  select string_agg(v.table_name, ', ' order by v.table_name)
    into surviving_tables
  from (values
    ('project_rooms'),
    ('project_room_participants'),
    ('project_room_agenda_items'),
    ('project_room_messages'),
    ('project_room_findings'),
    ('project_room_decisions'),
    ('project_room_action_items')
  ) as v(table_name)
  where to_regclass('public.' || v.table_name) is not null;

  if surviving_tables is not null then
    raise exception 'War Room rollback left tables behind: %', surviving_tables;
  end if;

  select string_agg(v.function_signature, ', ' order by v.function_signature)
    into surviving_functions
  from (values
    ('app_private.validate_project_room_participant_independence()'),
    ('app_private.assert_project_room_audit_readiness(uuid,uuid,uuid)'),
    ('app_private.enforce_project_room_ready_state()'),
    ('app_private.enforce_project_room_participant_post_ready()')
  ) as v(function_signature)
  where to_regprocedure(v.function_signature) is not null;

  if surviving_functions is not null then
    raise exception 'War Room rollback left helper functions behind: %',
      surviving_functions;
  end if;
end
$$;
