"""T-003 — Phase A tenant/bot isolation boundary.

``data-access`` is the only path to the database
(``docs/product/MCP_TOOLS_V1.md``). Phase A has **no** database-enforced
row-level security, so isolation depends entirely on every query carrying
both ``tenant_id`` and ``bot_id`` (``docs/data/LITE_SCHEMA_V1.md``).

Therefore a call that is missing full scope must fail *before* any database
contact: :class:`MissingScopeError` is raised before ``self._connect()`` is
invoked, so a scopeless call can never reach the database.

Even with scope values supplied, the SQL itself must carry both columns:
:func:`_sql_is_scoped` rejects any query that does not reference both
``tenant_id`` and ``bot_id``, raising :class:`UnsafeQueryError` before
``self._connect()`` as well.

Queries are always executed parameterized (``cursor.execute(sql, params)``);
never by string interpolation.

Stdlib only.
"""

from __future__ import annotations

import re

__all__ = ["MissingScopeError", "UnsafeQueryError", "UnknownQueryError", "DataAccess"]


class MissingScopeError(ValueError):
    """Raised when ``tenant_id`` or ``bot_id`` is missing or blank.

    Raised BEFORE any database connection is opened.
    """


class UnsafeQueryError(ValueError):
    """Raised when ``sql`` does not reference both scope columns.

    Phase A has no database-level RLS, so a scope-aware call paired with an
    unscoped query would still read across tenants. Raised BEFORE any
    database connection is opened.
    """


class UnknownQueryError(ValueError):
    """Raised when a query name is not found in the registry.

    Raised BEFORE any database connection is opened.
    """


def _require_scope(name, value):
    """Fail closed: only an explicit, non-blank value passes."""
    if value is None:
        raise MissingScopeError("%s is required" % name)
    if isinstance(value, str):
        if not value.strip():
            raise MissingScopeError("%s must not be blank" % name)
    elif not value:
        raise MissingScopeError("%s is required" % name)


def _sql_is_scoped(sql: str) -> bool:
    """True ONLY if ``sql`` references BOTH scope columns as identifiers.

    Case-insensitive, whole-word matches only: ``tenant_id_extra`` is a
    different identifier and does **not** count as ``tenant_id``.
    """
    return bool(
        re.search(r"\btenant_id\b", sql, re.IGNORECASE)
        and re.search(r"\bbot_id\b", sql, re.IGNORECASE)
    )


class DataAccess:
    """Single choke point for all Phase A database access.

    Parameters
    ----------
    connect:
        A zero-argument callable returning a DB-API connection.
    queries:
        Optional mapping name -> sql. Default: empty dict.
        At construction, validate EVERY provided query with _sql_is_scoped;
        raise UnsafeQueryError if any fails.
    """

    def __init__(self, connect, queries=None):
        if not callable(connect):
            raise TypeError("connect must be a zero-argument callable")
        self._connect = connect
        self._queries = {}
        if queries:
            for name, sql in queries.items():
                self.register(name, sql)

    def register(self, name: str, sql: str) -> None:
        """Register a named query.

        Validate _sql_is_scoped(sql) else UnsafeQueryError; then store it.
        """
        if not _sql_is_scoped(sql):
            raise UnsafeQueryError("sql must filter on tenant_id and bot_id")
        self._queries[name] = sql

    def execute(self, query_name, params=(), *, tenant_id, bot_id) -> list[tuple]:
        """Run a registered named query under full tenant + bot scope.

        1. Missing/blank ``tenant_id`` or ``bot_id`` -> :class:`MissingScopeError`
           raised before any database contact.
        2. ``query_name`` not in registry -> :class:`UnknownQueryError` raised
           before any database contact.
        3. Otherwise open a connection, force a single transaction, run the
           transaction-local scope GUC setters
           (``SELECT set_config('app.tenant_id', %s, true)`` and
           ``SELECT set_config('app.bot_id', %s, true)`` — parameterised, since
           ``SET LOCAL ... = %s`` cannot take parameters) on the same cursor,
           then execute the registered sql with ``params`` inside the same
           transaction, commit, fetch all rows, close the connection, return
           the rows.
        """
        _require_scope("tenant_id", tenant_id)
        _require_scope("bot_id", bot_id)

        if query_name not in self._queries:
            raise UnknownQueryError("unknown query: %s" % query_name)

        sql = self._queries[query_name]

        conn = self._connect()
        try:
            # Force one transaction so the transaction-local GUCs below apply to
            # the caller's query. On an autocommit connection each statement is
            # its own transaction and "set_config(..., true)" would be reset
            # before the query ran (proved: RLS then sees no scope and returns
            # zero rows). With autocommit off, the same transaction also lets
            # writes persist via the commit below.
            if hasattr(conn, "autocommit"):
                try:
                    conn.autocommit = False
                except Exception:
                    pass  # connection does not allow toggling; proceed as-is
            try:
                cursor = conn.cursor()
                try:
                    # Transaction-local scope GUCs on the same cursor/connection
                    # as the caller's query (one transaction), parameterised.
                    cursor.execute(
                        "SELECT set_config('app.tenant_id', %s, true)",
                        (str(tenant_id),),
                    )
                    cursor.execute(
                        "SELECT set_config('app.bot_id', %s, true)",
                        (str(bot_id),),
                    )
                    cursor.execute(sql, params)
                    rows = list(cursor.fetchall())
                finally:
                    close_cursor = getattr(cursor, "close", None)
                    if callable(close_cursor):
                        close_cursor()
                commit = getattr(conn, "commit", None)
                if callable(commit):
                    commit()
            except Exception:
                rollback = getattr(conn, "rollback", None)
                if callable(rollback):
                    try:
                        rollback()
                    except Exception:
                        pass
                raise
        finally:
            conn.close()
        return rows