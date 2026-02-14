"""StateV1: Estimated plant state with sensor readings and confidence scores."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StateV1(BaseModel):
    """
    Estimated plant state from State Estimator Agent.

    Represents a snapshot of plant health, environmental conditions, and sensor confidence.
    Includes multi-sensor fusion results and derived metrics.

    Example:
        ```python
        state = StateV1(
            schema_version="state_v1",
            timestamp=datetime.now(timezone.utc),
            soil_moisture_p1=0.65,
            soil_moisture_p2=0.58,
            soil_moisture_avg=0.615,
            air_temperature=22.5,
            air_humidity=65.0,
            vpd=1.2,
            co2_ppm=420,
            light_intensity=450,
            confidence=0.92,
        )
        ```
    """

    model_config = ConfigDict(
        ser_json_timedelta="float",
        strict=True,
    )

    # Contract metadata
    schema_version: str = Field(
        description="Schema version identifier. Must be 'state_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when this state was estimated."
    )

    # Soil moisture (multi-probe)
    soil_moisture_p1: float = Field(
        ge=0.0,
        le=1.0,
        description="Soil moisture at probe 1 (0.0=dry, 1.0=saturated).",
    )
    soil_moisture_p2: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Soil moisture at probe 2. None if not available.",
    )
    soil_moisture_avg: float = Field(
        ge=0.0,
        le=1.0,
        description="Average soil moisture across all probes.",
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

    # Derived metrics
    vpd: float = Field(
        ge=0.0,
        description="Vapor Pressure Deficit (kPa) computed from temperature and humidity.",
    )
    co2_ppm: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="CO2 concentration in ppm. None if not measured.",
    )
    light_intensity: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Light intensity (umol/m²/s). None if not measured.",
    )

    # Confidence and health
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="State estimate confidence (0.0=unreliable, 1.0=fully trusted). "
        "Reflects sensor health, data freshness, and fusion quality.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional human-readable notes or warnings.",
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
        """Ensure schema_version is exactly 'state_v1'."""
        if v != "state_v1":
            raise ValueError(
                f"schema_version must be 'state_v1', got '{v}'"
            )
        return v
