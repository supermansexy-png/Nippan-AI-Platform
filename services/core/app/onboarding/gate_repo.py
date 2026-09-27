"""Repository seam for the go-live gate (T-079d part 1).

A small interface over the ``bots`` table, matching
``docs/data/LITE_SCHEMA_V1.md`` column names and status values EXACTLY:
``bots.status`` is ``active | paused`` only. No live database, no
credentials, no migration — an in-memory implementation backs the tests
and the proof script. A real Supabase implementation is out of scope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

__all__ = [
    "BOT_STATUS_VALUES",
    "BotRecord",
    "BotRepository",
    "InMemoryBotRepository",
]

# LITE_SCHEMA_V1.md §bots.status: "active / paused" — these two, never invented.
BOT_STATUS_VALUES: tuple[str, ...] = ("active", "paused")


@dataclass
class BotRecord:
    """One ``bots`` row — LITE_SCHEMA_V1.md column names, no extras."""

    bot_id: str
    tenant_id: str
    bot_type: str = "chat"
    tone: str | None = None  # fixed-menu Tone value (§bots.tone)
    business_info: dict[str, Any] = field(default_factory=dict)  # structured fields, never prompt text
    enabled_tools: tuple[str, ...] = ()  # fixed-menu tool keys
    monthly_message_quota: int = 300
    monthly_push_quota: int = 200
    status: str = "paused"  # active / paused — fail-closed default

    def validate(self) -> None:
        """Fail-closed shape check: no unknown status, no empty scope keys."""
        if self.status not in BOT_STATUS_VALUES:
            raise ValueError(f"invalid bot status {self.status!r}; allowed: {BOT_STATUS_VALUES}")
        if not self.bot_id or not self.tenant_id:
            raise ValueError("bot_id and tenant_id are required")
        if self.monthly_message_quota < 0 or self.monthly_push_quota < 0:
            raise ValueError("quotas must be non-negative")


class BotRepository(Protocol):
    """Read/write seam the gate uses to persist the bot row."""

    def get(self, *, bot_id: str, tenant_id: str) -> BotRecord | None: ...

    def save(self, record: BotRecord) -> BotRecord: ...


class InMemoryBotRepository:
    """Thread-free in-memory ``BotRepository`` — keyed by (tenant_id, bot_id);
    every access is tenant-scoped, so cross-tenant writes cannot collide."""

    def __init__(self) -> None:
        self._rows: dict[tuple[str, str], BotRecord] = {}

    def get(self, *, bot_id: str, tenant_id: str) -> BotRecord | None:
        return self._rows.get((tenant_id, bot_id))

    def save(self, record: BotRecord) -> BotRecord:
        record.validate()
        key = (record.tenant_id, record.bot_id)
        # Store a copy so callers cannot mutate persisted state by reference.
        row = _copy(record)
        self._rows[key] = row
        return _copy(row)

    def all(self) -> tuple[BotRecord, ...]:
        return tuple(_copy(r) for r in self._rows.values())


def _copy(record: BotRecord) -> BotRecord:
    import copy

    return copy.deepcopy(record)
