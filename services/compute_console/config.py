"""
Configuration module for Nippan AI Compute Console MVP.
Reads configuration from environment variables and local .env files.
Never hardcodes secrets or vendor-specific model identifiers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _load_env_file(env_path: Path) -> None:
    """Lightweight .env reader without requiring third-party dotenv library."""
    if not env_path.is_file():
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # Do not overwrite if already set in environment
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception:
        # Ignore errors loading .env file; defaults will apply
        pass


@dataclass(frozen=True)
class ConsoleConfig:
    env: str
    compute_provider: str
    storage_provider: str
    http_host: str
    http_port: int
    colab_endpoint_url: Optional[str]
    colab_auth_token: Optional[str]
    gdrive_models_path: str
    timeout_connect_sec: float
    timeout_load_sec: float
    timeout_chat_sec: float
    mock_simulate_latency_sec: float
    mock_default_gpu: str

    @classmethod
    def load(cls, env_file_path: Optional[str] = None) -> ConsoleConfig:
        """Load configuration from environment variables with optional .env file."""
        if env_file_path:
            _load_env_file(Path(env_file_path))
        else:
            # Check default .env locations
            default_env = Path(".env")
            if default_env.is_file():
                _load_env_file(default_env)
            else:
                service_env = Path(__file__).parent / ".env"
                if service_env.is_file():
                    _load_env_file(service_env)

        return cls(
            env=os.getenv("COMPUTE_ENV", "development").lower(),
            compute_provider=os.getenv("COMPUTE_PROVIDER", "mock").lower(),
            storage_provider=os.getenv("STORAGE_PROVIDER", "gdrive").lower(),
            http_host=os.getenv("HTTP_HOST", "127.0.0.1"),
            http_port=int(os.getenv("HTTP_PORT", "8080")),
            colab_endpoint_url=os.getenv("COLAB_ENDPOINT_URL") or None,
            colab_auth_token=os.getenv("COLAB_AUTH_TOKEN") or None,
            gdrive_models_path=os.getenv("GDRIVE_MODELS_PATH", "gdrive:/models"),
            timeout_connect_sec=float(os.getenv("TIMEOUT_CONNECT_SEC", "15.0")),
            timeout_load_sec=float(os.getenv("TIMEOUT_LOAD_SEC", "45.0")),
            timeout_chat_sec=float(os.getenv("TIMEOUT_CHAT_SEC", "20.0")),
            mock_simulate_latency_sec=float(os.getenv("MOCK_SIMULATE_LATENCY_SEC", "0.3")),
            mock_default_gpu=os.getenv("MOCK_DEFAULT_GPU", "NVIDIA Tesla T4 (16GB GDDR6)"),
        )

    def to_safe_dict(self) -> dict:
        """Returns a dict suitable for UI/API display, ensuring secrets are masked."""
        return {
            "env": self.env,
            "compute_provider": self.compute_provider,
            "storage_provider": self.storage_provider,
            "http_host": self.http_host,
            "http_port": self.http_port,
            "colab_endpoint_url": self.colab_endpoint_url or "(not configured)",
            "colab_auth_token_set": bool(self.colab_auth_token),
            "gdrive_models_path": self.gdrive_models_path,
            "timeout_connect_sec": self.timeout_connect_sec,
            "timeout_load_sec": self.timeout_load_sec,
            "timeout_chat_sec": self.timeout_chat_sec,
        }
