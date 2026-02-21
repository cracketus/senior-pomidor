"""Deterministic baseline vision analyzer for Stage 4 simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from brain.contracts import VisionExplanationV1, VisionInputV1, VisionV1


@dataclass(frozen=True)
class BaselineVisionAnalyzer:
    """Rule-based deterministic analyzer over structured vision input."""

    source_name: str = "vision_baseline_stub_v1"

    def analyze(self, payload: VisionInputV1) -> tuple[VisionV1, VisionExplanationV1]:
        metrics = _parse_metrics(payload.telemetry_summary)
        vpd = metrics.get("vpd")
        soil_avg = metrics.get("soil_avg_pct")
        confidence_signal = metrics.get("conf")

        findings: list[str] = []
        stress_signals: list[str] = []

        if vpd is not None and vpd >= 1.6:
            findings.append("high_vpd_context")
            stress_signals.append("potential_transpiration_stress")
        if soil_avg is not None and soil_avg <= 30.0:
            findings.append("low_soil_moisture_context")
            stress_signals.append("potential_hydration_stress")
        if confidence_signal is not None and confidence_signal < 0.5:
            findings.append("low_telemetry_confidence")

        if confidence_signal is not None and confidence_signal < 0.5:
            plant_status = "unknown"
            model_confidence = 0.4
        elif stress_signals:
            plant_status = "stress"
            model_confidence = 0.75
        elif _is_watch(vpd=vpd, soil_avg=soil_avg):
            plant_status = "watch"
            model_confidence = 0.68
        else:
            plant_status = "healthy"
            model_confidence = 0.82

        vision = VisionV1(
            schema_version="vision_v1",
            timestamp=payload.timestamp,
            image_ref=payload.image_ref,
            source=self.source_name,
            plant_status=plant_status,
            confidence=model_confidence,
            findings=_sorted_unique(findings),
            stress_signals=_sorted_unique(stress_signals),
        )

        explanation = VisionExplanationV1(
            schema_version="vision_explanation_v1",
            timestamp=payload.timestamp,
            image_ref=payload.image_ref,
            vision_ref=f"{vision.schema_version}:{payload.state_ref}",
            summary=_build_summary(plant_status),
            evidence=_sorted_unique(findings or ["telemetry_context_nominal"]),
            limitations=["deterministic_baseline_no_image_pixels"],
        )
        return vision, explanation


def _parse_metrics(summary: str) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for token in summary.split():
        if "=" not in token:
            continue
        key, raw_value = token.split("=", 1)
        try:
            metrics[key] = float(raw_value)
        except ValueError:
            continue
    return metrics


def _is_watch(*, vpd: float | None, soil_avg: float | None) -> bool:
    return (vpd is not None and vpd >= 1.3) or (soil_avg is not None and soil_avg <= 38.0)


def _build_summary(plant_status: str) -> str:
    summaries = {
        "healthy": "Visual context appears stable in this cycle.",
        "watch": "Mild visual risk context detected; continue monitoring.",
        "stress": "Visual risk context indicates potential stress.",
        "unknown": "Insufficient confidence for a reliable visual assessment.",
    }
    return summaries[plant_status]


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))
