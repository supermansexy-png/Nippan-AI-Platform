"""Tests for services/dev/tools/data_access.py (T-003).

No real database: a fake ``connect`` records whether it was ever called and
captures the exact sql + params handed to the DB-API cursor.
"""

import pytest

from data_access import DataAccess, MissingScopeError, UnsafeQueryError, UnknownQueryError

SCOPED_SQL = "SELECT id FROM conversations WHERE tenant_id = %s AND bot_id = %s"
PARAMS = ("t-1", "b-1")

# Transaction-local scope GUC setters execute() runs on the same cursor
# BEFORE the caller's query (exact SQL, parameterised).
SET_TENANT_SQL = "SELECT set_config('app.tenant_id', %s, true)"
SET_BOT_SQL = "SELECT set_config('app.bot_id', %s, true)"


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows
        self.executed = []  # list[(sql, params)] in call order
        self.closed = False

    def execute(self, sql, params):
        self.executed.append((sql, params))

    def fetchall(self):
        return list(self._rows)

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, rows):
        self.fake_cursor = FakeCursor(rows)
        self.closed = False

    def cursor(self):
        return self.fake_cursor

    def close(self):
        self.closed = True


class FakeConnect:
    """Zero-arg callable standing in for the real DB connect."""

    def __init__(self, rows=(("r1", "r2"), ("r3", "r4"))):
        self.rows = rows
        self.calls = 0
        self.connections = []

    def __call__(self):
        self.calls += 1
        conn = FakeConnection(self.rows)
        self.connections.append(conn)
        return conn


# --- Scope checks (MissingScopeError) ---

# a) missing tenant_id -> error AND no database contact
def test_missing_tenant_id_raises_before_connect():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    with pytest.raises(MissingScopeError):
        da.execute("test", PARAMS, tenant_id=None, bot_id="b-1")
    assert connect.calls == 0
    assert connect.connections == []


# b) missing bot_id -> error AND no database contact
def test_missing_bot_id_raises_before_connect():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    with pytest.raises(MissingScopeError):
        da.execute("test", PARAMS, tenant_id="t-1", bot_id=None)
    assert connect.calls == 0
    assert connect.connections == []


# c) blank / empty-string / whitespace scope -> error, still no DB contact
@pytest.mark.parametrize(
    "tenant_id, bot_id",
    [
        ("", "b-1"),
        ("   ", "b-1"),
        ("t-1", ""),
        ("t-1", "   "),
        ("", ""),
    ],
)
def test_blank_scope_raises_before_connect(tenant_id, bot_id):
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    with pytest.raises(MissingScopeError):
        da.execute("test", PARAMS, tenant_id=tenant_id, bot_id=bot_id)
    assert connect.calls == 0


# c2) fail-closed on bot_id alone: None or blank -> MissingScopeError and
# NO connection is ever opened / nothing ever executed
def test_blank_or_none_bot_id_fails_closed_before_connect():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    for bad_bot_id in (None, "", "   "):
        with pytest.raises(MissingScopeError):
            da.execute("test", PARAMS, tenant_id="t-1", bot_id=bad_bot_id)
    assert connect.calls == 0
    assert connect.connections == []


# missing/blank scope is a ValueError subclass
def test_missing_scope_error_is_value_error():
    assert issubclass(MissingScopeError, ValueError)


# d) both scopes present -> connects, executes, closes, returns rows
def test_full_scope_executes_and_returns_rows():
    rows = [("alice", "2026-01-01"), ("bob", "2026-01-02")]
    connect = FakeConnect(rows=rows)
    da = DataAccess(connect, {"test": SCOPED_SQL})
    got = da.execute("test", PARAMS, tenant_id="t-1", bot_id="b-1")

    assert connect.calls == 1
    assert got == rows
    assert all(isinstance(row, tuple) for row in got)

    conn = connect.connections[0]
    assert conn.fake_cursor.executed == [
        (SET_TENANT_SQL, ("t-1",)),
        (SET_BOT_SQL, ("b-1",)),
        (SCOPED_SQL, PARAMS),
    ]
    assert conn.fake_cursor.closed is True  # cursor closed
    assert conn.closed is True  # connection closed


# d2) both GUC setters run, in order, on the SAME cursor, with the PASSED
# values (distinct from the usual t-1/b-1 to catch swaps/defaults), and the
# caller's query runs last on that same cursor/transaction
def test_execute_sets_tenant_and_bot_gucs_in_order_on_same_cursor():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    da.execute("test", PARAMS, tenant_id="t-9", bot_id="b-7")

    cursor = connect.connections[0].fake_cursor
    assert len(cursor.executed) == 3
    assert cursor.executed[0] == (SET_TENANT_SQL, ("t-9",))
    assert cursor.executed[1] == (SET_BOT_SQL, ("b-7",))
    assert cursor.executed[2] == (SCOPED_SQL, PARAMS)
    # one connection, one cursor: all three calls shared it (one transaction)
    assert len(connect.connections) == 1
    assert connect.connections[0].fake_cursor is cursor


# e) sql + params pass through unchanged (parameterized, not interpolated)
def test_sql_and_params_pass_through_unchanged():
    sql = "SELECT name FROM bots WHERE tenant_id = %s AND bot_id = %s AND name = %s"
    params = ("t-1", "b-1", "Robert'); DROP TABLE bots;--")
    connect = FakeConnect(rows=())
    da = DataAccess(connect, {"test": sql})

    da.execute("test", params, tenant_id="t-1", bot_id="b-1")

    executed = connect.connections[0].fake_cursor.executed
    assert len(executed) == 3  # 2 GUC setters + the caller's query
    recorded_sql, recorded_params = executed[2]
    assert recorded_sql == sql  # byte-for-byte, no interpolation of values
    assert recorded_params is params or recorded_params == params


# default params=() also reaches the driver untouched
def test_default_params_passthrough():
    sql = "SELECT count(*) FROM conversations WHERE tenant_id = %s AND bot_id = %s"
    connect = FakeConnect(rows=((0,),))
    da = DataAccess(connect, {"test": sql})
    da.execute("test", tenant_id="t-1", bot_id="b-1")
    assert connect.connections[0].fake_cursor.executed == [
        (SET_TENANT_SQL, ("t-1",)),
        (SET_BOT_SQL, ("b-1",)),
        (sql, ()),
    ]


# connection is closed even when execution fails
def test_connection_closed_on_execution_error():
    class ExplodingCursor(FakeCursor):
        def execute(self, sql, params):
            raise RuntimeError("boom")

    class ExplodingConnection(FakeConnection):
        def cursor(self):
            self.fake_cursor = ExplodingCursor(())
            return self.fake_cursor

    connect = FakeConnect()

    def exploding_connect():
        connect.calls += 1
        conn = ExplodingConnection(())
        connect.connections.append(conn)
        return conn

    da = DataAccess(exploding_connect, {"test": SCOPED_SQL})
    with pytest.raises(RuntimeError):
        da.execute("test", PARAMS, tenant_id="t-1", bot_id="b-1")
    assert connect.connections[0].closed is True


# --- UnsafeQueryError: sql itself must be scoped ---

# a) unscoped sql -> UnsafeQueryError AND no database contact
def test_unscoped_sql_raises_before_connect():
    connect = FakeConnect()
    with pytest.raises(UnsafeQueryError):
        DataAccess(connect, {"bad": "SELECT * FROM lite_conversations"})
    assert connect.calls == 0
    assert connect.connections == []


# b) sql filtering only on tenant_id -> UnsafeQueryError, no DB contact
def test_tenant_only_sql_raises_before_connect():
    connect = FakeConnect()
    with pytest.raises(UnsafeQueryError):
        DataAccess(connect, {"bad": "SELECT * FROM lite_conversations WHERE tenant_id = %s"})
    assert connect.calls == 0


# c) sql filtering only on bot_id -> UnsafeQueryError, no DB contact
def test_bot_only_sql_raises_before_connect():
    connect = FakeConnect()
    with pytest.raises(UnsafeQueryError):
        DataAccess(connect, {"bad": "SELECT * FROM lite_conversations WHERE bot_id = %s"})
    assert connect.calls == 0


# d) sql filtering on both columns -> executes and returns rows
def test_scoped_sql_executes_and_returns_rows():
    rows = [("alice", "2026-01-01")]
    sql = "SELECT * FROM lite_conversations WHERE tenant_id = %s AND bot_id = %s"
    connect = FakeConnect(rows=rows)
    da = DataAccess(connect, {"test": sql})
    got = da.execute("test", PARAMS, tenant_id="t-1", bot_id="b-1")

    assert connect.calls == 1
    assert got == rows
    assert connect.connections[0].fake_cursor.executed == [
        (SET_TENANT_SQL, ("t-1",)),
        (SET_BOT_SQL, ("b-1",)),
        (sql, PARAMS),
    ]


# e) tenant_id_extra is a different identifier: does NOT satisfy the guard
def test_tenant_id_extra_does_not_satisfy_guard():
    connect = FakeConnect()
    with pytest.raises(UnsafeQueryError):
        DataAccess(connect, {"bad": "SELECT * FROM lite_conversations WHERE tenant_id_extra = %s"})
    # even with a genuine bot_id column, the fake tenant_id_extra prefix is not enough
    with pytest.raises(UnsafeQueryError):
        DataAccess(connect, {"bad": "SELECT * FROM lite_conversations WHERE tenant_id_extra = %s AND bot_id = %s"})
    assert connect.calls == 0


# UnsafeQueryError is a ValueError subclass (consistent with MissingScopeError)
def test_unsafe_query_error_is_value_error():
    assert issubclass(UnsafeQueryError, ValueError)


# --- NEW: UnknownQueryError ---

# a) passing a raw SQL string (not a registered name) as the first arg -> UnknownQueryError AND the fake connect was NOT called
def test_raw_sql_string_raises_unknown_query_error():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    with pytest.raises(UnknownQueryError):
        da.execute("SELECT * FROM lite_conversations WHERE tenant_id = %s AND bot_id = %s", PARAMS, tenant_id="t-1", bot_id="b-1")
    assert connect.calls == 0
    assert connect.connections == []


# b) register("x", sql_without_scope) -> UnsafeQueryError
def test_register_unscoped_sql_raises_unsafe_query_error():
    connect = FakeConnect()
    da = DataAccess(connect, {"good": SCOPED_SQL})
    with pytest.raises(UnsafeQueryError):
        da.register("bad", "SELECT * FROM lite_conversations")
    # ensure the bad query was not registered
    with pytest.raises(UnknownQueryError):
        da.execute("bad", PARAMS, tenant_id="t-1", bot_id="b-1")


# c) constructing DataAccess(queries={...unscoped...}) -> UnsafeQueryError
def test_constructor_with_unscoped_queries_raises():
    connect = FakeConnect()
    with pytest.raises(UnsafeQueryError):
        DataAccess(connect, {"bad": "SELECT * FROM lite_conversations"})


# d) missing/blank tenant_id or bot_id -> MissingScopeError and connect NOT called (before the registry lookup)
def test_missing_scope_before_registry_lookup():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    with pytest.raises(MissingScopeError):
        da.execute("test", PARAMS, tenant_id=None, bot_id="b-1")
    assert connect.calls == 0


def test_blank_scope_before_registry_lookup():
    connect = FakeConnect()
    da = DataAccess(connect, {"test": SCOPED_SQL})
    with pytest.raises(MissingScopeError):
        da.execute("test", PARAMS, tenant_id="", bot_id="b-1")
    assert connect.calls == 0


# e) a registered name with both predicates -> executes and returns rows
def test_registered_scoped_query_executes_and_returns():
    rows = [("result1",), ("result2",)]
    sql = "SELECT col FROM my_table WHERE tenant_id = %s AND bot_id = %s"
    connect = FakeConnect(rows=rows)
    da = DataAccess(connect)
    da.register("my_query", sql)
    got = da.execute("my_query", ("t-1", "b-1"), tenant_id="t-1", bot_id="b-1")

    assert connect.calls == 1
    assert got == rows
    assert connect.connections[0].fake_cursor.executed == [
        (SET_TENANT_SQL, ("t-1",)),
        (SET_BOT_SQL, ("b-1",)),
        (sql, ("t-1", "b-1")),
    ]


# UnknownQueryError is a ValueError subclass
def test_unknown_query_error_is_value_error():
    assert issubclass(UnknownQueryError, ValueError)


# --- Transaction handling: transaction-local GUCs must survive to the query ---
# Regression for the 2026-09-25 bug where an autocommit connection reset
# `set_config(..., true)` before the caller query ran (RLS then saw no scope).

class TxConnection(FakeConnection):
    def __init__(self, rows, autocommit=True, explode_execute=False):
        super().__init__(rows)
        self.autocommit = autocommit
        self.explode_execute = explode_execute
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        if self.explode_execute:
            class ExplodingCursor(FakeCursor):
                def execute(self, sql, params):
                    raise RuntimeError("boom")
            self.fake_cursor = ExplodingCursor(())
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_execute_forces_single_transaction_and_commits():
    conn = TxConnection([("x",)], autocommit=True)
    da = DataAccess(lambda: conn, {"q": SCOPED_SQL})
    rows = da.execute("q", PARAMS, tenant_id="t-1", bot_id="b-1")

    assert rows == [("x",)]
    assert conn.autocommit is False  # forced off so the GUCs survive to the query
    assert conn.commits == 1
    assert conn.rollbacks == 0
    assert conn.closed is True


def test_execute_rolls_back_and_reraises_on_query_error():
    conn = TxConnection([], autocommit=False, explode_execute=True)
    da = DataAccess(lambda: conn, {"q": SCOPED_SQL})
    with pytest.raises(RuntimeError):
        da.execute("q", PARAMS, tenant_id="t-1", bot_id="b-1")

    assert conn.rollbacks == 1
    assert conn.commits == 0
    assert conn.closed is True

