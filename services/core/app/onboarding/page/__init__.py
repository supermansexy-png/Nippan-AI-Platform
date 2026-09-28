"""Customer setup page (card T-079c).

A real page where a prospect sets up their bot by chatting, over web-chat.
It drives the EXISTING onboarding assistant — the menu rules, cost bounds
and ingestion there are the single implementation; this package is only
the HTTP surface that serves them.

Exports:
- ``PDPA_NOTICE``               the short consent notice, verbatim wording
- ``OnboardingPageStore``       per-session draft + progress store
- ``create_onboarding_router``  the FastAPI router to mount in ``app/main.py``
- ``DevEscapes``                OFF-by-default shell in-process dev escape
                                hatches (T-079c Part B — fail-closed identity)
"""

from .body_limit import BodyLimitMiddleware
from .router import (
    PDPA_NOTICE,
    PDPA_SAMPLE_MARKER,
    DevEscapes,
    OnboardingPageStore,
    create_onboarding_router,
)

__all__ = [
    "PDPA_NOTICE",
    "PDPA_SAMPLE_MARKER",
    "DevEscapes",
    "OnboardingPageStore",
    "create_onboarding_router",
    "BodyLimitMiddleware",
]
