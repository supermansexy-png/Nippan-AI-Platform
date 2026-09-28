"""HTTP router for the public storefront page (T-079f).

GET ``/`` serves the server-rendered page. POST ``/demo/chat`` is the live
demo bot (Part 2): public and unauthenticated, answered by an injectable
``StorefrontDemoService`` with its OWN daily cap — no tenant data path.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .demo import StorefrontDemoService
from .render import render_storefront

__all__ = ["create_storefront_router"]


class DemoChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class DemoChatResponse(BaseModel):
    reply: str
    stopped: bool
    remaining: int | None


def create_storefront_router(
    demo_service: StorefrontDemoService | None = None,
) -> APIRouter:
    router = APIRouter(tags=["storefront"])

    @router.get("/", response_class=HTMLResponse)
    def storefront_page() -> HTMLResponse:
        """The public storefront: the six sections from STOREFRONT.md."""
        return HTMLResponse(
            content=render_storefront(),
            media_type="text/html; charset=utf-8",
        )

    if demo_service is not None:

        @router.post("/demo/chat", response_model=DemoChatResponse)
        def demo_chat(req: DemoChatRequest) -> DemoChatResponse:
            """One demo exchange; the cap is enforced inside the service."""
            result = demo_service.reply(req.text)
            return DemoChatResponse(
                reply=result.text,
                stopped=result.stopped,
                remaining=result.remaining,
            )

    return router
