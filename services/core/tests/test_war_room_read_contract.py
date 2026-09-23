import json
from pathlib import Path
from uuid import UUID

import pytest

from app.war_room import (
    DenyAllRoomReadAuthorizer,
    InterfaceViolation,
    ParticipantType,
    RoomReadKind,
    RoomReadRequest,
    TrustedActorContext,
)


ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "schemas"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def read_request(
    *,
    kind: RoomReadKind = RoomReadKind.SNAPSHOT,
    after_sequence: int | None = None,
) -> RoomReadRequest:
    return RoomReadRequest(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        room_id=UUID(int=3),
        read_kind=kind,
        after_sequence=after_sequence,
    )


def actor() -> TrustedActorContext:
    return TrustedActorContext(
        tenant_id=UUID(int=1),
        application_id=UUID(int=2),
        principal_type=ParticipantType.HUMAN,
        principal_id="user-1",
    )


def test_read_cursor_rejects_negative_sequence() -> None:
    with pytest.raises(InterfaceViolation):
        read_request(
            kind=RoomReadKind.EVENT_STREAM,
            after_sequence=-1,
        )


@pytest.mark.anyio
async def test_default_read_authorizer_fails_closed() -> None:
    authorizer = DenyAllRoomReadAuthorizer()

    assert (
        await authorizer.authorize_read(
            request=read_request(),
            actor=actor(),
        )
        is False
    )


def test_event_schema_freezes_wire_primitives_and_event_payloads() -> None:
    schema = json.loads(
        (SCHEMAS / "war-room-event-v1.schema.json").read_text()
    )

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["event_id"]["format"] == "uuid"
    assert schema["properties"]["occurred_at"]["format"] == "date-time"
    assert "TURN_FAILED" in schema["properties"]["event_type"]["enum"]

    payload = schema["$defs"]["payload"]
    assert payload["additionalProperties"] is False
    assert "failure_kind" in payload["properties"]
    assert "automatic_retry_allowed" in payload["properties"]
    assert payload["properties"]["provider_request_id"]["type"] == "string"
    assert payload["properties"]["model"]["type"] == "string"

    agent_evidence_rules = [
        item
        for item in schema["allOf"]
        if item.get("if", {})
        .get("properties", {})
        .get("message_type", {})
        .get("enum")
        == ["AGENT_MESSAGE", "CHAIR_SYNTHESIS"]
    ]
    assert len(agent_evidence_rules) == 1
    required = agent_evidence_rules[0]["then"]["properties"]["payload"]["allOf"][1][
        "required"
    ]
    assert required == ["provider_request_id", "model"]


def test_snapshot_schema_serializes_decimal_cost_as_string() -> None:
    schema = json.loads(
        (SCHEMAS / "war-room-snapshot-v1.schema.json").read_text()
    )

    assert schema["additionalProperties"] is False
    usage = schema["$defs"]["usage"]
    normalized_cost = usage["properties"]["normalized_cost"]

    assert "string" in normalized_cost["type"]
    assert "number" not in normalized_cost["type"]
    assert usage["properties"]["currency"]["pattern"] == "^[A-Z]{3}$"
    assert (
        schema["properties"]["recent_events"]["items"]["$ref"]
        == "https://nippan.org/schemas/war-room-event-v1.schema.json"
    )


def test_snapshot_source_contract_reuses_platform_usage_evidence() -> None:
    contract = (
        ROOT / "docs" / "data" / "WAR_ROOM_READ_SNAPSHOT_CONTRACT_V1.md"
    ).read_text()

    assert "public.usage_events" in contract
    assert "public.ai_calls" in contract
    assert "project_room_messages.request_id" in contract
    assert "no new usage ledger or aggregate table" in contract
    assert "DenyAllRoomReadAuthorizer" in contract
