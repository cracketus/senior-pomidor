"""Tests for hardware execution runtime state machine."""

from datetime import datetime, timedelta, timezone

from brain.contracts import DeviceStatusV1
from brain.executor import (
    ExecutorRuntimeState,
    HardwareExecutionStateMachine,
    StateMachineConfig,
)


def _device_status(ts: datetime, *, connected: bool = True) -> DeviceStatusV1:
    return DeviceStatusV1(
        schema_version="device_status_v1",
        timestamp=ts,
        light_on=False,
        fans_on=True,
        heater_on=False,
        pump_on=False,
        co2_on=False,
        mcu_connected=connected,
        mcu_uptime_seconds=1000,
        mcu_reset_count=0,
    )


def test_telemetry_stale_degrades_state():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    machine = HardwareExecutionStateMachine()
    stale = _device_status(now - timedelta(minutes=20))

    transitions = machine.observe_telemetry(now=now, device_status=stale)

    assert machine.state == ExecutorRuntimeState.DEGRADED
    assert len(transitions) == 1
    assert transitions[0].reason == "telemetry_stale_degraded"


def test_disconnected_mcu_faults_state():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    machine = HardwareExecutionStateMachine()

    transitions = machine.observe_telemetry(
        now=now,
        device_status=_device_status(now, connected=False),
    )

    assert machine.state == ExecutorRuntimeState.FAULTED
    assert transitions[0].reason == "mcu_disconnected"
    assert machine.can_execute() is False


def test_adapter_errors_enter_safe_mode():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    machine = HardwareExecutionStateMachine()

    machine.observe_dispatch_result(accepted=False, now=now)
    machine.observe_dispatch_result(accepted=False, now=now + timedelta(seconds=1))
    transitions = machine.observe_dispatch_result(
        accepted=False,
        now=now + timedelta(seconds=2),
    )

    assert machine.state == ExecutorRuntimeState.SAFE_MODE
    assert transitions[0].reason == "adapter_errors_safe_mode"
    assert machine.can_execute() is False


def test_recovery_to_nominal_after_healthy_cycles():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    config = StateMachineConfig(healthy_cycles_for_recovery=2)
    machine = HardwareExecutionStateMachine(config=config)
    machine.observe_telemetry(
        now=now,
        device_status=_device_status(now - timedelta(minutes=20)),
    )
    assert machine.state == ExecutorRuntimeState.DEGRADED

    machine.observe_dispatch_result(accepted=True, now=now + timedelta(minutes=1))
    first = machine.observe_telemetry(
        now=now + timedelta(minutes=1),
        device_status=_device_status(now + timedelta(minutes=1)),
    )
    second = machine.observe_telemetry(
        now=now + timedelta(minutes=2),
        device_status=_device_status(now + timedelta(minutes=2)),
    )

    assert first == []
    assert machine.state == ExecutorRuntimeState.NOMINAL
    assert len(second) == 1
    assert second[0].reason == "telemetry_recovered"


def test_safe_mode_recovers_to_degraded_after_healthy_window():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    config = StateMachineConfig(healthy_cycles_for_recovery=2)
    machine = HardwareExecutionStateMachine(config=config)
    machine.observe_dispatch_result(accepted=False, now=now)
    machine.observe_dispatch_result(accepted=False, now=now + timedelta(seconds=1))
    machine.observe_dispatch_result(accepted=False, now=now + timedelta(seconds=2))
    assert machine.state == ExecutorRuntimeState.SAFE_MODE

    machine.observe_dispatch_result(accepted=True, now=now + timedelta(seconds=3))
    machine.observe_telemetry(
        now=now + timedelta(minutes=1),
        device_status=_device_status(now + timedelta(minutes=1)),
    )
    transitions = machine.observe_telemetry(
        now=now + timedelta(minutes=2),
        device_status=_device_status(now + timedelta(minutes=2)),
    )

    assert machine.state == ExecutorRuntimeState.DEGRADED
    assert len(transitions) == 1
    assert transitions[0].reason == "safe_mode_recovery_window"
