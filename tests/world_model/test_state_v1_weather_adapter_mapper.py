"""Tests for StateV1 -> weather-adapter mapper."""

from datetime import datetime, timezone

import pytest

from brain.contracts import StateV1
from brain.world_model import map_state_v1_to_weather_adapter_input


def _state(**overrides) -> StateV1:
    payload = {
        "schema_version": "state_v1",
        "timestamp": datetime(2026, 2, 15, 10, 0, tzinfo=timezone.utc),
        "soil_moisture_p1": 0.61,
        "soil_moisture_p2": 0.57,
        "soil_moisture_avg": 0.59,
        "air_temperature": 23.5,
        "air_humidity": 62.0,
        "vpd": 1.1,
        "co2_ppm": 450.0,
        "light_intensity": 320.0,
        "confidence": 0.93,
    }
    payload.update(overrides)
    return StateV1(**payload)


def test_flat_to_nested_mapping():
    state = _state()
    mapped = map_state_v1_to_weather_adapter_input(state)

    assert mapped.schema_version == "weather_adapter_state_input_v1"
    assert mapped.source_schema_version == "state_v1"
    assert mapped.timestamp == state.timestamp
    assert mapped.env.air_temp_c == 23.5
    assert mapped.env.rh_pct == 62.0
    assert mapped.env.vpd_kpa == 1.1
    assert mapped.soil.avg_moisture_pct == 59.0
    assert [probe.probe_id for probe in mapped.soil.probes] == ["p1", "p2"]
    assert [probe.moisture_pct for probe in mapped.soil.probes] == pytest.approx(
        [61.0, 57.0]
    )
    assert mapped.confidence == 0.93


def test_missing_optional_fields_handled():
    state = _state(soil_moisture_p2=None, co2_ppm=None, light_intensity=None)
    mapped = map_state_v1_to_weather_adapter_input(state)

    assert [probe.probe_id for probe in mapped.soil.probes] == ["p1"]
    assert mapped.env.co2_ppm is None
    assert mapped.env.light_umol_m2_s is None
