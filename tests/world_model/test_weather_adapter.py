"""Tests for Stage 3 weather adapter baseline."""

from datetime import datetime, timedelta, timezone

from brain.contracts import Forecast36hV1, StateV1
from brain.contracts.forecast_36h_v1 import ForecastPointV1
from brain.world_model import WeatherAdapter, map_state_v1_to_weather_adapter_input


def _forecast(points: list[ForecastPointV1]) -> Forecast36hV1:
    return Forecast36hV1(
        schema_version="forecast_36h_v1",
        generated_at=datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc),
        source="test",
        timezone="Europe/Vienna",
        freq_minutes=60,
        horizon_hours=36,
        points=points,
    )


def _state() -> StateV1:
    return StateV1(
        schema_version="state_v1",
        timestamp=datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc),
        soil_moisture_p1=0.5,
        soil_moisture_p2=0.52,
        soil_moisture_avg=0.51,
        air_temperature=24.0,
        air_humidity=60.0,
        vpd=1.2,
        co2_ppm=420.0,
        light_intensity=300.0,
        confidence=0.9,
    )


def test_weather_adapter_routes_high_risk_scenarios_and_overrides():
    base_ts = datetime(2026, 2, 15, 1, 0, tzinfo=timezone.utc)
    forecast = _forecast(
        [
            ForecastPointV1(
                timestamp=base_ts,
                ext_temp_c=33.0,
                ext_rh_pct=30.0,
                ext_wind_mps=12.0,
                ext_cloud_cover_pct=20.0,
            ),
            ForecastPointV1(
                timestamp=base_ts + timedelta(hours=1),
                ext_temp_c=31.0,
                ext_rh_pct=40.0,
                ext_wind_mps=4.0,
                ext_cloud_cover_pct=30.0,
            ),
        ]
    )
    adapter = WeatherAdapter()
    state_input = map_state_v1_to_weather_adapter_input(_state())

    result = adapter.apply(forecast, state_input)

    assert "heatwave" in result.targets.active_scenarios
    assert "dry_inflow" in result.targets.active_scenarios
    assert "wind_spike" in result.targets.active_scenarios
    assert result.sampling_plan.overrides
    assert result.targets.adapted_targets.vpd_max_kpa < result.targets.base_targets.vpd_max_kpa


def test_weather_adapter_noop_window_keeps_base_targets():
    base_ts = datetime(2026, 2, 15, 1, 0, tzinfo=timezone.utc)
    forecast = _forecast(
        [
            ForecastPointV1(
                timestamp=base_ts,
                ext_temp_c=24.0,
                ext_rh_pct=55.0,
                ext_wind_mps=3.0,
                ext_cloud_cover_pct=40.0,
            ),
            ForecastPointV1(
                timestamp=base_ts + timedelta(hours=1),
                ext_temp_c=23.0,
                ext_rh_pct=58.0,
                ext_wind_mps=2.0,
                ext_cloud_cover_pct=45.0,
            ),
        ]
    )
    adapter = WeatherAdapter()
    state_input = map_state_v1_to_weather_adapter_input(_state())

    result = adapter.apply(forecast, state_input)

    assert result.targets.active_scenarios == []
    assert result.targets.base_targets == result.targets.adapted_targets
    assert result.sampling_plan.overrides == []


def test_weather_adapter_is_deterministic_for_identical_inputs():
    base_ts = datetime(2026, 2, 15, 1, 0, tzinfo=timezone.utc)
    forecast = _forecast(
        [
            ForecastPointV1(
                timestamp=base_ts,
                ext_temp_c=33.0,
                ext_rh_pct=30.0,
                ext_wind_mps=12.0,
                ext_cloud_cover_pct=20.0,
            )
        ]
    )
    adapter = WeatherAdapter()
    state_input = map_state_v1_to_weather_adapter_input(_state())
    now = datetime(2026, 2, 15, 0, 30, tzinfo=timezone.utc)

    a = adapter.apply(forecast, state_input, now=now)
    b = adapter.apply(forecast, state_input, now=now)

    assert a.targets.model_dump(mode="json") == b.targets.model_dump(mode="json")
    assert a.sampling_plan.model_dump(mode="json") == b.sampling_plan.model_dump(mode="json")
    assert a.log.model_dump(mode="json") == b.log.model_dump(mode="json")
