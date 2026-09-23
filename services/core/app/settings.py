from functools import lru_cache

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
