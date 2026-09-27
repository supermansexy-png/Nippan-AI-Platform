"""Per-session state for the customer setup page.

Tenant isolation is explicit: every entry is keyed by
``(tenant_scope_id, session_id)``. A session created under scope A is
INVISIBLE to scope B â not error-hidden, structurally unreadable, because
every lookup goes through ``_scope_key`` and cross-scope access raises
``SessionScopeError`` (fail-closed). This is proven by a test.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

from ..assistant import OnboardingSession

__all__ = [
    "SessionScopeError",
    "SessionLimitError",
    "MAX_SESSIONS",
    "SESSION_TTL_SECONDS",
    "OnboardingPageStore",
    "PageSession",
]

# A4 hardening: the in-memory store is BOUNDED — a fixed session cap plus a
# TTL. Beyond these, behaviour is explicit and fail-closed: TTL-expired
# sessions are evicted (and read as not found), and a new session beyond
# the cap evicts the OLDEST session first; when nothing can be freed a
# new creation is REFUSED with ``SessionLimitError``. No database, no
# unbounded memory, nothing silently unlimited.
MAX_SESSIONS = 200
SESSION_TTL_SECONDS = 3600  # one hour of draft life


class SessionScopeError(KeyError):
    """The session does not exist in THIS scope — another scope/tenant's
    draft must never be readable (tenant isolation, fail-closed)."""


class SessionLimitError(RuntimeError):
    """The bounded store cannot accept another session — memory-exhaustion
    is refused, never absorbed silently."""


@dataclass
class PageSession:
    """One prospect's setup conversation: the existing driver + bounded
    ingestion, plus the transcript of what the page showed."""

    tenant_scope_id: str
    session_id: str
    session: OnboardingSession
    transcript: list[dict[str, str]] = field(default_factory=list)
    used_url: bool = False
    used_file: bool = False
    done: bool = False
    # G: the site the session ALREADY knows (tenant/session config) —
    # the own-site anchor for SSRF validation. None ⇒ URL ingestion is
    # refused (fail-closed); it never comes from a submitted URL.
    site_origin: str | None = None
    created_at: float = 0.0

    def is_expired(self, now: float | None = None) -> bool:
        at = time.monotonic() if now is None else now
        return bool(self.created_at) and (at - self.created_at) > SESSION_TTL_SECONDS


class OnboardingPageStore:
    """In-memory sessions, scoped strictly by ``tenant_scope_id``.

    Bounded (A4): every read purges expired rows; every create evicts
    expired rows first, then the oldest rows over ``MAX_SESSIONS``, and
    raises ``SessionLimitError`` only if the store truly cannot fit one
    more (never more than one active session is dropped to make room).
    """

    def __init__(self, *, max_sessions: int = MAX_SESSIONS,
                 ttl_seconds: int = SESSION_TTL_SECONDS) -> None:
        self._rows: dict[tuple[str, str], PageSession] = {}
        self._max = max_sessions
        self._ttl = ttl_seconds

    def create(self, *, tenant_scope_id: str,
               site_origin: str | None = None) -> PageSession:
        self._purge_expired()
        if len(self._rows) >= self._max:
            self._evict_oldest()
        if len(self._rows) >= self._max:
            raise SessionLimitError(
                f"session store full ({self._max} active sessions) — new session refused"
            )
        session_id = f"s-{len(self._rows) + 1:04d}-{_nonce()}"
        row = PageSession(
            tenant_scope_id=tenant_scope_id,
            session_id=session_id,
            session=OnboardingSession(),
            site_origin=site_origin,
            created_at=time.monotonic(),
        )
        self._rows[(tenant_scope_id, session_id)] = row
        return row

    def get(self, *, tenant_scope_id: str, session_id: str) -> PageSession:
        """Fail-closed read: only a same-scope session is returned.

        A session_id from ANOTHER scope raises ``SessionScopeError`` â the
        caller never sees another tenant's draft config. An EXPIRED
        session is indistinguishable from a missing one: it is evicted
        and read as not found (fail-closed, no stale draft served).
        """
        self._purge_expired()
        row = self._rows.get((tenant_scope_id, session_id))
        if row is None:
            raise SessionScopeError(
                f"session {session_id!r} not found in scope {tenant_scope_id!r}"
            )
        return row

    def _purge_expired(self) -> None:
        now = time.monotonic()
        for key, row in list(self._rows.items()):
            if row.created_at and (now - row.created_at) > self._ttl:
                del self._rows[key]

    def active_count(self) -> int:
        self._purge_expired()
        return len(self._rows)

    def _evict_oldest(self) -> None:
        if not self._rows:
            return
        oldest_key = min(self._rows, key=lambda k: self._rows[k].created_at or 0.0)
        del self._rows[oldest_key]


def _nonce() -> str:
    # T-079c D2: the session id is the ONLY thing protecting a draft, so
    # its entropy IS the security margin. token_hex(4) (~4.3e9, enumerable)
    # is replaced by token_urlsafe(24): 192 bits from a CSPRNG, URL-safe,
    # 32 chars. URL/path shape unchanged — the value is still a plain
    # URL-safe string inside the same path segment.
    return secrets.token_urlsafe(24)
