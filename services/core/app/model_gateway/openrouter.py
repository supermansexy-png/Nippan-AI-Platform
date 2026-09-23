from __future__ import annotations

import asyncio
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
    fallbacks: tuple[ModelRoute, ...] = ()
    timeout_seconds: float = 30.0
    max_retries_per_route: int = 1
    retry_backoff_seconds: float = 0.5

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_retries_per_route < 0:
            raise ValueError("max_retries_per_route must not be negative")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds must not be negative")


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
        routes = (policy.primary,) + policy.fallbacks

        # Formal audit identity is governance-significant. Provider routing for
        # the same model is allowed, but silently changing to a fallback model is not.
        if request.role is ParticipantRole.INDEPENDENT_AUDITOR:
            routes = routes[:1]

        last_error: Exception | None = None
        for route in routes:
            for attempt in range(policy.max_retries_per_route + 1):
                try:
                    return await self._call_route(
                        request=request,
                        route=route,
                        timeout_seconds=policy.timeout_seconds,
                    )
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    last_error = exc
                except OpenRouterGatewayError as exc:
                    last_error = exc
                    # Retry only transient provider/server failures. Invalid
                    # payloads are deterministic and should fail immediately.
                    if "non-retryable" in str(exc):
                        raise

                if attempt < policy.max_retries_per_route:
                    await asyncio.sleep(
                        policy.retry_backoff_seconds * (2**attempt)
                    )

        if isinstance(last_error, httpx.TimeoutException):
            raise TimeoutError("all configured model routes timed out") from last_error
        raise OpenRouterGatewayError("all configured model routes failed") from last_error

    async def _call_route(
        self,
        *,
        request: ModelTurnRequest,
        route: ModelRoute,
        timeout_seconds: float,
    ) -> ModelTurnResult:
        payload: dict[str, object] = {
            "model": route.model_id,
            "messages": self._messages(request),
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
            usage_raw = body.get("usage") or {}
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OpenRouterGatewayError(
                "non-retryable invalid OpenRouter response"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterGatewayError(
                "non-retryable empty OpenRouter response"
            )

        input_tokens = int(usage_raw.get("prompt_tokens") or 0)
        output_tokens = int(usage_raw.get("completion_tokens") or 0)
        cost = self._parse_cost(usage_raw.get("cost"))

        return ModelTurnResult(
            content_text=content,
            content_reference=None,
            usage=UsageDelta(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                normalized_cost=cost,
                currency="USD" if cost is not None else None,
            ),
            provider_request_id=(
                str(body["id"]) if body.get("id") is not None else None
            ),
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
                    "Stay within your assigned role and answer only the agenda objective."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Role: {request.role.value}\n"
                    f"Agenda objective: {request.agenda_objective}\n"
                    f"Context references:\n{references}\n"
                    f"Prior-round synthesis: {synthesis}"
                ),
            },
        ]

    @staticmethod
    def _parse_cost(value: object) -> Decimal | None:
        if value is None:
            return None
        try:
            parsed = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
        return parsed if parsed >= 0 else None
