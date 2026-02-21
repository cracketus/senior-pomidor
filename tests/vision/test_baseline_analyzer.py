"""Tests for deterministic baseline vision analyzer."""

from __future__ import annotations

from datetime import datetime, timezone

from brain.contracts import VisionInputV1
from brain.vision import BaselineVisionAnalyzer


def _input(summary: str) -> VisionInputV1:
    return VisionInputV1(
        schema_version="vision_input_v1",
        timestamp=datetime(2026, 2, 20, 12, 0, tzinfo=timezone.utc),
        image_ref="sim://frame/0001.jpg",
        state_ref="state_v1:run_001:cycle_1",
        telemetry_summary=summary,
        camera_id="cam-1",
    )


def test_analyzer_is_deterministic_for_same_input():
    analyzer = BaselineVisionAnalyzer()
    payload = _input("vpd=1.22 soil_avg_pct=44.0 conf=0.93")
    left_vision, left_expl = analyzer.analyze(payload)
    right_vision, right_expl = analyzer.analyze(payload)
    assert left_vision.model_dump(mode="json") == right_vision.model_dump(mode="json")
    assert left_expl.model_dump(mode="json") == right_expl.model_dump(mode="json")


def test_analyzer_emits_stress_for_hot_dry_context():
    analyzer = BaselineVisionAnalyzer()
    vision, explanation = analyzer.analyze(_input("vpd=1.90 soil_avg_pct=25.0 conf=0.88"))
    assert vision.plant_status == "stress"
    assert "potential_hydration_stress" in vision.stress_signals
    assert explanation.schema_version == "vision_explanation_v1"


def test_analyzer_emits_unknown_for_low_confidence_context():
    analyzer = BaselineVisionAnalyzer()
    vision, explanation = analyzer.analyze(_input("vpd=1.00 soil_avg_pct=50.0 conf=0.20"))
    assert vision.plant_status == "unknown"
    assert vision.confidence == 0.4
    assert "Insufficient confidence" in explanation.summary
