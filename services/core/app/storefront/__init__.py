"""Public storefront page (T-079f).

Server-rendered HTML only — no framework, no build step, in the same
style as ``app/onboarding/page/``. Honesty rule 2: no model/vendor name
anywhere (enforced by ``tests/test_storefront_page.py``).
"""

from .demo import StorefrontDemoService
from .render import render_storefront
from .router import create_storefront_router

__all__ = [
    "StorefrontDemoService",
    "render_storefront",
    "create_storefront_router",
]
