"""
Integration tests for the Compute Console HTTP Server and REST API.
Verifies all REST endpoints against a live local server instance.
"""

import json
import threading
import unittest
import urllib.request
import urllib.error

from services.compute_console.config import ConsoleConfig
from services.compute_console.server import create_server
from services.compute_console.service import ComputeConsoleService


class TestComputeConsoleAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = ConsoleConfig.load()
        object.__setattr__(cls.config, "mock_simulate_latency_sec", 0.0)
        cls.service = ComputeConsoleService(config=cls.config)
        # Port 0 selects an arbitrary free port
        cls.server = create_server(host="127.0.0.1", port=0, service=cls.service)
        cls.port = cls.server.server_port
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path: str):
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as resp:
            status_code = resp.getcode()
            body = resp.read().decode("utf-8")
            return status_code, body

    def _post(self, path: str, data: dict = None):
        url = f"{self.base_url}{path}"
        payload = json.dumps(data or {}).encode("utf-8")
        req = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                status_code = resp.getcode()
                body = json.loads(resp.read().decode("utf-8"))
                return status_code, body
        except urllib.error.HTTPError as e:
            err_body = json.loads(e.read().decode("utf-8"))
            return e.code, err_body

    def test_get_root_html(self):
        code, body = self._get("/")
        self.assertEqual(code, 200)
        self.assertIn("Nippan AI Compute Console", body)
        self.assertIn("Model Test Chat", body)

    def test_full_console_api_flow(self):
        # 1. Check initial status
        code, body = self._get("/api/status")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertTrue(data["ok"])
        self.assertEqual(data["state"]["status"], "disconnected")

        # 2. Connect runtime
        code, data = self._post("/api/runtime/connect")
        self.assertEqual(code, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(data["state"]["status"], "connected")
        self.assertIsNotNone(data["state"]["gpu_info"])

        # 3. List models from Google Drive storage
        code, body = self._get("/api/models")
        self.assertEqual(code, 200)
        m_data = json.loads(body)
        self.assertTrue(m_data["ok"])
        self.assertGreater(len(m_data["models"]), 0)
        selected_model = m_data["models"][0]["id"]

        # 4. Load model
        code, data = self._post("/api/model/load", {"model_id": selected_model})
        self.assertEqual(code, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(data["state"]["status"], "ready")

        # 5. Send Chat
        code, data = self._post("/api/chat", {"message": "Hello from API test!"})
        self.assertEqual(code, 200)
        self.assertTrue(data["ok"])
        self.assertIn("Simulated Response", data["reply"])

        # 6. Verify chat history
        code, body = self._get("/api/chat/history")
        self.assertEqual(code, 200)
        h_data = json.loads(body)
        self.assertGreaterEqual(len(h_data["history"]), 2)

        # 7. Clear chat
        code, data = self._post("/api/chat/clear")
        self.assertEqual(code, 200)
        self.assertTrue(data["ok"])

        # 8. Check adapters list
        code, body = self._get("/api/adapters")
        self.assertEqual(code, 200)
        a_data = json.loads(body)
        self.assertTrue(a_data["ok"])
        self.assertIn("mock", [x["id"] for x in a_data["compute_adapters"]])
        self.assertIn("colab", [x["id"] for x in a_data["compute_adapters"]])
        self.assertIn("hermes", [x["id"] for x in a_data["compute_adapters"]])
        self.assertIn("ollama", [x["id"] for x in a_data["compute_adapters"]])

        # 9. Disconnect runtime
        code, data = self._post("/api/runtime/disconnect")
        self.assertEqual(code, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(data["state"]["status"], "disconnected")

    def test_api_chat_rejected_when_disconnected(self):
        # Disconnect first
        self._post("/api/runtime/disconnect")

        # Attempt chat
        code, data = self._post("/api/chat", {"message": "Are you there?"})
        self.assertEqual(code, 400)
        self.assertFalse(data["ok"])
        self.assertIn("must be 'ready'", data["error"])

    def test_api_invalid_endpoint(self):
        code, body = self._post("/api/unknown_endpoint")
        self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main()
