"""Tests for ObservationV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import ObservationV1


class TestObservationV1Valid:
    """Test valid ObservationV1 payloads."""

    def test_valid_observation_passes(self):
        """Valid ObservationV1 payload should pass validation."""
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
        assert obs.schema_version == "observation_v1"
        assert obs.soil_moisture_p1 == 0.62
        assert obs.soil_moisture_p2 == 0.58
        assert obs.air_temperature == 22.3
        assert obs.air_humidity == 64.5

    def test_minimal_observation_payload(self):
        """ObservationV1 with only required fields should pass."""
        obs = ObservationV1(
            schema_version="observation_v1",
            timestamp=datetime.now(timezone.utc),
            soil_moisture_p1=0.5,
            air_temperature=20.0,
            air_humidity=50.0,
        )
        assert obs.schema_version == "observation_v1"
        assert obs.soil_moisture_p1 == 0.5
        assert obs.soil_moisture_p2 is None
        assert obs.co2_ppm is None
        assert obs.light_intensity is None

    def test_observation_with_sensor_faults(self):
        """ObservationV1 with sensor fault flags should pass."""
        obs = ObservationV1(
            schema_version="observation_v1",
            timestamp=datetime.now(timezone.utc),
            soil_moisture_p1=0.5,
            air_temperature=20.0,
            air_humidity=50.0,
            sensor_faults={"soil_p1": False, "air_temp": True},
        )
        assert obs.sensor_faults == {"soil_p1": False, "air_temp": True}


class TestObservationV1Invalid:
    """Test invalid ObservationV1 payloads."""

    def test_missing_schema_version_fails(self):
        """Missing schema_version should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ObservationV1(
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
            )
        assert "schema_version" in str(exc_info.value)

    def test_missing_required_soil_moisture_fails(self):
        """Missing soil_moisture_p1 should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                air_temperature=20.0,
                air_humidity=50.0,
            )
        assert "soil_moisture_p1" in str(exc_info.value)

    def test_missing_air_temperature_fails(self):
        """Missing air_temperature should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_humidity=50.0,
            )
        assert "air_temperature" in str(exc_info.value)

    def test_missing_air_humidity_fails(self):
        """Missing air_humidity should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_temperature=20.0,
            )
        assert "air_humidity" in str(exc_info.value)

    def test_invalid_schema_version_fails(self):
        """Invalid schema_version should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ObservationV1(
                schema_version="observation_v2",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
            )
        assert "schema_version" in str(exc_info.value)

    def test_timestamp_without_timezone_fails(self):
        """Timestamp without timezone should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(),  # No timezone
                soil_moisture_p1=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
            )
        assert "timezone" in str(exc_info.value).lower()

    def test_soil_moisture_out_of_range_fails(self):
        """Soil moisture out of [0, 1] should fail validation."""
        with pytest.raises(ValidationError):
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=1.5,  # Out of range
                air_temperature=20.0,
                air_humidity=50.0,
            )

    def test_humidity_out_of_range_fails(self):
        """Humidity out of [0, 100] should fail validation."""
        with pytest.raises(ValidationError):
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_temperature=20.0,
                air_humidity=105.0,  # Out of range
            )

    def test_co2_negative_fails(self):
        """Negative CO2 should fail validation."""
        with pytest.raises(ValidationError):
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                co2_ppm=-100.0,  # Negative not allowed
            )

    def test_light_intensity_negative_fails(self):
        """Negative light intensity should fail validation."""
        with pytest.raises(ValidationError):
            ObservationV1(
                schema_version="observation_v1",
                timestamp=datetime.now(timezone.utc),
                soil_moisture_p1=0.5,
                air_temperature=20.0,
                air_humidity=50.0,
                light_intensity=-50.0,  # Negative not allowed
            )


class TestObservationV1Serialization:
    """Test ObservationV1 serialization and deserialization."""

    def test_roundtrip_dump_and_validate(self):
        """ObservationV1 dump -> dict -> load should be stable."""
        original = ObservationV1(
            schema_version="observation_v1",
            timestamp=datetime.now(timezone.utc),
            soil_moisture_p1=0.62,
            soil_moisture_p2=0.58,
            air_temperature=22.3,
            air_humidity=64.5,
            co2_ppm=415.0,
            light_intensity=420.5,
        )
        dumped = original.model_dump()
        restored = ObservationV1(**dumped)
        assert restored.schema_version == original.schema_version
        assert restored.timestamp == original.timestamp
        assert restored.soil_moisture_p1 == original.soil_moisture_p1

    def test_json_schema_export(self):
        """ObservationV1 should export valid JSON Schema."""
        schema = ObservationV1.model_json_schema()
        assert schema is not None
        assert "properties" in schema
        assert "schema_version" in schema["properties"]
        assert "timestamp" in schema["properties"]
        assert "soil_moisture_p1" in schema["properties"]
        assert "air_temperature" in schema["properties"]
        assert "air_humidity" in schema["properties"]
