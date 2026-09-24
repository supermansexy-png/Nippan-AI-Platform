from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Callable
from uuid import UUID

from app.db import Database

from .contracts import HaltReason, MessageType, ParticipantRole, RoomMode, RoomState
from .interfaces import (
    CorrelationContext,
    OrderedRoomEvent,
    RoomAgendaSnapshot,
    RoomDecisionSnapshot,
    RoomEventType,
    RoomFindingSnapshot,
    RoomParticipantSnapshot,
    RoomSnapshot,
    RoomUsageSnapshot,
)


class RoomSnapshotError(RuntimeError):
    """Base error for fail-closed War Room snapshot projection."""


class RoomSnapshotNotFound(RoomSnapshotError):
    """Raised when the scoped room does not exist or is not visible."""


class RoomUsageProjectionError(RoomSnapshotError):
    """Raised when usage/cost evidence cannot be projected without guessing."""


class RoomEventProjectionError(RoomSnapshotError):
    """Raised when durable event evidence cannot satisfy the frozen wire contract."""


class PostgresRoomSnapshotSource:
    """Builds the frozen Track D RoomSnapshot from PostgreSQL sources of truth."""

    def __init__(
        self,
        database: Database,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._database = database
        self._clock = clock or (lambda: datetime.now(UTC))

    async def load_snapshot(
        self,
        *,
        tenant_id: UUID,
        application_id: UUID,
        room_id: UUID,
        recent_event_limit: int = 100,
    ) -> RoomSnapshot:
        if not 1 <= recent_event_limit <= 500:
            raise ValueError("recent_event_limit must be between 1 and 500")

        async with self._database.tenant_transaction(
            tenant_id=tenant_id,
            application_id=application_id,
        ) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    select mode, state
                    from public.project_rooms
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    """,
                    (tenant_id, application_id, room_id),
                )
                room_row = await cur.fetchone()
                if room_row is None:
                    raise RoomSnapshotNotFound("room not found in scoped read")

                await cur.execute(
                    """
                    select participant_id, role, display_name, active
                    from public.project_room_participants
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    order by created_at, participant_id
                    """,
                    (tenant_id, application_id, room_id),
                )
                participant_rows = await cur.fetchall()

                await cur.execute(
                    """
                    select agenda_item_id, sequence, title, objective, status, round_limit
                    from public.project_room_agenda_items
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    order by sequence
                    """,
                    (tenant_id, application_id, room_id),
                )
                agenda_rows = await cur.fetchall()

                await cur.execute(
                    """
                    select finding_id, severity, status, summary
                    from public.project_room_findings
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    order by created_at, finding_id
                    """,
                    (tenant_id, application_id, room_id),
                )
                finding_rows = await cur.fetchall()

                await cur.execute(
                    """
                    select decision_id, decision_type, status, decision,
                           owner_principal_id
                    from public.project_room_decisions
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    order by created_at, decision_id
                    """,
                    (tenant_id, application_id, room_id),
                )
                decision_rows = await cur.fetchall()

                await cur.execute(
                    """
                    select coalesce(max(sequence), 0)
                    from public.project_room_messages
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    """,
                    (tenant_id, application_id, room_id),
                )
                sequence_row = await cur.fetchone()
                last_sequence = int(sequence_row[0]) if sequence_row else 0

                await cur.execute(
                    """
                    select
                      message_id,
                      agenda_item_id,
                      participant_id,
                      request_id,
                      message_type,
                      sequence,
                      content_text,
                      created_at
                    from public.project_room_messages
                    where tenant_id = %s
                      and application_id = %s
                      and room_id = %s
                    order by sequence desc
                    limit %s
                    """,
                    (
                        tenant_id,
                        application_id,
                        room_id,
                        recent_event_limit,
                    ),
                )
                event_rows = await cur.fetchall()

                await cur.execute(
                    """
                    with room_requests as (
                      select distinct request_id
                      from public.project_room_messages
                      where tenant_id = %s
                        and application_id = %s
                        and room_id = %s
                        and request_id is not null
                    )
                    select
                      coalesce(sum(
                        case
                          when u.event_type = 'ai_tokens'
                           and u.unit = 'input_tokens'
                          then u.quantity else 0
                        end
                      ), 0),
                      coalesce(sum(
                        case
                          when u.event_type = 'ai_tokens'
                           and u.unit = 'output_tokens'
                          then u.quantity else 0
                        end
                      ), 0)
                    from public.usage_events u
                    join room_requests r on r.request_id = u.request_id
                    where u.tenant_id = %s
                      and u.application_id = %s
                    """,
                    (
                        tenant_id,
                        application_id,
                        room_id,
                        tenant_id,
                        application_id,
                    ),
                )
                token_row = await cur.fetchone()

                await cur.execute(
                    """
                    with room_requests as (
                      select distinct request_id
                      from public.project_room_messages
                      where tenant_id = %s
                        and application_id = %s
                        and room_id = %s
                        and request_id is not null
                    )
                    select
                      u.event_type,
                      u.unit,
                      u.currency,
                      sum(u.quantity),
                      sum(u.normalized_cost)
                    from public.usage_events u
                    join room_requests r on r.request_id = u.request_id
                    where u.tenant_id = %s
                      and u.application_id = %s
                      and u.event_type in ('ai_tokens', 'ai_cost')
                    group by u.event_type, u.unit, u.currency
                    order by u.event_type, u.unit, u.currency
                    """,
                    (
                        tenant_id,
                        application_id,
                        room_id,
                        tenant_id,
                        application_id,
                    ),
                )
                usage_rows = await cur.fetchall()

        if token_row is None:
            raise RoomUsageProjectionError("directional token query returned no row")
        input_tokens, output_tokens = token_row

        currencies = {
            row[2]
            for row in usage_rows
            if row[2] is not None
        }
        if len(currencies) > 1:
            raise RoomUsageProjectionError(
                "room usage contains multiple currencies"
            )

        cost_values = [
            Decimal(row[4])
            for row in usage_rows
            if row[0] == "ai_cost" and row[4] is not None
        ]
        normalized_cost: Decimal | None = None
        currency: str | None = None
        if cost_values:
            if not currencies:
                raise RoomUsageProjectionError(
                    "normalized cost requires a currency"
                )
            normalized_cost = sum(cost_values, Decimal("0"))
            currency = next(iter(currencies))

        participants = tuple(
            RoomParticipantSnapshot(
                participant_id=row[0],
                role=ParticipantRole(row[1]),
                display_name=row[2],
                active=bool(row[3]),
            )
            for row in participant_rows
        )
        agenda = tuple(
            RoomAgendaSnapshot(
                agenda_item_id=row[0],
                sequence=int(row[1]),
                title=row[2],
                objective=row[3],
                status=row[4],
                round_limit=int(row[5]),
            )
            for row in agenda_rows
        )
        findings = tuple(
            RoomFindingSnapshot(
                finding_id=row[0],
                severity=row[1],
                status=row[2],
                summary=row[3],
            )
            for row in finding_rows
        )
        decisions = tuple(
            RoomDecisionSnapshot(
                decision_id=row[0],
                decision_type=row[1],
                status=row[2],
                decision=row[3],
                owner_principal_id=row[4],
            )
            for row in decision_rows
        )
        events = tuple(
            self._event_from_row(
                row,
                tenant_id=tenant_id,
                application_id=application_id,
                room_id=room_id,
            )
            for row in reversed(event_rows)
        )

        return RoomSnapshot(
            tenant_id=tenant_id,
            application_id=application_id,
            room_id=room_id,
            mode=RoomMode(room_row[0]),
            state=RoomState(room_row[1]),
            generated_at=self._clock(),
            last_sequence=last_sequence,
            participants=participants,
            agenda=agenda,
            findings=findings,
            decisions=decisions,
            usage=RoomUsageSnapshot(
                input_tokens=int(input_tokens or 0),
                output_tokens=int(output_tokens or 0),
                normalized_cost=normalized_cost,
                currency=currency,
            ),
            recent_events=events,
        )

    @staticmethod
    def _event_from_row(
        row: tuple[object, ...],
        *,
        tenant_id: UUID,
        application_id: UUID,
        room_id: UUID,
    ) -> OrderedRoomEvent:
        (
            message_id,
            agenda_item_id,
            participant_id,
            request_id,
            stored_message_type,
            sequence,
            content_text,
            created_at,
        ) = row

        if request_id is None:
            raise RoomEventProjectionError(
                "durable War Room event is missing request_id"
            )
        if not isinstance(content_text, str):
            raise RoomEventProjectionError(
                "durable War Room event is missing JSON content_text"
            )

        try:
            envelope = json.loads(content_text)
            event_type = RoomEventType(envelope["event_type"])
            trace_id = envelope["trace_id"]
            payload = envelope.get("payload", {})
            room_state_raw = envelope.get("room_state")
            message_type_raw = envelope.get("message_type")
            halt_reason_raw = envelope.get("halt_reason")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise RoomEventProjectionError(
                "invalid durable War Room event envelope"
            ) from exc

        if not isinstance(payload, dict):
            raise RoomEventProjectionError("event payload must be an object")

        message_type = (
            MessageType(message_type_raw)
            if message_type_raw is not None
            else None
        )
        if message_type is not None and message_type.value != stored_message_type:
            raise RoomEventProjectionError(
                "event envelope message_type disagrees with durable row"
            )

        try:
            correlation = CorrelationContext(
                tenant_id=tenant_id,
                application_id=application_id,
                room_id=room_id,
                agenda_item_id=agenda_item_id,
                request_id=request_id,
                trace_id=trace_id,
            )
            return OrderedRoomEvent(
                event_id=message_id,
                sequence=int(sequence),
                event_type=event_type,
                correlation=correlation,
                occurred_at=created_at,
                room_state=(
                    RoomState(room_state_raw)
                    if room_state_raw is not None
                    else None
                ),
                participant_id=(
                    str(participant_id) if participant_id is not None else None
                ),
                message_type=message_type,
                halt_reason=(
                    HaltReason(halt_reason_raw)
                    if halt_reason_raw is not None
                    else None
                ),
                payload=payload,
            )
        except (TypeError, ValueError) as exc:
            raise RoomEventProjectionError(
                "durable War Room event violates frozen contract"
            ) from exc


def serialize_ordered_event(event: OrderedRoomEvent) -> dict[str, object]:
    """Serialize exactly the N-10 OrderedRoomEvent wire shape."""

    return {
        "event_id": str(event.event_id),
        "sequence": event.sequence,
        "event_type": event.event_type.value,
        "correlation": {
            "tenant_id": str(event.correlation.tenant_id),
            "application_id": str(event.correlation.application_id),
            "room_id": str(event.correlation.room_id),
            "agenda_item_id": str(event.correlation.agenda_item_id),
            "request_id": str(event.correlation.request_id),
            "trace_id": event.correlation.trace_id,
        },
        "occurred_at": event.occurred_at.isoformat(),
        "room_state": event.room_state.value if event.room_state else None,
        "participant_id": event.participant_id,
        "message_type": event.message_type.value if event.message_type else None,
        "halt_reason": event.halt_reason.value if event.halt_reason else None,
        "payload": _json_safe(event.payload),
    }


def serialize_room_snapshot(snapshot: RoomSnapshot) -> dict[str, object]:
    """Serialize exactly the N-10 RoomSnapshot wire shape."""

    return {
        "tenant_id": str(snapshot.tenant_id),
        "application_id": str(snapshot.application_id),
        "room_id": str(snapshot.room_id),
        "mode": snapshot.mode.value,
        "state": snapshot.state.value,
        "generated_at": snapshot.generated_at.isoformat(),
        "last_sequence": snapshot.last_sequence,
        "participants": [
            {
                "participant_id": str(item.participant_id),
                "role": item.role.value,
                "display_name": item.display_name,
                "active": item.active,
            }
            for item in snapshot.participants
        ],
        "agenda": [
            {
                "agenda_item_id": str(item.agenda_item_id),
                "sequence": item.sequence,
                "title": item.title,
                "objective": item.objective,
                "status": item.status,
                "round_limit": item.round_limit,
            }
            for item in snapshot.agenda
        ],
        "findings": [
            {
                "finding_id": str(item.finding_id),
                "severity": item.severity,
                "status": item.status,
                "summary": item.summary,
            }
            for item in snapshot.findings
        ],
        "decisions": [
            {
                "decision_id": str(item.decision_id),
                "decision_type": item.decision_type,
                "status": item.status,
                "decision": item.decision,
                "owner_principal_id": item.owner_principal_id,
            }
            for item in snapshot.decisions
        ],
        "usage": {
            "input_tokens": snapshot.usage.input_tokens,
            "output_tokens": snapshot.usage.output_tokens,
            "normalized_cost": (
                format(snapshot.usage.normalized_cost, "f")
                if snapshot.usage.normalized_cost is not None
                else None
            ),
            "currency": snapshot.usage.currency,
        },
        "recent_events": [
            serialize_ordered_event(event)
            for event in snapshot.recent_events
        ],
    }


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    raise RoomEventProjectionError(
        f"unsupported event payload value: {type(value).__name__}"
    )
