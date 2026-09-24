from __future__ import annotations

from uuid import UUID

from app.db import Database

from .interfaces import OrderedRoomEvent
from .read_model import PostgresRoomSnapshotSource


class PostgresRoomEventReader:
    """Reads committed ordered War Room events after a durable sequence cursor."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def load_after(
        self,
        *,
        tenant_id: UUID,
        application_id: UUID,
        room_id: UUID,
        after_sequence: int,
        limit: int = 100,
    ) -> tuple[OrderedRoomEvent, ...]:
        if after_sequence < 0:
            raise ValueError("after_sequence must not be negative")
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")

        async with self._database.tenant_transaction(
            tenant_id=tenant_id,
            application_id=application_id,
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select
                      message_id,
                      agenda_item_id,
                      participant_id,
                      request_id,
                      message_type,
                      sequence,
                      content_text,
                      created_at
                    from public.project_room_messages
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                      and sequence > %s
                    order by sequence asc
                    limit %s
                    """,
                    (
                        tenant_id,
                        application_id,
                        room_id,
                        after_sequence,
                        limit,
                    ),
                )
                rows = await cur.fetchall()

        return tuple(
            PostgresRoomSnapshotSource._event_from_row(
                row,
                tenant_id=tenant_id,
                application_id=application_id,
                room_id=room_id,
            )
            for row in rows
        )
