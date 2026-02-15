"""Tests for sensor health fault detection."""

from datetime import datetime, timedelta, timezone

from brain.contracts import ObservationV1
from brain.contracts.sensor_health_v1 import FaultType
from brain.estimator.sensor_health import evaluate_sensor_health


def _make_obs(timestamp: datetime, soil_p1: float) -> ObservationV1:
    return ObservationV1(
        schema_version="observation_v1",
        timestamp=timestamp,
        soil_moisture_p1=soil_p1,
        soil_moisture_p2=0.5,
        air_temperature=22.0,
        air_humidity=65.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )


def _get_sensor(health_list, name: str):
    for health in health_list:
        if health.sensor_name == name:
            return health
    raise AssertionError("Sensor not found")


def test_fault_detection_stuck_at():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    history = [
        _make_obs(now - timedelta(minutes=50), 0.55),
        _make_obs(now - timedelta(minutes=10), 0.55),
    ]
    current = _make_obs(now, 0.55)
    health = evaluate_sensor_health(current, history)
    soil_health = _get_sensor(health, "soil_moisture_p1")
    assert soil_health.fault_state == FaultType.STUCK


def test_fault_detection_jump():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    history = [
        _make_obs(now - timedelta(minutes=1), 0.1),
    ]
    current = _make_obs(now, 0.9)
    health = evaluate_sensor_health(current, history)
    soil_health = _get_sensor(health, "soil_moisture_p1")
    assert soil_health.fault_state == FaultType.JUMP


def test_fault_detection_drift():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    history = [
        _make_obs(now - timedelta(hours=4), 0.10),
        _make_obs(now - timedelta(hours=2), 0.15),
        _make_obs(now - timedelta(hours=1), 0.18),
    ]
    current = _make_obs(now, 0.22)
    health = evaluate_sensor_health(current, history)
    soil_health = _get_sensor(health, "soil_moisture_p1")
    assert soil_health.fault_state in {FaultType.DRIFT, FaultType.JUMP}
