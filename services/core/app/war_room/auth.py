from __future__ import annotations

from app.db import Database

from .interfaces import (
    RoomCommand,
    RoomReadRequest,
    TrustedActorContext,
)


class DatabaseRoomCommandAuthorizer:
    """Fail-closed owner authorization backed by the existing participant table."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def authorize(
        self,
        *,
        command: RoomCommand,
        actor: TrustedActorContext,
    ) -> bool:
        correlation = command.correlation

        if actor.principal_type.value != "HUMAN":
            return False
        if actor.tenant_id != correlation.tenant_id:
            return False
        if actor.application_id != correlation.application_id:
            return False

        async with self._database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select exists (
                        select 1
                        from public.project_room_participants
                        where tenant_id = %s
                          and application_id = %s
                          and room_id = %s
                          and principal_type = %s
                          and principal_id = %s
                          and role = 'OWNER'
                          and active
                    )
                    """,
                    (
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.room_id,
                        actor.principal_type.value,
                        actor.principal_id,
                    ),
                )
                row = await cur.fetchone()

        return bool(row and row[0])



class DatabaseRoomReadAuthorizer:
    """Fail-closed active-participant authorization for snapshot/SSE reads."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def authorize_read(
        self,
        *,
        request: RoomReadRequest,
        actor: TrustedActorContext,
    ) -> bool:
        if actor.tenant_id != request.tenant_id:
            return False
        if actor.application_id != request.application_id:
            return False

        try:
            async with self._database.tenant_transaction(
                tenant_id=request.tenant_id,
                application_id=request.application_id,
            ) as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        select exists (
                            select 1
                            from public.project_room_participants
                            where tenant_id = %s
                              and application_id = %s
                              and room_id = %s
                              and principal_type = %s
                              and principal_id = %s
                              and active
                        )
                        """,
                        (
                            request.tenant_id,
                            request.application_id,
                            request.room_id,
                            actor.principal_type.value,
                            actor.principal_id,
                        ),
                    )
                    row = await cur.fetchone()
        except Exception:
            return False

        return bool(row and row[0])


class DenyAllRoomReadAuthorizer:
    """Fail-closed default for snapshot/SSE reads until a reviewed policy is injected."""

    async def authorize_read(
        self,
        *,
        request: RoomReadRequest,
        actor: TrustedActorContext,
    ) -> bool:
        return False
