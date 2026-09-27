"""uvicorn target for the real-server proof (kept separate so importing
it has no side effects for pytest collection under scripts/)."""

from __future__ import annotations

import sys
from pathlib import Path

CORE = Path(__file__).resolve().parent.parent
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from fastapi import FastAPI  # noqa: E402

from app.onboarding.page import BodyLimitMiddleware, create_onboarding_router  # noqa: E402

app = FastAPI()
app.add_middleware(BodyLimitMiddleware)
app.include_router(create_onboarding_router(
    store=__import__("app.onboarding.page", fromlist=["x"]).OnboardingPageStore(),
    tenant_scope_id="tenant-A",
    dev_escapes=__import__("app.onboarding.page", fromlist=["x"]).DevEscapes(
        unverified_scope_header=True),
    web_fetch_fn=(lambda u: "coffee,50\n"),
    site_origin="https://jea-ma.example",
    resolve_fn=(lambda h: ["93.184.216.34"]),
))
