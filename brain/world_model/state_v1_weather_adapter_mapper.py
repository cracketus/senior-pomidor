"""Bridge mapper from flat StateV1 to weather-adapter nested input."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from brain.contracts import StateV1


class WeatherAdapterProbeV1(BaseModel):
    """Single soil probe payload for weather-adapter input."""

    model_config = ConfigDict(strict=True)

    probe_id: str = Field(description="Probe identifier (for example p1, p2).")
    moisture_pct: float = Field(
        ge=0.0,
        le=100.0,
        description="Probe moisture in percent (0-100).",
    )


class WeatherAdapterEnvV1(BaseModel):
    """Nested environmental data expected by weather adapter."""

    model_config = ConfigDict(strict=True)

    air_temp_c: float = Field(description="Air temperature in Celsius.")
    rh_pct: float = Field(
        ge=0.0,
        le=100.0,
        description="Relative humidity percentage (0-100).",
    )
    vpd_kpa: float = Field(
        ge=0.0,
        description="Vapor Pressure Deficit in kPa.",
    )
    co2_ppm: float | None = Field(
        default=None,
        ge=0.0,
        description="CO2 concentration in ppm.",
    )
    light_umol_m2_s: float | None = Field(
        default=None,
        ge=0.0,
        description="Light intensity in umol/m^2/s.",
    )


class WeatherAdapterSoilV1(BaseModel):
    """Nested soil data expected by weather adapter."""

    model_config = ConfigDict(strict=True)

    avg_moisture_pct: float = Field(
        ge=0.0,
        le=100.0,
        description="Average soil moisture in percent (0-100).",
    )
    probes: list[WeatherAdapterProbeV1] = Field(
        min_length=1,
        description="Available soil probe measurements.",
    )


class WeatherAdapterStateInputV1(BaseModel):
    """Normalized state payload consumed by Stage 3 weather adapter."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["weather_adapter_state_input_v1"]
    source_schema_version: Literal["state_v1"]
    timestamp: datetime = Field(
        description="ISO8601 timestamp with timezone, copied from StateV1.",
    )
    env: WeatherAdapterEnvV1
    soil: WeatherAdapterSoilV1
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="State-level confidence copied from StateV1.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, value: datetime) -> datetime:
        """Ensure timestamp is timezone-aware."""
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone info")
        return value


def map_state_v1_to_weather_adapter_input(
    state: StateV1,
) -> WeatherAdapterStateInputV1:
    """
    Map flat StateV1 fields to nested weather-adapter schema.

    This function performs post-map validation by constructing
    `WeatherAdapterStateInputV1` before returning.
    """
    probes = [
        WeatherAdapterProbeV1(
            probe_id="p1",
            moisture_pct=state.soil_moisture_p1 * 100.0,
        )
    ]
    if state.soil_moisture_p2 is not None:
        probes.append(
            WeatherAdapterProbeV1(
                probe_id="p2",
                moisture_pct=state.soil_moisture_p2 * 100.0,
            )
        )

    return WeatherAdapterStateInputV1(
        schema_version="weather_adapter_state_input_v1",
        source_schema_version="state_v1",
        timestamp=state.timestamp,
        env=WeatherAdapterEnvV1(
            air_temp_c=state.air_temperature,
            rh_pct=state.air_humidity,
            vpd_kpa=state.vpd,
            co2_ppm=state.co2_ppm,
            light_umol_m2_s=state.light_intensity,
        ),
        soil=WeatherAdapterSoilV1(
            avg_moisture_pct=state.soil_moisture_avg * 100.0,
            probes=probes,
        ),
        confidence=state.confidence,
    )
