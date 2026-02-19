"""Forecast36hV1: normalized weather forecast contract for Stage 3 ingestion."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ForecastPointV1(BaseModel):
    """Single forecast point at a fixed cadence."""

    model_config = ConfigDict(strict=True)

    timestamp: datetime = Field(
        description="ISO8601 timestamp for this forecast point.",
    )
    ext_temp_c: float = Field(description="External air temperature in Celsius.")
    ext_rh_pct: float = Field(
        ge=0.0,
        le=100.0,
        description="External relative humidity percentage (0-100).",
    )
    ext_wind_mps: float = Field(
        ge=0.0,
        description="External wind speed in m/s.",
    )
    ext_cloud_cover_pct: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="External cloud cover percentage (0-100).",
    )
    ext_solar_wm2: float | None = Field(
        default=None,
        ge=0.0,
        description="External solar radiation in W/m^2.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, value: datetime) -> datetime:
        """Ensure forecast timestamps are timezone-aware."""
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone info")
        return value

    @model_validator(mode="after")
    def validate_cloud_or_solar_present(self) -> "ForecastPointV1":
        """At least one sky/solar signal must be present."""
        if self.ext_cloud_cover_pct is None and self.ext_solar_wm2 is None:
            raise ValueError("either ext_cloud_cover_pct or ext_solar_wm2 must be provided")
        return self


class Forecast36hV1(BaseModel):
    """Normalized weather forecast for Stage 3 world-model ingestion."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["forecast_36h_v1"]
    generated_at: datetime = Field(
        description="Timestamp when forecast normalization was produced.",
    )
    source: str = Field(description="Source name for normalized forecast data.")
    timezone: str = Field(description="IANA timezone name for timestamps.")
    freq_minutes: int = Field(
        ge=1,
        description="Forecast cadence in minutes (typically 60).",
    )
    horizon_hours: int = Field(
        ge=1,
        le=36,
        description="Forecast horizon in hours.",
    )
    points: list[ForecastPointV1] = Field(
        min_length=1,
        max_length=36,
        description="Ordered forecast points for the horizon.",
    )

    @field_validator("generated_at")
    @classmethod
    def validate_generated_at_has_timezone(cls, value: datetime) -> datetime:
        """Ensure generated_at is timezone-aware."""
        if value.tzinfo is None:
            raise ValueError("generated_at must include timezone info")
        return value

    @model_validator(mode="after")
    def validate_points_are_ordered(self) -> "Forecast36hV1":
        """Forecast points must be strictly ordered by timestamp."""
        if len(self.points) < 2:
            return self
        for prev, curr in zip(self.points, self.points[1:]):
            if curr.timestamp <= prev.timestamp:
                raise ValueError("points must be strictly ordered by timestamp")
        return self
