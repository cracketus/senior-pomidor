"""Contract tests for VisionInputV1."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from brain.contracts import VisionInputV1


def test_vision_input_v1_valid_payload():
    payload = {
        "schema_version": "vision_input_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        "image_ref": "sim://frame/0001.jpg",
        "state_ref": "state_v1:run_001:cycle_1",
        "telemetry_summary": "vpd=1.28 soil_avg=42.1 confidence=0.91",
        "camera_id": "cam-front",
    }
    model = VisionInputV1.model_validate(payload)
    assert model.schema_version == "vision_input_v1"
    assert model.camera_id == "cam-front"


def test_vision_input_v1_requires_timezone():
    payload = {
        "schema_version": "vision_input_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0),
        "image_ref": "sim://frame/0001.jpg",
        "state_ref": "state_v1:run_001:cycle_1",
        "telemetry_summary": "summary",
    }
    with pytest.raises(ValueError, match="timezone"):
        VisionInputV1.model_validate(payload)


def test_vision_input_v1_rejects_empty_refs():
    payload = {
        "schema_version": "vision_input_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        "image_ref": "",
        "state_ref": "",
        "telemetry_summary": "summary",
    }
    with pytest.raises(ValueError):
        VisionInputV1.model_validate(payload)
