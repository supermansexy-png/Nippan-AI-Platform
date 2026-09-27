"""Ingestion — URL (`web-fetch`) and file (`file-reader`) with enforced cost
bounds. The network/file system are injectable so the flow runs fully
offline with stubs (no paid call, no internet required).
"""

from __future__ import annotations

import html
import inspect
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit, parse_qsl

from .cost_bounds import (
    MAX_FILE_BYTES,
    MAX_PAGES,
    MAX_PAGE_BYTES,
    DomainError,
    normalize_site_url,
    same_site,
)

__all__ = [
    "FetchBudgetExhausted",
    "WebPage",
    "FetchedFile",
    "WebFetcher",
    "FileReader",
]

_TAG_RE = re.compile(r"<(script|style)\b.*?</\1>", re.IGNORECASE | re.DOTALL)
_ANY_TAG_RE = re.compile(r"<[^>]+>")


class FetchBudgetExhausted(RuntimeError):
    """The bounded page count for this onboarding session is used up —
    the fetcher refuses further fetches (no full crawl, by design)."""


@dataclass(frozen=True)
class WebPage:
    url: str
    text: str

    @property
    def byte_size(self) -> int:
        return len(self.text.encode("utf-8"))


@dataclass(frozen=True)
class FetchedFile:
    name: str
    text: str

    @property
    def byte_size(self) -> int:
        return len(self.text.encode("utf-8"))


class WebFetcher:
    """Fetches pages on the shop's own site only, bounded count.

    ``fetch_fn`` is injectable: ``fetch_fn(url) -> str`` returns the page
    HTML. Tests/e2e supply a stub — no internet, no paid call.
    """

    def __init__(self, *, site_origin: str, fetch_fn=None, max_pages: int = MAX_PAGES) -> None:
        self._origin = normalize_site_url(site_origin)
        self._fetch = fetch_fn
        # E: does the wired fetch_fn accept the pinned-address argument?
        self._fetch_takes_ip = False
        if fetch_fn is not None:
            try:
                params = list(inspect.signature(fetch_fn).parameters.values())
                self._fetch_takes_ip = any(
                    p.name == "connect_ip" for p in params[1:]
                )
            except (TypeError, ValueError):
                self._fetch_takes_ip = False
        self._max_pages = max_pages
        self._fetched_count = 0

    @property
    def fetched_count(self) -> int:
        return self._fetched_count

    def fetch_page(self, url: str, *, connect_ip: str | None = None) -> WebPage:
        """Fetch ONE page on the shop's own domain, size-capped.

        ``connect_ip`` (E, T-079c): the PINNED address returned by
        ``validate_fetch_url``. A REAL fetch_fn must connect to THIS
        address and must not do a second DNS lookup (which could return
        a different, unchecked answer). The dev/test stub fetch_fn
        ignores it (no network at all) — documented contract, fail-closed
        by the gate upstream either way.

        Raises:
        - ``DomainError``: off-domain link — own-site-only rule.
        - ``FetchBudgetExhausted``: page budget (no full crawl) reached.
        - ``ValueError``: malformed URL.
        """
        if self._fetched_count >= self._max_pages:
            raise FetchBudgetExhausted(
                f"page budget {self._max_pages} exhausted — no full crawl"
            )
        if not same_site(url, self._origin):
            raise DomainError(f"off-domain link rejected: {url!r}")
        if self._fetch is None:
            # B2 fail-closed: an absent fetch function is a deliberate,
            # handled state — a clear error, never a TypeError.
            raise RuntimeError(
                "WebFetcher has no fetch_fn bound — ingestion is not "
                "configured in this deployment"
            )
        self._fetched_count += 1
        if connect_ip is not None and self._fetch_takes_ip:
            # E: a real fetch_fn gets the pinned address explicitly
            raw = self._fetch(url, connect_ip=connect_ip)
        else:
            raw = self._fetch(url)
        text = _html_to_text(raw[:MAX_PAGE_BYTES * 6])  # decode-side guard
        return WebPage(url=url, text=text[:MAX_PAGE_BYTES])


def _html_to_text(raw: str) -> str:
    raw = _TAG_RE.sub(" ", raw)
    raw = _ANY_TAG_RE.sub(" ", raw)
    raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw).strip()


def text_to_links(page_url: str, text: str, limit: int = 50) -> list[str]:
    """Extract same-domain links from fetched text so the driver can pull a
    menu page — bounded by ``limit``; still never a full crawl because the
    fetcher enforces ``MAX_PAGES`` regardless."""
    urls: list[str] = []
    for m in re.finditer(r"https?://[^\s)\"'<>]+", text):
        candidate = m.group(0)
        try:
            if same_site(candidate, page_url):
                # treat fragments only
                parts = urlsplit(candidate)
                query = dict(parse_qsl(parts.query))
                query.pop("utm_source", None)
                cleaned = parts._replace(fragment="").geturl()
                if cleaned not in urls:
                    urls.append(cleaned)
        except (ValueError, DomainError):
            continue
        if len(urls) >= limit:
            break
    return urls


class FileReader:
    """Reads an uploaded menu/price file into text.

    ``read_fn`` is injectable: ``read_fn(name, data: bytes) -> str``.
    Tests/e2e supply a stub. Size-capped at ``MAX_FILE_BYTES``; larger
    files are REJECTED, not truncated silently through the model.
    """

    def __init__(self, *, read_fn=None, max_bytes: int = MAX_FILE_BYTES) -> None:
        self._read = read_fn
        self._max = max_bytes

    def read_file(self, *, name: str, data: bytes) -> FetchedFile:
        if len(data) > self._max:
            raise ValueError(
                f"file {name!r} is {len(data)} bytes — over the "
                f"{self._max}-byte onboarding cap"
            )
        text = (self._read or (lambda n, d: d.decode("utf-8", errors="replace")))(name, data)
        return FetchedFile(name=name, text=text[:MAX_FILE_BYTES])
