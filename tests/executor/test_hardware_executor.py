"""Tests for hardware-backed executor foundation."""

from datetime import datetime, timedelta, timezone

from brain.contracts import ActionV1, DeviceStatusV1, GuardrailResultV1
from brain.contracts.action_v1 import ActionType
from brain.contracts.guardrail_result_v1 import (
    GuardrailDecision,
    GuardrailReasonCode,
)
from brain.executor import (
    HardwareDispatchResult,
    HardwareExecutor,
    HardwareStubAdapter,
    IdempotencyConfig,
    RetryPolicyConfig,
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


def _device_status(now: datetime, *, connected: bool = True) -> DeviceStatusV1:
    return DeviceStatusV1(
        schema_version="device_status_v1",
        timestamp=now,
        light_on=False,
        fans_on=True,
        heater_on=False,
        pump_on=False,
        co2_on=False,
        mcu_connected=connected,
        mcu_uptime_seconds=1000,
        mcu_reset_count=0,
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
        device_status=_device_status(now),
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
        device_status=_device_status(now),
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
        device_status=_device_status(now),
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
        device_status=_device_status(now),
    )

    assert event.status == "skipped"
    assert event.notes == (
        "adapter_rejected_non_retryable:rejecting_adapter:REJECTED_CMD:unknown_error"
    )


def test_blocks_execution_when_telemetry_is_missing():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(HardwareStubAdapter())
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.APPROVED)

    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
        device_status=None,
    )
    transitions = executor.drain_runtime_events()

    assert event.status == "skipped"
    assert event.notes == "blocked_by_state:faulted"
    assert transitions
    assert transitions[0].notes == "state_transition:nominal->faulted:telemetry_missing"


def test_retries_retryable_failure_then_executes():
    class _FlakyThenSuccessAdapter:
        def __init__(self) -> None:
            self.calls = 0

        @property
        def adapter_name(self) -> str:
            return "flaky_then_success"

        def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
            self.calls += 1
            if self.calls == 1:
                return HardwareDispatchResult(
                    accepted=False,
                    command="TEMP_FAIL",
                    duration_seconds=action.duration_seconds,
                    adapter_name=self.adapter_name,
                    retryable=True,
                    error_class="transient_io",
                )
            return HardwareDispatchResult(
                accepted=True,
                command="RECOVERED",
                duration_seconds=action.duration_seconds,
                adapter_name=self.adapter_name,
            )

    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    policy = RetryPolicyConfig(max_attempts=3, base_backoff_seconds=5.0)
    executor = HardwareExecutor(_FlakyThenSuccessAdapter(), retry_policy=policy)
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.APPROVED)

    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
        device_status=_device_status(now),
    )
    runtime_events = executor.drain_runtime_events()

    assert event.status == "executed"
    assert event.notes == "executed_after_retry_flaky_then_success:RECOVERED:attempts=2"
    assert any(
        "retry_scheduled:adapter=flaky_then_success:attempt=2:" in e.notes
        for e in runtime_events
    )


def test_non_retryable_failure_fails_fast_with_reason_code():
    class _NonRetryableAdapter:
        @property
        def adapter_name(self) -> str:
            return "non_retryable"

        def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
            return HardwareDispatchResult(
                accepted=False,
                command="FATAL",
                duration_seconds=action.duration_seconds,
                adapter_name=self.adapter_name,
                retryable=False,
                error_class="fatal_config",
            )

    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(_NonRetryableAdapter())
    action = _action(now)
    result = _guardrail(now, GuardrailDecision.APPROVED)
    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
        device_status=_device_status(now),
    )

    assert event.status == "skipped"
    assert "non_retryable_dispatch" in event.reason_codes
    assert event.notes == "adapter_rejected_non_retryable:non_retryable:FATAL:fatal_config"


def test_duplicate_idempotency_key_is_skipped():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(
        HardwareStubAdapter(),
        idempotency=IdempotencyConfig(ttl_seconds=3600),
    )
    action = _action(now).model_copy(update={"idempotency_key": "idem-key-9999"})
    result = _guardrail(now, GuardrailDecision.APPROVED)

    first = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now,
        device_status=_device_status(now),
    )
    _ = executor.drain_runtime_events()
    second = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=result,
        now=now + timedelta(minutes=1),
        device_status=_device_status(now + timedelta(minutes=1)),
    )

    assert first.status == "executed"
    assert second.status == "skipped"
    assert second.notes == "skipped_duplicate_idempotency_key:idem-key-9999"
