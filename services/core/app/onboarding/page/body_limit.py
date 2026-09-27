"""T-079c Part E — request-body size limit AT THE MIDDLEWARE LAYER,
correct this time.

The first version wrapped ``starlette.requests.Request._receive`` on a
``BaseHTTPMiddleware``-produced Request wrapper. Starlette's multipart /
JSON parsers never got the original chunks through that wrapper, so
EVERY POST route broke with 400 "error parsing the body" — reproduced on
a real uvicorn server, not only ASGITransport.

This version is a PURE-ASGI middleware: it intercepts the raw
``http.request`` channel and passes every chunk through UNCHANGED to the
real app. Starlette sees exactly the original ASGI stream, so multipart
and JSON parsing are untouched. Two enforcement points:

1. an honest, over-cap ``Content-Length`` header is refused BEFORE the
   app runs (no route, no parser);
2. a chunked / lying-length body is cut MID-READ: the receive wrapper
   flags an over-cap chunk, and the send wrapper replaces the app's
   response with a clean, non-informative 413.

The limit relation (unchanged): ``MAX_BODY_BYTES = 2 x MAX_FILE_BYTES`` —
one allowed upload + multipart overhead (boundaries ~2x a 30-char
boundary, part headers, encoding slack). ``MAX_FILE_BYTES`` itself is
NOT touched.
"""

from __future__ import annotations

from ..cost_bounds import MAX_FILE_BYTES
from .limit_registry import _413_BODY

__all__ = ["MAX_BODY_BYTES", "BodyLimitMiddleware"]

# 2x the per-file cap — see module docstring. One max-size upload plus
# multipart overhead; never tighter than the route's own cap.
MAX_BODY_BYTES = MAX_FILE_BYTES * 2


class BodyLimitMiddleware:
    """Pure-ASGI request-body cap. Bounds what is READ, not just STORED."""

    def __init__(self, app, max_bytes: int = MAX_BODY_BYTES) -> None:
        self.app = app
        self._max = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 1. honest Content-Length: reject before anything runs.
        for name, value in scope.get("headers") or []:
            if name == b"content-length":
                if value.isdigit() and int(value) > self._max:
                    await _body_over_limit(send)
                    return
                break  # only the first Content-Length header counts

        # 2. bound the stream itself for chunked / lying-length bodies.
        # uvicorn (and any chunked encoding) delivers the body as MANY
        # messages of at most ~131 KiB each, so no single chunk ever
        # exceeds the cap. Only the CUMULATIVE total can reveal an
        # over-cap body — hence the running `seen` counter (T-079c G).
        over_limit = False
        seen = 0

        async def limited_receive():
            nonlocal over_limit, seen
            message = await receive()
            if message.get("type") == "http.request":
                seen += len(message.get("body", b""))
                if seen > self._max:
                    # strictly greater: a body of exactly the cap is allowed
                    over_limit = True
                    # stop the stream: hand the app an EMPTY, FINAL body so
                    # it cannot read the rest of the over-cap request
                    message = dict(message, body=b"", more_body=False)
            return message

        async def limited_send(message):
            # mid-read cut: the app saw a truncated body; replace its
            # response (whatever it was) with the clean 413
            if over_limit and message["type"] == "http.response.start":
                message = dict(message, status=413, headers=[
                    (b"content-type", b"text/plain"),
                    (b"content-length",
                     str(len(_413_BODY)).encode()),
                ])
            elif over_limit and message["type"] == "http.response.body":
                message = dict(
                    message,
                    body=b"" if message.get("more_body") else _413_BODY,
                )
            await send(message)

        await self.app(scope, limited_receive, limited_send)


async def _body_over_limit(send) -> None:
    from .limit_registry import body_over_limit  # local, avoids a cycle
    await body_over_limit(send)
