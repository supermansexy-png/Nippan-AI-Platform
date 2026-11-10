"""
Mock Compute Provider Adapter.
Simulates GPU allocation, latency, state transitions, and inference for local
development and test verification without live Colab credentials.
"""

from __future__ import annotations

import time
from typing import List, Optional, Tuple

from services.compute_console.adapters.base import ComputeProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ChatMessage, GPUInfo, ModelSource, RuntimeStatus


class MockComputeAdapter(ComputeProviderAdapter):
    """Local simulation adapter for Compute Console testing."""

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._latency = config.mock_simulate_latency_sec
        self._default_gpu_name = config.mock_default_gpu
        self._connected = False
        self._loaded_model: Optional[ModelSource] = None
        self._gpu_info: Optional[GPUInfo] = None

        # Fault injection toggles for automated testing
        self.fail_next_connect = False
        self.fail_next_load = False
        self.simulate_timeout = False

    @property
    def name(self) -> str:
        return "mock"

    @property
    def display_name(self) -> str:
        return "Mock Colab Runtime (Local Simulation)"

    @property
    def is_mock(self) -> bool:
        return True

    def connect(self, timeout_sec: float) -> Tuple[bool, Optional[GPUInfo], str]:
        if self.simulate_timeout:
            time.sleep(min(timeout_sec + 0.1, 0.5))
            return False, None, f"Mock runtime connection timed out after {timeout_sec:.1f}s"

        if self.fail_next_connect:
            self.fail_next_connect = False
            self._connected = False
            return False, None, "Mock runtime connection failed: Simulated kernel initialization error"

        if self._latency > 0:
            time.sleep(self._latency)

        self._connected = True
        self._gpu_info = GPUInfo(
            name=self._default_gpu_name,
            memory_total_mb=15360,  # 16 GB T4
            memory_used_mb=768,
            utilization_pct=3.5,
        )
        return True, self._gpu_info, "Connected to simulated Colab runtime environment"

    def disconnect(self, timeout_sec: float) -> Tuple[bool, str]:
        if self._latency > 0:
            time.sleep(self._latency / 2)
        self._connected = False
        self._loaded_model = None
        self._gpu_info = None
        return True, "Disconnected from simulated runtime"

    def get_status(self, timeout_sec: float) -> Tuple[RuntimeStatus, Optional[GPUInfo], str]:
        if not self._connected:
            return RuntimeStatus.DISCONNECTED, None, "Runtime is offline"

        if self._loaded_model:
            return (
                RuntimeStatus.READY,
                self._gpu_info,
                f"Simulated runtime ready with model '{self._loaded_model.name}'",
            )
        return RuntimeStatus.CONNECTED, self._gpu_info, "Simulated runtime connected (no model loaded)"

    def load_model(self, source: ModelSource, timeout_sec: float) -> Tuple[bool, str]:
        if not self._connected:
            return False, "Cannot load model: Runtime is disconnected"

        if self.simulate_timeout:
            time.sleep(min(timeout_sec + 0.1, 0.5))
            return False, f"Model loading timed out after {timeout_sec:.1f}s"

        if self.fail_next_load:
            self.fail_next_load = False
            return False, f"Mock load error: Unable to map tensor weights for {source.name} (Simulated OOM)"

        if self._latency > 0:
            time.sleep(self._latency)

        self._loaded_model = source
        # Update GPU memory usage based on model size
        if self._gpu_info:
            vram_added = min(source.size_mb, 14000)
            self._gpu_info.memory_used_mb = 768 + vram_added
            self._gpu_info.utilization_pct = round(min(100.0, (self._gpu_info.memory_used_mb / 15360) * 100), 1)

        return True, f"Model '{source.name}' loaded successfully into simulated VRAM"

    def chat(self, messages: List[ChatMessage], timeout_sec: float) -> str:
        if not self._connected or not self._loaded_model:
            raise RuntimeError("Runtime is not ready or model is not loaded")

        if self.simulate_timeout:
            time.sleep(min(timeout_sec + 0.1, 0.5))
            raise TimeoutError(f"Chat generation timed out after {timeout_sec:.1f}s")

        if self._latency > 0:
            time.sleep(self._latency / 2)

        last_user_msg = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_msg = m.content
                break

        # Standard simulated response adhering to platform policies (no vendor leaks)
        return (
            f"[Simulated Response from {self._loaded_model.name}]\n"
            f"Received: '{last_user_msg}'\n"
            f"VRAM Active: {self._gpu_info.memory_used_mb if self._gpu_info else 0} MB / 15360 MB. "
            f"Runtime status is stable."
        )
