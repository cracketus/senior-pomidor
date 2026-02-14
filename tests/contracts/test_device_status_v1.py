"""Tests for DeviceStatusV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import DeviceStatusV1


class TestDeviceStatusV1Valid:
    """Test valid DeviceStatusV1 payloads."""

    def test_valid_device_status_passes(self):
        """Valid DeviceStatusV1 payload should pass validation."""
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
        assert device.schema_version == "device_status_v1"
        assert device.light_on is True
        assert device.fans_on is True
        assert device.heater_on is False
        assert device.pump_on is False
        assert device.co2_on is False
        assert device.mcu_connected is True

    def test_minimal_device_status_payload(self):
        """DeviceStatusV1 with only required fields should pass."""
        device = DeviceStatusV1(
            schema_version="device_status_v1",
            timestamp=datetime.now(timezone.utc),
            light_on=False,
            fans_on=False,
            heater_on=False,
            pump_on=False,
            co2_on=False,
            mcu_connected=True,
        )
        assert device.schema_version == "device_status_v1"
        assert device.mcu_uptime_seconds is None
        assert device.mcu_reset_count is None
        assert device.light_intensity_setpoint is None
        assert device.pump_pulse_count is None

    def test_device_status_with_mcu_telemetry(self):
        """DeviceStatusV1 with MCU telemetry should pass."""
        device = DeviceStatusV1(
            schema_version="device_status_v1",
            timestamp=datetime.now(timezone.utc),
            light_on=True,
            fans_on=True,
            heater_on=False,
            pump_on=False,
            co2_on=False,
            mcu_connected=True,
            mcu_uptime_seconds=172800,
            mcu_reset_count=3,
            light_intensity_setpoint=500.0,
            pump_pulse_count=1250,
        )
        assert device.mcu_uptime_seconds == 172800
        assert device.mcu_reset_count == 3
        assert device.light_intensity_setpoint == 500.0
        assert device.pump_pulse_count == 1250

    def test_device_status_all_off_mcu_connected(self):
        """DeviceStatusV1 with all devices off but MCU connected should pass."""
        device = DeviceStatusV1(
            schema_version="device_status_v1",
            timestamp=datetime.now(timezone.utc),
            light_on=False,
            fans_on=False,
            heater_on=False,
            pump_on=False,
            co2_on=False,
            mcu_connected=True,
        )
        assert all(
            not getattr(device, attr)
            for attr in ["light_on", "fans_on", "heater_on", "pump_on", "co2_on"]
        )
        assert device.mcu_connected is True


class TestDeviceStatusV1Invalid:
    """Test invalid DeviceStatusV1 payloads."""

    def test_missing_schema_version_fails(self):
        """Missing schema_version should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceStatusV1(
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
            )
        assert "schema_version" in str(exc_info.value)

    def test_missing_timestamp_fails(self):
        """Missing timestamp should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceStatusV1(
                schema_version="device_status_v1",
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
            )
        assert "timestamp" in str(exc_info.value)

    def test_timestamp_without_timezone_fails(self):
        """Timestamp without timezone should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(),  # No timezone
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
            )
        assert "timezone" in str(exc_info.value).lower()

    def test_invalid_schema_version_fails(self):
        """Invalid schema_version should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceStatusV1(
                schema_version="device_status_v2",
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
            )
        assert "schema_version" in str(exc_info.value)

    def test_missing_light_on_fails(self):
        """Missing light_on should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(timezone.utc),
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
            )
        assert "light_on" in str(exc_info.value)

    def test_missing_mcu_connected_fails(self):
        """Missing mcu_connected should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
            )
        assert "mcu_connected" in str(exc_info.value)

    def test_negative_mcu_uptime_fails(self):
        """Negative MCU uptime should fail validation."""
        with pytest.raises(ValidationError):
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
                mcu_uptime_seconds=-100,  # Negative not allowed
            )

    def test_negative_mcu_reset_count_fails(self):
        """Negative MCU reset count should fail validation."""
        with pytest.raises(ValidationError):
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
                mcu_reset_count=-1,  # Negative not allowed
            )

    def test_negative_pump_pulse_count_fails(self):
        """Negative pump pulse count should fail validation."""
        with pytest.raises(ValidationError):
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
                pump_pulse_count=-50,  # Negative not allowed
            )

    def test_negative_light_intensity_setpoint_fails(self):
        """Negative light intensity setpoint should fail validation."""
        with pytest.raises(ValidationError):
            DeviceStatusV1(
                schema_version="device_status_v1",
                timestamp=datetime.now(timezone.utc),
                light_on=True,
                fans_on=False,
                heater_on=False,
                pump_on=False,
                co2_on=False,
                mcu_connected=True,
                light_intensity_setpoint=-100.0,  # Negative not allowed
            )


class TestDeviceStatusV1Serialization:
    """Test DeviceStatusV1 serialization and deserialization."""

    def test_roundtrip_dump_and_validate(self):
        """DeviceStatusV1 dump -> dict -> load should be stable."""
        original = DeviceStatusV1(
            schema_version="device_status_v1",
            timestamp=datetime.now(timezone.utc),
            light_on=True,
            fans_on=True,
            heater_on=False,
            pump_on=False,
            co2_on=False,
            mcu_connected=True,
            mcu_uptime_seconds=86400,
            mcu_reset_count=2,
        )
        dumped = original.model_dump()
        restored = DeviceStatusV1(**dumped)
        assert restored.schema_version == original.schema_version
        assert restored.timestamp == original.timestamp
        assert restored.light_on == original.light_on
        assert restored.mcu_uptime_seconds == original.mcu_uptime_seconds

    def test_json_schema_export(self):
        """DeviceStatusV1 should export valid JSON Schema."""
        schema = DeviceStatusV1.model_json_schema()
        assert schema is not None
        assert "properties" in schema
        assert "schema_version" in schema["properties"]
        assert "timestamp" in schema["properties"]
        assert "light_on" in schema["properties"]
        assert "fans_on" in schema["properties"]
        assert "heater_on" in schema["properties"]
        assert "pump_on" in schema["properties"]
        assert "co2_on" in schema["properties"]
        assert "mcu_connected" in schema["properties"]
