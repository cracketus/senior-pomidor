"""Tests for AnomalyV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import AnomalyV1
from brain.contracts.anomaly_v1 import AnomalyType, SeverityLevel


class TestAnomalyV1Valid:
    """Test valid AnomalyV1 payloads."""

    def test_valid_anomaly_payload(self):
        """Valid anomaly payload should pass validation."""
        anomaly = AnomalyV1(
            schema_version="anomaly_v1",
            timestamp=datetime.now(timezone.utc),
            anomaly_type=AnomalyType.MOISTURE_STRESS,
            severity=SeverityLevel.HIGH,
            affected_sensor="soil_p1",
            description="Soil moisture below minimum",
            confidence=0.95,
            action_recommended=True,
        )
        assert anomaly.schema_version == "anomaly_v1"
        assert anomaly.severity == "high"


class TestAnomalyV1Invalid:
    """Test invalid AnomalyV1 payloads."""

    def test_strict_types_reject_coercion(self):
        """Strict types should reject implicit coercion."""
        # String confidence instead of float
        with pytest.raises(ValidationError):
            AnomalyV1(
                schema_version="anomaly_v1",
                timestamp=datetime.now(timezone.utc),
                anomaly_type=AnomalyType.SENSOR_DISCONNECT,
                severity=SeverityLevel.CRITICAL,
                description="Sensor offline",
                confidence="0.95",  # Should be float, not string
            )

    def test_severity_levels_are_valid(self):
        """Only valid severity levels should be accepted."""
        for severity in SeverityLevel:
            anomaly = AnomalyV1(
                schema_version="anomaly_v1",
                timestamp=datetime.now(timezone.utc),
                anomaly_type=AnomalyType.TEMPERATURE_STRESS,
                severity=severity,
                description="Test anomaly",
                confidence=0.8,
            )
            assert anomaly.severity == severity.value

    def test_invalid_severity_fails(self):
        """Invalid severity level should fail."""
        with pytest.raises(ValidationError):
            AnomalyV1(
                schema_version="anomaly_v1",
                timestamp=datetime.now(timezone.utc),
                anomaly_type=AnomalyType.SENSOR_DRIFT,
                severity="invalid_severity",
                description="Test",
                confidence=0.8,
            )

    def test_timestamp_without_timezone_fails(self):
        """Timestamp without timezone should fail."""
        with pytest.raises(ValidationError):
            AnomalyV1(
                schema_version="anomaly_v1",
                timestamp=datetime.now(),  # No timezone
                anomaly_type=AnomalyType.SENSOR_STUCK,
                severity=SeverityLevel.MEDIUM,
                description="Sensor stuck",
                confidence=0.85,
            )

    def test_confidence_bounds(self):
        """Confidence must be 0 to 1."""
        with pytest.raises(ValidationError):
            AnomalyV1(
                schema_version="anomaly_v1",
                timestamp=datetime.now(timezone.utc),
                anomaly_type=AnomalyType.WIND_SPIKE,
                severity=SeverityLevel.LOW,
                description="Wind detected",
                confidence=1.5,
            )


class TestAnomalyV1Serialization:
    """Test serialization and deserialization."""

    def test_roundtrip_dump_and_validate(self):
        """JSON roundtrip should preserve data."""
        original = AnomalyV1(
            schema_version="anomaly_v1",
            timestamp=datetime.now(timezone.utc),
            anomaly_type=AnomalyType.MCU_RESET,
            severity=SeverityLevel.HIGH,
            affected_sensor="mcu",
            description="MCU has reset",
            confidence=0.99,
            action_recommended=True,
            requires_safe_mode=True,
        )

        json_str = original.model_dump_json()
        restored = AnomalyV1.model_validate_json(json_str)
        assert restored.anomaly_type == original.anomaly_type
        assert restored.requires_safe_mode == original.requires_safe_mode

    def test_json_schema_export(self):
        """AnomalyV1 should export valid JSON Schema."""
        schema = AnomalyV1.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "severity" in schema["properties"]
