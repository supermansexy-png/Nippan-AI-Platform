import os
from urllib.parse import urlsplit, urlunsplit

import psycopg
import pytest

from app.preview_bootstrap import PreviewBootstrapError, bootstrap_preview_database
from app.settings import Settings
from scripts.seed_war_room_preview import DEFAULT_ROOM_ID


TEST_DB = "nippan_preview_bootstrap_it"


def _admin_dsn() -> str:
    value = os.getenv("NIPPAN_TEST_POSTGRES_ADMIN_DSN")
    if not value:
        pytest.skip("NIPPAN_TEST_POSTGRES_ADMIN_DSN is required")
    return value


def _database_dsn(admin_dsn: str, database: str) -> str:
    parts = urlsplit(admin_dsn)
    if parts.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("integration test requires URL-form PostgreSQL DSN")
    return urlunsplit(
        (parts.scheme, parts.netloc, f"/{database}", parts.query, parts.fragment)
    )


def _drop_database(admin_dsn: str) -> None:
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(
            f'drop database if exists "{TEST_DB}" with (force)'
        )


def test_preview_bootstrap_builds_fresh_database_and_is_restart_safe() -> None:
    admin_dsn = _admin_dsn()
    _drop_database(admin_dsn)

    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(f'create database "{TEST_DB}"')

    database_dsn = _database_dsn(admin_dsn, TEST_DB)
    settings = Settings(
        environment="development",
        database_url=database_dsn,
        war_room_preview_enabled=True,
        war_room_preview_bootstrap=True,
    )

    try:
        bootstrap_preview_database(settings)

        with psycopg.connect(database_dsn) as conn:
            state = conn.execute(
                "select state from public.project_rooms where room_id = %s",
                (DEFAULT_ROOM_ID,),
            ).fetchone()
            participant_count = conn.execute(
                """
                select count(*)
                from public.project_room_participants
                where room_id = %s and active
                """,
                (DEFAULT_ROOM_ID,),
            ).fetchone()
            agenda_count = conn.execute(
                """
                select count(*)
                from public.project_room_agenda_items
                where room_id = %s
                """,
                (DEFAULT_ROOM_ID,),
            ).fetchone()

        assert state == ("DRAFT",)
        assert participant_count == (8,)
        assert agenda_count == (1,)

        # A service restart must not reset the durable room or duplicate seed rows.
        bootstrap_preview_database(settings)

        with psycopg.connect(database_dsn) as conn:
            room_count = conn.execute(
                "select count(*) from public.project_rooms where room_id = %s",
                (DEFAULT_ROOM_ID,),
            ).fetchone()
            participant_count_after = conn.execute(
                """
                select count(*)
                from public.project_room_participants
                where room_id = %s and active
                """,
                (DEFAULT_ROOM_ID,),
            ).fetchone()

        assert room_count == (1,)
        assert participant_count_after == (8,)
    finally:
        _drop_database(admin_dsn)


def test_preview_bootstrap_refuses_production_before_connecting() -> None:
    settings = Settings(
        environment="production",
        database_url="postgresql://unused/unused",
        war_room_preview_enabled=True,
        war_room_preview_bootstrap=True,
    )

    with pytest.raises(PreviewBootstrapError, match="non-development"):
        bootstrap_preview_database(settings)
