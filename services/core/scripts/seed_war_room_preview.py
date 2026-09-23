from __future__ import annotations

import os
import sys
from uuid import UUID, NAMESPACE_URL, uuid5

import psycopg

from app.settings import Settings


DEFAULT_TENANT_ID = UUID("c1111111-1111-4111-8111-111111111111")
DEFAULT_APPLICATION_ID = UUID("c2222222-2222-4222-8222-222222222222")
DEFAULT_ROOM_ID = UUID("c3333333-3333-4333-8333-333333333333")
DEFAULT_AGENDA_ID = UUID("c4444444-4444-4444-8444-444444444444")
DEFAULT_OWNER_PARTICIPANT_ID = UUID("c5555555-5555-4555-8555-555555555555")
DEFAULT_OWNER_PRINCIPAL_ID = "preview-owner"

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
    room_id = DEFAULT_ROOM_ID
    agenda_id = DEFAULT_AGENDA_ID
    owner_participant_id = DEFAULT_OWNER_PARTICIPANT_ID

    tenant_slug = f"war-room-preview-{tenant_id.hex[:8]}"
    application_slug = f"war-room-preview-{application_id.hex[:8]}"

    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        # Reset only the deterministic local preview room.
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
              %s, %s, %s, 'local-preview', 'Nippan AI War Room — Preview ภาษาไทย',
              'FORMAL_MEETING', 'DRAFT', %s,
              12000, 5.00, 'USD'
            )
            """,
            (room_id, tenant_id, application_id, principal_id),
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
            participant_id = _stable_uuid("participant", role)
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
                _stable_uuid("finding", "local-preview"),
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
                _stable_uuid("decision", "local-preview"),
                tenant_id,
                application_id,
                room_id,
                agenda_id,
                owner_participant_id,
            ),
        )

    return tenant_id, application_id, room_id, principal_id


def main() -> int:
    try:
        tenant_id, application_id, room_id, principal_id = seed()
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
