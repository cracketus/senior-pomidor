"""Tests for SensorHealthV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import SensorHealthV1
from brain.contracts.sensor_health_v1 import FaultType


class TestSensorHealthV1Valid:
    """Test valid SensorHealthV1 payloads."""

    def test_valid_health_payload(self):
        """Valid sensor health payload should pass validation."""
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
        assert health.schema_version == "sensor_health_v1"
        assert health.fault_state == "none"


class TestSensorHealthV1Invalid:
    """Test invalid SensorHealthV1 payloads."""

    def test_fault_types_are_valid_enum(self):
        """Only valid fault types should be accepted."""
        for fault in FaultType:
            health = SensorHealthV1(
                schema_version="sensor_health_v1",
                timestamp=datetime.now(timezone.utc),
                sensor_name="test_sensor",
                status="healthy",
                confidence=0.9,
                fault_state=fault,
            )
            assert health.fault_state == fault.value

    def test_invalid_fault_type_fails(self):
        """Invalid fault type should fail."""
        with pytest.raises(ValidationError):
            SensorHealthV1(
                schema_version="sensor_health_v1",
                timestamp=datetime.now(timezone.utc),
                sensor_name="test_sensor",
                status="healthy",
                confidence=0.9,
                fault_state="invalid_fault",
            )

    def test_confidence_bounds(self):
        """Confidence must be 0 to 1."""
        with pytest.raises(ValidationError):
            SensorHealthV1(
                schema_version="sensor_health_v1",
                timestamp=datetime.now(timezone.utc),
                sensor_name="test_sensor",
                confidence=1.5,
                fault_state=FaultType.NONE,
            )

    def test_signal_quality_bounds(self):
        """Signal quality must be 0 to 1."""
        with pytest.raises(ValidationError):
            SensorHealthV1(
                schema_version="sensor_health_v1",
                timestamp=datetime.now(timezone.utc),
                sensor_name="test_sensor",
                confidence=0.9,
                fault_state=FaultType.NONE,
                signal_quality=1.5,
            )

    def test_timestamp_without_timezone_fails(self):
        """Timestamp without timezone should fail."""
        with pytest.raises(ValidationError):
            SensorHealthV1(
                schema_version="sensor_health_v1",
                timestamp=datetime.now(),  # No timezone
                sensor_name="test_sensor",
                confidence=0.9,
                fault_state=FaultType.NONE,
            )


class TestSensorHealthV1Serialization:
    """Test serialization and deserialization."""

    def test_roundtrip_dump_and_validate(self):
        """JSON roundtrip should preserve data."""
        original = SensorHealthV1(
            schema_version="sensor_health_v1",
            timestamp=datetime.now(timezone.utc),
            sensor_name="soil_moisture_p2",
            sensor_type="capacitive_probe",
            status="healthy",
            confidence=0.95,
            fault_state=FaultType.NONE,
            last_reading=0.58,
            readings_since_fault=500,
            voltage_mv=3.3,
            signal_quality=0.92,
        )

        json_str = original.model_dump_json()
        restored = SensorHealthV1.model_validate_json(json_str)
        assert restored.sensor_name == original.sensor_name
        assert restored.fault_state == original.fault_state
        assert restored.confidence == original.confidence

    def test_json_schema_export(self):
        """SensorHealthV1 should export valid JSON Schema."""
        schema = SensorHealthV1.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "fault_state" in schema["properties"]
