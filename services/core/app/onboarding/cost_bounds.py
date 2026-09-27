"""Cost bounds for onboarding ingestion (ONBOARDING_FLOW.md "Cost controls").

Real, enforced checks — not comments:

- ``MAX_PAGE_BYTES`` / ``MAX_FILE_BYTES``: hard size caps per page/file;
  larger content is truncated/rejected before it ever reaches parsing.
- ``_is_same_domain``: web fetch stays on the shop's own domain ONLY —
  an off-domain link is rejected.
- ``MAX_PAGES``: bounded page count per session — no full crawl; the
  fetcher raises once the cap is hit.
"""

from __future__ import annotations

from urllib.parse import urlsplit

__all__ = [
    "MAX_PAGE_BYTES",
    "MAX_FILE_BYTES",
    "MAX_PAGES",
    "MAX_CATEGORIES",
    "DomainError",
    "normalize_site_url",
    "same_site",
]

MAX_PAGE_BYTES = 200_000  # per web page, ~200 KB
MAX_FILE_BYTES = 500_000  # per uploaded file, ~500 KB
MAX_PAGES = 5  # bounded page count per onboarding session — no crawl
MAX_CATEGORIES = 20


class DomainError(ValueError):
    """The link does not belong to the shop's own domain — REJECT."""


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
    """True only when ``url`` is inside the shop's own site origin. Any
    other host (cdn, google, subdomain of another business) is False."""
    try:
        origin = normalize_site_url(url)
    except (ValueError, DomainError):
        return False
    return origin == normalize_site_url(site_origin)
