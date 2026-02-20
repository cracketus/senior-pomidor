"""Contract tests for VisionExplanationV1."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from brain.contracts import VisionExplanationV1


def test_vision_explanation_v1_valid_payload():
    payload = {
        "schema_version": "vision_explanation_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        "image_ref": "sim://frame/0001.jpg",
        "vision_ref": "vision_v1:run_001:cycle_1",
        "summary": "Leaf edges show mild upward curl; monitor humidity trend.",
        "evidence": ["edge curl in upper leaves", "no necrotic spotting"],
        "limitations": ["single-frame assessment"],
    }
    model = VisionExplanationV1.model_validate(payload)
    assert model.schema_version == "vision_explanation_v1"
    assert "single-frame assessment" in model.limitations


def test_vision_explanation_v1_requires_summary():
    payload = {
        "schema_version": "vision_explanation_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        "image_ref": "sim://frame/0001.jpg",
        "vision_ref": "vision_v1:run_001:cycle_1",
        "summary": "",
    }
    with pytest.raises(ValueError):
        VisionExplanationV1.model_validate(payload)


def test_vision_explanation_v1_requires_timezone():
    payload = {
        "schema_version": "vision_explanation_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0),
        "image_ref": "sim://frame/0001.jpg",
        "vision_ref": "vision_v1:run_001:cycle_1",
        "summary": "summary",
    }
    with pytest.raises(ValueError, match="timezone"):
        VisionExplanationV1.model_validate(payload)
