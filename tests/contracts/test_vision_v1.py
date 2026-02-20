"""Contract tests for VisionV1."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from brain.contracts import VisionV1


def test_vision_v1_valid_payload():
    payload = {
        "schema_version": "vision_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        "image_ref": "sim://frame/0001.jpg",
        "source": "vision_stub_v1",
        "plant_status": "watch",
        "confidence": 0.74,
        "findings": ["slight_leaf_curl"],
        "stress_signals": ["leaf_curl"],
    }
    model = VisionV1.model_validate(payload)
    assert model.plant_status == "watch"
    assert model.confidence == 0.74


def test_vision_v1_confidence_bounds():
    payload = {
        "schema_version": "vision_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        "image_ref": "sim://frame/0001.jpg",
        "source": "vision_stub_v1",
        "plant_status": "healthy",
        "confidence": 1.1,
    }
    with pytest.raises(ValueError):
        VisionV1.model_validate(payload)


def test_vision_v1_requires_timezone():
    payload = {
        "schema_version": "vision_v1",
        "timestamp": datetime(2026, 2, 20, 12, 0),
        "image_ref": "sim://frame/0001.jpg",
        "source": "vision_stub_v1",
        "plant_status": "unknown",
        "confidence": 0.5,
    }
    with pytest.raises(ValueError, match="timezone"):
        VisionV1.model_validate(payload)
