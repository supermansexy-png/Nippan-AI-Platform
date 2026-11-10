"""
Base interfaces for Compute and Storage Providers in Nippan AI Platform.
Provides clean abstraction for Google Colab, Mock runtime, and future
extensions (Hermes, Ollama, NAS).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from services.compute_console.models import ChatMessage, GPUInfo, ModelSource, RuntimeStatus


class ComputeProviderAdapter(ABC):
    """Abstract interface for execution and compute runtimes."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'mock', 'colab', 'hermes', 'ollama')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """Indicates if this is a simulation adapter."""
        pass

    @property
    @abstractmethod
    def adapter_tier(self) -> str:
        """Adapter operational classification: 'simulation' | 'live' | 'stub'."""
        pass

    @abstractmethod
    def connect(self, timeout_sec: float) -> Tuple[bool, Optional[GPUInfo], str]:
        """
        Connect or reconnect to the compute runtime.
        Returns: (success, gpu_info, message)
        """
        pass

    @abstractmethod
    def disconnect(self, timeout_sec: float) -> Tuple[bool, str]:
        """
        Disconnect from compute runtime.
        Returns: (success, message)
        """
        pass

    @abstractmethod
    def get_status(self, timeout_sec: float) -> Tuple[RuntimeStatus, Optional[GPUInfo], str]:
        """
        Poll current runtime status and GPU allocation.
        Returns: (status, gpu_info, message)
        """
        pass

    @abstractmethod
    def load_model(self, source: ModelSource, timeout_sec: float) -> Tuple[bool, str]:
        """
        Load weights from specified model source into runtime memory.
        Returns: (success, message)
        """
        pass

    @abstractmethod
    def chat(self, messages: List[ChatMessage], timeout_sec: float) -> str:
        """
        Generate completion for conversation messages.
        Returns assistant reply text or raises RuntimeError/TimeoutError.
        """
        pass


class StorageProviderAdapter(ABC):
    """Abstract interface for model storage sources (Google Drive, NAS, etc.)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Storage identifier (e.g. 'gdrive', 'nas')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable storage name."""
        pass

    @abstractmethod
    def list_models(self, timeout_sec: float) -> List[ModelSource]:
        """
        List available model weights from storage.
        """
        pass

    @abstractmethod
    def validate_source(self, path: str, timeout_sec: float) -> Tuple[bool, str]:
        """
        Check if model path exists and is accessible.
        Returns: (valid, message)
        """
        pass
