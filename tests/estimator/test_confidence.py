"""Tests for confidence scoring."""

from datetime import datetime, timedelta, timezone

from brain.contracts import AnomalyV1, ObservationV1, SensorHealthV1
from brain.contracts.anomaly_v1 import AnomalyType, SeverityLevel
from brain.contracts.sensor_health_v1 import FaultType
from brain.estimator.confidence import compute_confidence


def _make_observation(timestamp: datetime, soil_p2=None) -> ObservationV1:
    return ObservationV1(
        schema_version="observation_v1",
        timestamp=timestamp,
        soil_moisture_p1=0.55,
        soil_moisture_p2=soil_p2,
        air_temperature=22.0,
        air_humidity=65.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )


def test_confidence_with_missing_sensors_decreases():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    observation = _make_observation(now, soil_p2=None)
    sensor_health = [
        SensorHealthV1(
            schema_version="sensor_health_v1",
            timestamp=now,
            sensor_name="soil_moisture_p2",
            sensor_type=None,
            status="degraded",
            confidence=0.5,
            fault_state=FaultType.DISCONNECTED,
            last_reading=None,
            readings_since_fault=0,
            consecutive_failures=1,
            voltage_mv=None,
            signal_quality=None,
            notes=None,
        )
    ]
    confidence = compute_confidence(
        observation, 1.2, [observation], sensor_health, []
    )
    assert confidence < 1.0


def test_confidence_algorithm_matches_spec():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    observation = _make_observation(now, soil_p2=0.55)
    anomaly = AnomalyV1(
        schema_version="anomaly_v1",
        timestamp=now,
        anomaly_type=AnomalyType.MOISTURE_STRESS,
        severity=SeverityLevel.LOW,
        affected_sensor="soil_moisture_p1",
        description="Minor anomaly",
        confidence=0.8,
        action_recommended=False,
    )
    sensor_health = [
        SensorHealthV1(
            schema_version="sensor_health_v1",
            timestamp=now,
            sensor_name="soil_moisture_p1",
            sensor_type=None,
            status="degraded",
            confidence=0.5,
            fault_state=FaultType.STUCK,
            last_reading=0.55,
            readings_since_fault=0,
            consecutive_failures=0,
            voltage_mv=None,
            signal_quality=None,
            notes=None,
        )
    ]

    confidence = compute_confidence(
        observation,
        1.2,
        [observation],
        sensor_health,
        [anomaly],
        now=now + timedelta(minutes=25),
    )

    # age(25)=0.10 + stuck(0.50) + minor anomaly(0.10) => 0.30 confidence
    assert abs(confidence - 0.30) < 1e-6
