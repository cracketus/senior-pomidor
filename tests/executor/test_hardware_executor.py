"""Tests for hardware-backed executor foundation."""

from datetime import datetime, timezone

from brain.contracts import ActionV1, GuardrailResultV1
from brain.contracts.action_v1 import ActionType
from brain.contracts.guardrail_result_v1 import (
    GuardrailDecision,
    GuardrailReasonCode,
)
from brain.executor import HardwareExecutor, HardwareStubAdapter


def _action(now: datetime) -> ActionV1:
    return ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=10.0,
        intensity=0.8,
        reason="test",
    )


def _guardrail(now: datetime, decision: GuardrailDecision) -> GuardrailResultV1:
    if decision == GuardrailDecision.REJECTED:
        reason_codes = [GuardrailReasonCode.INTERVAL_VIOLATION]
    elif decision == GuardrailDecision.CLIPPED:
        reason_codes = [GuardrailReasonCode.ACTION_CLIPPED]
    else:
        reason_codes = []
    return GuardrailResultV1(
        schema_version="guardrail_result_v1",
        timestamp=now,
        decision=decision,
        reason_codes=reason_codes,
    )


def test_executes_effective_action_via_adapter():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(HardwareStubAdapter())
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.APPROVED)

    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
    )

    assert event.status == "executed"
    assert event.duration_seconds == 10.0
    assert event.notes == "executed_hardware_stub:WATER_PULSE"


def test_skips_when_guardrails_reject():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(HardwareStubAdapter())
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.REJECTED)

    event = executor.execute(
        proposed_action=action,
        effective_action=None,
        guardrail_result=result,
        now=now,
    )

    assert event.status == "skipped"
    assert "interval_violation" in event.reason_codes
