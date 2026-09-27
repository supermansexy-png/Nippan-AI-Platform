from __future__ import annotations

import argparse
import os
import sys
import uuid as uuid_module
from uuid import UUID, NAMESPACE_URL, uuid5

import psycopg

from app.settings import Settings


DEFAULT_TENANT_ID = UUID("c1111111-1111-4111-8111-111111111111")
DEFAULT_APPLICATION_ID = UUID("c2222222-2222-4222-8222-222222222222")
DEFAULT_ROOM_ID = UUID("c3333333-3333-4333-8333-333333333333")
DEFAULT_OWNER_PRINCIPAL_ID = "preview-owner"
DEFAULT_ROOM_TITLE = "Nippan AI War Room — Preview ภาษาไทย"

AGENT_ROLES = (
    ("CHAIR", "ประธาน Preview", "chair"),
    ("ARCHITECT", "สถาปนิก Preview", "architect"),
    ("BUILDER", "ผู้พัฒนา Preview", "builder"),
    ("SECURITY_REVIEWER", "ผู้ตรวจความปลอดภัย Preview", "security"),
    ("COST_OPS_REVIEWER", "ผู้ตรวจต้นทุนและปฏิบัติการ Preview", "cost-ops"),
    ("INDEPENDENT_AUDITOR", "ผู้ตรวจอิสระ Preview", "auditor"),
    ("SECRETARY", "เลขานุการ Preview", "secretary"),
)


def _stable_uuid(kind: str, value: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"nippan-war-room-preview:{kind}:{value}")


def _required_admin_dsn() -> str:
    value = os.getenv("NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN")
    if not value:
        raise RuntimeError(
            "NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN is required for local seed"
        )
    return value


def _preview_scope(settings: Settings) -> tuple[UUID, UUID, str]:
    tenant_id = settings.war_room_preview_tenant_id or DEFAULT_TENANT_ID
    application_id = (
        settings.war_room_preview_application_id or DEFAULT_APPLICATION_ID
    )
    principal_id = (
        settings.war_room_preview_principal_id or DEFAULT_OWNER_PRINCIPAL_ID
    )
    return tenant_id, application_id, principal_id


def seed(
    *,
    settings: Settings | None = None,
    admin_dsn: str | None = None,
    room_id: UUID | None = None,
    title: str | None = None,
    force: bool = False,
) -> tuple[UUID, UUID, UUID, str]:
    settings = settings or Settings()
    if settings.environment.lower() != "development":
        raise RuntimeError("preview seed refuses non-development environment")
    if not settings.war_room_preview_enabled:
        raise RuntimeError(
            "set NIPPAN_WAR_ROOM_PREVIEW_ENABLED=true before seeding"
        )

    admin_dsn = admin_dsn or _required_admin_dsn()
    tenant_id, application_id, principal_id = _preview_scope(settings)
    room_id = room_id or DEFAULT_ROOM_ID
    room_title = DEFAULT_ROOM_TITLE if title is None else title
    if not room_title or not room_title.strip():
        raise ValueError("room_title must not be empty or whitespace only")
    agenda_id = _stable_uuid("agenda-item", str(room_id))
    owner_participant_id = _stable_uuid("owner-participant", str(room_id))

    tenant_slug = f"war-room-preview-{tenant_id.hex[:8]}"
    application_slug = f"war-room-preview-{application_id.hex[:8]}"

    with psycopg.connect(admin_dsn) as conn:
        # Look up existing title before deciding on --force
        row = conn.execute(
            "select title from public.project_rooms where room_id = %s and tenant_id = %s and application_id = %s",
            (room_id, tenant_id, application_id),
        ).fetchone()
        existing_title = row[0] if row else None
        if room_id != DEFAULT_ROOM_ID and row is not None and not force:
            raise RuntimeError(
                f"refusing to reset room {room_id}: not the default preview room; "
                "pass --force to allow deleting its rows"
            )
        print(f"preview seed target: room_id={room_id} title={room_title!r}" + (f" (existing title: {existing_title!r})" if existing_title else ""))
        # Deletes run in one transaction; the context manager rolls back on error
        # existing rows for the target room, scoped to the preview tenant and
        # application. Without --force only the deterministic default preview
        # room may be targeted; a live room is therefore not touched by
        # accident, but a forced run on a non-default room is destructive.
        conn.execute(
            """
            delete from public.project_room_action_items
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )
        conn.execute(
            """
            delete from public.project_room_findings
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )
        conn.execute(
            """
            delete from public.project_room_decisions
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )
        conn.execute(
            """
            delete from public.project_room_messages
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )
        conn.execute(
            """
            delete from public.project_room_agenda_items
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )
        conn.execute(
            """
            delete from public.project_room_participants
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )
        conn.execute(
            """
            delete from public.project_rooms
            where room_id = %s and tenant_id = %s and application_id = %s
            """,
            (room_id, tenant_id, application_id),
        )

        conn.execute(
            """
            insert into public.tenants (
              tenant_id, slug, display_name, tenant_type, status
            ) values (
              %s, %s, 'War Room Local Preview', 'internal', 'active'
            )
            on conflict (tenant_id) do update
            set display_name = excluded.display_name,
                status = excluded.status
            """,
            (tenant_id, tenant_slug),
        )
        conn.execute(
            """
            insert into public.applications (
              application_id, tenant_id, slug, display_name,
              application_type, status
            ) values (
              %s, %s, %s, 'War Room Local Preview',
              'development_preview', 'active'
            )
            on conflict (application_id) do update
            set display_name = excluded.display_name,
                status = excluded.status
            """,
            (application_id, tenant_id, application_slug),
        )

        agent_rows: list[tuple[UUID, str, str, str]] = []
        for role, display_name, slug in AGENT_ROLES:
            agent_id = _stable_uuid("agent", role)
            agent_slug = f"preview-{slug}"
            conn.execute(
                """
                insert into public.agents (
                  agent_id, tenant_id, application_id,
                  slug, display_name, role, status
                ) values (%s, %s, %s, %s, %s, %s, 'active')
                on conflict (agent_id) do update
                set display_name = excluded.display_name,
                    role = excluded.role,
                    status = excluded.status
                """,
                (
                    agent_id,
                    tenant_id,
                    application_id,
                    agent_slug,
                    display_name,
                    role.lower(),
                ),
            )
            agent_rows.append((agent_id, role, display_name, slug))

        conn.execute(
            """
            insert into public.project_rooms (
              room_id, tenant_id, application_id, project_key, title,
              mode, state, created_by_principal_id,
              token_budget, cost_budget, cost_currency
            ) values (
              %s, %s, %s, 'local-preview', %s,
              'FORMAL_MEETING', 'DRAFT', %s,
              12000, 5.00, 'USD'
            )
            """,
            (room_id, tenant_id, application_id, room_title, principal_id),
        )
        conn.execute(
            """
            insert into public.project_room_participants (
              participant_id, tenant_id, application_id, room_id,
              principal_type, principal_id, agent_id,
              participant_type, role, display_name, active
            ) values (
              %s, %s, %s, %s,
              'HUMAN', %s, null,
              'HUMAN', 'OWNER', 'เจ้าของโปรเจกต์', true
            )
            """,
            (
                owner_participant_id,
                tenant_id,
                application_id,
                room_id,
                principal_id,
            ),
        )

        for agent_id, role, display_name, slug in agent_rows:
            participant_id = _stable_uuid("participant", f"{room_id}:{role}")
            conn.execute(
                """
                insert into public.project_room_participants (
                  participant_id, tenant_id, application_id, room_id,
                  principal_type, principal_id, agent_id,
                  participant_type, role, display_name,
                  model_policy_ref, active
                ) values (
                  %s, %s, %s, %s,
                  'AGENT', %s, %s,
                  'AGENT', %s, %s,
                  %s, true
                )
                """,
                (
                    participant_id,
                    tenant_id,
                    application_id,
                    room_id,
                    f"preview-{slug}",
                    agent_id,
                    role,
                    display_name,
                    f"preview/{slug}",
                ),
            )

        conn.execute(
            """
            insert into public.project_room_agenda_items (
              agenda_item_id, tenant_id, application_id, room_id,
              sequence, title, objective, status,
              round_limit, token_budget
            ) values (
              %s, %s, %s, %s,
              1, 'ประชุม #001 — Preview ภาษาไทย',
              'ทดสอบหน้า War Room, คำสั่งเจ้าของห้อง, การ replay และให้ผู้เข้าร่วม AI สนทนาเป็นภาษาไทยเป็นค่าเริ่มต้น',
              'OPEN', 2, 6000
            )
            """,
            (agenda_id, tenant_id, application_id, room_id),
        )
        conn.execute(
            """
            insert into public.project_room_findings (
              finding_id, tenant_id, application_id, room_id,
              agenda_item_id, raised_by_participant_id,
              severity, status, summary
            ) values (
              %s, %s, %s, %s, %s, %s,
              'NOTE', 'OPEN',
              'ห้อง Preview นี้ใช้ตรวจการทำงานและภาษาไทยเป็นค่าเริ่มต้นก่อนเปิดใช้งาน provider traffic จริง'
            )
            """,
            (
                _stable_uuid("finding", str(room_id)),
                tenant_id,
                application_id,
                room_id,
                agenda_id,
                owner_participant_id,
            ),
        )
        conn.execute(
            """
            insert into public.project_room_decisions (
              decision_id, tenant_id, application_id, room_id,
              agenda_item_id, decision_type,
              proposed_by_participant_id, decision, status
            ) values (
              %s, %s, %s, %s, %s,
              'PROPOSAL', %s,
              'ใช้ห้องนี้ยืนยันว่า controls ของ Track D และข้อความภาษาไทยทำงานถูกต้องก่อนเริ่มใช้งานจริง',
              'PROPOSED'
            )
            """,
            (
                _stable_uuid("decision", str(room_id)),
                tenant_id,
                application_id,
                room_id,
                agenda_id,
                owner_participant_id,
            ),
        )

    return tenant_id, application_id, room_id, principal_id


def main() -> int:
    # The preview title and failure details contain Thai text; keep stdout and
    # stderr UTF-8 so non-Windows-default consoles do not crash the report.
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Seed the War Room local preview (development only)."
    )
    parser.add_argument(
        "--room-id",
        type=uuid_module.UUID,
        default=None,
        help="Custom room UUID (defaults to the deterministic preview room id).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Custom room title (defaults to the standard preview title).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Allow resetting a custom --room-id other than the default "
            "preview room (deletes that room's rows)."
        ),
    )
    args = parser.parse_args()
    try:
        tenant_id, application_id, room_id, principal_id = seed(
            room_id=args.room_id, title=args.title, force=args.force
        )
    except Exception as exc:
        print(f"seed failed: {exc}", file=sys.stderr)
        return 1

    print("War Room local preview seeded.")
    print(f"NIPPAN_WAR_ROOM_PREVIEW_ENABLED=true")
    print(f"NIPPAN_WAR_ROOM_PREVIEW_TENANT_ID={tenant_id}")
    print(f"NIPPAN_WAR_ROOM_PREVIEW_APPLICATION_ID={application_id}")
    print(f"NIPPAN_WAR_ROOM_PREVIEW_PRINCIPAL_ID={principal_id}")
    print(f"ROOM_ID={room_id}")
    print(f"URL=http://127.0.0.1:8000/war-room/?room_id={room_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
