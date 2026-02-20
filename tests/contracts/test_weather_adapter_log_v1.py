"""Tests for weather_adapter_log_v1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts.targets_v1 import TargetEnvelopeV1
from brain.contracts.weather_adapter_log_v1 import WeatherAdapterLogV1


def test_weather_adapter_log_valid_payload():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    log = WeatherAdapterLogV1(
        schema_version="weather_adapter_log_v1",
        timestamp=now,
        forecast_ref="forecast_36h_v1",
        state_ref="state_v1",
        matched_scenarios=["heatwave"],
        applied_changes=["heatwave:lower_vpd_max_raise_soil_min"],
        guardrail_clips=[],
        final_targets=TargetEnvelopeV1(
            vpd_min_kpa=0.8,
            vpd_max_kpa=1.3,
            soil_moisture_min_pct=40.0,
            soil_moisture_max_pct=75.0,
        ),
    )
    assert log.schema_version == "weather_adapter_log_v1"


def test_weather_adapter_log_requires_timezone():
    with pytest.raises(ValidationError):
        WeatherAdapterLogV1(
            schema_version="weather_adapter_log_v1",
            timestamp=datetime(2026, 2, 15, 0, 0),
            forecast_ref="forecast_36h_v1",
            state_ref="state_v1",
            final_targets=TargetEnvelopeV1(
                vpd_min_kpa=0.8,
                vpd_max_kpa=1.3,
                soil_moisture_min_pct=40.0,
                soil_moisture_max_pct=75.0,
            ),
        )
