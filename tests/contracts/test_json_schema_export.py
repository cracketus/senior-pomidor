"""Tests for JSON Schema export from all contracts."""

import json

import pytest

from brain.contracts import (
    ActionV1,
    AnomalyV1,
    ExecutorEventV1,
    Forecast36hV1,
    GuardrailResultV1,
    SensorHealthV1,
    StateV1,
)


class TestJsonSchemaExport:
    """Test that all contracts can export valid JSON Schema."""

    def test_all_contracts_export_json_schema(self):
        """All contracts should export valid JSON Schema."""
        contracts = [
            StateV1,
            ActionV1,
            AnomalyV1,
            SensorHealthV1,
            GuardrailResultV1,
            ExecutorEventV1,
            Forecast36hV1,
        ]

        for contract in contracts:
            schema = contract.model_json_schema()
            assert isinstance(schema, dict), f"{contract.__name__} schema is not a dict"
            assert "properties" in schema, f"{contract.__name__} schema missing 'properties'"

    def test_state_v1_schema_structure(self):
        """StateV1 schema should have expected structure."""
        schema = StateV1.model_json_schema()
        props = schema["properties"]

        # Required fields
        assert "schema_version" in props
        assert "timestamp" in props
        assert "soil_moisture_p1" in props
        assert "confidence" in props

        # Check property types
        assert props["confidence"]["type"] == "number"
        assert props["confidence"]["maximum"] == 1.0
        assert props["confidence"]["minimum"] == 0.0

    def test_action_v1_schema_structure(self):
        """ActionV1 schema should have expected structure."""
        schema = ActionV1.model_json_schema()
        props = schema["properties"]

        assert "action_type" in props
        assert "reason" in props

        # Verify enum for action_type
        if "enum" in props["action_type"]:
            action_types = props["action_type"]["enum"]
            assert "water" in action_types

    def test_schemas_are_serializable(self):
        """All schemas should be JSON serializable."""
        for contract in [
            StateV1,
            ActionV1,
            AnomalyV1,
            SensorHealthV1,
            GuardrailResultV1,
            ExecutorEventV1,
            Forecast36hV1,
        ]:
            schema = contract.model_json_schema()
            json_str = json.dumps(schema)
            assert isinstance(json_str, str)
            assert len(json_str) > 0
