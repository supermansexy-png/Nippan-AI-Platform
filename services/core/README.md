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

## Phase 2 constraints

This service is a skeleton only. It does not send production traffic, call OpenRouter, execute MCP tools, or migrate legacy bots.

Every tenant-scoped database operation must run inside `Database.tenant_transaction(...)`; pooled connections must never rely on session-persistent tenant context.
