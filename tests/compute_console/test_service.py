"""
Unit tests for ComputeConsoleService.
Tests state machine transitions: DISCONNECTED -> RECONNECTING -> CONNECTED -> LOADING -> READY -> ERROR,
chat restrictions (chat only permitted when READY), and error recovery.
"""

import unittest
from services.compute_console.config import ConsoleConfig
from services.compute_console.models import RuntimeStatus
from services.compute_console.service import ComputeConsoleService
from services.compute_console.adapters.mock import MockComputeAdapter


class TestComputeConsoleService(unittest.TestCase):
    def setUp(self):
        self.config = ConsoleConfig.load()
        object.__setattr__(self.config, "mock_simulate_latency_sec", 0.0)
        self.service = ComputeConsoleService(config=self.config)

    def test_initial_state(self):
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.DISCONNECTED)
        self.assertIsNone(state.gpu_info)
        self.assertIsNone(state.loaded_model)
        self.assertIsNone(state.active_error)

    def test_connect_and_disconnect_lifecycle(self):
        # Connect
        ok, msg = self.service.connect()
        self.assertTrue(ok)
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.CONNECTED)
        self.assertIsNotNone(state.gpu_info)
        self.assertIsNone(state.loaded_model)

        # Disconnect
        ok, msg = self.service.disconnect()
        self.assertTrue(ok)
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.DISCONNECTED)
        self.assertIsNone(state.gpu_info)

    def test_cannot_chat_when_not_ready(self):
        # When disconnected
        ok, reply = self.service.chat("Hello?")
        self.assertFalse(ok)
        self.assertIn("must be 'ready'", reply)

        # When connected but no model loaded
        self.service.connect()
        ok, reply = self.service.chat("Hello?")
        self.assertFalse(ok)
        self.assertIn("must be 'ready'", reply)

    def test_load_model_and_chat_success(self):
        self.service.connect()
        models = self.service.list_models()
        self.assertGreater(len(models), 0)

        # Load first model
        target_model = models[0]
        ok, msg = self.service.load_model(target_model.id)
        self.assertTrue(ok)

        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.READY)
        self.assertIsNotNone(state.loaded_model)
        self.assertEqual(state.loaded_model.id, target_model.id)

        # Chat works when READY
        ok, reply = self.service.chat("How are you?")
        self.assertTrue(ok)
        self.assertIn("Simulated Response", reply)

        history = self.service.get_chat_history()
        self.assertEqual(len(history), 2)  # 1 user + 1 assistant
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")

    def test_error_state_on_connect_failure(self):
        mock_adapter: MockComputeAdapter = self.service.compute_adapter
        mock_adapter.fail_next_connect = True

        ok, msg = self.service.connect()
        self.assertFalse(ok)
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.ERROR)
        self.assertIsNotNone(state.active_error)

        # Reconnect recovery
        ok, msg = self.service.connect()
        self.assertTrue(ok)
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.CONNECTED)

    def test_error_state_on_load_failure(self):
        self.service.connect()
        mock_adapter: MockComputeAdapter = self.service.compute_adapter
        mock_adapter.fail_next_load = True

        models = self.service.list_models()
        ok, msg = self.service.load_model(models[0].id)
        self.assertFalse(ok)
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.ERROR)
        self.assertIn("OOM", state.active_error)

    def test_switch_adapter(self):
        ok, msg = self.service.set_adapter("colab")
        self.assertTrue(ok)
        self.assertEqual(self.service.compute_adapter.name, "colab")

        # Switch to invalid adapter returns False
        ok, msg = self.service.set_adapter("nonexistent")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
