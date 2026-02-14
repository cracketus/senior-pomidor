"""Tests for StateV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import StateV1


class TestStateV1Valid:
    """Test valid StateV1 payloads."""

    def test_valid_state_payload_passes(self):
        """Valid StateV1 payload should pass validation."""
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
        assert state.schema_version == "state_v1"
        assert state.confidence == 0.92
        assert state.soil_moisture_p1 == 0.65

    def test_minimal_state_payload(self):
        """StateV1 with only required fields should pass."""
        state = StateV1(
            schema_version="state_v1",
            timestamp=datetime.now(timezone.utc),
            soil_moisture_p1=0.5,
            soil_moisture_avg=0.5,
            air_temperature=20.0,
            air_humidity=50.0,
            vpd=1.0,
            confidence=0.8,
        )
        assert state.schema_version == "state_v1"
        assert state.soil_moisture_p2 is None
        assert state.co2_ppm is None


class TestStateV1Invalid:
    """Test invalid StateV1 payloads."""

    def test_missing_schema_version_fails(self):
        """Missing schema_version should fail validation."""
        with pytest.raises(ValidationError):
            StateV1(
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                vpd=1.0,
                confidence=0.8,
            )

    def test_wrong_schema_version_fails(self):
        """Wrong schema_version should fail validation."""
        with pytest.raises(ValidationError):
            StateV1(
                schema_version="state_v2",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                vpd=1.0,
                confidence=0.8,
            )

    def test_timestamp_without_timezone_fails(self):
        """Timestamp without timezone info should fail."""
        with pytest.raises(ValidationError):
            StateV1(
                schema_version="state_v1",
                timestamp=datetime.now(),  # No timezone
                soil_moisture_p1=0.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                vpd=1.0,
                confidence=0.8,
            )

    def test_confidence_field_is_float_0_to_1(self):
        """Confidence must be between 0.0 and 1.0."""
        # Too high
        with pytest.raises(ValidationError):
            StateV1(
                schema_version="state_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                vpd=1.0,
                confidence=1.5,
            )

        # Too low
        with pytest.raises(ValidationError):
            StateV1(
                schema_version="state_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                vpd=1.0,
                confidence=-0.1,
            )

    def test_soil_moisture_bounds(self):
        """Soil moisture must be between 0.0 and 1.0."""
        with pytest.raises(ValidationError):
            StateV1(
                schema_version="state_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=1.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                vpd=1.0,
                confidence=0.8,
            )

    def test_humidity_bounds(self):
        """Humidity must be between 0 and 100."""
        with pytest.raises(ValidationError):
            StateV1(
                schema_version="state_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                soil_moisture_avg=0.5,
                air_temperature=20.0,
                air_humidity=105.0,
                vpd=1.0,
                confidence=0.8,
            )


class TestStateV1Serialization:
    """Test serialization and deserialization."""

    def test_roundtrip_dump_and_validate(self):
        """JSON roundtrip should preserve data and still validate."""
        original = StateV1(
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

        # Serialize to JSON
        json_str = original.model_dump_json()
        assert isinstance(json_str, str)

        # Deserialize back
        restored = StateV1.model_validate_json(json_str)
        assert restored.confidence == original.confidence
        assert restored.soil_moisture_p1 == original.soil_moisture_p1
        assert restored.timestamp == original.timestamp

    def test_json_schema_export(self):
        """StateV1 should export valid JSON Schema."""
        schema = StateV1.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "confidence" in schema["properties"]
        assert "soil_moisture_p1" in schema["properties"]
        assert "timestamp" in schema["properties"]
