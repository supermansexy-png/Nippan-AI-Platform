"""
Compute Console Core Service.
Coordinates compute runtime lifecycle, model storage, and test chat sessions.
Enforces strict state transitions, timeouts, and error handling.
"""

from __future__ import annotations

import datetime
import threading
from typing import Any, Dict, List, Optional, Tuple

from services.compute_console.adapters import COMPUTE_ADAPTERS, STORAGE_ADAPTERS
from services.compute_console.adapters.base import ComputeProviderAdapter, StorageProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ChatMessage, ConsoleState, GPUInfo, ModelSource, RuntimeStatus


class ComputeConsoleService:
    """Core stateful orchestrator for the internal Compute Console."""

    def __init__(
        self,
        config: Optional[ConsoleConfig] = None,
        compute_adapter: Optional[ComputeProviderAdapter] = None,
        storage_adapter: Optional[StorageProviderAdapter] = None,
    ):
        self._config = config or ConsoleConfig.load()
        self._lock = threading.RLock()

        # Initialize adapters
        provider_key = self._config.compute_provider.lower()
        if compute_adapter:
            self._compute = compute_adapter
        elif provider_key in COMPUTE_ADAPTERS:
            self._compute = COMPUTE_ADAPTERS[provider_key](self._config)
        else:
            # Fallback to mock adapter
            self._compute = COMPUTE_ADAPTERS["mock"](self._config)

        storage_key = self._config.storage_provider.lower()
        if storage_adapter:
            self._storage = storage_adapter
        elif storage_key in STORAGE_ADAPTERS:
            self._storage = STORAGE_ADAPTERS[storage_key](self._config)
        else:
            self._storage = STORAGE_ADAPTERS["gdrive"](self._config)

        # Internal state
        self._status = RuntimeStatus.DISCONNECTED
        self._status_message = "Runtime initialized. Click 'Connect Runtime' to start."
        self._gpu_info: Optional[GPUInfo] = None
        self._loaded_model: Optional[ModelSource] = None
        self._active_error: Optional[str] = None
        self._chat_history: List[ChatMessage] = []
        self._op_generation: int = 0

    @property
    def config(self) -> ConsoleConfig:
        return self._config

    @property
    def compute_adapter(self) -> ComputeProviderAdapter:
        return self._compute

    @property
    def storage_adapter(self) -> StorageProviderAdapter:
        return self._storage

    def get_state(self, live: bool = False) -> ConsoleState:
        """Return current console state. If live=True, re-poll the compute adapter."""
        if live:
            poll_gen: Optional[int] = None
            with self._lock:
                if self._status in (RuntimeStatus.CONNECTED, RuntimeStatus.READY):
                    poll_gen = self._op_generation

            if poll_gen is not None:
                try:
                    status, gpu, msg = self._compute.get_status(
                        timeout_sec=self._config.timeout_connect_sec
                    )
                    with self._lock:
                        # Guard against Race Condition A3:
                        # Discard stale poll if superseded by disconnect or state changed away from connected/ready
                        if poll_gen == self._op_generation and self._status in (RuntimeStatus.CONNECTED, RuntimeStatus.READY):
                            self._status = status
                            self._gpu_info = gpu
                            if status == RuntimeStatus.ERROR:
                                self._active_error = msg
                                self._status_message = f"Runtime error detected: {msg}"
                            elif msg:
                                self._status_message = msg
                except Exception as e:
                    with self._lock:
                        if poll_gen == self._op_generation and self._status in (RuntimeStatus.CONNECTED, RuntimeStatus.READY):
                            self._status = RuntimeStatus.ERROR
                            self._active_error = str(e)
                            self._status_message = f"Status poll failed: {str(e)}"

        with self._lock:
            return ConsoleState(
                status=self._status,
                status_message=self._status_message,
                active_provider=self._compute.name,
                active_storage=self._storage.name,
                adapter_tier=self._compute.adapter_tier,
                gpu_info=self._gpu_info,
                loaded_model=self._loaded_model,
                active_error=self._active_error,
            )

    def set_adapter(self, provider_name: str) -> Tuple[bool, str]:
        """Switch compute provider adapter dynamically (e.g. mock <-> colab)."""
        with self._lock:
            self._op_generation += 1
            key = provider_name.strip().lower()
            if key not in COMPUTE_ADAPTERS:
                return False, f"Unknown compute adapter '{provider_name}'. Available: {list(COMPUTE_ADAPTERS.keys())}"

            # Disconnect current if active
            if self._status != RuntimeStatus.DISCONNECTED:
                self.disconnect()

            self._compute = COMPUTE_ADAPTERS[key](self._config)
            self._status_message = f"Switched compute provider to '{self._compute.display_name}'."
            return True, self._status_message

    def connect(self) -> Tuple[bool, str]:
        """Initiate connection or reconnection to runtime."""
        with self._lock:
            self._op_generation += 1
            gen = self._op_generation
            self._status = RuntimeStatus.RECONNECTING
            self._status_message = f"Connecting to {self._compute.display_name}..."
            self._active_error = None

        # Execute connection outside lock to avoid blocking status queries
        try:
            ok, gpu, msg = self._compute.connect(timeout_sec=self._config.timeout_connect_sec)
            with self._lock:
                if gen != self._op_generation:
                    return False, "Connection superseded by a newer operation."
                if ok:
                    self._gpu_info = gpu
                    self._loaded_model = None
                    self._status = RuntimeStatus.CONNECTED
                    self._status_message = msg or f"Connected to {self._compute.display_name}"
                    return True, self._status_message
                else:
                    self._status = RuntimeStatus.ERROR
                    self._active_error = msg
                    self._status_message = f"Connection error: {msg}"
                    return False, self._status_message
        except Exception as e:
            with self._lock:
                if gen != self._op_generation:
                    return False, "Connection superseded by a newer operation."
                self._status = RuntimeStatus.ERROR
                self._active_error = str(e)
                self._status_message = f"Connection exception: {str(e)}"
                return False, self._status_message

    def disconnect(self) -> Tuple[bool, str]:
        """Disconnect and release runtime session. Returns adapter's actual result."""
        with self._lock:
            self._op_generation += 1
            try:
                ok, msg = self._compute.disconnect(timeout_sec=self._config.timeout_connect_sec)
            except Exception as e:
                ok, msg = False, str(e)

            if ok:
                self._status = RuntimeStatus.DISCONNECTED
                self._gpu_info = None
                self._loaded_model = None
                self._active_error = None
                self._status_message = msg or "Runtime disconnected."
                return True, self._status_message
            else:
                self._status = RuntimeStatus.ERROR
                self._active_error = f"Disconnect failed: {msg}"
                self._status_message = self._active_error
                return False, self._status_message

    def list_models(self) -> List[ModelSource]:
        """Discover model sources available in active storage (e.g. Google Drive)."""
        try:
            return self._storage.list_models(timeout_sec=self._config.timeout_connect_sec)
        except Exception as e:
            with self._lock:
                self._active_error = f"Storage list error: {str(e)}"
            return []

    def load_model(self, model_identifier: str) -> Tuple[bool, str]:
        """Load selected model into runtime memory."""
        with self._lock:
            if self._status in (RuntimeStatus.DISCONNECTED, RuntimeStatus.RECONNECTING):
                return False, "Cannot load model: Runtime is not connected. Connect first."

            self._op_generation += 1
            gen = self._op_generation
            self._status = RuntimeStatus.LOADING
            self._status_message = f"Loading model '{model_identifier}'..."
            self._active_error = None

        # Resolve model source
        models = self.list_models()
        target_source: Optional[ModelSource] = None
        for m in models:
            if model_identifier in (m.id, m.name, m.path):
                target_source = m
                break

        if not target_source:
            # Create ad-hoc ModelSource if user typed direct path
            target_source = ModelSource(
                id="custom-source",
                name=model_identifier.split("/")[-1],
                path=model_identifier,
                size_mb=4000,
                format="GGUF",
            )

        # Validate storage path
        valid, val_msg = self._storage.validate_source(target_source.path, timeout_sec=self._config.timeout_load_sec)
        if not valid:
            with self._lock:
                if gen != self._op_generation:
                    return False, "Load superseded by a newer operation."
                self._status = RuntimeStatus.ERROR
                self._active_error = f"Storage validation failed: {val_msg}"
                self._status_message = self._active_error
                return False, self._active_error

        # Dispatch load to compute runtime
        try:
            ok, msg = self._compute.load_model(target_source, timeout_sec=self._config.timeout_load_sec)
            with self._lock:
                if gen != self._op_generation:
                    return False, "Load superseded by a newer operation."
                if ok:
                    self._loaded_model = target_source
                    self._status = RuntimeStatus.READY
                    self._status_message = msg or f"Model '{target_source.name}' ready for inference."
                    # Refresh GPU stats
                    _, gpu, _ = self._compute.get_status(timeout_sec=self._config.timeout_connect_sec)
                    if gpu:
                        self._gpu_info = gpu
                    return True, self._status_message
                else:
                    self._status = RuntimeStatus.ERROR
                    self._active_error = msg
                    self._status_message = f"Model load failed: {msg}"
                    return False, self._status_message
        except Exception as e:
            with self._lock:
                if gen != self._op_generation:
                    return False, "Load superseded by a newer operation."
                self._status = RuntimeStatus.ERROR
                self._active_error = str(e)
                self._status_message = f"Model load exception: {str(e)}"
                return False, self._status_message

    def chat(self, user_text: str) -> Tuple[bool, str]:
        """Test chat with the currently loaded model."""
        with self._lock:
            if self._status != RuntimeStatus.READY:
                return False, f"Chat unavailable: Runtime status is '{self._status.value}' (must be 'ready')"
            if not self._loaded_model:
                return False, "Chat unavailable: No model loaded"

            if not user_text or not user_text.strip():
                return False, "Message content cannot be empty"

            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            user_msg = ChatMessage(role="user", content=user_text.strip(), timestamp=now_str)
            self._chat_history.append(user_msg)
            # Create a snapshot of history to send
            history_copy = list(self._chat_history)

        try:
            assistant_reply = self._compute.chat(history_copy, timeout_sec=self._config.timeout_chat_sec)
            reply_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            bot_msg = ChatMessage(role="assistant", content=assistant_reply, timestamp=reply_time)
            with self._lock:
                self._chat_history.append(bot_msg)
            return True, assistant_reply
        except TimeoutError as te:
            with self._lock:
                self._active_error = f"Inference timed out: {str(te)}"
            return False, f"Inference timed out after {self._config.timeout_chat_sec:.1f}s"
        except Exception as e:
            with self._lock:
                self._active_error = f"Inference error: {str(e)}"
            return False, f"Inference error: {str(e)}"

    def get_chat_history(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [m.to_dict() for m in self._chat_history]

    def clear_chat_history(self) -> None:
        with self._lock:
            self._chat_history.clear()
