"""T-079c PART C regression tests — the six bypasses the reviewer proved
PLUS fail-closed/pinning/metadata/name/own-site rules. Every rejected
case is asserted BEFORE the fetch callable is invoked (the stub records
calls and must stay EMPTY). Offline only — no network, no secrets."""

import pytest

from app.onboarding.cost_bounds import (
    SiteNotEstablishedError,
    UnsafeUrlError,
    check_redirect_target,
    validate_fetch_url,
)
from app.onboarding.page.handlers import submit_url
from app.onboarding.page.store import OnboardingPageStore

OWN = "shop.example"
PUBLIC = "93.184.216.34"  # public unicast — the one address that stays OK

# The six reviewer bypasses + the classic blocklist, all REJECTED:
BYPASSES = [
    "http://2130706433/",                # decimal 127.0.0.1
    "http://0x7f000001/",                # hex 127.0.0.1
    "http://017700000001/",              # octal 127.0.0.1
    "http://127.1/",                     # short 127.0.0.1
    "http://2852039166/",                # decimal 169.254.169.254
    "http://metadata.google.internal/",  # metadata by name
    "http://metadata.goog/",
]


# ── gate level: bypass rejected even against ITS OWN origin (the old
#    tautological call), and the resolver is never even reached ──
@pytest.mark.parametrize("url", BYPASSES)
def test_c_bypass_rejected_at_gate(url: str) -> None:
    called = []

    def resolver(host):
        called.append(host)
        return [PUBLIC]

    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(url, url, resolve=resolver)
    assert called == []  # rejected BEFORE any resolution attempt


# ── fetch path level: the stub is NEVER invoked for a bypass ──
@pytest.mark.parametrize("url", BYPASSES + [
    "http://127.0.0.1/", "http://localhost/", "http://10.0.0.5/",
    "http://[::1]/", "file:///etc/passwd", "gopher://x",
])
def test_c_fetch_stub_not_called(url: str) -> None:
    calls = []

    def stub(u, connect_ip=None):
        calls.append(u)
        return "cat,10"

    def res(h):
        # DNS for "localhost" points at loopback — caught by the
        # resolved-address check; every other name resolves publicly
        return ["127.0.0.1"] if h == "localhost" else [PUBLIC]

    row = OnboardingPageStore().create(tenant_scope_id="t",
                                       site_origin=f"https://{OWN}")
    with pytest.raises((UnsafeUrlError, ValueError)):
        submit_url(row, url, fetch_fn=stub, resolve=res)
    assert calls == []


def test_c_own_site_still_accepted_and_pinned() -> None:
    calls = []

    def stub(u, connect_ip=None):
        calls.append((u, connect_ip))
        return "cat,10"

    row = OnboardingPageStore().create(tenant_scope_id="t",
                                       site_origin=f"https://{OWN}")
    submit_url(row, f"https://{OWN}/menu", fetch_fn=stub,
               resolve=lambda h: [PUBLIC])
    # pinned address flows to the fetch: origin URL + the validated IP
    assert calls == [(f"https://{OWN}", PUBLIC)]


def test_c_own_site_with_tautology_origin_still_rejected() -> None:
    # the decimal bypass submitted as "its own site" can never pass G
    row = OnboardingPageStore().create(
        tenant_scope_id="t", site_origin="http://2130706433")
    with pytest.raises(UnsafeUrlError):
        submit_url(row, "http://2130706433/",
                   fetch_fn=lambda u: "cat,10",
                   resolve=lambda h: [PUBLIC])


def test_c_no_known_site_fails_closed() -> None:
    row = OnboardingPageStore().create(tenant_scope_id="t")  # no site yet
    with pytest.raises(SiteNotEstablishedError):
        submit_url(row, f"https://{OWN}/menu",
                   fetch_fn=lambda u: "cat,10")


def test_c_resolver_failure_fail_closed() -> None:
    def boom(host):
        raise OSError("dns down")

    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(f"https://{OWN}/menu", f"https://{OWN}",
                           resolve=boom)


def test_c_empty_answer_fail_closed() -> None:
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(f"https://{OWN}/", f"https://{OWN}",
                           resolve=lambda h: [])


def test_c_link_local_via_dns_rejected() -> None:
    # metadata.google.internal resolving into link-local: blocked by name,
    # and even a renamed host resolving into 169.254/16 is blocked by range
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(f"https://{OWN}/", f"https://{OWN}",
                           resolve=lambda h: ["169.254.169.254"])


def test_c_cgnat_and_reserved_rejected() -> None:
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url(f"https://{OWN}/", f"https://{OWN}",
                           resolve=lambda h: ["100.64.1.1"])
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url("http://240.0.0.1/", "http://240.0.0.1")


def test_c_redirect_to_metadata_blocked() -> None:
    with pytest.raises(UnsafeUrlError):
        check_redirect_target("http://169.254.169.254/latest/meta-data/",
                              f"https://{OWN}", resolve=lambda h: [PUBLIC])


def test_c_off_site_rejected() -> None:
    with pytest.raises(UnsafeUrlError):
        validate_fetch_url("https://evil.example/", f"https://{OWN}",
                           resolve=lambda h: [PUBLIC])
