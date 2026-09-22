import os
import subprocess
import tempfile
import time
from pathlib import Path


PSQL = ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-qAt"]
TENANT_ID = "44444444-4444-4444-8444-444444444444"
APPLICATION_ID = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"


def run_sql(sql, *, app_name="war-room-concurrency", expect_error=None):
    env = os.environ.copy()
    env["PGAPPNAME"] = app_name
    result = subprocess.run(
        PSQL,
        input=sql,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    output = result.stdout + result.stderr
    if expect_error is None and result.returncode != 0:
        raise AssertionError(f"psql failed for {app_name}:\n{output}")
    if expect_error is not None:
        if result.returncode == 0:
            raise AssertionError(
                f"{app_name} unexpectedly committed; expected {expect_error!r}"
            )
        if expect_error not in output:
            raise AssertionError(
                f"{app_name} failed without expected evidence {expect_error!r}:\n{output}"
            )
    return output.strip()


def scalar(sql):
    return run_sql(sql).splitlines()[-1]


def run_serialized_race(name, holder_mutation, contender_mutation, expected_error):
    with tempfile.TemporaryDirectory(prefix="war-room-race-") as temp_dir:
        marker = Path(temp_dir) / "holder-locked"
        holder_sql = rf"""
begin;
set local statement_timeout = '15s';
{holder_mutation}
\! touch {marker.as_posix()}
select pg_sleep(1.25);
commit;
"""
        env = os.environ.copy()
        env["PGAPPNAME"] = f"war-room-{name}-holder"
        holder = subprocess.Popen(
            PSQL,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        assert holder.stdin is not None
        holder.stdin.write(holder_sql)
        holder.stdin.close()

        deadline = time.monotonic() + 10
        while not marker.exists():
            if holder.poll() is not None:
                assert holder.stdout is not None
                raise AssertionError(
                    f"{name} holder exited before acquiring the room lock:\n"
                    f"{holder.stdout.read()}"
                )
            if time.monotonic() >= deadline:
                holder.kill()
                raise AssertionError(f"{name} holder did not acquire the room lock")
            time.sleep(0.025)

        started = time.monotonic()
        contender_output = run_sql(
            f"""
begin;
set local lock_timeout = '8s';
set local statement_timeout = '12s';
{contender_mutation}
commit;
""",
            app_name=f"war-room-{name}-contender",
            expect_error=expected_error,
        )
        waited_seconds = time.monotonic() - started

        holder_returncode = holder.wait(timeout=10)
        assert holder.stdout is not None
        holder_output = holder.stdout.read()
        if holder_returncode != 0:
            raise AssertionError(f"{name} holder failed:\n{holder_output}")
        if waited_seconds < 0.75:
            raise AssertionError(
                f"{name} contender did not wait for room serialization "
                f"({waited_seconds:.3f}s)"
            )

        evidence_line = next(
            line for line in contender_output.splitlines() if expected_error in line
        )
        print(
            f"PASS {name}: waited={waited_seconds:.3f}s; "
            f"evidence={evidence_line.strip()}"
        )


SETUP_SQL = f"""
update public.project_rooms
set state = 'DRAFT'
where tenant_id = '{TENANT_ID}';
delete from public.project_room_participants where tenant_id = '{TENANT_ID}';
delete from public.project_rooms where tenant_id = '{TENANT_ID}';
delete from public.applications where tenant_id = '{TENANT_ID}';
delete from public.tenants where tenant_id = '{TENANT_ID}';

insert into public.tenants (
  tenant_id, slug, display_name, tenant_type, status
) values (
  '{TENANT_ID}', 'war-concurrency', 'War Concurrency', 'internal', 'active'
);

insert into public.applications (
  application_id, tenant_id, slug, display_name, application_type, status
) values (
  '{APPLICATION_ID}', '{TENANT_ID}', 'war-concurrency',
  'War Concurrency', 'test', 'active'
);

insert into public.project_rooms (
  room_id, tenant_id, application_id, project_key, title, mode, state,
  created_by_principal_id, token_budget
) values
  ('90000000-0000-4000-8000-000000000001','{TENANT_ID}','{APPLICATION_ID}','race-separation','Race Separation','FORMAL_MEETING','DRAFT','ci',1000),
  ('90000000-0000-4000-8000-000000000002','{TENANT_ID}','{APPLICATION_ID}','race-auditor-ready-first','Race Auditor Ready First','AUDIT_REVIEW','DRAFT','ci',1000),
  ('90000000-0000-4000-8000-000000000003','{TENANT_ID}','{APPLICATION_ID}','race-deactivate-ready-first','Race Deactivate Ready First','AUDIT_REVIEW','DRAFT','ci',1000),
  ('90000000-0000-4000-8000-000000000004','{TENANT_ID}','{APPLICATION_ID}','race-identity-ready-first','Race Identity Ready First','AUDIT_REVIEW','DRAFT','ci',1000),
  ('90000000-0000-4000-8000-000000000005','{TENANT_ID}','{APPLICATION_ID}','race-auditor-participant-first','Race Auditor Participant First','AUDIT_REVIEW','DRAFT','ci',1000),
  ('90000000-0000-4000-8000-000000000006','{TENANT_ID}','{APPLICATION_ID}','race-deactivate-participant-first','Race Deactivate Participant First','AUDIT_REVIEW','DRAFT','ci',1000);

insert into public.project_room_participants (
  participant_id, tenant_id, application_id, room_id,
  principal_type, principal_id, participant_type, role, display_name
) values
  ('91000000-0000-4000-8000-000000000001','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000001','HUMAN','owner-1','HUMAN','OWNER','Owner 1'),
  ('91000000-0000-4000-8000-000000000002','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000002','HUMAN','owner-2','HUMAN','OWNER','Owner 2'),
  ('91000000-0000-4000-8000-000000000003','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000002','HUMAN','auditor-2','HUMAN','INDEPENDENT_AUDITOR','Auditor 2'),
  ('91000000-0000-4000-8000-000000000004','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000003','HUMAN','owner-3','HUMAN','OWNER','Owner 3'),
  ('91000000-0000-4000-8000-000000000005','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000003','HUMAN','auditor-3','HUMAN','INDEPENDENT_AUDITOR','Auditor 3'),
  ('91000000-0000-4000-8000-000000000006','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000004','HUMAN','owner-4','HUMAN','OWNER','Owner 4'),
  ('91000000-0000-4000-8000-000000000007','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000004','HUMAN','builder-4','HUMAN','BUILDER','Builder 4'),
  ('91000000-0000-4000-8000-000000000008','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000004','HUMAN','auditor-4','HUMAN','INDEPENDENT_AUDITOR','Auditor 4'),
  ('91000000-0000-4000-8000-000000000009','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000005','HUMAN','owner-5','HUMAN','OWNER','Owner 5'),
  ('91000000-0000-4000-8000-000000000010','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000005','HUMAN','auditor-5','HUMAN','INDEPENDENT_AUDITOR','Auditor 5'),
  ('91000000-0000-4000-8000-000000000011','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000006','HUMAN','owner-6','HUMAN','OWNER','Owner 6'),
  ('91000000-0000-4000-8000-000000000012','{TENANT_ID}','{APPLICATION_ID}','90000000-0000-4000-8000-000000000006','HUMAN','auditor-6','HUMAN','INDEPENDENT_AUDITOR','Auditor 6');
"""

CLEANUP_SQL = f"""
update public.project_rooms
set state = 'DRAFT'
where tenant_id = '{TENANT_ID}';
delete from public.project_room_participants where tenant_id = '{TENANT_ID}';
delete from public.project_rooms where tenant_id = '{TENANT_ID}';
delete from public.applications where tenant_id = '{TENANT_ID}';
delete from public.tenants where tenant_id = '{TENANT_ID}';
"""


def main():
    run_sql(SETUP_SQL, app_name="war-room-concurrency-setup")
    try:
        run_serialized_race(
            "builder-auditor",
            f"""insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, participant_type, role, display_name
            ) values (
              '92000000-0000-4000-8000-000000000001','{TENANT_ID}','{APPLICATION_ID}',
              '90000000-0000-4000-8000-000000000001','HUMAN','shared-principal',
              'HUMAN','BUILDER','Concurrent Builder'
            );""",
            f"""insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, participant_type, role, display_name
            ) values (
              '92000000-0000-4000-8000-000000000002','{TENANT_ID}','{APPLICATION_ID}',
              '90000000-0000-4000-8000-000000000001','HUMAN','shared-principal',
              'HUMAN','INDEPENDENT_AUDITOR','Concurrent Auditor'
            );""",
            "cannot be both BUILDER and INDEPENDENT_AUDITOR",
        )

        run_serialized_race(
            "ready-before-second-auditor",
            """update public.project_rooms set state = 'READY'
               where room_id = '90000000-0000-4000-8000-000000000002';""",
            f"""insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, participant_type, role, display_name
            ) values (
              '92000000-0000-4000-8000-000000000003','{TENANT_ID}','{APPLICATION_ID}',
              '90000000-0000-4000-8000-000000000002','HUMAN','auditor-2b',
              'HUMAN','INDEPENDENT_AUDITOR','Auditor 2B'
            );""",
            "requires exactly one active INDEPENDENT_AUDITOR; found 2",
        )

        run_serialized_race(
            "ready-before-auditor-deactivate",
            """update public.project_rooms set state = 'READY'
               where room_id = '90000000-0000-4000-8000-000000000003';""",
            """update public.project_room_participants set active = false
               where participant_id = '91000000-0000-4000-8000-000000000005';""",
            "requires exactly one active INDEPENDENT_AUDITOR; found 0",
        )

        run_serialized_race(
            "ready-before-identity-collision",
            """update public.project_rooms set state = 'READY'
               where room_id = '90000000-0000-4000-8000-000000000004';""",
            """update public.project_room_participants
               set principal_id = 'builder-4'
               where participant_id = '91000000-0000-4000-8000-000000000008';""",
            "cannot be both BUILDER and INDEPENDENT_AUDITOR",
        )

        run_serialized_race(
            "second-auditor-before-ready",
            f"""insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, participant_type, role, display_name
            ) values (
              '92000000-0000-4000-8000-000000000004','{TENANT_ID}','{APPLICATION_ID}',
              '90000000-0000-4000-8000-000000000005','HUMAN','auditor-5b',
              'HUMAN','INDEPENDENT_AUDITOR','Auditor 5B'
            );""",
            """update public.project_rooms set state = 'READY'
               where room_id = '90000000-0000-4000-8000-000000000005';""",
            "requires exactly one active INDEPENDENT_AUDITOR; found 2",
        )

        run_serialized_race(
            "auditor-deactivate-before-ready",
            """update public.project_room_participants set active = false
               where participant_id = '91000000-0000-4000-8000-000000000012';""",
            """update public.project_rooms set state = 'READY'
               where room_id = '90000000-0000-4000-8000-000000000006';""",
            "requires exactly one active INDEPENDENT_AUDITOR; found 0",
        )

        checks = {
            "builder_auditor_final": """select count(*) from public.project_room_participants
              where room_id = '90000000-0000-4000-8000-000000000001'
                and active and role in ('BUILDER','INDEPENDENT_AUDITOR');""",
            "ready_second_auditor_final": """select state || ':' || count(*)::text
              from public.project_rooms r
              join public.project_room_participants p using (tenant_id, application_id, room_id)
              where r.room_id = '90000000-0000-4000-8000-000000000002'
                and p.active and p.role = 'INDEPENDENT_AUDITOR'
              group by state;""",
            "ready_deactivate_final": """select state || ':' || count(*)::text
              from public.project_rooms r
              join public.project_room_participants p using (tenant_id, application_id, room_id)
              where r.room_id = '90000000-0000-4000-8000-000000000003'
                and p.active and p.role = 'INDEPENDENT_AUDITOR'
              group by state;""",
            "identity_final": """select count(distinct principal_id)::text
              from public.project_room_participants
              where room_id = '90000000-0000-4000-8000-000000000004'
                and active and role in ('BUILDER','INDEPENDENT_AUDITOR');""",
            "participant_first_second_auditor_final": """select state || ':' || count(*)::text
              from public.project_rooms r
              join public.project_room_participants p using (tenant_id, application_id, room_id)
              where r.room_id = '90000000-0000-4000-8000-000000000005'
                and p.active and p.role = 'INDEPENDENT_AUDITOR'
              group by state;""",
            "participant_first_deactivate_final": """select r.state || ':' || count(p.participant_id)::text
              from public.project_rooms r
              left join public.project_room_participants p
                on p.tenant_id = r.tenant_id
               and p.application_id = r.application_id
               and p.room_id = r.room_id
               and p.active
               and p.role = 'INDEPENDENT_AUDITOR'
              where r.room_id = '90000000-0000-4000-8000-000000000006'
              group by r.state;""",
        }
        expected = {
            "builder_auditor_final": "1",
            "ready_second_auditor_final": "READY:1",
            "ready_deactivate_final": "READY:1",
            "identity_final": "2",
            "participant_first_second_auditor_final": "DRAFT:2",
            "participant_first_deactivate_final": "DRAFT:0",
        }
        for name, query in checks.items():
            actual = scalar(query)
            if actual != expected[name]:
                raise AssertionError(
                    f"{name} expected {expected[name]!r}, got {actual!r}"
                )
            print(f"PASS {name}: final_state={actual}")
    finally:
        run_sql(CLEANUP_SQL, app_name="war-room-concurrency-cleanup")


if __name__ == "__main__":
    main()
