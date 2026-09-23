from __future__ import annotations

import os
from pathlib import Path

import psycopg

from app.settings import Settings
from scripts.seed_war_room_preview import DEFAULT_ROOM_ID, seed


MIGRATION_FILES = (
    "20260922174011_phase2_core_foundation.sql",
    "20260922174227_phase2_core_fk_indexes.sql",
    "20260922180029_phase2_request_trace_telemetry.sql",
    "20260922180107_phase2_idempotency_usage_audit.sql",
    "20260922193829_phase2_a001_least_privilege.sql",
    "20260922231000_war_room_v1_increment_b.sql",
)


class PreviewBootstrapError(RuntimeError):
    """Raised when the preview database cannot be initialized safely."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _relation_exists(conn: psycopg.Connection, qualified_name: str) -> bool:
    row = conn.execute(
        "select to_regclass(%s) is not null",
        (qualified_name,),
    ).fetchone()
    return bool(row and row[0])


def _prepare_supabase_compatibility(conn: psycopg.Connection) -> None:
    conn.execute("create schema if not exists extensions")
    conn.execute(
        """
        do $$
        begin
          if not exists (select 1 from pg_roles where rolname = 'anon') then
            create role anon nologin;
          end if;
          if not exists (select 1 from pg_roles where rolname = 'authenticated') then
            create role authenticated nologin;
          end if;
          if not exists (select 1 from pg_roles where rolname = 'service_role') then
            create role service_role nologin;
          end if;
        end
        $$;
        """
    )


def _apply_reviewed_migrations(
    conn: psycopg.Connection,
    *,
    migrations_dir: Path,
) -> None:
    for filename in MIGRATION_FILES:
        path = migrations_dir / filename
        if not path.is_file():
            raise PreviewBootstrapError(f"reviewed migration missing: {filename}")
        conn.execute(path.read_text())


def bootstrap_preview_database(
    settings: Settings,
    *,
    migrations_dir: Path | None = None,
) -> None:
    """Initialize an isolated development preview using reviewed migrations only."""

    if settings.environment.lower() != "development":
        raise PreviewBootstrapError(
            "preview bootstrap refuses non-development environment"
        )
    if not settings.war_room_preview_enabled:
        raise PreviewBootstrapError(
            "preview bootstrap requires war_room_preview_enabled"
        )
    if not settings.database_url:
        raise PreviewBootstrapError("preview bootstrap requires database_url")

    directory = migrations_dir or (_repo_root() / "migrations")

    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        has_core = _relation_exists(conn, "public.tenants")
        has_requests = _relation_exists(conn, "public.requests")
        has_war_room = _relation_exists(conn, "public.project_rooms")

        if not has_core and not has_requests and not has_war_room:
            _prepare_supabase_compatibility(conn)
            _apply_reviewed_migrations(conn, migrations_dir=directory)
        elif not (has_core and has_requests and has_war_room):
            raise PreviewBootstrapError(
                "preview database is partially initialized; refusing automatic repair"
            )

        room_exists = conn.execute(
            "select exists(select 1 from public.project_rooms where room_id = %s)",
            (DEFAULT_ROOM_ID,),
        ).fetchone()
        if room_exists and room_exists[0]:
            return

    previous_seed_dsn = os.environ.get("NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN")
    os.environ["NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN"] = settings.database_url
    try:
        seed()
    finally:
        if previous_seed_dsn is None:
            os.environ.pop("NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN", None)
        else:
            os.environ["NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN"] = previous_seed_dsn
