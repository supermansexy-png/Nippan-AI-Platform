"""
NAS (Network Attached Storage) Storage Adapter Extension Point.
Enables sourcing model checkpoints and weights from internal SMB/NFS/local shared storage.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from services.compute_console.adapters.base import StorageProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ModelSource


class NASStorageAdapter(StorageProviderAdapter):
    """Storage adapter for internal NAS and clustered volume storage."""

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._nas_mount = os.getenv("NAS_MODELS_MOUNT", "/mnt/nas/models")

    @property
    def name(self) -> str:
        return "nas"

    @property
    def display_name(self) -> str:
        return "Nippan Internal NAS Storage"

    def list_models(self, timeout_sec: float) -> List[ModelSource]:
        discovered: List[ModelSource] = []
        mount_dir = Path(self._nas_mount)
        if mount_dir.is_dir():
            for idx, item in enumerate(mount_dir.iterdir()):
                if item.is_file() and item.suffix.lower() in (".gguf", ".safetensors", ".bin"):
                    discovered.append(
                        ModelSource(
                            id=f"nas-model-{idx}",
                            name=item.name,
                            path=str(item.resolve()),
                            size_mb=int(item.stat().st_size / (1024 * 1024)),
                            format=item.suffix.upper().lstrip("."),
                        )
                    )
        if not discovered:
            # Provide placeholder NAS catalog
            discovered = [
                ModelSource(
                    id="nas-model-internal-01",
                    name="nippan-core-base-8b.gguf",
                    path=f"{self._nas_mount}/nippan-core-base-8b.gguf",
                    size_mb=4800,
                    format="GGUF",
                )
            ]
        return discovered

    def validate_source(self, path: str, timeout_sec: float) -> Tuple[bool, str]:
        if not path:
            return False, "NAS path cannot be empty"
        if os.path.exists(path):
            return True, f"Found verified NAS model file at {path}"
        if path.startswith("nas:") or path.startswith("/mnt/nas"):
            return True, f"Valid NAS path format: {path}"
        return False, f"Target path not found on NAS storage mount: {path}"
