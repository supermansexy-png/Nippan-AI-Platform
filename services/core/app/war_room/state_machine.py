from __future__ import annotations

from enum import StrEnum

from .contracts import RoomState


class InvalidRoomTransition(ValueError):
    """Raised when a room action is not allowed from the current state."""


class RoomAction(StrEnum):
    PREPARE = "PREPARE"
    START = "START"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    REQUEST_OWNER_DECISION = "REQUEST_OWNER_DECISION"
    RESOLVE_OWNER_DECISION = "RESOLVE_OWNER_DECISION"
    BEGIN_SUMMARY = "BEGIN_SUMMARY"
    CLOSE = "CLOSE"
    STOP = "STOP"


_TRANSITIONS: dict[tuple[RoomState, RoomAction], RoomState] = {
    (RoomState.DRAFT, RoomAction.PREPARE): RoomState.READY,
    (RoomState.READY, RoomAction.START): RoomState.RUNNING,
    (RoomState.RUNNING, RoomAction.PAUSE): RoomState.PAUSED,
    (RoomState.PAUSED, RoomAction.RESUME): RoomState.RUNNING,
    (
        RoomState.RUNNING,
        RoomAction.REQUEST_OWNER_DECISION,
    ): RoomState.NEEDS_OWNER_DECISION,
    (
        RoomState.NEEDS_OWNER_DECISION,
        RoomAction.RESOLVE_OWNER_DECISION,
    ): RoomState.RUNNING,
    (RoomState.RUNNING, RoomAction.BEGIN_SUMMARY): RoomState.SUMMARIZING,
    (RoomState.SUMMARIZING, RoomAction.CLOSE): RoomState.CLOSED,
}

_TERMINAL_STATES = {RoomState.CLOSED, RoomState.STOPPED}


def transition_room_state(current: RoomState, action: RoomAction) -> RoomState:
    if action is RoomAction.STOP and current not in _TERMINAL_STATES:
        return RoomState.STOPPED

    try:
        return _TRANSITIONS[(current, action)]
    except KeyError as exc:
        raise InvalidRoomTransition(
            f"action {action.value} is not allowed from state {current.value}"
        ) from exc
