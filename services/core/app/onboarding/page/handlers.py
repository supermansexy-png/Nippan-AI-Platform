"""Thin orchestration: delegates every rule to ``app/onboarding/``.

The handlers own NO menu, NO cost bound and NO ingestion logic — they only
pick the right existing call for the current missing field and map its
result/error to API-friendly shapes. Tenant isolation lives in
``store.py``; parsing lives in ``signals.py``; caps live in ``cost_bounds``.
"""

from __future__ import annotations

from ..assistant import LLMClient, OnboardingSession
from ..ingest import (
    FetchBudgetExhausted,
    FileReader,
    WebFetcher,
)
from ..cost_bounds import (
    MAX_FILE_BYTES,
    DomainError,
    SiteNotEstablishedError,
    UnsafeUrlError,
    normalize_site_url,
    validate_fetch_url,
    check_redirect_target,
)
from ..menus import UnmappedInputError
from .store import PageSession

from .store import OnboardingPageStore

__all__ = ["MAX_FILE_BYTES", "sanitize_filename", "start_session",
           "session_state", "apply_answer", "submit_url", "upload_file",
           "FetcherNotConfiguredError"]


class FetcherNotConfiguredError(RuntimeError):
    """``/website`` was reached without any fetcher wired at construction
    time — a handled state, not a code bug (B2, fail-closed)."""


def start_session(store: OnboardingPageStore, *, tenant_scope_id: str,
                  llm: LLMClient | None = None,
                  site_origin: str | None = None):
    row = store.create(tenant_scope_id=tenant_scope_id,
                       site_origin=site_origin)
    if llm is not None:
        row.session._llm = llm  # injectable assistant; stub allowed
    return state_of(row)


def state_of(row: PageSession) -> dict:
    return {
        "session_id": row.session_id,
        "tenant_scope_id": row.tenant_scope_id,
        "missing_fields": list(row.session.next_questions()),
        "draft": _draft_json(row),
        "done": row.done,
        "used_url": row.used_url,
        "used_file": row.used_file,
        "transcript": list(row.transcript),
    }


def _note(row: PageSession, role: str, text: str) -> None:
    row.transcript.append({"role": role, "text": text[:200]})


def sanitize_filename(raw: str) -> str:
    """A3 hardening: the uploaded filename is NEVER echoed/raw-stored.

    Keep a safe basename only: strip every path separator, drop control
    characters, and neutralize markup characters (``<>`` and quotes) so a
    name like ``<img src=x onerror=alert(1)>.csv`` cannot be stored as a
    stored-XSS payload in the transcript/JSON. The sanitization is
    RECORDED: the transcript shows the sanitized name plus a note that
    the name was rewritten, never silently dropped.
    """
    name = (raw or "").replace("\\", "/").split("/")[-1]
    name = "".join(ch for ch in name if ord(ch) >= 32 and ord(ch) != 127)
    for ch in "<>\"'`":
        name = name.replace(ch, "_")
    name = name.strip(". ")
    return name[:120] or "upload"


def apply_answer(row: PageSession, text: str) -> dict:
    """Feed ONE typed answer into the driver's FIRST missing field.

    Unmapped input raises ``UnmappedInputError`` → 400; nothing guessed.
    """
    text = (text or "").strip()
    if not text:
        raise UnmappedInputError("answer text is required")
    session: OnboardingSession = row.session
    missing = session.next_questions()
    if not missing:
        row.done = True
        raise UnmappedInputError("draft is already complete")
    field = missing[0]
    if field == "tone":
        if session.offer_tone_menu(text) is None:
            raise UnmappedInputError("tone not in the fixed menu (1-5)")
    elif field == "business_type":
        session.set_business_type(text)  # raises UnmappedInputError
    elif field == "business_name":
        session.set_business_name(text)  # raises ValueError if empty
    elif field == "opening_hours":
        session.set_opening_hours(text)  # raises UnmappedInputError
    elif field == "enabled_tools":
        session.set_enabled_tools(text)  # raises UnmappedInputError
    elif field == "fallback_contact":
        session.set_fallback_contact(text)  # raises ValueError if empty
    else:  # menu_categories — only via URL/file ingestion
        raise UnmappedInputError(
            "menu_categories must come from a website URL or uploaded file"
        )
    _note(row, "user", text)
    _note(row, "assistant", f"recorded {field}")
    return state_of(row)


def submit_url(row: PageSession, url: str, *, fetch_fn=None,
               resolve=None) -> dict:
    """Ingest the shop's own site (existing WebFetcher + bounded count).

    G (tautology fix): the EXPECTED site comes from the session's
    already-known ``site_origin`` (tenant/session config), NEVER from the
    submitted URL itself. A session with no known site yet raises
    ``SiteNotEstablishedError`` — fail-closed, nothing is accepted.

    SSRF-gated: ``validate_fetch_url`` runs BEFORE any bytes are fetched
    and returns the PINNED address the fetch must connect to (no second
    DNS lookup). Internal/cloud-metadata/unresolvable targets raise
    ``UnsafeUrlError`` (subclass of ``DomainError``) → 4xx, never a 500.
    Off-domain/malformed → DomainError/ValueError; budget → 429.

    Redirects (F): this ingest path does NOT follow redirects at all —
    disabled outright (fail-closed). If a real fetcher is ever wired to
    follow redirects, it MUST re-validate every redirect Location via
    ``check_redirect_target`` first, else keep redirects disabled.
    """
    expected = getattr(row, "site_origin", None)
    if not expected:
        raise SiteNotEstablishedError(
            "the session has no known site yet — establish the shop's "
            "site before URL ingestion (fail-closed)"
        )
    pinned = validate_fetch_url(url, expected, resolve=resolve)
    origin = normalize_site_url(url)
    fetcher = WebFetcher(site_origin=expected, fetch_fn=fetch_fn)
    if getattr(fetcher, "_fetch", None) is None:
        # B2 fail-closed: an unconfigured fetcher is a deliberate handled
        # state, never a TypeError escaping to a raw 500.
        raise FetcherNotConfiguredError(
            "WebFetcher was built without a fetch_fn — /website must be "
            "wired with web_fetch_fn at router construction"
        )
    # E: the fetch connects to the PINNED validated address — never a
    # second DNS answer. The dev stub ignores it (no network at all).
    page = fetcher.fetch_page(origin, connect_ip=pinned)
    row.session.set_menu_categories(extract_page_categories(page.text))
    row.used_url = True
    _note(row, "user", f"read site {origin}")
    _note(row, "assistant", "menu categories read from site")
    return state_of(row)


def extract_page_categories(text: str) -> list[str]:
    from ..signals import extract_categories_from_price_file

    return extract_categories_from_price_file(
        "\n".join(line.strip() for line in text.splitlines() if line.strip())
    )


def upload_file(row: PageSession, *, name: str, data: bytes,
                read_fn=None) -> dict:
    """Read an uploaded menu/price file through the EXISTING FileReader.

    Over-cap (``MAX_FILE_BYTES``) raises ``ValueError`` mapped to 413 by
    the router — the cap is the shared constant, not a new number.
    """
    from ..signals import extract_categories_from_price_file

    reader = FileReader(read_fn=read_fn)  # caps at MAX_FILE_BYTES itself
    try:
        blob = reader.read_file(name=name, data=data)
    except ValueError as exc:
        if len(data) > MAX_FILE_BYTES:
            row.done = True
        raise
    cats = extract_categories_from_price_file(blob.text)
    row.session.set_menu_categories(cats)  # raises if nothing valid
    row.used_file = True
    safe_name = sanitize_filename(name)
    if safe_name != (name or ""):
        _note(row, "assistant",
              "filename was rewritten to a safe form for storage")
    _note(row, "user", f"uploaded file {safe_name}")
    _note(row, "assistant", "categories read from file")
    return state_of(row)


def _draft_json(row: PageSession) -> dict:
    out: dict = {}
    for key, value in row.session.draft.to_row().items():
        if key.startswith("monthly_"):
            continue
        if value is None:
            out[key] = None
        elif hasattr(value, "value"):
            out[key] = value.value
        elif isinstance(value, dict):
            out[key] = value
        elif isinstance(value, tuple):
            out[key] = [v.value if hasattr(v, "value") else v for v in value]
        else:
            out[key] = value
    return out
