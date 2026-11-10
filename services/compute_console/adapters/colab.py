"""
Google Colab Compute Provider Adapter.
Integrates with Google Colab runtimes via HTTP Kernel Gateway / Tunnel.
Enforces timeout and structured error handling.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from typing import List, Optional, Tuple

from services.compute_console.adapters.base import ComputeProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ChatMessage, GPUInfo, ModelSource, RuntimeStatus


class ColabComputeAdapter(ComputeProviderAdapter):
    """
    Adapter communicating with an active Google Colab runtime instance.
    Requires an endpoint URL (e.g. ngrok, Cloudflare tunnel, or Jupyter Kernel Gateway).
    """

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._endpoint = config.colab_endpoint_url
        self._token = config.colab_auth_token
        self._connected = False
        self._loaded_model: Optional[ModelSource] = None
        self._current_gpu: Optional[GPUInfo] = None

    @property
    def name(self) -> str:
        return "colab"

    @property
    def display_name(self) -> str:
        return "Google Colab Runtime (Remote)"

    @property
    def is_mock(self) -> bool:
        return False

    def _make_request(
        self, path: str, method: str = "GET", data: Optional[dict] = None, timeout_sec: float = 10.0
    ) -> Tuple[int, dict, str]:
        """Helper to execute HTTP requests to Colab runtime with timeout & error handling."""
        if not self._endpoint:
            return 0, {}, "Colab endpoint URL is not configured (check COLAB_ENDPOINT_URL in .env)"

        url = f"{self._endpoint.rstrip('/')}/{path.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "NippanAI-ComputeConsole/1.0",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None

        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                status_code = resp.getcode()
                raw = resp.read().decode("utf-8")
                try:
                    payload = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    payload = {"raw": raw}
                return status_code, payload, ""
        except urllib.error.HTTPError as e:
            err_msg = f"Colab HTTP Error {e.code}: {e.reason}"
            return e.code, {}, err_msg
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                return 408, {}, f"Colab request timed out after {timeout_sec:.1f}s"
            return 503, {}, f"Colab connection failed: {e.reason}"
        except socket.timeout:
            return 408, {}, f"Colab socket timed out after {timeout_sec:.1f}s"
        except Exception as e:
            return 500, {}, f"Colab unexpected communication error: {str(e)}"

    def connect(self, timeout_sec: float) -> Tuple[bool, Optional[GPUInfo], str]:
        """Establish or verify connection to Colab runtime."""
        if not self._endpoint:
            return False, None, "Colab connection failed: COLAB_ENDPOINT_URL is not set"

        status_code, payload, err = self._make_request("api/status", method="GET", timeout_sec=timeout_sec)
        if err or status_code not in (200, 201):
            self._connected = False
            return False, None, err or f"Colab returned status {status_code}"

        # Parse GPU info from runtime response if available
        gpu_data = payload.get("gpu", {})
        gpu_info = GPUInfo(
            name=gpu_data.get("name", "NVIDIA GPU (Colab Allocated)"),
            memory_total_mb=int(gpu_data.get("memory_total_mb", 15360)),
            memory_used_mb=int(gpu_data.get("memory_used_mb", 1024)),
            utilization_pct=float(gpu_data.get("utilization_pct", 5.0)),
        )
        self._current_gpu = gpu_info
        self._connected = True
        return True, gpu_info, f"Successfully connected to Colab runtime at {self._endpoint}"

    def disconnect(self, timeout_sec: float) -> Tuple[bool, str]:
        """Disconnect from Colab runtime session."""
        if self._endpoint and self._connected:
            self._make_request("api/disconnect", method="POST", timeout_sec=timeout_sec)
        self._connected = False
        self._loaded_model = None
        self._current_gpu = None
        return True, "Disconnected from Colab runtime"

    def get_status(self, timeout_sec: float) -> Tuple[RuntimeStatus, Optional[GPUInfo], str]:
        """Poll Colab status."""
        if not self._connected or not self._endpoint:
            return RuntimeStatus.DISCONNECTED, None, "Runtime disconnected"

        status_code, payload, err = self._make_request("api/status", method="GET", timeout_sec=timeout_sec)
        if err or status_code != 200:
            self._connected = False
            return RuntimeStatus.ERROR, None, f"Colab health check failed: {err}"

        if self._loaded_model:
            return RuntimeStatus.READY, self._current_gpu, f"Ready with model {self._loaded_model.name}"
        return RuntimeStatus.CONNECTED, self._current_gpu, "Connected to Colab runtime (no model loaded)"

    def load_model(self, source: ModelSource, timeout_sec: float) -> Tuple[bool, str]:
        """Load model weights on Colab instance."""
        if not self._connected:
            return False, "Cannot load model: Colab runtime is not connected"

        status_code, _, err = self._make_request(
            "api/model/load",
            method="POST",
            data={"model_path": source.path, "format": source.format},
            timeout_sec=timeout_sec,
        )
        if err or status_code != 200:
            return False, f"Failed to load model on Colab: {err}"

        self._loaded_model = source
        return True, f"Model '{source.name}' successfully loaded into Colab VRAM"

    def chat(self, messages: List[ChatMessage], timeout_sec: float) -> str:
        """Execute chat inference on Colab."""
        if not self._connected or not self._loaded_model:
            raise RuntimeError("Colab runtime is not connected or model is not loaded")

        payload_msgs = [msg.to_dict() for msg in messages]
        status_code, resp, err = self._make_request(
            "api/chat", method="POST", data={"messages": payload_msgs}, timeout_sec=timeout_sec
        )
        if err or status_code != 200:
            raise RuntimeError(f"Colab chat inference error: {err}")

        reply = resp.get("reply") or resp.get("content") or resp.get("response", "")
        return reply
