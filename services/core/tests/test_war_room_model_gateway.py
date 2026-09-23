import json
from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import UUID

import httpx
import pytest

from app.model_gateway import (
    ModelPolicy,
    ModelRoute,
    OpenRouterGateway,
    OpenRouterGatewayError,
)
from app.war_room import (
    BudgetLimit,
    CorrelationContext,
    ModelTurnRequest,
    ParticipantRole,
    RoomState,
    UsageDelta,
)
from app.war_room.budget import (
    BudgetPolicy,
    PostgresRoomTurnGuard,
    UsageBackedBudgetAuthority,
    UsageTotals,
)


class Resolver:
    def __init__(self, policy: ModelPolicy) -> None:
        self.policy = policy

    async def resolve(self, _model_policy_ref: str) -> ModelPolicy:
        return self.policy


class BudgetResolver:
    def __init__(self, policy: BudgetPolicy) -> None:
        self.policy = policy

    async def resolve(self, **_) -> BudgetPolicy:
        return self.policy


class UsageStore:
    def __init__(self, totals: UsageTotals) -> None:
        self.totals = totals
        self.recorded = []

    async def read_totals(self, **_) -> UsageTotals:
        return self.totals

    async def record_usage(self, **values) -> None:
        self.recorded.append(values)


class LockResult:
    def __init__(self, row=None) -> None:
        self.row = row

    async def fetchone(self):
        return self.row


class LockConnection:
    def __init__(self) -> None:
        self.executed = []

    async def execute(self, query, params):
        self.executed.append((query, params))
        if "select state" in query.lower():
            return LockResult(("RUNNING",))
        return LockResult()


class LockDatabase:
    def __init__(self) -> None:
        self.connection = LockConnection()
        self.scopes = []

    @asynccontextmanager
    async def tenant_transaction(self, **scope):
        self.scopes.append(scope)
        yield self.connection


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def correlation() -> CorrelationContext:
    return CorrelationContext(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        room_id=UUID(int=3),
        agenda_item_id=UUID(int=4),
        request_id=UUID(int=5),
        trace_id="0123456789abcdef0123456789abcdef",
    )


def turn_request(
    role: ParticipantRole = ParticipantRole.BUILDER,
    *,
    max_output_tokens: int = 120,
) -> ModelTurnRequest:
    return ModelTurnRequest(
        correlation=correlation(),
        participant_id="agent-1",
        role=role,
        model_policy_ref="policy/agent-1",
        agenda_objective="Review the implementation",
        max_output_tokens=max_output_tokens,
        context_references=("github://evidence/1",),
    )


@pytest.mark.anyio
async def test_openrouter_uses_one_request_and_enforces_smallest_output_cap() -> None:
    calls = []
    payloads = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        payloads.append(json.loads(request.content.decode()))
        return httpx.Response(
            200,
            json={
                "id": "req-123",
                "model": "model-primary",
                "choices": [{"message": {"content": "bounded response"}}],
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                    "cost": "0.0123",
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(
                    primary=ModelRoute(
                        "model-primary",
                        provider_order=("Provider-A", "Provider-B"),
                    ),
                    max_output_tokens=80,
                )
            ),
            client=client,
        )
        result = await gateway.generate_turn(
            turn_request(max_output_tokens=120)
        )

    assert len(calls) == 1
    assert payloads[0]["model"] == "model-primary"
    assert payloads[0]["max_tokens"] == 80
    assert payloads[0]["provider"] == {
        "order": ["Provider-A", "Provider-B"]
    }
    assert result.content_text == "bounded response"
    assert result.provider_request_id == "req-123"
    assert result.responded_model == "model-primary"
    assert result.usage.normalized_cost == Decimal("0.0123")
    assert result.usage.currency == "USD"


@pytest.mark.anyio
async def test_transient_provider_failure_is_not_retried_by_application() -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={"error": "busy"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(primary=ModelRoute("model-primary"))
            ),
            client=client,
        )
        with pytest.raises(OpenRouterGatewayError):
            await gateway.generate_turn(turn_request())

    assert calls == 1


@pytest.mark.anyio
async def test_timeout_is_one_billable_attempt_and_preserves_failure_kind() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("provider timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(primary=ModelRoute("model-primary"))
            ),
            client=client,
        )
        with pytest.raises(TimeoutError):
            await gateway.generate_turn(turn_request())

    assert calls == 1


@pytest.mark.anyio
async def test_success_without_usage_fails_closed_instead_of_zero_accounting() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "req-no-usage",
                "model": "model-primary",
                "choices": [{"message": {"content": "response"}}],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(primary=ModelRoute("model-primary"))
            ),
            client=client,
        )
        with pytest.raises(OpenRouterGatewayError):
            await gateway.generate_turn(turn_request())


@pytest.mark.anyio
async def test_success_without_cost_fails_closed() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "req-no-cost",
                "model": "model-primary",
                "choices": [{"message": {"content": "response"}}],
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(primary=ModelRoute("model-primary"))
            ),
            client=client,
        )
        with pytest.raises(OpenRouterGatewayError):
            await gateway.generate_turn(turn_request())


@pytest.mark.anyio
async def test_budget_authority_grants_only_remaining_output_allowance() -> None:
    policy = BudgetPolicy(
        room=BudgetLimit(
            token_limit=1000,
            cost_limit=Decimal("10"),
            currency="USD",
        ),
        agenda=BudgetLimit(
            token_limit=500,
            cost_limit=Decimal("5"),
            currency="USD",
        ),
        participant=BudgetLimit(
            token_limit=200,
            cost_limit=Decimal("1"),
            currency="USD",
        ),
    )
    store = UsageStore(
        UsageTotals(
            room_tokens=100,
            agenda_tokens=50,
            participant_tokens=20,
            room_cost=Decimal("1"),
            agenda_cost=Decimal("0.5"),
            participant_cost=Decimal("0.1"),
        )
    )
    authority = UsageBackedBudgetAuthority(
        policy_resolver=BudgetResolver(policy),
        usage_store=store,
    )

    decision = await authority.authorize_turn(
        correlation=correlation(),
        participant_id="agent-1",
    )

    assert decision.allowed is True
    assert decision.max_output_tokens == 180


@pytest.mark.anyio
async def test_usage_backed_budget_authority_denies_before_provider_at_limit() -> None:
    policy = BudgetPolicy(
        room=BudgetLimit(
            token_limit=1000,
            cost_limit=Decimal("10"),
            currency="USD",
        ),
        agenda=BudgetLimit(
            token_limit=500,
            cost_limit=Decimal("5"),
            currency="USD",
        ),
        participant=BudgetLimit(
            token_limit=200,
            cost_limit=Decimal("1"),
            currency="USD",
        ),
    )
    store = UsageStore(
        UsageTotals(
            room_tokens=100,
            agenda_tokens=50,
            participant_tokens=200,
            room_cost=Decimal("1"),
            agenda_cost=Decimal("0.5"),
            participant_cost=Decimal("1"),
        )
    )
    authority = UsageBackedBudgetAuthority(
        policy_resolver=BudgetResolver(policy),
        usage_store=store,
    )

    decision = await authority.authorize_turn(
        correlation=correlation(),
        participant_id="agent-1",
    )

    assert decision.allowed is False
    assert decision.halt_reason.value == "PARTICIPANT_BUDGET_EXHAUSTED"
    assert decision.max_output_tokens is None


@pytest.mark.anyio
async def test_usage_record_is_forwarded_to_platform_usage_owner() -> None:
    policy = BudgetPolicy(
        room=BudgetLimit(token_limit=1000),
        agenda=BudgetLimit(token_limit=500),
        participant=BudgetLimit(token_limit=200),
    )
    store = UsageStore(UsageTotals())
    authority = UsageBackedBudgetAuthority(
        policy_resolver=BudgetResolver(policy),
        usage_store=store,
    )
    usage = UsageDelta(
        input_tokens=7,
        output_tokens=3,
        normalized_cost=Decimal("0.001"),
        currency="USD",
    )

    await authority.record_usage(
        correlation=correlation(),
        participant_id="agent-1",
        usage=usage,
    )

    assert len(store.recorded) == 1
    assert store.recorded[0]["usage"] == usage


@pytest.mark.anyio
async def test_postgres_turn_guard_takes_room_scoped_advisory_lock() -> None:
    database = LockDatabase()
    guard = PostgresRoomTurnGuard(database)  # type: ignore[arg-type]

    async with guard.hold(correlation=correlation()) as durable_state:
        assert durable_state is RoomState.RUNNING

    assert database.scopes == [
        {
            "tenant_id": UUID(int=1),
            "application_id": UUID(int=2),
            "request_id": UUID(int=5),
        }
    ]
    assert len(database.connection.executed) == 3
    timeout_query, timeout_params = database.connection.executed[0]
    lock_query, lock_params = database.connection.executed[1]
    state_query, state_params = database.connection.executed[2]
    assert "idle_in_transaction_session_timeout" in timeout_query
    assert timeout_params == ()
    assert "pg_advisory_xact_lock" in lock_query
    assert str(UUID(int=3)) in lock_params[0]
    assert "select state" in state_query.lower()
    assert state_params == (UUID(int=1), UUID(int=2), UUID(int=3))


@pytest.mark.anyio
async def test_openrouter_rejects_responded_model_mismatch() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "req-mismatch",
                "model": "different-model",
                "choices": [{"message": {"content": "wrong model"}}],
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                    "cost": "0.0123",
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(primary=ModelRoute("model-primary"))
            ),
            client=client,
        )
        with pytest.raises(OpenRouterGatewayError, match="model mismatch"):
            await gateway.generate_turn(turn_request())
