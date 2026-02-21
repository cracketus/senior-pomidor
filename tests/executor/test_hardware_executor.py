"""Tests for hardware-backed executor foundation."""

from datetime import datetime, timezone

from brain.contracts import ActionV1, GuardrailResultV1
from brain.contracts.action_v1 import ActionType
from brain.contracts.guardrail_result_v1 import (
    GuardrailDecision,
    GuardrailReasonCode,
)
from brain.executor import (
    HardwareDispatchResult,
    HardwareExecutor,
    HardwareStubAdapter,
    create_hardware_adapter,
)


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


def test_executes_with_production_scaffold_adapter():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(create_hardware_adapter("production_scaffold"))
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.APPROVED)

    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
    )

    assert event.status == "executed"
    assert event.notes == "executed_production_scaffold:ACTUATOR_WATER_PULSE"


def test_marks_event_skipped_when_adapter_rejects():
    class _RejectingAdapter:
        @property
        def adapter_name(self) -> str:
            return "rejecting_adapter"

        def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
            return HardwareDispatchResult(
                accepted=False,
                command="REJECTED_CMD",
                duration_seconds=action.duration_seconds,
                adapter_name=self.adapter_name,
                details=now.isoformat(),
            )

    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(_RejectingAdapter())
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.APPROVED)

    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
    )

    assert event.status == "skipped"
    assert event.notes == "adapter_rejected:rejecting_adapter:REJECTED_CMD"
