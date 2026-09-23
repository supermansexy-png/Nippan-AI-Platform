from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from urllib.parse import urlsplit

from app.settings import Settings


SESSION_COOKIE_NAME = "__Secure-nippan_war_room_session"
CSRF_COOKIE_NAME = "__Secure-nippan_war_room_csrf"
CSRF_HEADER_NAME = "X-War-Room-CSRF"
SESSION_SCOPE = "war-room-preview"
_SESSION_VERSION = 1


@dataclass(frozen=True)
class PreviewSession:
    issued_at: int
    expires_at: int
    nonce: str
    csrf_token: str


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def canonical_remote_origin(settings: Settings) -> str | None:
    value = settings.war_room_preview_remote_origin
    if value is None:
        return None

    try:
        parsed = urlsplit(value.strip())
        port = parsed.port
    except ValueError:
        return None

    if parsed.scheme.lower() != "https":
        return None
    if not parsed.hostname or parsed.username or parsed.password:
        return None
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        return None

    host = parsed.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    if port not in {None, 443}:
        host = f"{host}:{port}"
    return f"https://{host}"


def remote_auth_configured(settings: Settings) -> bool:
    token = settings.war_room_preview_remote_auth_token
    return (
        settings.war_room_preview_remote_auth_enabled
        and token is not None
        and len(token) >= 32
        and canonical_remote_origin(settings) is not None
    )


def request_origin_allowed(origin: str | None, settings: Settings) -> bool:
    expected = canonical_remote_origin(settings)
    if expected is None or origin is None:
        return False

    probe = settings.model_copy(
        update={"war_room_preview_remote_origin": origin},
    )
    return canonical_remote_origin(probe) == expected


def access_token_matches(candidate: str, settings: Settings) -> bool:
    token = settings.war_room_preview_remote_auth_token
    if not remote_auth_configured(settings) or token is None:
        return False
    return hmac.compare_digest(candidate.encode("utf-8"), token.encode("utf-8"))


def _session_signing_key(settings: Settings) -> bytes | None:
    token = settings.war_room_preview_remote_auth_token
    if not remote_auth_configured(settings) or token is None:
        return None
    return hmac.new(
        token.encode("utf-8"),
        b"nippan-war-room-preview/session-signing-key/v1",
        hashlib.sha256,
    ).digest()


def issue_preview_session(
    settings: Settings,
    *,
    now: int | None = None,
) -> tuple[str, PreviewSession]:
    key = _session_signing_key(settings)
    if key is None:
        raise RuntimeError("War Room remote auth is not fully configured")

    issued_at = int(time.time() if now is None else now)
    expires_at = issued_at + settings.war_room_preview_remote_session_seconds
    session = PreviewSession(
        issued_at=issued_at,
        expires_at=expires_at,
        nonce=secrets.token_urlsafe(24),
        csrf_token=secrets.token_urlsafe(32),
    )
    payload = {
        "csrf": session.csrf_token,
        "exp": session.expires_at,
        "iat": session.issued_at,
        "nonce": session.nonce,
        "scope": SESSION_SCOPE,
        "v": _SESSION_VERSION,
    }
    body = _b64url_encode(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    signature = _b64url_encode(
        hmac.new(key, body.encode("ascii"), hashlib.sha256).digest()
    )
    return f"{body}.{signature}", session


def verify_preview_session(
    value: str | None,
    settings: Settings,
    *,
    now: int | None = None,
) -> PreviewSession | None:
    key = _session_signing_key(settings)
    if key is None or value is None:
        return None

    try:
        body, signature = value.split(".", 1)
        expected_signature = _b64url_encode(
            hmac.new(key, body.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected_signature):
            return None

        payload = json.loads(_b64url_decode(body))
        issued_at = int(payload["iat"])
        expires_at = int(payload["exp"])
        nonce = str(payload["nonce"])
        csrf_token = str(payload["csrf"])
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    current = int(time.time() if now is None else now)
    max_lifetime = settings.war_room_preview_remote_session_seconds

    if payload.get("v") != _SESSION_VERSION or payload.get("scope") != SESSION_SCOPE:
        return None
    if not nonce or len(nonce) < 16 or not csrf_token or len(csrf_token) < 24:
        return None
    if issued_at > current + 60:
        return None
    if expires_at <= current or expires_at < issued_at:
        return None
    if expires_at - issued_at > max_lifetime + 60:
        return None

    return PreviewSession(
        issued_at=issued_at,
        expires_at=expires_at,
        nonce=nonce,
        csrf_token=csrf_token,
    )


def csrf_matches(
    *,
    session: PreviewSession,
    cookie_value: str | None,
    header_value: str | None,
) -> bool:
    if cookie_value is None or header_value is None:
        return False
    return (
        hmac.compare_digest(cookie_value, session.csrf_token)
        and hmac.compare_digest(header_value, session.csrf_token)
    )


class PreviewLoginRateLimiter:
    def __init__(
        self,
        *,
        window_seconds: int = 300,
        per_client_limit: int = 8,
        global_limit: int = 100,
    ) -> None:
        self._window_seconds = window_seconds
        self._per_client_limit = per_client_limit
        self._global_limit = global_limit
        self._by_client: dict[str, deque[float]] = defaultdict(deque)
        self._global: deque[float] = deque()

    def _prune(self, queue: deque[float], now: float) -> None:
        cutoff = now - self._window_seconds
        while queue and queue[0] <= cutoff:
            queue.popleft()

    def allowed(self, client_key: str, *, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        client = self._by_client[client_key]
        self._prune(client, current)
        self._prune(self._global, current)
        return (
            len(client) < self._per_client_limit
            and len(self._global) < self._global_limit
        )

    def record_failure(self, client_key: str, *, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        self._by_client[client_key].append(current)
        self._global.append(current)

    def record_success(self, client_key: str) -> None:
        self._by_client.pop(client_key, None)
