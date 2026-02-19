"""Tests for Guardrails v1 runtime validator."""

from datetime import datetime, timedelta, timezone

from brain.contracts import ActionV1, AnomalyV1, DeviceStatusV1, StateV1
from brain.contracts.action_v1 import ActionType
from brain.contracts.anomaly_v1 import AnomalyType, SeverityLevel
from brain.guardrails import GuardrailsConfig, GuardrailsValidator


def _state(
    *,
    now: datetime,
    confidence: float = 0.9,
    age: timedelta = timedelta(0),
) -> StateV1:
    return StateV1(
        schema_version="state_v1",
        timestamp=now - age,
        soil_moisture_p1=0.2,
        soil_moisture_p2=0.2,
        soil_moisture_avg=0.2,
        air_temperature=24.0,
        air_humidity=60.0,
        vpd=1.3,
        co2_ppm=420.0,
        light_intensity=450.0,
        confidence=confidence,
        notes=None,
    )


def _device(*, now: datetime, mcu_connected: bool = True) -> DeviceStatusV1:
    return DeviceStatusV1(
        schema_version="device_status_v1",
        timestamp=now,
        light_on=True,
        fans_on=True,
        heater_on=False,
        pump_on=False,
        co2_on=False,
        mcu_connected=mcu_connected,
        mcu_uptime_seconds=1000,
    )


def _action(*, now: datetime, duration_seconds: float = 12.0, intensity: float = 0.8) -> ActionV1:
    return ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=duration_seconds,
        intensity=intensity,
        reason="test",
    )


def _critical_anomaly(now: datetime) -> AnomalyV1:
    return AnomalyV1(
        schema_version="anomaly_v1",
        timestamp=now,
        anomaly_type=AnomalyType.UNKNOWN,
        severity=SeverityLevel.CRITICAL,
        description="critical",
        confidence=1.0,
        requires_safe_mode=True,
    )


def test_approved_action_in_normal_conditions():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    validator = GuardrailsValidator()

    effective, result = validator.validate(
        _action(now=now),
        state=_state(now=now),
        device_status=_device(now=now),
        anomalies=[],
        now=now,
    )

    assert effective is not None
    assert result.decision == "approved"
    assert result.reason_codes == []


def test_rejected_when_device_offline():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    validator = GuardrailsValidator()

    effective, result = validator.validate(
        _action(now=now),
        state=_state(now=now),
        device_status=_device(now=now, mcu_connected=False),
        anomalies=[],
        now=now,
    )

    assert effective is None
    assert result.decision == "rejected"
    assert "device_offline" in result.reason_codes


def test_rejected_on_min_interval_violation():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    validator = GuardrailsValidator()

    first_effective, first_result = validator.validate(
        _action(now=now),
        state=_state(now=now),
        device_status=_device(now=now),
        anomalies=[],
        now=now,
    )
    second_effective, second_result = validator.validate(
        _action(now=now + timedelta(minutes=5)),
        state=_state(now=now + timedelta(minutes=5)),
        device_status=_device(now=now + timedelta(minutes=5)),
        anomalies=[],
        now=now + timedelta(minutes=5),
    )

    assert first_effective is not None
    assert first_result.decision == "approved"
    assert second_effective is None
    assert second_result.decision == "rejected"
    assert "interval_violation" in second_result.reason_codes


def test_clipped_when_duration_exceeds_max_limit():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    validator = GuardrailsValidator()

    effective, result = validator.validate(
        _action(now=now, duration_seconds=50.0),
        state=_state(now=now),
        device_status=_device(now=now),
        anomalies=[],
        now=now,
    )

    assert effective is not None
    assert result.decision == "clipped"
    assert "action_clipped" in result.reason_codes
    assert "duration_seconds" in (result.clipped_fields or [])
    assert effective.duration_seconds == 30.0


def test_clipped_when_budget_requires_shorter_action():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    validator = GuardrailsValidator(
        GuardrailsConfig(
            daily_water_budget_ml=100.0,
            water_ml_per_second=10.0,
            max_water_duration_seconds=30.0,
        )
    )

    effective, result = validator.validate(
        _action(now=now, duration_seconds=20.0, intensity=1.0),
        state=_state(now=now),
        device_status=_device(now=now),
        anomalies=[],
        now=now,
    )

    assert effective is not None
    assert result.decision == "clipped"
    assert "budget_exceeded" in result.reason_codes
    assert effective.duration_seconds == 10.0


def test_rejected_when_state_is_stale_low_confidence_or_critical():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    validator = GuardrailsValidator()

    effective, result = validator.validate(
        _action(now=now),
        state=_state(now=now, confidence=0.2, age=timedelta(hours=1)),
        device_status=_device(now=now),
        anomalies=[_critical_anomaly(now)],
        now=now,
    )

    assert effective is None
    assert result.decision == "rejected"
    assert "stale_data" in result.reason_codes
    assert "low_confidence" in result.reason_codes
    assert "environment_limit" in result.reason_codes


def test_deterministic_output_for_identical_inputs_with_fresh_validators():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    action = _action(now=now, duration_seconds=35.0)
    state = _state(now=now)
    device = _device(now=now)

    effective_a, result_a = GuardrailsValidator().validate(
        action,
        state=state,
        device_status=device,
        anomalies=[],
        now=now,
    )
    effective_b, result_b = GuardrailsValidator().validate(
        action,
        state=state,
        device_status=device,
        anomalies=[],
        now=now,
    )

    assert effective_a is not None
    assert effective_b is not None
    assert effective_a.model_dump(mode="json") == effective_b.model_dump(mode="json")
    assert result_a.model_dump(mode="json") == result_b.model_dump(mode="json")
