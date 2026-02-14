"""SensorHealthV1: Per-sensor diagnostics and fault detection."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FaultType(str, Enum):
    """Types of sensor faults."""

    NONE = "none"
    DISCONNECTED = "disconnected"
    STUCK = "stuck"
    DRIFT = "drift"
    JUMP = "jump"
    OUT_OF_RANGE = "out_of_range"
    INTERMITTENT = "intermittent"
    UNKNOWN = "unknown"


class SensorHealthV1(BaseModel):
    """
    Per-sensor diagnostic information and fault detection status.

    Emitted by State Estimator Agent as part of state update.
    Tracks confidence, fault history, and sensor-specific metadata.

    Example:
        ```python
        health = SensorHealthV1(
            schema_version="sensor_health_v1",
            timestamp=datetime.now(timezone.utc),
            sensor_name="soil_moisture_p1",
            sensor_type="capacitive_probe",
            status="healthy",
            confidence=0.98,
            fault_state=FaultType.NONE,
            last_reading=0.625,
            readings_since_fault=245,
            voltage_mv=3.2,
        )
        ```
    """

    model_config = ConfigDict(
        use_enum_values=True,
        strict=True,
    )

    # Contract metadata
    schema_version: str = Field(
        description="Schema version identifier. Must be 'sensor_health_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when diagnostics were computed."
    )

    # Sensor identification
    sensor_name: str = Field(
        description="Unique sensor identifier (e.g., 'soil_moisture_p1', 'air_temp')."
    )
    sensor_type: Optional[str] = Field(
        default=None,
        description="Sensor hardware type (e.g., 'capacitive_probe', 'DHT22'). "
        "None if unknown.",
    )

    # Health status
    status: str = Field(
        description="Health status: 'healthy', 'degraded', 'failed'."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in readings from this sensor (0.0=unreliable, 1.0=trustworthy).",
    )
    fault_state: FaultType = Field(
        description="Current fault type: none, disconnected, stuck, drift, jump, etc."
    )

    # Diagnostic metrics
    last_reading: Optional[float] = Field(
        default=None,
        description="Last raw sensor value. None if sensor offline.",
    )
    readings_since_fault: int = Field(
        default=0,
        ge=0,
        description="Number of successful readings since last detected fault (recovery indicator).",
    )
    consecutive_failures: int = Field(
        default=0,
        ge=0,
        description="Number of consecutive failed reads (escalation indicator).",
    )

    # Hardware diagnostics
    voltage_mv: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Sensor supply voltage in millivolts. None if not available.",
    )
    signal_quality: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Signal quality metric (0.0=poor, 1.0=excellent). "
        "None if not applicable.",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional diagnostic notes or recommendations.",
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
        """Ensure schema_version is exactly 'sensor_health_v1'."""
        if v != "sensor_health_v1":
            raise ValueError(
                f"schema_version must be 'sensor_health_v1', got '{v}'"
            )
        return v
