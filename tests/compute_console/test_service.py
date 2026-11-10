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
        self.assertEqual(self.service.get_state().adapter_tier, "live")

        # Switch to invalid adapter returns False
        ok, msg = self.service.set_adapter("nonexistent")
        self.assertFalse(ok)

    def test_set_adapter_aborts_and_preserves_provider_when_disconnect_fails(self):
        """If active provider disconnect returns False, set_adapter must abort and preserve original provider."""
        self.service.connect()
        self.assertEqual(self.service.get_state().status, RuntimeStatus.CONNECTED)
        original_provider_name = self.service.compute_adapter.name
        self.assertEqual(original_provider_name, "mock")

        # Inject disconnect failure on mock adapter
        mock_adapter: MockComputeAdapter = self.service.compute_adapter
        mock_adapter.fail_next_disconnect = True

        ok, msg = self.service.set_adapter("colab")
        self.assertFalse(ok)
        self.assertIn("Cannot switch provider to 'colab'", msg)
        self.assertIn("Failed to disconnect active provider 'mock'", msg)

        # Provider MUST NOT have changed
        self.assertEqual(self.service.compute_adapter.name, "mock")
        # State MUST be ERROR
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.ERROR)
        self.assertIsNotNone(state.active_error)
        self.assertIn("Cannot switch provider", state.active_error)

    def test_set_adapter_aborts_and_preserves_provider_when_disconnect_raises(self):
        """If active provider disconnect raises an exception, set_adapter must abort safely."""
        self.service.connect()
        self.assertEqual(self.service.get_state().status, RuntimeStatus.CONNECTED)

        def broken_disconnect(*args, **kwargs):
            raise ConnectionResetError("RPC pipe broken")

        self.service.compute_adapter.disconnect = broken_disconnect

        ok, msg = self.service.set_adapter("hermes")
        self.assertFalse(ok)
        self.assertIn("Cannot switch provider to 'hermes'", msg)
        self.assertEqual(self.service.compute_adapter.name, "mock")
        self.assertEqual(self.service.get_state().status, RuntimeStatus.ERROR)

    def test_race_condition_a3_stale_poll_cannot_overwrite_disconnected(self):
        """Race Condition A3: Stale status poll returning late must NOT overwrite DISCONNECTED state."""
        import time
        import threading

        self.service.connect()
        models = self.service.list_models()
        self.service.load_model(models[0].id)
        self.assertEqual(self.service.get_state().status, RuntimeStatus.READY)

        # Inject delay into compute_adapter.get_status to simulate slow network/kernel poll
        original_get_status = self.service.compute_adapter.get_status
        poll_started = threading.Event()

        def slow_get_status(timeout_sec):
            poll_started.set()
            time.sleep(0.05)
            return original_get_status(timeout_sec)

        self.service.compute_adapter.get_status = slow_get_status

        # Thread 1: Initiates live status poll
        poll_thread = threading.Thread(target=lambda: self.service.get_state(live=True))
        poll_thread.start()

        # Wait until poll has commenced
        poll_started.wait()

        # Thread 2 (Main): User triggers Disconnect while poll is in-flight
        ok, msg = self.service.disconnect()
        self.assertTrue(ok)
        self.assertEqual(self.service.get_state().status, RuntimeStatus.DISCONNECTED)

        # Wait for slow poll thread to finish
        poll_thread.join()

        # CRITICAL VERIFICATION: State MUST remain DISCONNECTED, never overwritten by late poll
        state_after = self.service.get_state()
        self.assertEqual(state_after.status, RuntimeStatus.DISCONNECTED)
        self.assertIsNone(state_after.gpu_info)
        self.assertIsNone(state_after.loaded_model)

    def test_disconnect_failure_sets_error_state_and_does_not_claim_disconnected(self):
        """Disconnect failure MUST NOT display as disconnected; it must transition to ERROR."""
        self.service.connect()
        self.assertEqual(self.service.get_state().status, RuntimeStatus.CONNECTED)

        # Inject failure into mock adapter disconnect
        mock_adapter: MockComputeAdapter = self.service.compute_adapter
        mock_adapter.fail_next_disconnect = True

        ok, msg = self.service.disconnect()
        self.assertFalse(ok)
        self.assertIn("Disconnect failed", msg)

        # Verify state is ERROR and active_error is set
        state = self.service.get_state()
        self.assertEqual(state.status, RuntimeStatus.ERROR)
        self.assertIsNotNone(state.active_error)
        self.assertIn("Disconnect failed", state.active_error)


if __name__ == "__main__":
    unittest.main()
