import pytest
from services.dev.tools.usage_tracker import UsageTracker, PushQuotaExceeded


class FakeDataAccess:
    def __init__(self):
        self.calls = []
        self.quota = 200
        self.push_used = 0
        self.reply_rows = {}
        self._queries = {}

    def register(self, name: str, sql: str) -> None:
        self._queries[name] = sql

    def execute(self, query_name, params=(), *, tenant_id, bot_id):
        self.calls.append((query_name, params, tenant_id, bot_id))

        if query_name == "bot_push_quota":
            return [(self.quota,)]
        if query_name == "usage_month_push_sum":
            return [(self.push_used,)]
        if query_name == "usage_upsert_push":
            self.push_used += 1
            return []
        if query_name == "usage_upsert_reply":
            key = (tenant_id, bot_id)
            self.reply_rows[key] = self.reply_rows.get(key, 0) + 1
            return []
        return []


def test_record_reply_increments_and_passes_scope():
    da = FakeDataAccess()
    tracker = UsageTracker(da)

    tracker.record_reply(tenant_id="t1", bot_id="b1", model_tokens=10, estimated_cost_thb=0.5)
    tracker.record_reply(tenant_id="t1", bot_id="b1", model_tokens=5, estimated_cost_thb=0.2)

    assert len(da.calls) == 2
    for name, _, t, b in da.calls:
        assert name == "usage_upsert_reply"
        assert t == "t1"
        assert b == "b1"


def test_record_push_under_quota_increments():
    da = FakeDataAccess()
    da.quota = 200
    da.push_used = 0
    tracker = UsageTracker(da)

    tracker.record_push(tenant_id="t1", bot_id="b1", model_tokens=8, estimated_cost_thb=0.3)

    assert da.push_used == 1
    assert any(name == "usage_upsert_push" for name, _, _, _ in da.calls)


def test_record_push_over_quota_raises_and_writes_nothing():
    da = FakeDataAccess()
    da.quota = 200
    da.push_used = 200
    tracker = UsageTracker(da)

    with pytest.raises(PushQuotaExceeded):
        tracker.record_push(tenant_id="t1", bot_id="b1")

    insert_calls = [c for c in da.calls if c[0] == "usage_upsert_push"]
    assert len(insert_calls) == 0


def test_token_and_cost_accumulate():
    da = FakeDataAccess()
    tracker = UsageTracker(da)

    tracker.record_reply(tenant_id="t1", bot_id="b1", model_tokens=100, estimated_cost_thb=1.0)
    tracker.record_reply(tenant_id="t1", bot_id="b1", model_tokens=50, estimated_cost_thb=0.5)
    tracker.record_push(tenant_id="t1", bot_id="b1", model_tokens=25, estimated_cost_thb=0.25)

    insert_calls = [c for c in da.calls if c[0] in ("usage_upsert_reply", "usage_upsert_push")]
    assert len(insert_calls) == 3


# NEW: usage_tracker only ever calls registered names
def test_usage_tracker_only_calls_registered_names():
    da = FakeDataAccess()
    tracker = UsageTracker(da)

    tracker.record_reply(tenant_id="t1", bot_id="b1")
    tracker.record_push(tenant_id="t1", bot_id="b1")

    for name, _, _, _ in da.calls:
        assert name in ("bot_push_quota", "usage_month_push_sum", "usage_upsert_reply", "usage_upsert_push")