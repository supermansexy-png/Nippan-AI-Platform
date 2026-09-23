import base64
import time

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.settings import Settings
from app.war_room.remote_auth import (
    AccessAuthenticationError,
    CloudflareAccessVerifier,
)


TEAM_DOMAIN = "https://nippan-test.cloudflareaccess.com"
AUDIENCE = "war-room-preview-audience"
OWNER_EMAIL = "owner@example.com"
KID = "test-access-key"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _settings(**overrides) -> Settings:
    values = {
        "environment": "development",
        "war_room_preview_enabled": True,
        "war_room_preview_remote_access_enabled": True,
        "cloudflare_access_team_domain": TEAM_DOMAIN,
        "cloudflare_access_audience": AUDIENCE,
        "cloudflare_access_owner_email": OWNER_EMAIL,
        "cloudflare_access_jwks_ttl_seconds": 3600,
    }
    values.update(overrides)
    return Settings(**values)


def _b64uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _key_material():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    numbers = private_key.public_key().public_numbers()
    jwk = {
        "kty": "RSA",
        "kid": KID,
        "use": "sig",
        "alg": "RS256",
        "n": _b64uint(numbers.n),
        "e": _b64uint(numbers.e),
    }
    return private_key, jwk


def _token(
    private_key,
    *,
    audience: str = AUDIENCE,
    email: str = OWNER_EMAIL,
    issuer: str = TEAM_DOMAIN,
    token_type: str = "app",
    expires_in: int = 300,
    not_before_in: int = -1,
    kid: str = KID,
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "aud": [audience],
            "email": email,
            "exp": now + expires_in,
            "iat": now,
            "nbf": now + not_before_in,
            "iss": issuer,
            "type": token_type,
            "sub": "preview-owner-subject",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": kid, "typ": "JWT"},
    )


def _mock_client(jwk: dict[str, str]) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == (
            f"{TEAM_DOMAIN}/cdn-cgi/access/certs"
        )
        return httpx.Response(200, json={"keys": [jwk]})

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.mark.anyio
async def test_access_verifier_accepts_valid_owner_application_token() -> None:
    private_key, jwk = _key_material()
    async with _mock_client(jwk) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        email = await verifier.authenticate(_token(private_key))

    assert email == OWNER_EMAIL


@pytest.mark.anyio
async def test_access_verifier_rejects_wrong_audience_and_owner() -> None:
    private_key, jwk = _key_material()
    async with _mock_client(jwk) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)

        with pytest.raises(AccessAuthenticationError):
            await verifier.authenticate(
                _token(private_key, audience="other-app")
            )

        with pytest.raises(AccessAuthenticationError, match="preview owner"):
            await verifier.authenticate(
                _token(private_key, email="other@example.com")
            )


@pytest.mark.anyio
@pytest.mark.parametrize(
    "token_overrides",
    [
        {"issuer": "https://other.cloudflareaccess.com"},
        {"expires_in": -1},
        {"not_before_in": 300},
    ],
)
async def test_access_verifier_rejects_invalid_time_and_issuer_claims(
    token_overrides: dict[str, object],
) -> None:
    private_key, jwk = _key_material()
    async with _mock_client(jwk) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        with pytest.raises(AccessAuthenticationError, match="validation failed"):
            await verifier.authenticate(_token(private_key, **token_overrides))


@pytest.mark.anyio
async def test_access_verifier_rejects_non_app_token_and_incomplete_config() -> None:
    private_key, jwk = _key_material()
    async with _mock_client(jwk) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        with pytest.raises(AccessAuthenticationError, match="application token"):
            await verifier.authenticate(
                _token(private_key, token_type="org")
            )

    incomplete = CloudflareAccessVerifier(
        _settings(cloudflare_access_audience=None)
    )
    with pytest.raises(AccessAuthenticationError, match="incomplete"):
        await incomplete.authenticate("not-a-token")


@pytest.mark.anyio
async def test_access_verifier_rejects_malformed_and_invalid_signature() -> None:
    _, jwk = _key_material()
    untrusted_private_key, _ = _key_material()
    async with _mock_client(jwk) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        with pytest.raises(AccessAuthenticationError, match="header is invalid"):
            await verifier.authenticate("not-a-jwt")
        with pytest.raises(AccessAuthenticationError, match="validation failed"):
            await verifier.authenticate(_token(untrusted_private_key))


@pytest.mark.anyio
async def test_access_verifier_rejects_unknown_signing_key() -> None:
    private_key, jwk = _key_material()
    async with _mock_client(jwk) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        with pytest.raises(AccessAuthenticationError, match="key is unknown"):
            await verifier.authenticate(_token(private_key, kid="unknown-key"))


@pytest.mark.anyio
async def test_access_verifier_fails_closed_when_jwks_is_unavailable() -> None:
    private_key, _ = _key_material()

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        with pytest.raises(AccessAuthenticationError, match="unavailable"):
            await verifier.authenticate(_token(private_key))


@pytest.mark.anyio
async def test_access_verifier_fails_closed_when_jwks_refresh_fails() -> None:
    private_key, jwk = _key_material()
    requests = 0

    async def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        if requests == 1:
            return httpx.Response(200, json={"keys": [jwk]})
        return httpx.Response(503)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as client:
        verifier = CloudflareAccessVerifier(_settings(), client=client)
        with pytest.raises(AccessAuthenticationError, match="unavailable"):
            await verifier.authenticate(_token(private_key, kid="rotated-key"))

    assert requests == 2
