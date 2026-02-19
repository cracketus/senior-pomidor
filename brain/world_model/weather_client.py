"""Weather forecast normalization utilities for Stage 3."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from brain.contracts import Forecast36hV1
from brain.contracts.forecast_36h_v1 import ForecastPointV1


def _parse_datetime(value: Any, field_name: str) -> datetime:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"Invalid datetime for {field_name}: {value}") from exc
    else:
        raise ValueError(f"Missing or invalid datetime field: {field_name}")

    if dt.tzinfo is None:
        raise ValueError(f"Datetime field must include timezone: {field_name}")
    return dt


def _pick_float(item: dict[str, Any], keys: list[str], field_name: str) -> float | None:
    for key in keys:
        if key in item and item[key] is not None:
            try:
                return float(item[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value for {field_name}: {item[key]}") from exc
    return None


def _normalize_row(item: dict[str, Any]) -> ForecastPointV1:
    timestamp_raw = item.get("timestamp", item.get("ts", item.get("time")))
    timestamp = _parse_datetime(timestamp_raw, "timestamp")

    ext_temp_c = _pick_float(item, ["ext_temp_c", "temp_c", "temperature_c"], "ext_temp_c")
    ext_rh_pct = _pick_float(item, ["ext_rh_pct", "rh_pct", "humidity_pct"], "ext_rh_pct")
    ext_wind_mps = _pick_float(item, ["ext_wind_mps", "wind_mps", "wind_speed_mps"], "ext_wind_mps")
    ext_cloud_cover_pct = _pick_float(
        item, ["ext_cloud_cover_pct", "cloud_cover_pct", "cloud_pct"], "ext_cloud_cover_pct"
    )
    ext_solar_wm2 = _pick_float(item, ["ext_solar_wm2", "solar_wm2"], "ext_solar_wm2")

    if ext_temp_c is None:
        raise ValueError("Missing required temperature field for forecast row")
    if ext_rh_pct is None:
        raise ValueError("Missing required humidity field for forecast row")
    if ext_wind_mps is None:
        raise ValueError("Missing required wind field for forecast row")

    return ForecastPointV1(
        timestamp=timestamp,
        ext_temp_c=ext_temp_c,
        ext_rh_pct=ext_rh_pct,
        ext_wind_mps=ext_wind_mps,
        ext_cloud_cover_pct=ext_cloud_cover_pct,
        ext_solar_wm2=ext_solar_wm2,
    )


def normalize_forecast_36h(
    raw_payload: list[dict[str, Any]] | dict[str, Any],
    *,
    source: str = "weather_stub",
    timezone_name: str = "Europe/Vienna",
    freq_minutes: int = 60,
    horizon_hours: int = 36,
    generated_at: datetime | None = None,
) -> Forecast36hV1:
    """Normalize raw weather payload into strict `forecast_36h_v1` contract."""
    if freq_minutes <= 0:
        raise ValueError("freq_minutes must be positive")
    if horizon_hours <= 0:
        raise ValueError("horizon_hours must be positive")

    points_input = raw_payload.get("points") if isinstance(raw_payload, dict) else raw_payload
    if not isinstance(points_input, list) or not points_input:
        raise ValueError("raw_payload must contain a non-empty list of forecast points")

    normalized_points = [_normalize_row(item) for item in points_input]
    normalized_points.sort(key=lambda p: p.timestamp)

    max_points = max(1, int((horizon_hours * 60) / freq_minutes))
    normalized_points = normalized_points[:max_points]

    resolved_generated_at = generated_at or datetime.now(timezone.utc)
    if resolved_generated_at.tzinfo is None:
        raise ValueError("generated_at must include timezone info")

    return Forecast36hV1(
        schema_version="forecast_36h_v1",
        generated_at=resolved_generated_at,
        source=source,
        timezone=timezone_name,
        freq_minutes=freq_minutes,
        horizon_hours=min(horizon_hours, 36),
        points=normalized_points,
    )


class WeatherClient:
    """Deterministic normalization facade for Stage 3 weather ingestion."""

    def normalize(
        self,
        raw_payload: list[dict[str, Any]] | dict[str, Any],
        *,
        source: str = "weather_stub",
        timezone_name: str = "Europe/Vienna",
        freq_minutes: int = 60,
        horizon_hours: int = 36,
        generated_at: datetime | None = None,
    ) -> Forecast36hV1:
        return normalize_forecast_36h(
            raw_payload,
            source=source,
            timezone_name=timezone_name,
            freq_minutes=freq_minutes,
            horizon_hours=horizon_hours,
            generated_at=generated_at,
        )
