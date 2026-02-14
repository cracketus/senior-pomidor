"""DeviceStatusV1: Device ON/OFF states and telemetry from observation sources."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceStatusV1(BaseModel):
    """
    Device state telemetry from Observation Source Agent.

    Tracks ON/OFF states, uptime, and operational telemetry for all controllable
    and monitorable devices: lighting, ventilation, heating, watering, CO2 injection,
    and MCU connectivity.

    These records accompany observations and feed into State Estimator and health
    monitoring.

    Example:
        ```python
        device = DeviceStatusV1(
            schema_version="device_status_v1",
            timestamp=datetime.now(timezone.utc),
            light_on=True,
            fans_on=True,
            heater_on=False,
            pump_on=False,
            co2_on=False,
            mcu_connected=True,
            mcu_uptime_seconds=86400,
        )
        ```
    """

    model_config = ConfigDict(
        ser_json_timedelta="float",
        strict=True,
    )

    # Contract metadata
    schema_version: str = Field(
        description="Schema version identifier. Must be 'device_status_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when this device status was recorded."
    )

    # Device ON/OFF states
    light_on: bool = Field(
        description="Lighting system is ON (True) or OFF (False)."
    )
    fans_on: bool = Field(
        description="Ventilation fans are ON (True) or OFF (False)."
    )
    heater_on: bool = Field(
        description="Heater is ON (True) or OFF (False)."
    )
    pump_on: bool = Field(
        description="Water pump is ON (True) or OFF (False)."
    )
    co2_on: bool = Field(
        description="CO2 injection is ON (True) or OFF (False)."
    )

    # MCU telemetry
    mcu_connected: bool = Field(
        description="MCU is connected and communicating (True) or disconnected (False)."
    )
    mcu_uptime_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="MCU uptime in seconds since last reset. None if not available.",
    )
    mcu_reset_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of MCU resets since power-on or epoch. None if not tracked.",
    )

    # Additional telemetry (optional)
    light_intensity_setpoint: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Current light intensity setpoint/dimmer level. None if N/A.",
    )
    pump_pulse_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Cumulative water pump pulse count. None if not tracked.",
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
        """Ensure schema_version is exactly 'device_status_v1'."""
        if v != "device_status_v1":
            raise ValueError(
                f"schema_version must be 'device_status_v1', got '{v}'"
            )
        return v
