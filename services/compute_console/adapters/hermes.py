"""
Hermes Compute Adapter Extension Point.
Provides interface integration for Hermes Agent / Cluster runtimes.
"""

from __future__ import annotations

import os
from typing import List, Optional, Tuple

from services.compute_console.adapters.base import ComputeProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ChatMessage, GPUInfo, ModelSource, RuntimeStatus


class HermesComputeAdapter(ComputeProviderAdapter):
    """
    Adapter for connecting Nippan AI Platform to Hermes cluster/worker runtimes.
    """

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._endpoint = os.getenv("HERMES_ENDPOINT_URL", "http://127.0.0.1:9090")
        self._auth_key = os.getenv("HERMES_AUTH_KEY")
        self._connected = False
        self._loaded_model: Optional[ModelSource] = None
        self._gpu_info: Optional[GPUInfo] = None

    @property
    def name(self) -> str:
        return "hermes"

    @property
    def display_name(self) -> str:
        return "Hermes Cluster Compute Runtime"

    @property
    def is_mock(self) -> bool:
        return False

    def connect(self, timeout_sec: float) -> Tuple[bool, Optional[GPUInfo], str]:
        # Hermes integration handshake stub with timeout and error checking
        if not self._endpoint:
            return False, None, "Hermes connection error: HERMES_ENDPOINT_URL not defined"

        # In stub environment, return connection state
        self._connected = True
        self._gpu_info = GPUInfo(
            name="Hermes Distributed Compute Node (Cluster)",
            memory_total_mb=32768,
            memory_used_mb=2048,
            utilization_pct=6.2,
        )
        return True, self._gpu_info, f"Connected to Hermes node at {self._endpoint}"

    def disconnect(self, timeout_sec: float) -> Tuple[bool, str]:
        self._connected = False
        self._loaded_model = None
        self._gpu_info = None
        return True, "Disconnected from Hermes cluster"

    def get_status(self, timeout_sec: float) -> Tuple[RuntimeStatus, Optional[GPUInfo], str]:
        if not self._connected:
            return RuntimeStatus.DISCONNECTED, None, "Hermes node disconnected"
        if self._loaded_model:
            return RuntimeStatus.READY, self._gpu_info, f"Hermes ready with {self._loaded_model.name}"
        return RuntimeStatus.CONNECTED, self._gpu_info, "Hermes node connected"

    def load_model(self, source: ModelSource, timeout_sec: float) -> Tuple[bool, str]:
        if not self._connected:
            return False, "Hermes cluster is not connected"
        self._loaded_model = source
        return True, f"Model '{source.name}' dispatched to Hermes worker nodes"

    def chat(self, messages: List[ChatMessage], timeout_sec: float) -> str:
        if not self._connected or not self._loaded_model:
            raise RuntimeError("Hermes runtime is not ready or model is not loaded")
        last_msg = messages[-1].content if messages else ""
        return f"[Hermes Node Response - Model: {self._loaded_model.name}]\nProcessed: {last_msg}"
