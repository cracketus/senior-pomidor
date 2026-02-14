"""Tests for ActionV1 contract."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from brain.contracts import ActionV1
from brain.contracts.action_v1 import ActionType


class TestActionV1Valid:
    """Test valid ActionV1 payloads."""

    def test_valid_water_action_passes(self):
        """Valid water action should pass validation."""
        action = ActionV1(
            schema_version="action_v1",
            timestamp=datetime.now(timezone.utc),
            action_type=ActionType.WATER,
            duration_seconds=10,
            intensity=0.8,
            reason="Soil moisture p1 below target",
            estimated_impact=0.15,
            budget_remaining_ml=80.0,
        )
        assert action.schema_version == "action_v1"
        assert action.action_type == "water"

    def test_all_action_types_valid(self):
        """All ActionType enum values should be valid."""
        for action_type in ActionType:
            action = ActionV1(
                schema_version="action_v1",
                timestamp=datetime.now(timezone.utc),
                action_type=action_type,
                reason="Test action",
            )
            assert action.action_type == action_type.value


class TestActionV1Invalid:
    """Test invalid ActionV1 payloads."""

    def test_invalid_timestamp_fails(self):
        """Timestamp without timezone should fail."""
        with pytest.raises(ValidationError):
            ActionV1(
                schema_version="action_v1",
                timestamp=datetime.now(),  # No timezone
                action_type=ActionType.WATER,
                reason="Test",
            )

    def test_action_types_are_valid_enum(self):
        """Invalid action type should fail."""
        with pytest.raises(ValidationError):
            ActionV1(
                schema_version="action_v1",
                timestamp=datetime.now(timezone.utc),
                action_type="invalid_action",
                reason="Test",
            )

    def test_intensity_bounds(self):
        """Intensity must be 0 to 1 if provided."""
        with pytest.raises(ValidationError):
            ActionV1(
                schema_version="action_v1",
                timestamp=datetime.now(timezone.utc),
                action_type=ActionType.LIGHT,
                intensity=1.5,
                reason="Test",
            )

    def test_missing_schema_version_fails(self):
        """Missing schema_version should fail."""
        with pytest.raises(ValidationError):
            ActionV1(
                timestamp=datetime.now(timezone.utc),
                action_type=ActionType.WATER,
                reason="Test",
            )


class TestActionV1Serialization:
    """Test serialization and deserialization."""

    def test_roundtrip_dump_and_validate(self):
        """JSON roundtrip should preserve data."""
        original = ActionV1(
            schema_version="action_v1",
            timestamp=datetime.now(timezone.utc),
            action_type=ActionType.CO2,
            duration_seconds=30,
            intensity=0.5,
            reason="CO2 levels too low",
            confidence=0.9,
        )

        json_str = original.model_dump_json()
        restored = ActionV1.model_validate_json(json_str)
        assert restored.action_type == original.action_type
        assert restored.confidence == original.confidence

    def test_json_schema_export(self):
        """ActionV1 should export valid JSON Schema."""
        schema = ActionV1.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "action_type" in schema["properties"]
