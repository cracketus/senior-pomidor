"""Tests for anomaly detection."""

from datetime import datetime, timedelta, timezone

from brain.contracts import DeviceStatusV1, ObservationV1
from brain.contracts.anomaly_v1 import AnomalyType
from brain.estimator.anomaly_detector import THRESHOLDS, detect_anomalies


def _make_observation(timestamp: datetime, soil_p1: float) -> ObservationV1:
    return ObservationV1(
        schema_version="observation_v1",
        timestamp=timestamp,
        soil_moisture_p1=soil_p1,
        soil_moisture_p2=0.55,
        air_temperature=22.0,
        air_humidity=65.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )


def _device_status(timestamp: datetime) -> DeviceStatusV1:
    return DeviceStatusV1(
        schema_version="device_status_v1",
        timestamp=timestamp,
        light_on=True,
        fans_on=False,
        heater_on=False,
        pump_on=False,
        co2_on=False,
        mcu_connected=True,
        mcu_uptime_seconds=120,
        mcu_reset_count=0,
        light_intensity_setpoint=300.0,
        pump_pulse_count=0,
    )


def test_threshold_breach_emits_anomaly():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    obs = _make_observation(now, soil_p1=0.05)
    anomalies = detect_anomalies(
        obs,
        vpd_kpa=1.2,
        sensor_health=[],
        device_status=_device_status(now),
    )
    assert any(a.anomaly_type == AnomalyType.MOISTURE_STRESS for a in anomalies)


def test_all_thresholds_specified_in_spec():
    expected = {
        "soil_moisture_low",
        "soil_moisture_high",
        "soil_moisture_differential",
        "vpd_high",
        "vpd_low",
        "temperature_low",
        "temperature_high",
        "temperature_rate_10m",
        "moisture_drop_30m",
    }
    assert expected.issubset(THRESHOLDS.keys())


def test_sustained_threshold_trigger():
    now = datetime(2026, 2, 15, 0, 30, tzinfo=timezone.utc)
    prev = _make_observation(now - timedelta(minutes=15), soil_p1=0.05)
    obs = _make_observation(now, soil_p1=0.05)

    anomalies = detect_anomalies(
        obs,
        vpd_kpa=1.2,
        sensor_health=[],
        device_status=_device_status(now),
        history=[prev, obs],
    )
    moisture = [a for a in anomalies if a.anomaly_type == AnomalyType.MOISTURE_STRESS]
    assert moisture
    assert any((a.notes or "").endswith("sustained") for a in moisture)


def test_rate_of_change_trigger():
    now = datetime(2026, 2, 15, 0, 10, tzinfo=timezone.utc)
    prev = ObservationV1(
        schema_version="observation_v1",
        timestamp=now - timedelta(minutes=5),
        soil_moisture_p1=0.60,
        soil_moisture_p2=0.55,
        air_temperature=20.0,
        air_humidity=65.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )
    obs = ObservationV1(
        schema_version="observation_v1",
        timestamp=now,
        soil_moisture_p1=0.50,
        soil_moisture_p2=0.55,
        air_temperature=24.5,
        air_humidity=65.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )
    anomalies = detect_anomalies(
        obs,
        vpd_kpa=1.2,
        sensor_health=[],
        device_status=_device_status(now),
        history=[prev, obs],
    )
    assert any((a.notes or "").endswith("rate") for a in anomalies)


def test_no_false_positive_for_short_spikes():
    now = datetime(2026, 2, 15, 0, 5, tzinfo=timezone.utc)
    obs = _make_observation(now, soil_p1=0.05)
    anomalies = detect_anomalies(
        obs,
        vpd_kpa=1.2,
        sensor_health=[],
        device_status=_device_status(now),
        history=[obs],
    )
    moisture = [a for a in anomalies if a.anomaly_type == AnomalyType.MOISTURE_STRESS]
    assert moisture
    assert all((a.notes or "").endswith("instant") for a in moisture)
