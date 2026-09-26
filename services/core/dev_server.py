"""Local dev launcher for the core API, with a Windows-safe event loop.

On Windows uvicorn >= 0.36 creates a Proactor event loop through
``uvicorn.loops.asyncio.asyncio_loop_factory``, bypassing the event-loop
policy, but psycopg's async pool refuses to run on Proactor ("Psycopg cannot
use the 'ProactorEventLoop' to run in async mode"), so every DB-backed route
hangs; on Linux (and in containers) uvicorn already picks a selector loop, so
this module only swaps the loop factory to ``asyncio.SelectorEventLoop`` on
``win32`` and leaves every other platform untouched. Everything else in this
module is a thin ``--host``/``--port`` CLI wrapper around
``uvicorn.run("app.main:app")``: same app, same uvicorn, no extra dependency.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

if sys.platform == "win32":
    import uvicorn.loops.asyncio as _uvicorn_asyncio_loop

    # The factory symbol only exists in uvicorn >= 0.36 (pyproject allows
    # >= 0.35,<1); on 0.35.x the patch below would silently no-op and the
    # psycopg ProactorEventLoop would hang every DB-backed route.
    if not hasattr(_uvicorn_asyncio_loop, "asyncio_loop_factory"):
        raise RuntimeError(
            "dev_server: uvicorn.loops.asyncio.asyncio_loop_factory is missing "
            "from the installed uvicorn (found "
            f"{getattr(__import__('uvicorn'), '__version__', 'unknown')}). "
            "uvicorn >= 0.36 is required on win32: without that symbol uvicorn "
            "creates a ProactorEventLoop and psycopg's async pool cannot run "
            "on it, so every DB-backed route hangs. Upgrade uvicorn."
        )

    _uvicorn_asyncio_loop.asyncio_loop_factory = (
        lambda use_subprocess=False: asyncio.SelectorEventLoop
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Nippan core API locally.")
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Bind host (default: HOST env or 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8000")),
        help="Bind port (default: PORT env or 8000).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if os.environ.get("HOST") and "--host" not in sys.argv:
        print(
            "dev_server: WARNING: using HOST from the environment "
            f"({args.host!r}); a value such as 0.0.0.0 exposes this dev "
            "server on every network interface.",
            file=sys.stderr,
        )

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
