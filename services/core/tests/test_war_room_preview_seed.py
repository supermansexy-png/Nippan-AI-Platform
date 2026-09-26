import os
import subprocess
import sys
from pathlib import Path
import uuid
from uuid import UUID

import psycopg
import pytest


TENANT_ID = UUID("c1111111-1111-4111-8111-111111111111")
APPLICATION_ID = UUID("c2222222-2222-4222-8222-222222222222")
ROOM_ID = UUID("c3333333-3333-4333-8333-333333333333")
CORE_ROOT = Path(__file__).resolve().parents[1]
SEED_SCRIPT = CORE_ROOT / "scripts" / "seed_war_room_preview.py"


def _admin_dsn() -> str:
    value = os.getenv("NIPPAN_TEST_POSTGRES_ADMIN_DSN")
    if not value:
        pytest.skip("NIPPAN_TEST_POSTGRES_ADMIN_DSN is required")
    return value


def _cleanup(admin_dsn: str) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(
            "delete from public.project_room_action_items where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_findings where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_decisions where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_messages where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_agenda_items where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_room_participants where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            "delete from public.project_rooms where room_id = %s",
            (ROOM_ID,),
        )
        conn.execute(
            """
            delete from public.agents
            where tenant_id = %s and application_id = %s
              and slug like 'preview-%%'
            """,
            (TENANT_ID, APPLICATION_ID),
        )
        conn.execute(
            "delete from public.applications where application_id = %s",
            (APPLICATION_ID,),
        )
        conn.execute(
            "delete from public.tenants where tenant_id = %s",
            (TENANT_ID,),
        )


def _cleanup_room(admin_dsn: str, room_id: UUID) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(
            "delete from public.project_room_action_items where room_id = %s",
            (room_id,),
        )
        conn.execute(
            "delete from public.project_room_findings where room_id = %s",
            (room_id,),
        )
        conn.execute(
            "delete from public.project_room_decisions where room_id = %s",
            (room_id,),
        )
        conn.execute(
            "delete from public.project_room_messages where room_id = %s",
            (room_id,),
        )
        conn.execute(
            "delete from public.project_room_agenda_items where room_id = %s",
            (room_id,),
        )
        conn.execute(
            "delete from public.project_room_participants where room_id = %s",
            (room_id,),
        )
        conn.execute(
            "delete from public.project_rooms where room_id = %s",
            (room_id,),
        )


def test_local_preview_seed_creates_room_roster_and_context() -> None:
    admin_dsn = _admin_dsn()
    _cleanup(admin_dsn)

    env = os.environ.copy()
    env.update(
        {
            "NIPPAN_ENVIRONMENT": "development",
            "NIPPAN_WAR_ROOM_PREVIEW_ENABLED": "true",
            "NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN": admin_dsn,
        }
    )
    for key in (
        "NIPPAN_WAR_ROOM_PREVIEW_TENANT_ID",
        "NIPPAN_WAR_ROOM_PREVIEW_APPLICATION_ID",
        "NIPPAN_WAR_ROOM_PREVIEW_PRINCIPAL_ID",
    ):
        env.pop(key, None)

    try:
        result = subprocess.run(
            [sys.executable, str(SEED_SCRIPT)],
            cwd=CORE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert f"ROOM_ID={ROOM_ID}" in result.stdout
        assert (
            f"URL=http://127.0.0.1:8000/war-room/?room_id={ROOM_ID}"
            in result.stdout
        )

        with psycopg.connect(admin_dsn) as conn:
            room = conn.execute(
                """
                select mode, state, token_budget, cost_budget, cost_currency
                from public.project_rooms
                where room_id = %s
                """,
                (ROOM_ID,),
            ).fetchone()
            roles = {
                row[0]
                for row in conn.execute(
                    """
                    select role
                    from public.project_room_participants
                    where room_id = %s and active
                    """,
                    (ROOM_ID,),
                ).fetchall()
            }
            agenda_count = conn.execute(
                "select count(*) from public.project_room_agenda_items where room_id = %s",
                (ROOM_ID,),
            ).fetchone()
            finding_count = conn.execute(
                "select count(*) from public.project_room_findings where room_id = %s",
                (ROOM_ID,),
            ).fetchone()
            decision_count = conn.execute(
                "select count(*) from public.project_room_decisions where room_id = %s",
                (ROOM_ID,),
            ).fetchone()

        assert room == ("FORMAL_MEETING", "DRAFT", 12000, 5, "USD")
        assert roles == {
            "OWNER",
            "CHAIR",
            "ARCHITECT",
            "BUILDER",
            "SECURITY_REVIEWER",
            "COST_OPS_REVIEWER",
            "INDEPENDENT_AUDITOR",
            "SECRETARY",
        }
        assert agenda_count == (1,)
        assert finding_count == (1,)
        assert decision_count == (1,)
    finally:
        _cleanup(admin_dsn)


def test_local_preview_seed_refuses_production_environment() -> None:
    admin_dsn = _admin_dsn()
    env = os.environ.copy()
    env.update(
        {
            "NIPPAN_ENVIRONMENT": "production",
            "NIPPAN_WAR_ROOM_PREVIEW_ENABLED": "true",
            "NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN": admin_dsn,
        }
    )

    result = subprocess.run(
        [sys.executable, str(SEED_SCRIPT)],
        cwd=CORE_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "refuses non-development environment" in result.stderr


def test_local_preview_seed_new_custom_room_has_counts_unchanged_default() -> None:
    admin_dsn = _admin_dsn()
    custom_room_id = uuid.uuid4()
    _cleanup(admin_dsn)
    env = os.environ.copy()
    env.update({
        'NIPPAN_ENVIRONMENT': 'development',
        'NIPPAN_WAR_ROOM_PREVIEW_ENABLED': 'true',
        'NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN': admin_dsn,
    })
    for key in ('NIPPAN_WAR_ROOM_PREVIEW_TENANT_ID', 'NIPPAN_WAR_ROOM_PREVIEW_APPLICATION_ID', 'NIPPAN_WAR_ROOM_PREVIEW_PRINCIPAL_ID'):
        env.pop(key, None)
    try:
        # First seed default room
        result = subprocess.run(
            [sys.executable, str(SEED_SCRIPT)],
            cwd=CORE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        # Seed second room
        env_custom = env.copy()
        result2 = subprocess.run(
            [sys.executable, str(SEED_SCRIPT), '--room-id', str(custom_room_id), '--title', 'Custom Preview Room'],
            cwd=CORE_ROOT,
            env=env_custom,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result2.returncode == 0, result2.stderr
        with psycopg.connect(admin_dsn) as conn:
            default_participants = conn.execute(
                'select count(*) from public.project_room_participants where room_id = %s and active',
                (ROOM_ID,),
            ).fetchone()
            default_agenda = conn.execute(
                'select count(*) from public.project_room_agenda_items where room_id = %s',
                (ROOM_ID,),
            ).fetchone()
            custom_participants = conn.execute(
                'select count(*) from public.project_room_participants where room_id = %s and active',
                (custom_room_id,),
            ).fetchone()
            custom_agenda = conn.execute(
                'select count(*) from public.project_room_agenda_items where room_id = %s',
                (custom_room_id,),
            ).fetchone()
        assert default_participants == (8,)
        assert default_agenda == (1,)
        assert custom_participants == (8,)
        assert custom_agenda == (1,)
    finally:
        _cleanup_room(admin_dsn, custom_room_id)
        _cleanup(admin_dsn)


def test_local_preview_seed_repeat_non_default_without_force_fails() -> None:
    admin_dsn = _admin_dsn()
    custom_room_id = uuid.uuid4()
    env = os.environ.copy()
    env.update({
        'NIPPAN_ENVIRONMENT': 'development',
        'NIPPAN_WAR_ROOM_PREVIEW_ENABLED': 'true',
        'NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN': admin_dsn,
    })
    for key in ('NIPPAN_WAR_ROOM_PREVIEW_TENANT_ID', 'NIPPAN_WAR_ROOM_PREVIEW_APPLICATION_ID', 'NIPPAN_WAR_ROOM_PREVIEW_PRINCIPAL_ID'):
        env.pop(key, None)
    try:
        # Create custom room
        result = subprocess.run(
            [sys.executable, str(SEED_SCRIPT), '--room-id', str(custom_room_id), '--title', 'Custom Preview Room'],
            cwd=CORE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        # Try again without --force
        result2 = subprocess.run(
            [sys.executable, str(SEED_SCRIPT), '--room-id', str(custom_room_id), '--title', 'Custom Preview Room'],
            cwd=CORE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result2.returncode == 1
        with psycopg.connect(admin_dsn) as conn:
            room_exists = conn.execute(
                'select 1 from public.project_rooms where room_id = %s',
                (custom_room_id,),
            ).fetchone()
        assert room_exists is not None
    finally:
        _cleanup_room(admin_dsn, custom_room_id)
        _cleanup(admin_dsn)


def test_local_preview_seed_whitespace_title_fails() -> None:
    admin_dsn = _admin_dsn()
    whitespace_room_id = uuid.uuid4()
    env = os.environ.copy()
    env.update({
        'NIPPAN_ENVIRONMENT': 'development',
        'NIPPAN_WAR_ROOM_PREVIEW_ENABLED': 'true',
        'NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN': admin_dsn,
    })
    for key in ('NIPPAN_WAR_ROOM_PREVIEW_TENANT_ID', 'NIPPAN_WAR_ROOM_PREVIEW_APPLICATION_ID', 'NIPPAN_WAR_ROOM_PREVIEW_PRINCIPAL_ID'):
        env.pop(key, None)
    try:
        result = subprocess.run(
            [sys.executable, str(SEED_SCRIPT), '--room-id', str(whitespace_room_id), '--title', '   '],
            cwd=CORE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1
        with psycopg.connect(admin_dsn) as conn:
            room_exists = conn.execute(
                'select 1 from public.project_rooms where room_id = %s',
                (whitespace_room_id,),
            ).fetchone()
        assert room_exists is None
    finally:
        _cleanup_room(admin_dsn, whitespace_room_id)
        _cleanup(admin_dsn)
