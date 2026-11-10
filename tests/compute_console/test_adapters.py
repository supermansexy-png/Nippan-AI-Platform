"""
Unit tests for Compute and Storage Adapters.
Tests mock adapter behavior, timeouts, error injection, Colab adapter timeout handling,
and Hermes/Ollama/NAS extension stubs.
"""

import unittest
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import ChatMessage, ModelSource, RuntimeStatus
from services.compute_console.adapters.mock import MockComputeAdapter
from services.compute_console.adapters.colab import ColabComputeAdapter
from services.compute_console.adapters.hermes import HermesComputeAdapter
from services.compute_console.adapters.ollama import OllamaComputeAdapter
from services.compute_console.adapters.gdrive_storage import GoogleDriveStorageAdapter
from services.compute_console.adapters.nas_storage import NASStorageAdapter
from services.compute_console.adapters import COMPUTE_ADAPTERS, STORAGE_ADAPTERS


class TestAdapters(unittest.TestCase):
    def setUp(self):
        self.config = ConsoleConfig.load()
        # Ensure fast test runs
        object.__setattr__(self.config, "mock_simulate_latency_sec", 0.0)

    def test_adapter_registry(self):
        self.assertIn("mock", COMPUTE_ADAPTERS)
        self.assertIn("colab", COMPUTE_ADAPTERS)
        self.assertIn("hermes", COMPUTE_ADAPTERS)
        self.assertIn("ollama", COMPUTE_ADAPTERS)
        self.assertIn("gdrive", STORAGE_ADAPTERS)
        self.assertIn("nas", STORAGE_ADAPTERS)

    def test_mock_adapter_lifecycle(self):
        adapter = MockComputeAdapter(self.config)
        self.assertTrue(adapter.is_mock)
        self.assertEqual(adapter.name, "mock")
        self.assertEqual(adapter.adapter_tier, "simulation")

        # Initial status
        status, gpu, msg = adapter.get_status(timeout_sec=1.0)
        self.assertEqual(status, RuntimeStatus.DISCONNECTED)
        self.assertIsNone(gpu)

        # Connect
        success, gpu_info, msg = adapter.connect(timeout_sec=1.0)
        self.assertTrue(success)
        self.assertIsNotNone(gpu_info)
        self.assertIn("Tesla T4", gpu_info.name)

        # Connected status
        status, gpu, msg = adapter.get_status(timeout_sec=1.0)
        self.assertEqual(status, RuntimeStatus.CONNECTED)

        # Load Model
        source = ModelSource(
            id="test-1",
            name="test-model.gguf",
            path="gdrive:/models/test-model.gguf",
            size_mb=4000,
            format="GGUF",
        )
        success, msg = adapter.load_model(source, timeout_sec=1.0)
        self.assertTrue(success)

        # Ready status
        status, gpu, msg = adapter.get_status(timeout_sec=1.0)
        self.assertEqual(status, RuntimeStatus.READY)
        self.assertGreater(gpu.memory_used_mb, 4000)

        # Chat
        messages = [ChatMessage(role="user", content="Hello test model", timestamp="2026-11-10T12:00:00Z")]
        reply = adapter.chat(messages, timeout_sec=1.0)
        self.assertIn("Hello test model", reply)
        self.assertIn("test-model.gguf", reply)

        # Disconnect
        success, msg = adapter.disconnect(timeout_sec=1.0)
        self.assertTrue(success)
        status, gpu, _ = adapter.get_status(timeout_sec=1.0)
        self.assertEqual(status, RuntimeStatus.DISCONNECTED)

    def test_mock_adapter_error_injection(self):
        adapter = MockComputeAdapter(self.config)

        # Test connect failure
        adapter.fail_next_connect = True
        success, gpu, msg = adapter.connect(timeout_sec=1.0)
        self.assertFalse(success)
        self.assertIn("Simulated kernel initialization error", msg)

        # Recover connect
        success, gpu, msg = adapter.connect(timeout_sec=1.0)
        self.assertTrue(success)

        # Test load failure
        adapter.fail_next_load = True
        source = ModelSource(id="m1", name="m.gguf", path="p", size_mb=100, format="GGUF")
        success, msg = adapter.load_model(source, timeout_sec=1.0)
        self.assertFalse(success)
        self.assertIn("Simulated OOM", msg)

        # Test disconnect failure
        adapter.fail_next_disconnect = True
        success, msg = adapter.disconnect(timeout_sec=1.0)
        self.assertFalse(success)
        self.assertIn("Simulated disconnect RPC failure", msg)

    def test_colab_adapter_without_endpoint_fails_gracefully(self):
        # When COLAB_ENDPOINT_URL is not set
        empty_colab_config = ConsoleConfig(
            env="test",
            compute_provider="colab",
            storage_provider="gdrive",
            http_host="127.0.0.1",
            http_port=8080,
            colab_endpoint_url=None,
            colab_auth_token=None,
            gdrive_models_path="gdrive:/models",
            timeout_connect_sec=1.0,
            timeout_load_sec=1.0,
            timeout_chat_sec=1.0,
            mock_simulate_latency_sec=0.0,
            mock_default_gpu="NVIDIA T4",
        )
        colab = ColabComputeAdapter(empty_colab_config)
        self.assertFalse(colab.is_mock)
        self.assertEqual(colab.name, "colab")

        success, gpu, err = colab.connect(timeout_sec=0.5)
        self.assertFalse(success)
        self.assertIn("COLAB_ENDPOINT_URL is not set", err)

        # Loading model when disconnected
        source = ModelSource(id="m1", name="m.gguf", path="p", size_mb=100, format="GGUF")
        success, err = colab.load_model(source, timeout_sec=0.5)
        self.assertFalse(success)
        self.assertIn("not connected", err)

        # Chat when disconnected raises RuntimeError
        with self.assertRaises(RuntimeError):
            colab.chat([ChatMessage("user", "hi", "t")], timeout_sec=0.5)

    def test_gdrive_storage_adapter(self):
        gdrive = GoogleDriveStorageAdapter(self.config)
        models = gdrive.list_models(timeout_sec=1.0)
        self.assertGreater(len(models), 0)
        first_model = models[0]
        self.assertTrue(first_model.name.endswith(".gguf") or first_model.name.endswith(".safetensors"))

        # Validation
        valid, msg = gdrive.validate_source(first_model.path, timeout_sec=1.0)
        self.assertTrue(valid)

        invalid, msg = gdrive.validate_source("invalid/path/none.bin", timeout_sec=1.0)
        self.assertFalse(invalid)

    def test_hermes_and_ollama_and_nas_extensions(self):
        hermes = HermesComputeAdapter(self.config)
        self.assertEqual(hermes.name, "hermes")
        self.assertEqual(hermes.adapter_tier, "stub")
        ok, gpu, msg = hermes.connect(timeout_sec=1.0)
        self.assertTrue(ok)
        self.assertIn("Hermes", gpu.name)

        ollama = OllamaComputeAdapter(self.config)
        self.assertEqual(ollama.name, "ollama")
        self.assertEqual(ollama.adapter_tier, "live")

        nas = NASStorageAdapter(self.config)
        self.assertEqual(nas.name, "nas")
        nas_models = nas.list_models(timeout_sec=1.0)
        self.assertGreater(len(nas_models), 0)


if __name__ == "__main__":
    unittest.main()
