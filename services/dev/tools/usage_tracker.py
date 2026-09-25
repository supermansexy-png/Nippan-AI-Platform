class PushQuotaExceeded(RuntimeError):
    """Raised when a push would exceed the bot's monthly push quota."""


class UsageTracker:
    def __init__(self, data_access):
        self.data_access = data_access
        self._register_queries()

    def _register_queries(self):
        """Register all queries used by UsageTracker."""
        self.data_access.register("bot_push_quota",
            "SELECT monthly_push_quota FROM lite_bots WHERE tenant_id = %s AND bot_id = %s")
        self.data_access.register("usage_month_push_sum",
            """SELECT COALESCE(SUM(push_count), 0) FROM lite_usage_log
               WHERE tenant_id = %s AND bot_id = %s
               AND date_trunc('month', date) = date_trunc('month', CURRENT_DATE)""")
        self.data_access.register("usage_today_row",
            "SELECT * FROM lite_usage_log WHERE tenant_id = %s AND bot_id = %s AND date = CURRENT_DATE")
        self.data_access.register("usage_upsert_reply",
            """INSERT INTO lite_usage_log (tenant_id, bot_id, date, reply_count, push_count, model_tokens, estimated_cost_thb)
               VALUES (%s, %s, CURRENT_DATE, 1, 0, %s, %s)
               ON CONFLICT (tenant_id, bot_id, date)
               DO UPDATE SET
                   reply_count = lite_usage_log.reply_count + 1,
                   model_tokens = lite_usage_log.model_tokens + EXCLUDED.model_tokens,
                   estimated_cost_thb = lite_usage_log.estimated_cost_thb + EXCLUDED.estimated_cost_thb""")
        self.data_access.register("usage_upsert_push",
            """INSERT INTO lite_usage_log (tenant_id, bot_id, date, reply_count, push_count, model_tokens, estimated_cost_thb)
               VALUES (%s, %s, CURRENT_DATE, 0, 1, %s, %s)
               ON CONFLICT (tenant_id, bot_id, date)
               DO UPDATE SET
                   push_count = lite_usage_log.push_count + 1,
                   model_tokens = lite_usage_log.model_tokens + EXCLUDED.model_tokens,
                   estimated_cost_thb = lite_usage_log.estimated_cost_thb + EXCLUDED.estimated_cost_thb""")

    def record_reply(self, *, tenant_id, bot_id, model_tokens=0, estimated_cost_thb=0.0) -> None:
        self.data_access.execute(
            "usage_upsert_reply",
            (tenant_id, bot_id, model_tokens, estimated_cost_thb),
            tenant_id=tenant_id, bot_id=bot_id
        )

    def record_push(self, *, tenant_id, bot_id, model_tokens=0, estimated_cost_thb=0.0) -> None:
        quota_rows = self.data_access.execute(
            "bot_push_quota", (tenant_id, bot_id),
            tenant_id=tenant_id, bot_id=bot_id
        )
        if not quota_rows:
            raise ValueError("bot not found")
        monthly_quota = quota_rows[0][0]

        used_rows = self.data_access.execute(
            "usage_month_push_sum", (tenant_id, bot_id),
            tenant_id=tenant_id, bot_id=bot_id
        )
        current_used = used_rows[0][0]

        if current_used + 1 > monthly_quota:
            raise PushQuotaExceeded("monthly push quota exceeded")

        self.data_access.execute(
            "usage_upsert_push",
            (tenant_id, bot_id, model_tokens, estimated_cost_thb),
            tenant_id=tenant_id, bot_id=bot_id
        )