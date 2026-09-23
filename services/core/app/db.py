from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from .settings import Settings


@dataclass(slots=True)
class _TenantTransactionContext:
    database_identity: int
    connection: AsyncConnection
    tenant_id: UUID
    application_id: UUID | None
    request_id: UUID | None
    owner_task: asyncio.Task[object] | None
    active: bool = True


_current_tenant_transaction: ContextVar[_TenantTransactionContext | None] = ContextVar(
    "nippan_current_tenant_transaction",
    default=None,
)


class Database:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: AsyncConnectionPool | None = None

    @property
    def configured(self) -> bool:
        return bool(self._settings.database_url)

    async def open(self) -> None:
        if not self._settings.database_url:
            return
        self._pool = AsyncConnectionPool(
            conninfo=self._settings.database_url,
            min_size=self._settings.database_pool_min_size,
            max_size=self._settings.database_pool_max_size,
            open=False,
        )
        await self._pool.open()

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def ping(self) -> bool:
        if self._pool is None:
            return False
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select 1")
                row = await cur.fetchone()
                return row == (1,)

    @staticmethod
    def _assert_nested_scope(
        context: _TenantTransactionContext,
        *,
        tenant_id: UUID,
        application_id: UUID | None,
        request_id: UUID | None,
    ) -> None:
        if context.tenant_id != tenant_id:
            raise RuntimeError("nested tenant transaction cannot change tenant scope")
        if application_id is not None and context.application_id != application_id:
            raise RuntimeError(
                "nested tenant transaction cannot change application scope"
            )
        if request_id is not None and context.request_id != request_id:
            raise RuntimeError("nested tenant transaction cannot change request scope")

    @asynccontextmanager
    async def tenant_transaction(
        self,
        *,
        tenant_id: UUID,
        application_id: UUID | None = None,
        request_id: UUID | None = None,
    ) -> AsyncIterator[AsyncConnection]:
        current = _current_tenant_transaction.get()
        current_task = asyncio.current_task()
        if (
            current is not None
            and current.active
            and current.database_identity == id(self)
            and current.owner_task is current_task
        ):
            self._assert_nested_scope(
                current,
                tenant_id=tenant_id,
                application_id=application_id,
                request_id=request_id,
            )
            yield current.connection
            return

        if self._pool is None:
            raise RuntimeError("database pool is not configured")

        async with self._pool.connection() as conn:
            async with conn.transaction():
                await conn.execute(
                    "select set_config('app.tenant_id', %s, true)",
                    (str(tenant_id),),
                )

                if application_id is not None:
                    await conn.execute(
                        "select set_config('app.application_id', %s, true)",
                        (str(application_id),),
                    )

                if request_id is not None:
                    await conn.execute(
                        "select set_config('app.request_id', %s, true)",
                        (str(request_id),),
                    )

                context = _TenantTransactionContext(
                    database_identity=id(self),
                    connection=conn,
                    tenant_id=tenant_id,
                    application_id=application_id,
                    request_id=request_id,
                    owner_task=current_task,
                )
                token = _current_tenant_transaction.set(context)
                try:
                    yield conn
                finally:
                    context.active = False
                    _current_tenant_transaction.reset(token)
