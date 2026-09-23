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


@lru_cache
def get_settings() -> Settings:
    return Settings()
