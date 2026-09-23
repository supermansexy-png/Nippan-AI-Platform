from __future__ import annotations

import json
from uuid import UUID, uuid4

from app.db import Database

from .contracts import MessageType, RoomState
from .interfaces import CorrelationContext, OrderedRoomEvent, RoomEventDraft


class RoomPersistenceError(RuntimeError):
    """Raised when a durable War Room event cannot be committed."""


class RoomPersistenceConflict(RoomPersistenceError):
    """Raised when durable room state differs from the caller's expected state."""


class PostgresRoomEventSink:
    """Durable ordered event sink using the existing project_room_messages table.

    The room row is locked for every append so sequence allocation and optional
    room-state mutation are serialized per room. State mutation and event append
    share one database transaction.
    """

    def __init__(self, database: Database) -> None:
        self._database = database

    async def append(
        self,
        event: RoomEventDraft,
        *,
        expected_state: RoomState | None = None,
        new_state: RoomState | None = None,
    ) -> OrderedRoomEvent:
        if new_state is not None and expected_state is None:
            raise ValueError(
                "new_state requires expected_state"
            )

        correlation = event.correlation
        async with self._database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select state
                    from public.project_rooms
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    for update
                    """,
                    (
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.room_id,
                    ),
                )
                row = await cur.fetchone()
                if row is None:
                    raise RoomPersistenceError("room not found in durable scope")

                durable_state = RoomState(row[0])
                if expected_state is not None and durable_state is not expected_state:
                    raise RoomPersistenceConflict(
                        f"expected durable state {expected_state.value}, "
                        f"found {durable_state.value}"
                    )

                if new_state is not None:
                    await cur.execute(
                        """
                        update public.project_rooms
                        set state = %s,
                            updated_at = %s,
                            started_at = case
                              when %s = 'RUNNING' and started_at is null
                                then %s
                              else started_at
                            end,
                            closed_at = case
                              when %s in ('CLOSED', 'STOPPED')
                                then coalesce(closed_at, %s)
                              else null
                            end
                        where tenant_id = %s
                          and application_id = %s
                          and room_id = %s
                        """,
                        (
                            new_state.value,
                            event.occurred_at,
                            new_state.value,
                            event.occurred_at,
                            new_state.value,
                            event.occurred_at,
                            correlation.tenant_id,
                            correlation.application_id,
                            correlation.room_id,
                        ),
                    )

                await cur.execute(
                    """
                    select coalesce(max(sequence), 0) + 1
                    from public.project_room_messages
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    """,
                    (
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.room_id,
                    ),
                )
                sequence_row = await cur.fetchone()
                if sequence_row is None:
                    raise RoomPersistenceError("failed to allocate event sequence")
                sequence = int(sequence_row[0])

                message_id = uuid4()
                message_type = self._message_type(event)
                participant_id = self._participant_uuid(event.participant_id)
                round_number = self._round_number(event)
                content_reference = self._content_reference(event)
                content_text = self._encode_event(event)
                if len(content_text) > 32768:
                    raise RoomPersistenceError(
                        "durable event envelope exceeds project_room_messages limit"
                    )

                await cur.execute(
                    """
                    insert into public.project_room_messages (
                      message_id,
                      tenant_id,
                      application_id,
                      room_id,
                      agenda_item_id,
                      participant_id,
                      request_id,
                      message_type,
                      round_number,
                      sequence,
                      content_text,
                      content_reference,
                      created_at
                    ) values (
                      %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        message_id,
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.room_id,
                        correlation.agenda_item_id,
                        participant_id,
                        correlation.request_id,
                        message_type.value,
                        round_number,
                        sequence,
                        content_text,
                        content_reference,
                        event.occurred_at,
                    ),
                )

        return OrderedRoomEvent(
            event_id=message_id,
            sequence=sequence,
            event_type=event.event_type,
            correlation=event.correlation,
            occurred_at=event.occurred_at,
            room_state=event.room_state,
            participant_id=event.participant_id,
            message_type=event.message_type,
            halt_reason=event.halt_reason,
            payload=event.payload,
        )

    @staticmethod
    def _message_type(event: RoomEventDraft) -> MessageType:
        if event.message_type is not None:
            return event.message_type
        if event.event_type.value == "BUDGET_HARD_STOP":
            return MessageType.BUDGET_WARNING
        if event.event_type.value == "TURN_FAILED":
            return MessageType.ERROR
        return MessageType.SYSTEM_EVENT

    @staticmethod
    def _participant_uuid(participant_id: str | None) -> UUID | None:
        if participant_id is None:
            return None
        try:
            return UUID(participant_id)
        except ValueError as exc:
            raise RoomPersistenceError(
                "durable participant_id must be a UUID string"
            ) from exc

    @staticmethod
    def _round_number(event: RoomEventDraft) -> int | None:
        value = event.payload.get("round_number")
        if isinstance(value, int) and 1 <= value <= 2:
            return value
        return None

    @staticmethod
    def _content_reference(event: RoomEventDraft) -> str | None:
        value = event.payload.get("content_reference")
        if isinstance(value, str) and value.strip():
            return value
        return None

    @staticmethod
    def _encode_event(event: RoomEventDraft) -> str:
        envelope = {
            "event_type": event.event_type.value,
            "trace_id": event.correlation.trace_id,
            "room_state": (
                event.room_state.value if event.room_state is not None else None
            ),
            "participant_id": event.participant_id,
            "message_type": (
                event.message_type.value
                if event.message_type is not None
                else None
            ),
            "halt_reason": (
                event.halt_reason.value if event.halt_reason is not None else None
            ),
            "payload": event.payload,
        }
        return json.dumps(
            envelope,
            default=str,
            separators=(",", ":"),
            sort_keys=True,
        )



class PostgresRoomFailureHistorySource:
    """Restores automatic failure caps from durable TURN_FAILED events."""

    def __init__(self, database: Database) -> None:
        self._database = database

    async def load_failed_participant_ids(
        self,
        *,
        correlation: CorrelationContext,
    ) -> frozenset[str]:
        async with self._database.tenant_transaction(
            tenant_id=correlation.tenant_id,
            application_id=correlation.application_id,
            request_id=correlation.request_id,
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select participant_id, content_text
                    from public.project_room_messages
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                      and participant_id is not null
                      and message_type = 'ERROR'
                    order by sequence
                    """,
                    (
                        correlation.tenant_id,
                        correlation.application_id,
                        correlation.room_id,
                    ),
                )
                rows = await cur.fetchall()

        failed: set[str] = set()
        for participant_id, content_text in rows:
            try:
                envelope = json.loads(content_text)
            except (TypeError, json.JSONDecodeError) as exc:
                raise RoomPersistenceError(
                    "invalid durable ERROR event envelope"
                ) from exc

            if envelope.get("event_type") != "TURN_FAILED":
                continue
            if (
                envelope.get("halt_reason")
                != "PARTICIPANT_FAILURE_LIMIT_REACHED"
            ):
                continue

            failed.add(str(participant_id))

        return frozenset(failed)
