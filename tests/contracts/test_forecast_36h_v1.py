"""Tests for forecast_36h_v1 contract."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import Forecast36hV1
from brain.contracts.forecast_36h_v1 import ForecastPointV1


def _point(ts: datetime, *, cloud: float | None = 50.0, solar: float | None = None) -> ForecastPointV1:
    return ForecastPointV1(
        timestamp=ts,
        ext_temp_c=12.5,
        ext_rh_pct=70.0,
        ext_wind_mps=2.1,
        ext_cloud_cover_pct=cloud,
        ext_solar_wm2=solar,
    )


def test_valid_forecast_contract_passes():
    base = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    forecast = Forecast36hV1(
        schema_version="forecast_36h_v1",
        generated_at=base,
        source="test",
        timezone="Europe/Vienna",
        freq_minutes=60,
        horizon_hours=36,
        points=[_point(base), _point(base + timedelta(hours=1))],
    )
    assert forecast.schema_version == "forecast_36h_v1"
    assert len(forecast.points) == 2


def test_point_requires_cloud_or_solar():
    base = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        ForecastPointV1(
            timestamp=base,
            ext_temp_c=10.0,
            ext_rh_pct=70.0,
            ext_wind_mps=2.0,
            ext_cloud_cover_pct=None,
            ext_solar_wm2=None,
        )


def test_forecast_requires_ordered_timestamps():
    base = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        Forecast36hV1(
            schema_version="forecast_36h_v1",
            generated_at=base,
            source="test",
            timezone="Europe/Vienna",
            freq_minutes=60,
            horizon_hours=36,
            points=[_point(base + timedelta(hours=1)), _point(base)],
        )
