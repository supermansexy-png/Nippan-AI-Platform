"""
Compute and Storage Adapters registry for Nippan AI Compute Console.
"""

from typing import Dict, Type

from services.compute_console.adapters.base import ComputeProviderAdapter, StorageProviderAdapter
from services.compute_console.adapters.colab import ColabComputeAdapter
from services.compute_console.adapters.gdrive_storage import GoogleDriveStorageAdapter
from services.compute_console.adapters.hermes import HermesComputeAdapter
from services.compute_console.adapters.mock import MockComputeAdapter
from services.compute_console.adapters.nas_storage import NASStorageAdapter
from services.compute_console.adapters.ollama import OllamaComputeAdapter

COMPUTE_ADAPTERS: Dict[str, Type[ComputeProviderAdapter]] = {
    "mock": MockComputeAdapter,
    "colab": ColabComputeAdapter,
    "hermes": HermesComputeAdapter,
    "ollama": OllamaComputeAdapter,
}

STORAGE_ADAPTERS: Dict[str, Type[StorageProviderAdapter]] = {
    "gdrive": GoogleDriveStorageAdapter,
    "nas": NASStorageAdapter,
}

__all__ = [
    "ComputeProviderAdapter",
    "StorageProviderAdapter",
    "MockComputeAdapter",
    "ColabComputeAdapter",
    "HermesComputeAdapter",
    "OllamaComputeAdapter",
    "GoogleDriveStorageAdapter",
    "NASStorageAdapter",
    "COMPUTE_ADAPTERS",
    "STORAGE_ADAPTERS",
]
