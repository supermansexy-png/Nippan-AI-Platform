"""T-003 — Phase A ``monitor-log`` tool (WS3, free-model workstream).

Contract: ``docs/product/MCP_TOOLS_V1.md`` — ``monitor-log`` "Writes events
to the monitoring log; sends red alerts", used by all workflows, build
step 0.

Phase A has **no** monitoring/audit table: ``docs/data/LITE_SCHEMA_V1.md``
is a protected Phase A document and deliberately leaves formal
audit/monitoring tables out ("Deliberately left out"). Events therefore go
to an injectable *sink* — a callable that receives exactly one plain
``dict`` (always serialisable with ``json.dumps``). The default sink
appends one JSON line to ``monitor_log.jsonl`` beside this module; n8n or
any workflow can inject its own sink or alert channel without this file
knowing anything about the transport.

``alert_red`` must never fail just because nobody configured an alert
channel: the event is logged first, and a missing/``None``
``alert_channel`` is skipped silently.

Stdlib only (``json``, ``datetime``, ``pathlib``, ``typing``).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

__all__ = ["MonitorLog", "DEFAULT_SINK_PATH"]

#: Default JSONL target. Resolved at call time through the module attribute
#: so tests can point it at a tmp path (``monkeypatch.setattr``).
DEFAULT_SINK_PATH: Path = Path(__file__).resolve().with_name("monitor_log.jsonl")

#: sink: receives one plain dict per event.
EventSink = Callable[[Dict[str, Any]], None]
#: alert_channel: receives one single-line text.
AlertChannel = Callable[[str], None]

#: Exact key set of every event, in write order.
EVENT_KEYS = ("ts", "level", "event_type", "message", "tenant_id", "bot_id")


def _default_sink(event: Dict[str, Any]) -> None:
    """Append one JSON line to the default JSONL file."""
    path = DEFAULT_SINK_PATH  # module attribute, looked up per call
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _single_line(text: Any) -> str:
    """Collapse any line break so an alert is always one line."""
    return " ".join(str(text).splitlines())


class MonitorLog:
    """Writes monitoring events to a sink and raises red alerts.

    Parameters
    ----------
    sink:
        ``callable(event: dict) -> None``. ``None`` selects the default
        JSONL sink (:data:`DEFAULT_SINK_PATH`).
    alert_channel:
        ``callable(text: str) -> None``. ``None`` means alerts are logged
        only — that is not an error.
    """

    def __init__(
        self,
        sink: Optional[EventSink] = None,
        alert_channel: Optional[AlertChannel] = None,
    ) -> None:
        if sink is not None and not callable(sink):
            raise TypeError("sink must be callable(event: dict) -> None")
        if alert_channel is not None and not callable(alert_channel):
            raise TypeError("alert_channel must be callable(text: str) -> None")
        self._sink: EventSink = _default_sink if sink is None else sink
        self._alert_channel: Optional[AlertChannel] = alert_channel

    def log_event(
        self,
        level: str,
        event_type: str,
        message: str,
        *,
        tenant_id: Any = None,
        bot_id: Any = None,
    ) -> None:
        """Write one event dict (the six keys) to the sink."""
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event_type": event_type,
            "message": message,
            "tenant_id": tenant_id,
            "bot_id": bot_id,
        }
        self._sink(event)

    def alert_red(
        self,
        event_type: str,
        message: str,
        *,
        tenant_id: Any = None,
        bot_id: Any = None,
    ) -> None:
        """Log a ``level="red"`` event first, then notify the channel.

        Never raises because ``alert_channel`` is missing or ``None``.
        """
        self.log_event(
            "red", event_type, message, tenant_id=tenant_id, bot_id=bot_id
        )
        channel = self._alert_channel
        if channel is None:
            return
        parts = ["[RED] %s | %s" % (event_type, message)]
        if tenant_id is not None:
            parts.append("tenant=%s" % tenant_id)
        if bot_id is not None:
            parts.append("bot=%s" % bot_id)
        channel(_single_line(" | ".join(parts)))
