"""Fixture-driven estimator pipeline behavior tests."""

from datetime import datetime, timezone

from brain.contracts import DeviceStatusV1, ObservationV1
from brain.estimator.pipeline import EstimatorPipeline
from tests.fixtures.anomaly_test_scenarios import ANOMALY_TEST_SCENARIOS


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


def _scenario_observation(timestamp: datetime, scenario) -> ObservationV1:
    return ObservationV1(
        schema_version="observation_v1",
        timestamp=timestamp,
        soil_moisture_p1=scenario.soil_moisture_p1,
        soil_moisture_p2=scenario.soil_moisture_p2,
        air_temperature=scenario.air_temperature,
        air_humidity=scenario.air_humidity,
        co2_ppm=420.0,
        light_intensity=300.0,
    )


def _expected_families(expected_anomalies: list[str]) -> set[str]:
    families: set[str] = set()
    for name in expected_anomalies:
        if name.startswith("soil_moisture"):
            families.add("moisture")
        elif name.startswith("vpd"):
            families.add("vpd")
        elif name.startswith("temperature"):
            families.add("temperature")
    return families


def _actual_families(anomalies) -> set[str]:
    families: set[str] = set()
    for anomaly in anomalies:
        kind = str(anomaly.anomaly_type).lower()
        if "moisture" in kind:
            families.add("moisture")
        elif "vpd" in kind:
            families.add("vpd")
        elif "temperature" in kind:
            families.add("temperature")
    return families


def test_pipeline_matches_anomaly_fixtures():
    base_ts = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)

    for idx, scenario in enumerate(ANOMALY_TEST_SCENARIOS):
        pipeline = EstimatorPipeline()
        ts = base_ts.replace(minute=idx % 60)
        observation = _scenario_observation(ts, scenario)

        _, anomalies, _ = pipeline.process(observation, _device_status(ts))

        expected = _expected_families(scenario.expected_anomalies)
        actual = _actual_families(anomalies)

        if expected:
            assert expected.issubset(actual), (
                f"{scenario.scenario_id}: expected families {expected}, got {actual}"
            )


def test_confidence_degrades_on_fault_patterns():
    ts = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    pipeline = EstimatorPipeline()

    healthy = ObservationV1(
        schema_version="observation_v1",
        timestamp=ts,
        soil_moisture_p1=0.55,
        soil_moisture_p2=0.54,
        air_temperature=22.0,
        air_humidity=65.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )
    healthy_state, _, _ = pipeline.process(healthy, _device_status(ts))

    degraded = ObservationV1(
        schema_version="observation_v1",
        timestamp=ts.replace(minute=30),
        soil_moisture_p1=0.08,
        soil_moisture_p2=None,
        air_temperature=35.0,
        air_humidity=20.0,
        co2_ppm=420.0,
        light_intensity=300.0,
    )
    degraded_state, _, _ = pipeline.process(degraded, _device_status(degraded.timestamp))

    assert degraded_state.confidence < healthy_state.confidence
