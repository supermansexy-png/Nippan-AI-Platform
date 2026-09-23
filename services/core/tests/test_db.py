from contextlib import asynccontextmanager
from uuid import UUID

import pytest

from app.db import Database
from app.settings import Settings


class FakeTransaction:
    def __init__(self, connection) -> None:
        self.connection = connection

    async def __aenter__(self):
        self.connection.transaction_entries += 1
        return self.connection

    async def __aexit__(self, exc_type, exc, tb):
        self.connection.transaction_exits += 1
        return False


class FakeConnection:
    def __init__(self) -> None:
        self.executed = []
        self.transaction_entries = 0
        self.transaction_exits = 0

    def transaction(self):
        return FakeTransaction(self)

    async def execute(self, query, params=None):
        self.executed.append((query, params))


class FakePool:
    def __init__(self) -> None:
        self.connection_obj = FakeConnection()
        self.connection_entries = 0
        self.connection_exits = 0

    @asynccontextmanager
    async def connection(self):
        self.connection_entries += 1
        try:
            yield self.connection_obj
        finally:
            self.connection_exits += 1


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_nested_same_scope_reuses_one_pool_connection_and_transaction() -> None:
    database = Database(Settings(database_url="postgresql://example"))
    pool = FakePool()
    database._pool = pool  # type: ignore[assignment]

    scope = {
        "tenant_id": UUID(int=1),
        "application_id": UUID(int=2),
        "request_id": UUID(int=3),
    }

    async with database.tenant_transaction(**scope) as outer:
        async with database.tenant_transaction(**scope) as inner:
            assert inner is outer

    assert pool.connection_entries == 1
    assert pool.connection_exits == 1
    assert pool.connection_obj.transaction_entries == 1
    assert pool.connection_obj.transaction_exits == 1
    assert len(pool.connection_obj.executed) == 3


@pytest.mark.anyio
async def test_nested_transaction_fails_closed_on_scope_change() -> None:
    database = Database(Settings(database_url="postgresql://example"))
    pool = FakePool()
    database._pool = pool  # type: ignore[assignment]

    async with database.tenant_transaction(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        request_id=UUID(int=3),
    ):
        with pytest.raises(RuntimeError, match="application scope"):
            async with database.tenant_transaction(
                tenant_id=UUID(int=1),
                application_id=UUID(int=9),
                request_id=UUID(int=3),
            ):
                raise AssertionError("mismatched nested scope must not enter")

    assert pool.connection_entries == 1
    assert pool.connection_obj.transaction_entries == 1
