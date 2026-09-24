from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from .config_repository import ConfigRepository
from .db import Database
from .preview_bootstrap import bootstrap_preview_database
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
