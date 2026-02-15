"""Tests for GuardrailResultV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import GuardrailResultV1
from brain.contracts.guardrail_result_v1 import (
    GuardrailDecision,
    GuardrailReasonCode,
)


def test_reason_code_enum_values():
    """Reason-code taxonomy should include expected Stage 2 categories."""
    expected = {
        "budget_exceeded",
        "interval_violation",
        "stale_data",
        "low_confidence",
        "device_offline",
        "environment_limit",
        "action_invalid",
        "action_clipped",
    }
    assert {code.value for code in GuardrailReasonCode} == expected


def test_rejection_requires_reason_codes():
    """Rejected outcomes must include machine-readable reason codes."""
    with pytest.raises(ValidationError):
        GuardrailResultV1(
            schema_version="guardrail_result_v1",
            timestamp=datetime.now(timezone.utc),
            decision=GuardrailDecision.REJECTED,
            reason_codes=[],
        )


def test_clipped_requires_reason_codes():
    """Clipped outcomes must include reason codes as well."""
    with pytest.raises(ValidationError):
        GuardrailResultV1(
            schema_version="guardrail_result_v1",
            timestamp=datetime.now(timezone.utc),
            decision=GuardrailDecision.CLIPPED,
        )


def test_approved_can_have_no_reason_codes():
    """Approved outcomes should not require reason codes."""
    result = GuardrailResultV1(
        schema_version="guardrail_result_v1",
        timestamp=datetime.now(timezone.utc),
        decision=GuardrailDecision.APPROVED,
    )
    assert result.decision == GuardrailDecision.APPROVED.value
    assert result.reason_codes == []
