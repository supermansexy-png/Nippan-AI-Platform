"""T-079c PART A security tests: A1 SSRF gate (A1 table), A3 filename
sanitization, A4 bounded store. Runs offline — resolver is the real OS
resolver for ``localhost`` only; other hosts are textual-IP rejects."""

import httpx
import pytest

from app.onboarding.cost_bounds import (
    DomainError,
    UnsafeUrlError,
    validate_fetch_url,
    check_redirect_target,
)
from app.onboarding.page import create_onboarding_router
from app.onboarding.page.handlers import sanitize_filename

OWN = "shop.example"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


# ── A1 — unit: table of URLs that MUST now be rejected ──
@pytest.mark.parametrize("url", [
    "http://169.254.169.254/latest/meta-data/",
    "http://localhost:8080/",
    "http://127.0.0.1:9000/",
    "http://10.0.0.5/",
    "http://172.16.5.4/",
    "http://192.168.1.1/",
    "http://0.0.0.0/",
    "http://[::1]/",
    "http://[fc00::1]/",
    "http://[::ffff:10.0.0.5]/",
    "http://2130706433/",          # decimal-encoded 127.0.0.1
    "http://0x7f.0.0.1/",          # we still fall through to DNS — resolver
    "file:///etc/passwd",
    "ftp://shop.example/menu",
    "http://evil.example/menu",
])
def test_a1_urls_rejected(url: str) -> None:
    with pytest.raises((UnsafeUrlError, DomainError, ValueError)):
        validate_fetch_url(url, f"http://{OWN}")


def test_a1_localhost_rejected_via_resolved_ip() -> None:
    # localhost DOES resolve offline → the resolved-IP check must catch it
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url("http://localhost/x", f"http://{OWN}")


def test_a1_own_site_url_still_accepted() -> None:
    # a legitimate own-site URL whose DNS resolves to a PUBLIC address
    # is still ACCEPTED (over-blocking is also a finding)
    validate_fetch_url(f"http://{OWN}/menu", f"http://{OWN}",
                       resolve=lambda host: ["93.184.216.34"])


def test_a1_resolved_private_ip_rejected() -> None:
    # own-domain hostname that DNS points at an internal IP
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(f"http://{OWN}/menu", f"http://{OWN}",
                           resolve=lambda host: ["10.0.0.5"])


def test_a1_resolver_failure_fail_closed() -> None:
    # T-079c C: the OLD code returned (fail-open) on OSError — now an
    # unresolvable/erroring host must be REJECTED, never allowed through.
    def boom(host):
        raise OSError("dns unavailable")

    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(f"http://{OWN}/menu", f"http://{OWN}",
                           resolve=boom)


def test_a1_redirect_hook_revalidates() -> None:
    with pytest.raises((UnsafeUrlError, DomainError, ValueError)):
        check_redirect_target("http://169.254.169.254/latest/meta-data/",
                              f"http://{OWN}")


# ── A1 router-level tests continue in test_onboarding_page_security2.py
from app.onboarding.page.store import OnboardingPageStore  # noqa: E402
