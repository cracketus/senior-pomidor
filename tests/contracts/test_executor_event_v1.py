"""Tests for ExecutorEventV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import ExecutorEventV1
from brain.contracts.executor_event_v1 import ExecutorStatus
from brain.contracts.guardrail_result_v1 import GuardrailDecision


def test_valid_executor_event_passes():
    event = ExecutorEventV1(
        schema_version="executor_event_v1",
        timestamp=datetime.now(timezone.utc),
        status=ExecutorStatus.EXECUTED,
        action_type="water",
        guardrail_decision=GuardrailDecision.APPROVED,
        duration_seconds=12.0,
    )
    assert event.schema_version == "executor_event_v1"
    assert event.status == "executed"


def test_timestamp_requires_timezone():
    with pytest.raises(ValidationError):
        ExecutorEventV1(
            schema_version="executor_event_v1",
            timestamp=datetime.now(),
            status=ExecutorStatus.SKIPPED,
            action_type="water",
            guardrail_decision=GuardrailDecision.REJECTED,
        )


def test_schema_version_is_fixed():
    with pytest.raises(ValidationError):
        ExecutorEventV1(
            schema_version="wrong",
            timestamp=datetime.now(timezone.utc),
            status=ExecutorStatus.SKIPPED,
            action_type="water",
            guardrail_decision=GuardrailDecision.REJECTED,
        )


def test_json_roundtrip():
    original = ExecutorEventV1(
        schema_version="executor_event_v1",
        timestamp=datetime.now(timezone.utc),
        status=ExecutorStatus.SKIPPED,
        action_type="water",
        guardrail_decision=GuardrailDecision.REJECTED,
    )
    restored = ExecutorEventV1.model_validate_json(original.model_dump_json())
    assert restored.model_dump(mode="json") == original.model_dump(mode="json")
