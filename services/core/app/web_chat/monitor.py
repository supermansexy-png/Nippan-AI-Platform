"""Observability sinks for the web-chat adapter.

Contract: ``docs/product/INTEGRATIONS.md`` duty 6 — report usage to
``usage-tracker`` and errors to ``monitor-log``. Both are injectable callables
so the adapter stays independent of any specific sink implementation.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable, Protocol


class UsageEventSink(Protocol):
    def record(
        self,
        *,
        tenant_id: str,
        bot_id: str,
        channel_id: str,
        message_id: str,
        kind: str,
    ) -> None: ...


class MonitorSink:
    """Writes adapter events, one JSON line per event, to a JSONL file."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def log(
        self,
        *,
        level: str,
        event_type: str,
        message: str,
        tenant_id: str | None = None,
        bot_id: str | None = None,
        channel_id: str | None = None,
    ) -> None:
        event: dict[str, Any] = {
            "ts": time.time(),
            "level": level,
            "event_type": event_type,
            "message": message,
            "tenant_id": tenant_id,
            "bot_id": bot_id,
            "channel_id": channel_id,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


class NullUsageSink:
    """Usage sink that does nothing (for tests or channels with no billing)."""

    def record(
        self,
        *,
        tenant_id: str,
        bot_id: str,
        channel_id: str,
        message_id: str,
        kind: str,
    ) -> None:
        return None
