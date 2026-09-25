from __future__ import annotations

import hashlib
import hmac
import time
from typing import Protocol
from urllib.parse import urlsplit

import httpx
import jwt
from jwt import InvalidSignatureError, InvalidTokenError

from app.settings import Settings


class AccessAuthenticationError(RuntimeError):
    """Raised when a remote preview request cannot be authenticated safely."""


class RemoteAccessVerifier(Protocol):
    async def authenticate(self, assertion: str) -> str:
        """Return the verified owner email or raise AccessAuthenticationError."""


class CloudflareAccessVerifier:
    def __init__(
        self,
        settings: Settings,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._client = client
        self._keys: dict[str, object] = {}
        self._keys_expires_at = 0.0

    def _config(self) -> tuple[str, str, str]:
        team_domain = (
            self._settings.cloudflare_access_team_domain or ""
        ).strip().rstrip("/")
        audience = (self._settings.cloudflare_access_audience or "").strip()
        owner_email = (
            self._settings.cloudflare_access_owner_email or ""
        ).strip().lower()

        parsed = urlsplit(team_domain)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise AccessAuthenticationError(
                "Cloudflare Access team domain must be an HTTPS origin"
            )
        if not audience or not owner_email:
            raise AccessAuthenticationError(
                "Cloudflare Access audience/owner email settings are incomplete"
            )
        return team_domain, audience, owner_email

    async def _fetch_keys(self, *, force: bool = False) -> dict[str, object]:
        now = time.monotonic()
        if not force and self._keys and now < self._keys_expires_at:
            return self._keys

        team_domain, _, _ = self._config()
        url = f"{team_domain}/cdn-cgi/access/certs"
        try:
            if self._client is not None:
                response = await self._client.get(url)
            else:
                async with httpx.AsyncClient(
                    timeout=5.0,
                    follow_redirects=False,
                ) as client:
                    response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise AccessAuthenticationError(
                "Cloudflare Access signing keys are unavailable"
            ) from exc

        raw_keys = payload.get("keys") if isinstance(payload, dict) else None
        if not isinstance(raw_keys, list) or not raw_keys:
            raise AccessAuthenticationError(
                "Cloudflare Access signing key set is invalid"
            )

        keys: dict[str, object] = {}
        try:
            for raw in raw_keys:
                if not isinstance(raw, dict):
                    continue
                kid = raw.get("kid")
                alg = raw.get("alg")
                if not isinstance(kid, str) or not kid:
                    continue
                if alg not in {None, "RS256"}:
                    continue
                keys[kid] = jwt.PyJWK.from_dict(raw).key
        except (InvalidTokenError, ValueError, TypeError) as exc:
            raise AccessAuthenticationError(
                "Cloudflare Access signing key set is invalid"
            ) from exc

        if not keys:
            raise AccessAuthenticationError(
                "Cloudflare Access signing key set contains no RS256 keys"
            )

        self._keys = keys
        self._keys_expires_at = (
            now + self._settings.cloudflare_access_jwks_ttl_seconds
        )
        return keys

    async def _key_for(self, kid: str, *, force: bool = False) -> object:
        keys = await self._fetch_keys(force=force)
        key = keys.get(kid)
        if key is None and not force:
            keys = await self._fetch_keys(force=True)
            key = keys.get(kid)
        if key is None:
            raise AccessAuthenticationError(
                "Cloudflare Access signing key is unknown"
            )
        return key

    def _decode(
        self,
        assertion: str,
        *,
        key: object,
        audience: str,
        issuer: str,
    ) -> dict[str, object]:
        try:
            payload = jwt.decode(
                assertion,
                key,
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer,
                options={
                    "require": ["exp", "iat", "iss", "aud"],
                },
            )
        except InvalidTokenError as exc:
            raise AccessAuthenticationError(
                "Cloudflare Access JWT validation failed"
            ) from exc
        if not isinstance(payload, dict):
            raise AccessAuthenticationError(
                "Cloudflare Access JWT payload is invalid"
            )
        return payload

    async def authenticate(self, assertion: str) -> str:
        token = assertion.strip()
        if not token:
            raise AccessAuthenticationError(
                "Cloudflare Access JWT assertion is missing"
            )

        team_domain, audience, owner_email = self._config()
        try:
            header = jwt.get_unverified_header(token)
        except InvalidTokenError as exc:
            raise AccessAuthenticationError(
                "Cloudflare Access JWT header is invalid"
            ) from exc

        if header.get("alg") != "RS256":
            raise AccessAuthenticationError(
                "Cloudflare Access JWT algorithm is not allowed"
            )
        kid = header.get("kid")
        if not isinstance(kid, str) or not kid:
            raise AccessAuthenticationError(
                "Cloudflare Access JWT key id is missing"
            )

        key = await self._key_for(kid)
        try:
            payload = self._decode(
                token,
                key=key,
                audience=audience,
                issuer=team_domain,
            )
        except AccessAuthenticationError as exc:
            if not isinstance(exc.__cause__, InvalidSignatureError):
                raise
            key = await self._key_for(kid, force=True)
            payload = self._decode(
                token,
                key=key,
                audience=audience,
                issuer=team_domain,
            )

        if payload.get("type") != "app":
            raise AccessAuthenticationError(
                "Cloudflare Access JWT is not an application token"
            )
        email = payload.get("email")
        if not isinstance(email, str) or email.strip().lower() != owner_email:
            raise AccessAuthenticationError(
                "Cloudflare Access identity is not the configured preview owner"
            )
        return owner_email


class ApiKeyValidationError(AccessAuthenticationError):
    """Raised when a dev-time API key validation fails."""


class DevApiKeyAuthenticator:
    """Validates Bearer-token API keys for War Room preview access.

    Uses SHA-256 hashing + hmac.compare_digest so the comparison is
    constant-time and does not leak timing side-channels.
    """

    def __init__(self, *, api_key: str | None) -> None:
        self._hashed_key: str | None
        if api_key is not None and api_key.strip():
            self._hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        else:
            self._hashed_key = None

    @property
    def enabled(self) -> bool:
        return self._hashed_key is not None

    def authenticate(self, bearer_token: str | None) -> bool:
        if not self.enabled:
            return False
        if bearer_token is None or not bearer_token.strip():
            raise ApiKeyValidationError(
                "dev-time API key header is missing"
            )
        candidate = hashlib.sha256(bearer_token.encode()).hexdigest()
        if not hmac.compare_digest(candidate, self._hashed_key):
            raise ApiKeyValidationError(
                "dev-time API key does not match"
            )
        return True
