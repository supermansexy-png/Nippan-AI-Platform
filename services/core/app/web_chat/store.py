"""Deduplication store interface and in-memory implementation.

Contract: ``docs/architecture/MESSAGE_FLOW_V1.md`` ND-1 — de-dup on the
platform's message id so a repeated delivery is dropped, never answered
twice. Physical persistence (``lite_processed_events``, card T-077) is not
required for this adapter's local proof; the store is injectable so a
Postgres-backed implementation can replace the in-memory one without
touching the adapter.
"""

from __future__ import annotations

import time
from typing import Protocol


class DedupeStore(Protocol):
    """Returns True exactly once per (tenant, channel, message_id)."""

    def seen_before(
        self,
        *,
        tenant_id: str,
        channel_id: str,
        message_id: str,
    ) -> bool: ...


class InMemoryDedupeStore:
    """Sliding-window in-process dedupe store (single-instance preview)."""

    def __init__(self, *, ttl_seconds: float = 300.0) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = ttl_seconds
        self._seen: dict[tuple[str, str, str], float] = {}

    def seen_before(
        self,
        *,
        tenant_id: str,
        channel_id: str,
        message_id: str,
    ) -> bool:
        key = (tenant_id, channel_id, message_id)
        now = time.monotonic()
        for stale_key, ts in list(self._seen.items()):
            if now - ts >= self._ttl:
                del self._seen[stale_key]
        if key in self._seen:
            return True
        self._seen[key] = now
        return False
