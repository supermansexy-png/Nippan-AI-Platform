"""Fail-closed SSRF gate (T-079c PART C) — replaces the old fail-open
``validate_fetch_url``. NOTHING unvalidated reaches the fetch call site.

Checks, in order (every failure raises ``UnsafeUrlError`` → 4xx):

1. http/https only (``normalize_site_url`` rejects other schemes).
2. Same-site: the URL's origin must equal the EXPECTED site origin —
   the site the session/tenant config ALREADY knows, never the submitted
   URL itself (the old call compared the URL against itself: tautology).
3. Cloud-metadata hosts by name: ``metadata.google.internal``,
   ``metadata.goog``.
4. Host canonicalization BEFORE any decision: strip IPv6 brackets,
   lowercase, strip a trailing dot; any numeric-literal host in ANY
   notation (decimal ``2130706433``, hex ``0x7f000001``, octal
   ``017700000001``, short ``127.1``, mixed ``0x7f.0.0.1``) is converted
   via ``socket.inet_aton`` to a canonical ``ipaddress`` object; anything
   that is neither a canonical IP nor a syntactically valid DNS name is
   REJECTED — there is no "unparseable ⇒ treat as public" path anymore.
5. RESOLVE, then validate EVERY resolved address against loopback,
   link-local (169.254.0.0/16 metadata), private, CGNAT 100.64.0.0/10,
   reserved, multicast, unspecified, and IPv4-mapped/unique-local IPv6.
   ANY bad address in the answer ⇒ REJECT.
6. FAIL CLOSED: resolver raising (OSError/gaierror/anything), an empty
   answer, or a parse failure ⇒ REJECT. No ``return``-on-error path.

Pinning: ``validate_fetch_url`` RETURNS the validated address the fetch
must connect to. The fetch path must connect to THAT address and must
NOT do a second DNS lookup (which could return a different, unchecked
answer) — see ``WebFetcher.fetch_page(connect_ip=...)``.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlsplit

__all__ = [
    "DomainError", "UnsafeUrlError", "SiteNotEstablishedError",
    "METADATA_HOSTS", "normalize_site_url", "same_site",
    "validate_fetch_url", "check_redirect_target",
]


class DomainError(ValueError):
    """The link does not belong to the shop's own domain — REJECT."""


class UnsafeUrlError(DomainError):
    """SSRF surface: internal/private/metadata/unresolvable — REJECT."""


class SiteNotEstablishedError(DomainError):
    """The session has no known site yet — a URL cannot be validated
    against an unknown own-site, so it is REJECTED (fail-closed, G)."""


METADATA_HOSTS = frozenset({
    "metadata.google.internal",
    "metadata.goog",
})

_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_site_url(raw: str) -> str:
    """Return the origin (scheme://host) of a prospect's site link.

    Raises ``ValueError`` for a missing/malformed host and ``DomainError``
    for a non-http(s) scheme.
    """
    parts = urlsplit((raw or "").strip())
    if not parts.netloc:
        raise ValueError(f"URL has no host: {raw!r}")
    if parts.scheme not in ("http", "https"):
        raise DomainError(f"non-web scheme rejected: {raw!r}")
    return f"{parts.scheme}://{parts.netloc}"


def same_site(url: str, site_origin: str) -> bool:
    """True only when ``url`` is inside the shop's own site origin."""
    try:
        origin = normalize_site_url(url)
    except (ValueError, DomainError):
        return False
    return origin == normalize_site_url(site_origin)


def _ip_rejected(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        elif (int(ip) >> 112) & 0xFE00 == 0xFE00:  # fc00::/7 unique-local
            return True
    if isinstance(ip, ipaddress.IPv4Address) and ip in ipaddress.ip_network(
            "100.64.0.0/10"):  # CGNAT
        return True
    return (ip.is_loopback or ip.is_link_local or ip.is_private
            or ip.is_reserved or ip.is_multicast or ip.is_unspecified)


def _canonical_ip(host: str):
    """Canonical ``ipaddress`` object for ANY numeric notation, or None.

    Direct parse first; then BSD ``inet_aton`` semantics, which accept
    decimal (``2130706433``), hex (``0x7f000001``), octal
    (``017700000001``) and short (``127.1``) forms. None means "not an
    IP literal" — the caller then demands a valid DNS name instead.
    """
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        pass
    if host and (host[0].isdigit() or "x" in host or "X" in host):
        try:
            return ipaddress.ip_address(socket.inet_aton(host))
        except (OSError, ValueError):
            return None
    return None


def _checked_pinned(host: str, url: str, resolve) -> str:
    """Resolve ``host`` and validate EVERY answer; return the pinned addr.

    Fail closed: resolver error, empty answer, unparseable address, or
    any blocked address ⇒ ``UnsafeUrlError``.
    """
    try:
        addrs = resolve(host)
    except Exception as exc:  # fail closed — no exception may allow a fetch
        raise UnsafeUrlError(
            f"host {host!r} could not be resolved (fail-closed): "
            f"{type(exc).__name__}"
        ) from exc
    if not addrs:
        raise UnsafeUrlError(f"host {host!r} resolved to nothing (fail-closed)")
    pinned = None
    for raw in addrs:
        text = str(raw).strip("[]").rstrip(".").lower()
        ip = _canonical_ip(text)
        if ip is None or _ip_rejected(ip):
            raise UnsafeUrlError(
                f"host {host!r} resolves to internal address {raw!r}"
            )
        pinned = pinned or str(ip)
    return pinned


def validate_fetch_url(url: str, site_origin: str, *, resolve=None) -> str:
    """SSRF gate, run BEFORE any bytes are fetched.

    Returns the PINNED validated address: the caller's fetch path must
    connect to THIS address (no second DNS lookup). Raises
    ``UnsafeUrlError``/``DomainError``/``ValueError`` — never 500.
    """
    origin = normalize_site_url(url)  # raises before any fetch
    if origin != normalize_site_url(site_origin):
        raise UnsafeUrlError(f"off-site host rejected: {url!r}")
    host = (urlsplit(origin).hostname or "").rstrip(".").lower()
    if not host:
        raise UnsafeUrlError(f"URL has no host: {url!r}")
    if host in METADATA_HOSTS:
        raise UnsafeUrlError(f"cloud metadata endpoint rejected: {url!r}")
    literal = _canonical_ip(host)
    if literal is not None:
        if _ip_rejected(literal):
            raise UnsafeUrlError(f"internal address rejected: {url!r}")
        return str(literal)
    # Not an IP literal: must be a syntactically valid DNS name, then it
    # must resolve, and every resolved address must be safe (fail-closed).
    if len(host) > 253 or not all(_LABEL.match(label)
                                  for label in host.split(".")):
        raise UnsafeUrlError(f"unparseable host rejected: {url!r}")
    return _checked_pinned(host, url, resolve or _default_resolve)


def _default_resolve(host: str) -> list[str]:
    infos = socket.getaddrinfo(host, None)
    return [info[4][0] for info in infos]


def check_redirect_target(url: str, site_origin: str, *, resolve=None) -> str:
    """Re-validation for redirect targets — same gate, same fail-closed
    rules. A real fetcher MUST call this on every redirect Location
    before following it (and connect to the returned pinned address), or
    disable redirects entirely. Returns the pinned address.
    """
    return validate_fetch_url(url, site_origin, resolve=resolve)
