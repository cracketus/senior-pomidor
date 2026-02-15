"""Tests for estimator pipeline."""

from datetime import datetime, timezone

from brain.contracts import DeviceStatusV1, ObservationV1
from brain.estimator.pipeline import EstimatorPipeline


def _make_observation(timestamp: datetime) -> ObservationV1:
    return ObservationV1(
        schema_version="observation_v1",
        timestamp=timestamp,
        soil_moisture_p1=0.55,
        soil_moisture_p2=0.50,
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


def test_pipeline_returns_state_anomalies_sensor_health():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    pipeline = EstimatorPipeline()
    state, anomalies, sensor_health = pipeline.process(
        _make_observation(now), _device_status(now)
    )

    assert state.schema_version == "state_v1"
    assert isinstance(anomalies, list)
    assert isinstance(sensor_health, list)
    assert all(h.schema_version == "sensor_health_v1" for h in sensor_health)


def test_pipeline_is_deterministic_for_same_inputs():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    pipeline_a = EstimatorPipeline()
    pipeline_b = EstimatorPipeline()

    obs = _make_observation(now)
    device = _device_status(now)

    result_a = pipeline_a.process(obs, device)
    result_b = pipeline_b.process(obs, device)

    assert result_a[0].model_dump() == result_b[0].model_dump()
    assert [a.model_dump() for a in result_a[1]] == [
        b.model_dump() for b in result_b[1]
    ]
    assert [a.model_dump() for a in result_a[2]] == [
        b.model_dump() for b in result_b[2]
    ]
