"""T-029 frozen-contract conformance tests.

Validates real emitted JSON shapes against ``schemas/*.json`` so schema drift
(the T-008 class of bug) is caught by the suite, and closes the boundary gaps
found by the read-only contract sweep:

1. usage-event wire payloads conform to ``usage-event-v1.schema.json``;
2. the storage-only ``metadata`` column is NOT a wire field (the schema forbids
   it via ``additionalProperties:false``);
3. all-zero ``trace_id`` is rejected at the boundary (the frozen pattern
   ``^(?!0{32}$)[0-9a-f]{32}$`` forbids it).
"""
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from app.war_room import CorrelationContext
from app.war_room.interfaces import InterfaceViolation
from app.war_room.transport import (
    CorrelationPayload,
    build_usage_event_payload,
)

SCHEMAS = Path(__file__).resolve().parents[3] / "schemas"

TENANT = UUID("11111111-1111-4111-8111-111111111111")
APPLICATION = UUID("22222222-2222-4222-8222-222222222222")
ROOM = UUID("33333333-3333-4333-8333-333333333333")
AGENDA = UUID("44444444-4444-4444-8444-444444444444")
REQUEST = UUID("55555555-5555-4555-8555-555555555555")
AGENT = UUID("66666666-6666-4666-8666-666666666666")
TRACE = "1234567890abcdef1234567890abcdef"


def _schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _correlation() -> CorrelationContext:
    return CorrelationContext(
        tenant_id=TENANT,
        application_id=APPLICATION,
        room_id=ROOM,
        agenda_item_id=AGENDA,
        request_id=REQUEST,
        trace_id=TRACE,
    )


def _jsonable(payload: dict) -> dict:
    """Convert a production payload (native UUID/datetime) to JSON scalars."""
    converted: dict = {}
    for key, value in payload.items():
        if isinstance(value, UUID):
            converted[key] = str(value)
        elif isinstance(value, datetime):
            converted[key] = value.isoformat().replace("+00:00", "Z")
        else:
            converted[key] = value
    return converted


def _tokens_payload() -> dict:
    # Built by the SAME production function that record_usage inserts, so the
    # conformance check exercises production code (not a hand-built dict).
    return build_usage_event_payload(
        usage_event_id=UUID(int=7),
        occurred_at=datetime(2026, 9, 25, 3, 0, tzinfo=UTC),
        correlation=_correlation(),
        agent_id=AGENT,
        event_type="ai_tokens",
        quantity=120,
        unit="input",
        dedupe_key=f"war-room:{REQUEST}:preview-builder:input",
        source_type="request",
        source_id=str(REQUEST),
        provider="openrouter",
        model="z-ai/glm-5.3-flash",
    )


def test_usage_event_wire_payload_conforms_to_frozen_schema() -> None:
    payload = _tokens_payload()
    validator = Draft202012Validator(_schema("usage-event-v1.schema.json"))
    validator.validate(_jsonable(payload))  # must not raise
    assert "metadata" not in payload  # storage-only column is never a wire field


def test_usage_event_cost_payload_conforms_to_frozen_schema() -> None:
    payload = build_usage_event_payload(
        usage_event_id=UUID(int=8),
        occurred_at=datetime(2026, 9, 25, 3, 0, tzinfo=UTC),
        correlation=_correlation(),
        agent_id=AGENT,
        event_type="ai_cost",
        quantity=1,
        unit="request",
        dedupe_key=f"war-room:{REQUEST}:preview-builder:cost",
        source_type="request",
        source_id=str(REQUEST),
        provider="openrouter",
        model="z-ai/glm-5.3-flash",
        provider_reported_cost=0.03,
        normalized_cost=0.03,
        currency="USD",
        pricing_rate_version="openrouter-reported",
    )
    validator = Draft202012Validator(_schema("usage-event-v1.schema.json"))
    validator.validate(_jsonable(payload))  # must not raise
    assert payload["currency"] == "USD"
    assert payload["pricing_rate_version"] == "openrouter-reported"


def test_usage_event_schema_forbids_storage_only_metadata() -> None:
    validator = Draft202012Validator(_schema("usage-event-v1.schema.json"))
    poisoned = _jsonable(_tokens_payload()) | {"metadata": {}}
    assert list(validator.iter_errors(poisoned)), (
        "metadata must not be part of the wire usage-event contract"
    )


def test_all_zero_trace_id_rejected_by_correlation_context() -> None:
    with pytest.raises(InterfaceViolation):
        CorrelationContext(
            tenant_id=TENANT,
            application_id=APPLICATION,
            room_id=ROOM,
            agenda_item_id=AGENDA,
            request_id=REQUEST,
            trace_id="0" * 32,
        )


def test_valid_trace_id_accepted_by_correlation_context() -> None:
    context = CorrelationContext(
        tenant_id=TENANT,
        application_id=APPLICATION,
        room_id=ROOM,
        agenda_item_id=AGENDA,
        request_id=REQUEST,
        trace_id=TRACE,
    )
    assert context.trace_id == TRACE


def test_all_zero_trace_id_rejected_at_transport_boundary() -> None:
    with pytest.raises(ValidationError):
        CorrelationPayload(
            tenant_id=TENANT,
            application_id=APPLICATION,
            room_id=ROOM,
            agenda_item_id=AGENDA,
            request_id=REQUEST,
            trace_id="0" * 32,
        )


def test_frozen_schema_files_exist() -> None:
    # Guard: the conformance tests above must read the real frozen contracts.
    assert (SCHEMAS / "war-room-event-v1.schema.json").is_file()
    assert (SCHEMAS / "usage-event-v1.schema.json").is_file()
