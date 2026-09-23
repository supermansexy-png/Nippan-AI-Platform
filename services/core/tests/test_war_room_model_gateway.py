import json
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
    UsageDelta,
)
from app.war_room.budget import (
    BudgetPolicy,
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


def turn_request(role: ParticipantRole = ParticipantRole.BUILDER) -> ModelTurnRequest:
    return ModelTurnRequest(
        correlation=correlation(),
        participant_id="agent-1",
        role=role,
        model_policy_ref="policy/agent-1",
        agenda_objective="Review the implementation",
        context_references=("github://evidence/1",),
    )


@pytest.mark.anyio
async def test_openrouter_falls_back_to_configured_model_route() -> None:
    seen_models: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        seen_models.append(body["model"])
        if body["model"] == "model-primary":
            return httpx.Response(503, json={"error": "busy"})
        return httpx.Response(
            200,
            json={
                "id": "req-123",
                "choices": [{"message": {"content": "fallback response"}}],
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
                    primary=ModelRoute("model-primary"),
                    fallbacks=(ModelRoute("model-fallback"),),
                    max_retries_per_route=0,
                )
            ),
            client=client,
        )
        result = await gateway.generate_turn(turn_request())

    assert seen_models == ["model-primary", "model-fallback"]
    assert result.content_text == "fallback response"
    assert result.provider_request_id == "req-123"
    assert result.usage.input_tokens == 20
    assert result.usage.output_tokens == 10
    assert result.usage.normalized_cost == Decimal("0.0123")
    assert result.usage.currency == "USD"


@pytest.mark.anyio
async def test_independent_auditor_never_silently_switches_model_identity() -> None:
    seen_models: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        seen_models.append(body["model"])
        return httpx.Response(503, json={"error": "busy"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(
                    primary=ModelRoute("auditor-primary"),
                    fallbacks=(ModelRoute("different-model"),),
                    max_retries_per_route=0,
                )
            ),
            client=client,
        )
        with pytest.raises(OpenRouterGatewayError):
            await gateway.generate_turn(
                turn_request(ParticipantRole.INDEPENDENT_AUDITOR)
            )

    assert seen_models == ["auditor-primary"]


@pytest.mark.anyio
async def test_openrouter_timeout_kind_survives_retry_exhaustion() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("provider timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        gateway = OpenRouterGateway(
            api_key="test-key",
            policy_resolver=Resolver(
                ModelPolicy(
                    primary=ModelRoute("model-primary"),
                    max_retries_per_route=1,
                    retry_backoff_seconds=0,
                )
            ),
            client=client,
        )
        with pytest.raises(TimeoutError):
            await gateway.generate_turn(turn_request())

    assert calls == 2


@pytest.mark.anyio
async def test_usage_backed_budget_authority_denies_before_provider_at_limit() -> None:
    policy = BudgetPolicy(
        room=BudgetLimit(token_limit=1000, cost_limit=Decimal("10"), currency="USD"),
        agenda=BudgetLimit(token_limit=500, cost_limit=Decimal("5"), currency="USD"),
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
    usage = UsageDelta(input_tokens=7, output_tokens=3)

    await authority.record_usage(
        correlation=correlation(),
        participant_id="agent-1",
        usage=usage,
    )

    assert len(store.recorded) == 1
    assert store.recorded[0]["usage"] == usage
