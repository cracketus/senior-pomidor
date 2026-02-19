"""Tests for weather forecast normalization client."""

from datetime import datetime, timezone

import pytest

from brain.world_model import WeatherClient, normalize_forecast_36h


def test_normalization_maps_and_orders_points_deterministically():
    payload = [
        {
            "ts": "2026-02-15T02:00:00+00:00",
            "temp_c": 8.5,
            "rh_pct": 80.0,
            "wind_mps": 1.5,
            "cloud_cover_pct": 40.0,
        },
        {
            "timestamp": "2026-02-15T01:00:00+00:00",
            "ext_temp_c": 7.0,
            "ext_rh_pct": 82.0,
            "ext_wind_mps": 1.2,
            "ext_solar_wm2": 15.0,
        },
    ]
    generated_at = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)

    forecast_a = normalize_forecast_36h(payload, generated_at=generated_at)
    forecast_b = WeatherClient().normalize(payload, generated_at=generated_at)

    assert forecast_a.model_dump(mode="json") == forecast_b.model_dump(mode="json")
    assert forecast_a.points[0].timestamp.isoformat() == "2026-02-15T01:00:00+00:00"
    assert forecast_a.points[1].timestamp.isoformat() == "2026-02-15T02:00:00+00:00"


def test_normalization_rejects_missing_required_fields():
    payload = [
        {
            "timestamp": "2026-02-15T01:00:00+00:00",
            "ext_rh_pct": 82.0,
            "ext_wind_mps": 1.2,
            "ext_cloud_cover_pct": 50.0,
        }
    ]
    with pytest.raises(ValueError):
        normalize_forecast_36h(payload)


def test_normalization_rejects_empty_points():
    with pytest.raises(ValueError):
        normalize_forecast_36h({"points": []})
