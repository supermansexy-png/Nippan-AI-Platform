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


# Catalog used ONLY in development mode when no real mount is available.
# In production/test mode, discovery must come from a real filesystem or backend.
MOCK_CATALOG: List[ModelSource] = [
    ModelSource(
        id="gdrive-model-01",
        name="openthaigpt-1.5-7b-instruct.gguf",
        path="gdrive:/models/openthaigpt-1.5-7b-instruct.gguf",
        size_mb=4370,
        format="GGUF_Q4_K_M",
    ),
    ModelSource(
        id="gdrive-model-02",
        name="typhoon-v1.5-8b-instruct.gguf",
        path="gdrive:/models/typhoon-v1.5-8b-instruct.gguf",
        size_mb=4920,
        format="GGUF_Q4_K_M",
    ),
    ModelSource(
        id="gdrive-model-03",
        name="sea-lion-7b-instruct.gguf",
        path="gdrive:/models/sea-lion-7b-instruct.gguf",
        size_mb=4100,
        format="GGUF_Q4_K_M",
    ),
    ModelSource(
        id="gdrive-model-04",
        name="custom-finetuned-support-8b.safetensors",
        path="gdrive:/models/custom-finetuned-support-8b.safetensors",
        size_mb=8200,
        format="SafeTensors_FP16",
    ),
]


class GoogleDriveStorageAdapter(StorageProviderAdapter):
    """Storage adapter scanning Google Drive mount or catalog paths."""

    def __init__(self, config: ConsoleConfig):
        self._config = config
        self._root_path = config.gdrive_models_path
        self._is_dev_catalog = config.env == "development" and self._root_path.startswith("gdrive:")

    @property
    def name(self) -> str:
        return "gdrive"

    @property
    def display_name(self) -> str:
        return "Google Drive Model Storage"

    def list_models(self, timeout_sec: float) -> List[ModelSource]:
        """List models found in Google Drive storage.

        Resolution order:
        1. If root_path is a real local directory → scan it (may return empty).
        2. If development mode with gdrive: URI → return catalog for testing.
        3. Otherwise (live/production) → return empty list (no fabrication).
        """
        # Try real filesystem scan first
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
                return discovered

        # Development catalog — only in dev mode with virtual gdrive: path
        if self._is_dev_catalog:
            return list(MOCK_CATALOG)

        # Live/production: no real mount found, return empty (do NOT fabricate)
        return []

    def validate_source(self, path: str, timeout_sec: float) -> Tuple[bool, str]:
        """Validate if model path is supported and actually accessible.

        In live mode, gdrive: URIs are rejected unless a runtime can confirm existence.
        In development mode, catalog entries are accepted for testing convenience.
        """
        if not path or not path.strip():
            return False, "Model path cannot be empty"

        clean = path.strip()

        # Virtual gdrive: URI — only acceptable in development catalog mode
        if clean.startswith("gdrive:"):
            if self._is_dev_catalog:
                for m in MOCK_CATALOG:
                    if clean in (m.name, m.path, m.id):
                        return True, f"Valid development catalog entry: {m.path}"
                return False, f"Path not in development catalog: {clean}"
            return False, f"Cannot verify virtual gdrive: path without live runtime: {clean}"

        # Real filesystem check
        if os.path.exists(clean):
            return True, f"Found verified file on mounted storage: {clean}"

        # Development catalog fallback for non-gdrive paths matching catalog names
        if self._is_dev_catalog:
            for m in MOCK_CATALOG:
                if clean in (m.name, m.path, m.id):
                    return True, f"Valid development catalog entry: {m.path}"

        return False, f"Model file not found on storage: {clean}"
