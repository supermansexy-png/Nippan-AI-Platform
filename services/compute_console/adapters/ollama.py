"""
Ollama Compute Provider Adapter.
Enables internal connection to local or remote Ollama daemon endpoints.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import List, Optional, Tuple

from services.compute_console.adapters.base import ComputeProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ChatMessage, GPUInfo, ModelSource, RuntimeStatus


class OllamaComputeAdapter(ComputeProviderAdapter):
    """
    Adapter connecting to Ollama REST daemon.
    """

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._endpoint = os.getenv("OLLAMA_ENDPOINT_URL", "http://127.0.0.1:11434").rstrip("/")
        self._connected = False
        self._loaded_model: Optional[ModelSource] = None
        self._gpu_info: Optional[GPUInfo] = None

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def display_name(self) -> str:
        return "Ollama Local/Remote Runtime"

    @property
    def is_mock(self) -> bool:
        return False

    @property
    def adapter_tier(self) -> str:
        return "live"

    def connect(self, timeout_sec: float) -> Tuple[bool, Optional[GPUInfo], str]:
        url = f"{self._endpoint}/api/tags"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                if resp.getcode() == 200:
                    self._connected = True
                    # /api/tags does not expose GPU metrics — do NOT fabricate
                    self._gpu_info = None
                    return True, None, f"Connected to Ollama service at {self._endpoint}"
                return False, None, f"Ollama returned HTTP {resp.getcode()}"
        except urllib.error.URLError as e:
            self._connected = False
            return False, None, f"Cannot reach Ollama service at {self._endpoint}: {e.reason}"
        except Exception as e:
            self._connected = False
            return False, None, f"Ollama connection error: {str(e)}"

    def disconnect(self, timeout_sec: float) -> Tuple[bool, str]:
        self._connected = False
        self._loaded_model = None
        self._gpu_info = None
        return True, "Disconnected from Ollama service"

    def get_status(self, timeout_sec: float) -> Tuple[RuntimeStatus, Optional[GPUInfo], str]:
        if not self._connected:
            return RuntimeStatus.DISCONNECTED, None, "Ollama service disconnected"
        if self._loaded_model:
            return RuntimeStatus.READY, self._gpu_info, f"Ollama active with {self._loaded_model.name}"
        return RuntimeStatus.CONNECTED, self._gpu_info, "Ollama service connected"

    def load_model(self, source: ModelSource, timeout_sec: float) -> Tuple[bool, str]:
        if not self._connected:
            return False, "Ollama service is not connected"
        self._loaded_model = source
        return True, f"Ollama model '{source.name}' initialized"

    def chat(self, messages: List[ChatMessage], timeout_sec: float) -> str:
        if not self._connected or not self._loaded_model:
            raise RuntimeError("Ollama service is not ready or model is not loaded")

        url = f"{self._endpoint}/api/generate"
        last_msg = messages[-1].content if messages else ""
        payload = json.dumps({"model": self._loaded_model.name, "prompt": last_msg, "stream": False}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
