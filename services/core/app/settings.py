from functools import lru_cache
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NIPPAN_",
        env_file=".env",
        extra="ignore",
    )

    environment: str = Field(default="development")
    database_url: str | None = Field(default=None)
    database_pool_min_size: int = Field(default=1, ge=0)
    database_pool_max_size: int = Field(default=5, ge=1)
    openrouter_api_key: str | None = Field(default=None)
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")

    # Development-only War Room preview. The browser never supplies actor
    # identity; tenant/application/principal scope is established by server
    # configuration and still must pass the database-backed room authorizers.
    war_room_preview_enabled: bool = Field(default=False)
    war_room_preview_bootstrap: bool = Field(default=False)
    war_room_preview_tenant_id: UUID | None = Field(default=None)
    war_room_preview_application_id: UUID | None = Field(default=None)
    war_room_preview_principal_id: str | None = Field(default=None)
    war_room_preview_poll_seconds: float = Field(default=1.0, ge=0.1, le=10.0)
    # Optional billable preview turns. Disabled by default; when enabled, the
    # preview uses a tightly bounded low-cost OpenRouter model and per-room cap.
    war_room_preview_model_turns_enabled: bool = Field(default=False)
    war_room_preview_model_id: str = Field(default="poolside/laguna-s-2.1")
    war_room_preview_max_output_tokens: int = Field(default=160, ge=32, le=512)
    war_room_preview_max_turns_per_command: int = Field(default=3, ge=1, le=5)
    war_room_preview_room_token_limit: int = Field(default=6000, ge=256, le=50000)
    war_room_preview_room_cost_limit_usd: float = Field(default=0.01, ge=0.0, le=1.0)

    # Optional remote preview gate. Loopback stays available in development.
    # Remote traffic is accepted only after Cloudflare Access JWT verification
    # and an exact owner-email match; the verified request is then mapped to
    # the server-configured preview principal above.
    war_room_preview_remote_access_enabled: bool = Field(default=False)
    cloudflare_access_team_domain: str | None = Field(default=None)
    cloudflare_access_audience: str | None = Field(default=None)
    cloudflare_access_owner_email: str | None = Field(default=None)
    cloudflare_access_jwks_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=21600,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
