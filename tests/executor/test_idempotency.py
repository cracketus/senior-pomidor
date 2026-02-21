"""Tests for executor idempotency-key deduplication behavior."""

from datetime import datetime, timedelta, timezone

from brain.contracts import ActionV1, DeviceStatusV1, GuardrailResultV1
from brain.contracts.action_v1 import ActionType
from brain.contracts.guardrail_result_v1 import GuardrailDecision
from brain.executor import HardwareDispatchResult, HardwareExecutor, IdempotencyConfig


class _CountingAdapter:
    def __init__(self) -> None:
        self.calls = 0

    @property
    def adapter_name(self) -> str:
        return "counting"

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        self.calls += 1
        return HardwareDispatchResult(
            accepted=True,
            command="COUNTED",
            duration_seconds=action.duration_seconds,
            adapter_name=self.adapter_name,
        )


def _guardrail(now: datetime) -> GuardrailResultV1:
    return GuardrailResultV1(
        schema_version="guardrail_result_v1",
        timestamp=now,
        decision=GuardrailDecision.APPROVED,
        reason_codes=[],
    )


def _device_status(now: datetime) -> DeviceStatusV1:
    return DeviceStatusV1(
        schema_version="device_status_v1",
        timestamp=now,
        light_on=False,
        fans_on=True,
        heater_on=False,
        pump_on=False,
        co2_on=False,
        mcu_connected=True,
        mcu_uptime_seconds=100,
        mcu_reset_count=0,
    )


def _action(now: datetime, *, key: str | None) -> ActionV1:
    return ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=5.0,
        intensity=0.7,
        reason="idempotency-test",
        idempotency_key=key,
    )


def test_duplicate_key_is_skipped_without_redispatch():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    adapter = _CountingAdapter()
    executor = HardwareExecutor(adapter, idempotency=IdempotencyConfig(ttl_seconds=3600))
    action = _action(now, key="idem-key-0001")
    guardrail = _guardrail(now)
    device_status = _device_status(now)

    first = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now,
        device_status=device_status,
    )
    _ = executor.drain_runtime_events()
    second = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now + timedelta(minutes=1),
        device_status=_device_status(now + timedelta(minutes=1)),
    )
    runtime_events = executor.drain_runtime_events()

    assert first.status == "executed"
    assert second.status == "skipped"
    assert second.notes == "skipped_duplicate_idempotency_key:idem-key-0001"
    assert "idempotency_duplicate" in second.reason_codes
    assert adapter.calls == 1
    assert any(
        (e.notes or "").startswith("idempotency_hit:key=idem-key-0001")
        for e in runtime_events
    )


def test_expired_key_allows_new_dispatch():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    adapter = _CountingAdapter()
    executor = HardwareExecutor(adapter, idempotency=IdempotencyConfig(ttl_seconds=60))
    action = _action(now, key="idem-key-0002")
    guardrail = _guardrail(now)

    executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now,
        device_status=_device_status(now),
    )
    executor.drain_runtime_events()

    late_time = now + timedelta(minutes=2)
    second = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=late_time,
        device_status=_device_status(late_time),
    )

    assert second.status == "executed"
    assert adapter.calls == 2


def test_missing_key_keeps_backward_compatible_behavior():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    adapter = _CountingAdapter()
    executor = HardwareExecutor(adapter)
    action = _action(now, key=None)
    guardrail = _guardrail(now)

    first = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now,
        device_status=_device_status(now),
    )
    second = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now + timedelta(minutes=1),
        device_status=_device_status(now + timedelta(minutes=1)),
    )

    assert first.status == "executed"
    assert second.status == "executed"
    assert adapter.calls == 2
