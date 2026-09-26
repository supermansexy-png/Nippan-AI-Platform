"""Guard: on win32, dev_server's patch must make uvicorn resolve a selector loop."""

from __future__ import annotations

import asyncio
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


@pytest.mark.skipif(sys.platform != "win32", reason="win32-only patch")
def test_uvicorn_resolves_selector_event_loop() -> None:
    import dev_server  # noqa: F401  (import applies the win32 loop patch)
    import uvicorn

    config = uvicorn.Config("app.main:app", loop="asyncio")
    assert config.get_loop_factory() is asyncio.SelectorEventLoop
