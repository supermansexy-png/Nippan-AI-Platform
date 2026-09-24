from __future__ import annotations

from .interfaces import CorrelationContext, RoomFailureHistorySource
from .service import RoomSession


class RoomSessionFailureReconstructor:
    """Restores durable automatic-failure caps into a newly built RoomSession."""

    def __init__(self, source: RoomFailureHistorySource) -> None:
        self._source = source

    async def restore(
        self,
        session: RoomSession,
        *,
        correlation: CorrelationContext,
    ) -> RoomSession:
        failed = await self._source.load_failed_participant_ids(
            correlation=correlation,
        )
        session.failed_participant_ids.update(failed)
        return session
