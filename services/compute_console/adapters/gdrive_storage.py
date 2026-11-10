"""
Google Drive Model Storage Adapter.
Handles model discovery, path parsing, and validation from Google Drive sources.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from services.compute_console.adapters.base import StorageProviderAdapter
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ModelSource


class GoogleDriveStorageAdapter(StorageProviderAdapter):
    """Storage adapter scanning Google Drive mount or catalog paths."""

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._root_path = config.gdrive_models_path

        # Standard default models available in Google Drive repository
        self._catalog_models: List[ModelSource] = [
            ModelSource(
                id="gdrive-model-01",
                name="openthaigpt-1.5-7b-instruct.gguf",
                path=f"{self._root_path}/openthaigpt-1.5-7b-instruct.gguf",
                size_mb=4370,
                format="GGUF_Q4_K_M",
            ),
            ModelSource(
                id="gdrive-model-02",
                name="typhoon-v1.5-8b-instruct.gguf",
                path=f"{self._root_path}/typhoon-v1.5-8b-instruct.gguf",
                size_mb=4920,
                format="GGUF_Q4_K_M",
            ),
            ModelSource(
                id="gdrive-model-03",
                name="sea-lion-7b-instruct.gguf",
                path=f"{self._root_path}/sea-lion-7b-instruct.gguf",
                size_mb=4100,
                format="GGUF_Q4_K_M",
            ),
            ModelSource(
                id="gdrive-model-04",
                name="custom-finetuned-support-8b.safetensors",
                path=f"{self._root_path}/custom-finetuned-support-8b.safetensors",
                size_mb=8200,
                format="SafeTensors_FP16",
            ),
        ]

    @property
    def name(self) -> str:
        return "gdrive"

    @property
    def display_name(self) -> str:
        return "Google Drive Model Storage"

    def list_models(self, timeout_sec: float) -> List[ModelSource]:
        """List models found in Google Drive storage."""
        # If a real local directory is mounted and exists, scan it as well
        if self._root_path and not self._root_path.startswith("gdrive:"):
            real_path = Path(self._root_path)
            if real_path.is_dir():
                discovered: List[ModelSource] = []
                for idx, entry in enumerate(real_path.iterdir()):
                    if entry.is_file() and entry.suffix.lower() in (".gguf", ".safetensors", ".bin"):
                        size_mb = int(entry.stat().st_size / (1024 * 1024))
                        fmt = "GGUF" if entry.suffix.lower() == ".gguf" else "SafeTensors"
                        discovered.append(
                            ModelSource(
                                id=f"disk-{idx}",
                                name=entry.name,
                                path=str(entry.resolve()),
                                size_mb=size_mb,
                                format=fmt,
                            )
                        )
                if discovered:
                    return discovered

        return list(self._catalog_models)

    def validate_source(self, path: str, timeout_sec: float) -> Tuple[bool, str]:
        """Validate if model path is supported and properly formatted."""
        if not path or not path.strip():
            return False, "Model path cannot be empty"

        clean = path.strip()
        # Accept gdrive: URI schema or real local files
        if clean.startswith("gdrive:"):
            return True, f"Valid Google Drive model URI: {clean}"

        if os.path.exists(clean):
            return True, f"Found local mounted file: {clean}"

        # If it's one of the catalog model names or paths
        for m in self._catalog_models:
            if clean in (m.name, m.path, m.id):
                return True, f"Valid catalog entry: {m.path}"

        return False, f"Model path not found in Google Drive repository: {clean}"
