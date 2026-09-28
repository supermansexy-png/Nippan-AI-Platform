from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config_repository import ConfigRepository
from .db import Database
from .preview_bootstrap import bootstrap_preview_database
from .onboarding.page import BodyLimitMiddleware, create_onboarding_router
from .storefront import create_storefront_router
from .storefront.demo import StorefrontDemoService
from .settings import get_settings
from .war_room.transport import (
    create_war_room_preview_router,
    preview_mount_allowed,
)

settings = get_settings()
database = Database(settings)
config_repository = ConfigRepository(database)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.war_room_preview_bootstrap:
        bootstrap_preview_database(settings)
    await database.open()
    try:
        yield
    finally:
        await database.close()


app = FastAPI(
    title="Nippan AI Platform Core",
    version="0.1.0",
    lifespan=lifespan,
)

if preview_mount_allowed(settings):
    app.include_router(
        create_war_room_preview_router(
            settings=settings,
            database=database,
        )
    )


# T-079c D3: the request-body cap applies at the middleware layer, BEFORE
# the multipart/JSON parser reads the body (see onboarding/page/body_limit).
app.add_middleware(BodyLimitMiddleware)

# Customer setup page sessions (T-079c Part 1): mounted fail-closed
# (Part B, finding B1) — with no server ``tenant_scope_id`` wired, the
# router refuses to serve onboarding data until the deployment binds a
# verified scope at wiring time. The dev escape stays OFF here.
app.include_router(create_onboarding_router())

# Public storefront page + live demo (T-079f). The demo answers on the
# cheapest model tier per MODEL_POLICY.md tier-by-task; its daily cap is
# the explicit setting ``storefront_demo_daily_cap`` (None = demo closed,
# fail-closed — no document defines the number yet). The LLM is injectable;
# no live model is wired in this process until deployment binds the
# roster's cheapest-tier pin.
app.include_router(
    create_storefront_router(
        demo_service=StorefrontDemoService(
            llm=None,
            daily_cap=settings.storefront_demo_daily_cap,
        )
    )
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "nippan-core",
        "environment": settings.environment,
    }


@app.get("/ready")
async def ready() -> dict[str, str]:
    if not database.configured:
        raise HTTPException(status_code=503, detail="database_not_configured")

    if not await database.ping():
        raise HTTPException(status_code=503, detail="database_unavailable")

    return {"status": "ready"}
