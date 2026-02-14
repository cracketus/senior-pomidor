"""ObservationV1: Raw sensor readings from observation sources (synthetic or replay)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ObservationV1(BaseModel):
    """
    Raw sensor observation from Observation Source Agent.

    Represents unprocessed sensor readings at a point in time. Sources (synthetic
    or replay) emit ObservationV1 records that feed into the State Estimator.

    Designed to support:
    - Multiple soil moisture probes (P1, P2)
    - Air temperature and relative humidity
    - CO2 concentration
    - Light intensity / photosynthetically active radiation (PAR)

    Example:
        ```python
        obs = ObservationV1(
            schema_version="observation_v1",
            timestamp=datetime.now(timezone.utc),
            soil_moisture_p1=0.62,
            soil_moisture_p2=0.58,
            air_temperature=22.3,
            air_humidity=64.5,
            co2_ppm=415.0,
            light_intensity=420.5,
        )
        ```
    """

    model_config = ConfigDict(
        ser_json_timedelta="float",
        strict=True,
    )

    # Contract metadata
    schema_version: str = Field(
        description="Schema version identifier. Must be 'observation_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when this observation was recorded."
    )

    # Soil moisture probes
    soil_moisture_p1: float = Field(
        ge=0.0,
        le=1.0,
        description="Soil moisture at probe 1 (0.0=dry, 1.0=saturated).",
    )
    soil_moisture_p2: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Soil moisture at probe 2. None if probe not present or reading unavailable.",
    )

    # Air conditions
    air_temperature: float = Field(
        description="Air temperature in degrees Celsius."
    )
    air_humidity: float = Field(
        ge=0.0,
        le=100.0,
        description="Relative humidity as percentage (0-100).",
    )

    # Optional gas / light sensors
    co2_ppm: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="CO2 concentration in ppm. None if not measured.",
    )
    light_intensity: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Light intensity or PAR (umol/m²/s). None if not measured.",
    )

    # Sensor quality indicators (optional)
    sensor_faults: Optional[dict[str, bool]] = Field(
        default=None,
        description="Dictionary of sensor fault flags "
        "(e.g., {'soil_p1': False, 'air_temp': True}). "
        "None if not tracked at source level.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, v: datetime) -> datetime:
        """Ensure timestamp has timezone info (must be aware)."""
        if v.tzinfo is None:
            raise ValueError(
                "timestamp must include timezone info. Use datetime.now(timezone.utc)"
            )
        return v

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Ensure schema_version is exactly 'observation_v1'."""
        if v != "observation_v1":
            raise ValueError(
                f"schema_version must be 'observation_v1', got '{v}'"
            )
        return v
