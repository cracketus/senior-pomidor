"""AnomalyV1: Detected anomalies with severity and context."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SeverityLevel(str, Enum):
    """Anomaly severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    """Types of detectable anomalies."""

    SENSOR_DISCONNECT = "sensor_disconnect"
    SENSOR_STUCK = "sensor_stuck"
    SENSOR_DRIFT = "sensor_drift"
    SENSOR_JUMP = "sensor_jump"
    MOISTURE_STRESS = "moisture_stress"
    TEMPERATURE_STRESS = "temperature_stress"
    VPD_OUT_OF_RANGE = "vpd_out_of_range"
    DEVICE_OFFLINE = "device_offline"
    MCU_RESET = "mcu_reset"
    WIND_SPIKE = "wind_spike"
    UNKNOWN = "unknown"


class AnomalyV1(BaseModel):
    """
    Detected anomaly event from State Estimator Agent.

    Represents an unusual condition that may warrant immediate action or investigation.
    Triggers event-driven mode in the scheduler.

    Example:
        ```python
        anomaly = AnomalyV1(
            schema_version="anomaly_v1",
            timestamp=datetime.now(timezone.utc),
            anomaly_type=AnomalyType.MOISTURE_STRESS,
            severity=SeverityLevel.HIGH,
            affected_sensor="soil_p1",
            description="Soil moisture p1 dropped below minimum threshold",
            confidence=0.95,
            action_recommended=True,
        )
        ```
    """

    model_config = ConfigDict(
        use_enum_values=True,
        strict=True,
    )

    # Contract metadata
    schema_version: str = Field(
        description="Schema version identifier. Must be 'anomaly_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when anomaly was detected."
    )

    # Anomaly identification
    anomaly_type: AnomalyType = Field(
        description="Type of anomaly detected (sensor fault, stress, offline, etc)."
    )
    severity: SeverityLevel = Field(
        description="Severity level: low, medium, high, critical."
    )
    affected_sensor: Optional[str] = Field(
        default=None,
        description="Name of the affected sensor (e.g., 'soil_p1', 'air_temp'). "
        "None if not sensor-specific.",
    )

    # Context and justification
    description: str = Field(
        description="Human-readable description of the anomaly and its context."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that this is a real anomaly (0.0=noise, 1.0=certain).",
    )
    action_recommended: bool = Field(
        default=False,
        description="True if immediate operator action is recommended.",
    )

    # Recovery context
    expected_duration_seconds: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Expected duration of anomaly in seconds. None if unknown.",
    )
    requires_safe_mode: bool = Field(
        default=False,
        description="True if system should enter Safe Mode (disable risky actions).",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes or recovery suggestions.",
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
        """Ensure schema_version is exactly 'anomaly_v1'."""
        if v != "anomaly_v1":
            raise ValueError(
                f"schema_version must be 'anomaly_v1', got '{v}'"
            )
        return v
