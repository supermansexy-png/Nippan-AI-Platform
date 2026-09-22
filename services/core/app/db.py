from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from .settings import Settings


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

    @asynccontextmanager
    async def tenant_transaction(
        self,
        *,
        tenant_id: UUID,
        application_id: UUID | None = None,
        request_id: UUID | None = None,
    ) -> AsyncIterator[AsyncConnection]:
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

                yield conn
