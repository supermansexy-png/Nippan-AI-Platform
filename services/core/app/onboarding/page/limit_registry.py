"""Shared helpers for the body-limit middleware (kept small on purpose)."""

from __future__ import annotations

__all__ = ["_413_BODY", "body_over_limit"]

# non-informative: no sizes, no paths, no module names
_413_BODY = b"request body too large"
_413_RESPONSE_START = {
    "type": "http.response.start",
    "status": 413,
    "headers": [(b"content-type", b"text/plain"),
                (b"content-length", str(len(_413_BODY)).encode())],
}


async def body_over_limit(send) -> None:
    """Emit the non-informative 413 through an ASGI send callable."""
    await send(_413_RESPONSE_START)
    await send({"type": "http.response.body", "body": _413_BODY})
