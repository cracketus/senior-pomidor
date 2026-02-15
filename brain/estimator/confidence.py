"""Confidence scoring based on sensor quality and anomalies."""

from __future__ import annotations

from datetime import datetime
from statistics import pstdev
from typing import Iterable, Optional

from brain.contracts import AnomalyV1, ObservationV1, SensorHealthV1
from brain.contracts.anomaly_v1 import SeverityLevel
from brain.contracts.sensor_health_v1 import FaultType


def _age_deduction(age_minutes: float) -> float:
    if age_minutes <= 5:
        return 0.0
    if age_minutes <= 15:
        return 0.05
    if age_minutes <= 30:
        return 0.10
    if age_minutes <= 60:
        return 0.20
    return 0.50


def _variance_deduction(values: list[float], threshold: float, penalty: float) -> float:
    if len(values) < 2:
        return 0.0
    if pstdev(values) > threshold:
        return penalty
    return 0.0


def _sensor_fault_deduction(fault_state: FaultType) -> float:
    if fault_state == FaultType.STUCK:
        return 0.50
    if fault_state == FaultType.JUMP:
        return 0.30
    if fault_state == FaultType.DRIFT:
        return 0.25
    if fault_state == FaultType.DISCONNECTED:
        return 0.70
    if fault_state == FaultType.OUT_OF_RANGE:
        return 0.20
    return 0.0


def _anomaly_deduction(severity: SeverityLevel) -> float:
    if severity == SeverityLevel.LOW:
        return 0.10
    if severity == SeverityLevel.MEDIUM:
        return 0.25
    if severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL):
        return 0.50
    return 0.0


def compute_confidence(
    observation: ObservationV1,
    vpd_kpa: float,
    history: Iterable[ObservationV1],
    sensor_health: Iterable[SensorHealthV1],
    anomalies: Iterable[AnomalyV1],
    now: Optional[datetime] = None,
) -> float:
    """Compute confidence score from current observation and diagnostics."""
    if now is None:
        now = observation.timestamp

    age_minutes = (now - observation.timestamp).total_seconds() / 60.0
    deductions = [_age_deduction(age_minutes)]

    # Extreme value deductions
    if observation.soil_moisture_p1 < 0.10 or observation.soil_moisture_p1 > 0.90:
        deductions.append(0.20)
    if observation.air_temperature < 8.0 or observation.air_temperature > 32.0:
        deductions.append(0.20)
    if observation.air_humidity < 10.0 or observation.air_humidity > 95.0:
        deductions.append(0.15)
    if vpd_kpa < 0.2 or vpd_kpa > 3.5:
        deductions.append(0.15)

    # Variance deductions from recent history
    recent = list(history)
    soil_values = [obs.soil_moisture_p1 for obs in recent]
    temp_values = [obs.air_temperature for obs in recent]
    humidity_values = [obs.air_humidity for obs in recent]

    deductions.append(_variance_deduction(soil_values, 0.15, 0.15))
    deductions.append(_variance_deduction(temp_values, 2.0, 0.15))
    deductions.append(_variance_deduction(humidity_values, 10.0, 0.10))

    # Cross-sensor disagreement
    if observation.soil_moisture_p2 is not None:
        denom = max(
            observation.soil_moisture_p1, observation.soil_moisture_p2, 1e-6
        )
        if abs(observation.soil_moisture_p1 - observation.soil_moisture_p2) / denom > 0.40:
            deductions.append(0.30)

    # Sensor fault deductions
    for health in sensor_health:
        deductions.append(_sensor_fault_deduction(health.fault_state))

    # Anomaly deductions
    for anomaly in anomalies:
        deductions.append(_anomaly_deduction(anomaly.severity))

    confidence = max(0.0, 1.0 - sum(deductions))
    return min(1.0, confidence)
