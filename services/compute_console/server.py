"""
HTTP Server and REST API for Nippan AI Compute Console MVP.
Uses Python standard library (http.server) for zero third-party dependencies.
"""

from __future__ import annotations

import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional
from urllib.parse import urlparse

from services.compute_console.adapters import COMPUTE_ADAPTERS, STORAGE_ADAPTERS
from services.compute_console.config import ConsoleConfig
from services.compute_console.service import ComputeConsoleService
from services.compute_console.ui import HTML_TEMPLATE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("compute_console")


class ComputeConsoleHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Compute Console API and Web UI."""

    service: ComputeConsoleService  # Injected by server

    def _send_json(self, status_code: int, data: dict) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self, html_content: str) -> None:
        payload = html_content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ("", "/index.html"):
            self._send_html(HTML_TEMPLATE)
            return

        if path == "/api/status":
            state = self.service.get_state(live=True)
            safe_config = self.service.config.to_safe_dict()
            if hasattr(self.server, "actual_port") and self.server.actual_port:
                safe_config["http_port"] = self.server.actual_port
            self._send_json(HTTPStatus.OK, {"ok": True, "state": state.to_dict(), "config": safe_config})
            return

        if path == "/api/models":
            models = self.service.list_models()
            self._send_json(HTTPStatus.OK, {"ok": True, "models": [m.to_dict() for m in models]})
            return

        if path == "/api/adapters":
            compute_list = [
                {
                    "id": k,
                    "display_name": cls(self.service.config).display_name,
                    "is_mock": cls(self.service.config).is_mock,
                    "tier": cls(self.service.config).adapter_tier,
                }
                for k, cls in COMPUTE_ADAPTERS.items()
            ]
            storage_list = [
                {"id": k, "display_name": cls(self.service.config).display_name}
                for k, cls in STORAGE_ADAPTERS.items()
            ]
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "compute_adapters": compute_list,
                    "storage_adapters": storage_list,
                    "active_compute": self.service.compute_adapter.name,
                    "active_storage": self.service.storage_adapter.name,
                    "active_tier": self.service.compute_adapter.adapter_tier,
                },
            )
            return

        if path == "/api/chat/history":
            history = self.service.get_chat_history()
            self._send_json(HTTPStatus.OK, {"ok": True, "history": history})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": f"Endpoint '{path}' not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/runtime/connect":
            ok, msg = self.service.connect()
            state = self.service.get_state()
            status_code = HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST
            self._send_json(status_code, {"ok": ok, "message": msg, "state": state.to_dict()})
            return

        if path == "/api/runtime/disconnect":
            ok, msg = self.service.disconnect()
            state = self.service.get_state()
            status_code = HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST
            self._send_json(status_code, {"ok": ok, "message": msg, "state": state.to_dict()})
            return

        if path == "/api/model/load":
            body = self._read_json_body()
            model_id = body.get("model_id", "").strip()
            if not model_id:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Missing 'model_id' in payload"})
                return

            ok, msg = self.service.load_model(model_id)
            state = self.service.get_state()
            status_code = HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST
            self._send_json(status_code, {"ok": ok, "message": msg, "state": state.to_dict()})
            return

        if path == "/api/chat":
            body = self._read_json_body()
            message = body.get("message", "").strip()
            if not message:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "Empty message"})
                return

            ok, result = self.service.chat(message)
            if ok:
                self._send_json(HTTPStatus.OK, {"ok": True, "reply": result, "history": self.service.get_chat_history()})
            else:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": result})
            return

        if path == "/api/chat/clear":
            self.service.clear_chat_history()
            self._send_json(HTTPStatus.OK, {"ok": True, "message": "Chat history cleared"})
            return

        if path == "/api/adapter/select":
            body = self._read_json_body()
            provider = body.get("provider", "").strip()
            ok, msg = self.service.set_adapter(provider)
            status_code = HTTPStatus.OK if ok else HTTPStatus.BAD_REQUEST
            self._send_json(status_code, {"ok": ok, "message": msg, "active_provider": self.service.compute_adapter.name})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": f"Endpoint '{path}' not found"})

    def log_message(self, format: str, *args) -> None:
        # Avoid cluttering console during automated tests
        logger.debug("%s - - [%s] %s", self.client_address[0], self.log_date_time_string(), format % args)


def create_server(
    host: Optional[str] = None, port: Optional[int] = None, service: Optional[ComputeConsoleService] = None
) -> ThreadingHTTPServer:
    srv_service = service or ComputeConsoleService()
    cfg = srv_service.config
    bind_host = host or cfg.http_host
    bind_port = port if port is not None else cfg.http_port

    class CustomHandler(ComputeConsoleHTTPHandler):
        pass

    CustomHandler.service = srv_service
    server = ThreadingHTTPServer((bind_host, bind_port), CustomHandler)
    server.daemon_threads = True
    server.actual_port = server.server_address[1]
    return server


def run():
    service = ComputeConsoleService()
    cfg = service.config
    server = create_server(service=service)
    logger.info("Nippan AI Compute Console starting on http://%s:%d", cfg.http_host, cfg.http_port)
    logger.info("Active Compute Provider: %s (is_mock=%s)", service.compute_adapter.name, service.compute_adapter.is_mock)
    logger.info("Active Storage Provider: %s", service.storage_adapter.name)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Compute Console...")
        server.server_close()


if __name__ == "__main__":
    run()
