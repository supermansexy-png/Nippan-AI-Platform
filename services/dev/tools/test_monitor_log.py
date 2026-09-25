"""Tests for services/dev/tools/monitor_log.py (T-003, WS3).

No real file and no real alert channel unless the default sink is under
test: the sink and the alert channel are injected as plain lists.

Run: ``python -m pytest services/dev/tools/test_monitor_log.py -q``
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import monitor_log
import pytest
from monitor_log import MonitorLog

EXPECTED_KEYS = {"ts", "level", "event_type", "message", "tenant_id", "bot_id"}


# a) log_event -> one dict, six keys, right level/event_type/message
def test_log_event_writes_one_dict_with_six_keys():
    events = []
    log = MonitorLog(sink=events.append)

    log.log_event("warn", "usage.cap", "push quota nearly exhausted")

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, dict)
    assert set(event.keys()) == EXPECTED_KEYS
    assert event["level"] == "warn"
    assert event["event_type"] == "usage.cap"
    assert event["message"] == "push quota nearly exhausted"
    # the sink always receives something json.dumps can serialise
    assert json.loads(json.dumps(event)) == event
    # ts is current UTC time in ISO-8601
    ts = datetime.fromisoformat(event["ts"])
    assert ts.tzinfo is not None


# b) tenant_id / bot_id default to None and are present in the event
def test_scope_defaults_to_none_and_is_included():
    events = []
    log = MonitorLog(sink=events.append)

    log.log_event("info", "tool.call", "data-access ok")
    assert events[0]["tenant_id"] is None
    assert events[0]["bot_id"] is None

    log.log_event("info", "tool.call", "data-access ok",
                  tenant_id="t-1", bot_id="b-1")
    assert events[1]["tenant_id"] == "t-1"
    assert events[1]["bot_id"] == "b-1"


# c) alert_red logs level "red" first, then calls alert_channel once, one line
def test_alert_red_logs_then_notifies_once_with_single_line():
    events = []
    alerts = []
    order = []

    def sink(event):
        events.append(event)
        order.append("sink")

    def alert_channel(text):
        alerts.append(text)
        order.append("alert")

    log = MonitorLog(sink=sink, alert_channel=alert_channel)
    log.alert_red("db.down", "connection refused\nretrying now",
                  tenant_id="t-1", bot_id="b-1")

    assert len(events) == 1
    assert events[0]["level"] == "red"
    assert events[0]["event_type"] == "db.down"
    assert set(events[0].keys()) == EXPECTED_KEYS

    assert len(alerts) == 1
    assert isinstance(alerts[0], str)
    assert "\n" not in alerts[0] and "\r" not in alerts[0]

    assert order == ["sink", "alert"]  # log first, then notify


# d) alert_red with alert_channel=None still logs and does not raise
def test_alert_red_without_alert_channel_still_logs():
    events = []
    log = MonitorLog(sink=events.append, alert_channel=None)
    log.alert_red("bot.crash", "worker died")
    assert len(events) == 1
    assert events[0]["level"] == "red"

    # alert_channel omitted entirely -> same behaviour
    log2 = MonitorLog(sink=events.append)
    log2.alert_red("bot.crash", "worker died again")
    assert len(events) == 2
    assert events[1]["level"] == "red"


# e) default sink appends one valid JSON line to the (tmp) file
def test_default_sink_writes_valid_json_line(monkeypatch):
    # stdlib tmp dir on purpose: pytest's own tmp_path basetemp is not
    # usable on this machine (ACL), and the test must not depend on it.
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "monitor_log.jsonl"
        monkeypatch.setattr(monitor_log, "DEFAULT_SINK_PATH", target)

        log = MonitorLog()
        log.log_event("info", "tool.call", "first line")
        log.alert_red("quota.cap", "push cap reached", tenant_id="t-1", bot_id="b-1")

        lines = target.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert target.read_text(encoding="utf-8").endswith("\n")

        first, second = (json.loads(line) for line in lines)
        assert set(first.keys()) == EXPECTED_KEYS
        assert first["level"] == "info"
        assert first["message"] == "first line"
        assert set(second.keys()) == EXPECTED_KEYS
        assert second["level"] == "red"
        assert second["tenant_id"] == "t-1"
        assert second["bot_id"] == "b-1"
        datetime.fromisoformat(first["ts"])  # ISO-8601, parses


# the sink always receives a plain dict, never a string/object wrapper
def test_sink_always_receives_plain_dict():
    received = []
    MonitorLog(sink=received.append).log_event("error", "x.y", "boom")
    assert type(received[0]) is dict
    assert all(isinstance(v, (str, type(None))) for v in received[0].values())


# non-callable sink / alert_channel is rejected at construction time
def test_non_callable_injections_rejected():
    with pytest.raises(TypeError):
        MonitorLog(sink="not a callable")
    with pytest.raises(TypeError):
        MonitorLog(alert_channel=42)
