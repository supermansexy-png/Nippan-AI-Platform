"""Cost bounds for onboarding ingestion (ONBOARDING_FLOW.md "Cost controls").

Real, enforced checks — not comments:

- ``MAX_PAGE_BYTES`` / ``MAX_FILE_BYTES``: hard size caps per page/file;
  larger content is truncated/rejected before it ever reaches parsing.
- The SSRF gate (``validate_fetch_url`` / ``check_redirect_target``) now
  lives in ``app/onboarding/ssrf.py`` (T-079c PART C, fail-closed) and is
  re-exported here so every existing import keeps working.
- ``MAX_PAGES``: bounded page count per session — no full crawl; the
  fetcher raises once the cap is hit.
"""

from __future__ import annotations

# Re-exported from ssrf.py: the fail-closed SSRF gate and the URL/scheme
# helpers it owns. This module keeps only the numeric caps.
from .ssrf import (  # noqa: F401
    DomainError,
    SiteNotEstablishedError,
    UnsafeUrlError,
    check_redirect_target,
    normalize_site_url,
    same_site,
    validate_fetch_url,
)

__all__ = [
    "MAX_PAGE_BYTES",
    "MAX_FILE_BYTES",
    "MAX_PAGES",
    "MAX_CATEGORIES",
    "DomainError",
    "SiteNotEstablishedError",
    "UnsafeUrlError",
    "normalize_site_url",
    "same_site",
    "validate_fetch_url",
    "check_redirect_target",
]

MAX_PAGE_BYTES = 200_000  # per web page, ~200 KB
MAX_FILE_BYTES = 500_000  # per uploaded file, ~500 KB
MAX_PAGES = 5  # bounded page count per onboarding session — no crawl
MAX_CATEGORIES = 20
