# Nippan Core Runtime

Minimal FastAPI Core skeleton for Phase 2.

Current boundaries:

- `/health`: process-level liveness
- `/ready`: database readiness
- PostgreSQL connection pool
- tenant-scoped transactions using transaction-local `app.tenant_id`
- optional transaction-local `app.application_id` and `app.request_id`
- active Agent config loader that only accepts the activation -> PUBLISHED config path

## Environment

Runtime configuration is environment-only. Do not commit credentials.

Required for database-backed readiness/runtime work:

```text
NIPPAN_DATABASE_URL=postgresql://...
```

Optional:

```text
NIPPAN_ENVIRONMENT=development
NIPPAN_DATABASE_POOL_MIN_SIZE=1
NIPPAN_DATABASE_POOL_MAX_SIZE=5
```

## Run

```bash
python -m pip install -e ".[test]"
uvicorn app.main:app --reload
```


## War Room guarded-turn database capacity

War Room automatic turns use the N-11 **single-connection guarded transaction**
strategy. The room-scoped PostgreSQL advisory lock, durable state check, nested
budget/usage database work, and event persistence reuse the same
`Database.tenant_transaction(...)` connection when they run on the same task
and exact tenant/application/request scope.

Operational rule:

- one in-flight guarded turn consumes **1 pooled connection**;
- the default `NIPPAN_DATABASE_POOL_MAX_SIZE=5` therefore supports at most
  **4 concurrent guarded turns plus 1 spare connection** for control/readiness
  work;
- a future turn driver must cap concurrency at 4 with the default pool, or raise
  `NIPPAN_DATABASE_POOL_MAX_SIZE` so `pool_max >= max_concurrent_turns + 1`;
- nested database work must use the same `Database` instance; a scope change
  fails closed instead of borrowing the guarded connection;
- the guard sets `idle_in_transaction_session_timeout=0` transaction-locally
  so a managed PostgreSQL idle timeout cannot kill the advisory lock during the
  bounded provider HTTP wait. The model gateway HTTP timeout remains the
  application-side wait bound.

This capacity statement does not enable a turn driver. The preview transport
only invokes billable `run_next_turn` when `war_room_preview_model_turns_enabled`
is set together with a configured OpenRouter key/model (default OFF, zero
billable calls by default).

## Phase 2 constraints

This service is a skeleton only. It does not send production traffic, call OpenRouter, execute MCP tools, or migrate legacy bots.

Every tenant-scoped database operation must run inside `Database.tenant_transaction(...)`; pooled connections must never rely on session-persistent tenant context.
