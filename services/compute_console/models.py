"""
Data structures and Enums for Nippan AI Compute Console MVP.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class RuntimeStatus(str, Enum):
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    CONNECTED = "connected"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"


@dataclass
class GPUInfo:
    name: str
    memory_total_mb: int
    memory_used_mb: int
    utilization_pct: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ModelSource:
    id: str
    name: str
    path: str
    size_mb: int
    format: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConsoleState:
    status: RuntimeStatus
    status_message: str
    active_provider: str
    active_storage: str
    gpu_info: Optional[GPUInfo] = None
    loaded_model: Optional[ModelSource] = None
    active_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "status_message": self.status_message,
            "active_provider": self.active_provider,
            "active_storage": self.active_storage,
            "gpu_info": self.gpu_info.to_dict() if self.gpu_info else None,
            "loaded_model": self.loaded_model.to_dict() if self.loaded_model else None,
            "active_error": self.active_error,
        }
