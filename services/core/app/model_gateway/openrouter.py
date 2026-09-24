from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Protocol

import httpx

from app.war_room import (
    ModelTurnRequest,
    ModelTurnResult,
    ParticipantRole,
    UsageDelta,
)


class OpenRouterGatewayError(RuntimeError):
    """Raised when OpenRouter cannot produce a valid model turn."""


@dataclass(frozen=True, slots=True)
class ModelRoute:
    model_id: str
    provider_order: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id must not be blank")
        if any(not provider.strip() for provider in self.provider_order):
            raise ValueError("provider_order entries must not be blank")


@dataclass(frozen=True, slots=True)
class ModelPolicy:
    primary: ModelRoute
    timeout_seconds: float = 30.0
    max_output_tokens: int = 1024

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")


class ModelPolicyResolver(Protocol):
    async def resolve(self, model_policy_ref: str) -> ModelPolicy: ...


class OpenRouterGateway:
    """Configuration-driven OpenRouter implementation of the frozen ModelGateway."""

    def __init__(
        self,
        *,
        api_key: str,
        policy_resolver: ModelPolicyResolver,
        base_url: str = "https://openrouter.ai/api/v1",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be blank")
        self._api_key = api_key
        self._policy_resolver = policy_resolver
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def generate_turn(self, request: ModelTurnRequest) -> ModelTurnResult:
        policy = await self._policy_resolver.resolve(request.model_policy_ref)
        max_output_tokens = min(
            policy.max_output_tokens,
            request.max_output_tokens,
        )

        # War Room V1 intentionally performs one billable OpenRouter request
        # per automatic turn. Provider redundancy belongs inside OpenRouter's
        # provider routing for the configured primary model; application-level
        # retries/model fallback would create unaccounted repeated spend.
        try:
            return await self._call_route(
                request=request,
                route=policy.primary,
                timeout_seconds=policy.timeout_seconds,
                max_output_tokens=max_output_tokens,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError("OpenRouter turn timed out") from exc

    async def _call_route(
        self,
        *,
        request: ModelTurnRequest,
        route: ModelRoute,
        timeout_seconds: float,
        max_output_tokens: int,
    ) -> ModelTurnResult:
        payload: dict[str, object] = {
            "model": route.model_id,
            "messages": self._messages(request),
            "max_tokens": max_output_tokens,
        }
        if route.provider_order:
            payload["provider"] = {"order": list(route.provider_order)}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        if self._client is not None:
            response = await self._client.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout_seconds,
            )
        else:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

        if response.status_code >= 500 or response.status_code == 429:
            raise OpenRouterGatewayError(
                f"transient OpenRouter status {response.status_code}"
            )
        if response.status_code >= 400:
            raise OpenRouterGatewayError(
                f"non-retryable OpenRouter status {response.status_code}"
            )

        try:
            body = response.json()
            choice = body["choices"][0]
            content = choice["message"]["content"]
            provider_request_id = str(body["id"])
            responded_model = str(body["model"])
            usage_raw = body["usage"]
            input_tokens = int(usage_raw["prompt_tokens"])
            output_tokens = int(usage_raw["completion_tokens"])
            cost = self._required_cost(usage_raw["cost"])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OpenRouterGatewayError(
                "non-retryable invalid OpenRouter response"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterGatewayError(
                "non-retryable empty OpenRouter response"
            )
        if not provider_request_id.strip():
            raise OpenRouterGatewayError(
                "non-retryable missing OpenRouter request id"
            )
        if responded_model != route.model_id:
            raise OpenRouterGatewayError(
                "non-retryable OpenRouter model mismatch"
            )

        if input_tokens < 0 or output_tokens < 0:
            raise OpenRouterGatewayError(
                "non-retryable invalid OpenRouter usage"
            )

        return ModelTurnResult(
            content_text=content,
            content_reference=None,
            usage=UsageDelta(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                normalized_cost=cost,
                currency="USD",
            ),
            provider_request_id=provider_request_id,
            responded_model=responded_model,
        )

    @staticmethod
    def _messages(request: ModelTurnRequest) -> list[dict[str, str]]:
        references = (
            "\n".join(f"- {item}" for item in request.context_references)
            if request.context_references
            else "- none"
        )
        synthesis = request.prior_round_synthesis or "none"
        return [
            {
                "role": "system",
                "content": (
                    "You are participating in a bounded Nippan AI War Room turn. "
                    "Stay within your assigned role and answer only the agenda objective. "
                    "Default to Thai for all participant-facing prose, even when role "
                    "names and system identifiers are provided in English. Keep canonical "
                    "role names unchanged when referring to system roles."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Role: {request.role.value}\n"
                    "Default response language: Thai\n"
                    f"Agenda objective: {request.agenda_objective}\n"
                    f"Context references:\n{references}\n"
                    f"Prior-round synthesis: {synthesis}"
                ),
            },
        ]

    @staticmethod
    def _required_cost(value: object) -> Decimal:
        try:
            parsed = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("invalid provider cost") from exc
        if parsed < 0:
            raise ValueError("provider cost must not be negative")
        return parsed
