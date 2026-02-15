"""Sensor health diagnostics and fault detection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean
from typing import Iterable, Optional

from brain.contracts import ObservationV1, SensorHealthV1
from brain.contracts.sensor_health_v1 import FaultType


@dataclass(frozen=True)
class SensorConfig:
    name: str
    tolerance: float
    jump_rate_per_min: float
    drift_rate_per_hour: Optional[float]
    optional: bool = False


SENSOR_CONFIGS = {
    "soil_moisture_p1": SensorConfig(
        name="soil_moisture_p1",
        tolerance=0.002,
        jump_rate_per_min=0.3,
        drift_rate_per_hour=0.02,
    ),
    "soil_moisture_p2": SensorConfig(
        name="soil_moisture_p2",
        tolerance=0.002,
        jump_rate_per_min=0.3,
        drift_rate_per_hour=0.02,
        optional=True,
    ),
    "air_temperature": SensorConfig(
        name="air_temperature",
        tolerance=0.1,
        jump_rate_per_min=1.0,
        drift_rate_per_hour=0.5,
    ),
    "air_humidity": SensorConfig(
        name="air_humidity",
        tolerance=0.5,
        jump_rate_per_min=5.0,
        drift_rate_per_hour=2.0,
    ),
    "co2_ppm": SensorConfig(
        name="co2_ppm",
        tolerance=5.0,
        jump_rate_per_min=100.0,
        drift_rate_per_hour=None,
        optional=True,
    ),
    "light_intensity": SensorConfig(
        name="light_intensity",
        tolerance=5.0,
        jump_rate_per_min=200.0,
        drift_rate_per_hour=None,
        optional=True,
    ),
}


def _get_value(obs: ObservationV1, sensor_name: str) -> Optional[float]:
    return getattr(obs, sensor_name, None)


def _recent_window(
    history: Iterable[ObservationV1], now: datetime, minutes: int
) -> list[ObservationV1]:
    cutoff = now - timedelta(minutes=minutes)
    return [obs for obs in history if obs.timestamp >= cutoff]


def _history_window(
    history: Iterable[ObservationV1], now: datetime, hours: int
) -> list[ObservationV1]:
    cutoff = now - timedelta(hours=hours)
    return [obs for obs in history if obs.timestamp >= cutoff]


def _detect_stuck(values: list[float], tolerance: float) -> bool:
    if len(values) < 2:
        return False
    return max(values) - min(values) <= tolerance


def _detect_jump(
    prev_value: float,
    current_value: float,
    delta_minutes: float,
    max_rate_per_min: float,
) -> bool:
    if delta_minutes <= 0:
        return False
    return abs(current_value - prev_value) > max_rate_per_min * delta_minutes


def _detect_drift(
    values: list[float], timestamps: list[datetime], threshold_per_hour: float
) -> bool:
    if len(values) < 3:
        return False
    base_time = timestamps[0]
    hours = [(ts - base_time).total_seconds() / 3600.0 for ts in timestamps]
    if max(hours) == 0:
        return False
    mean_x = mean(hours)
    mean_y = mean(values)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(hours, values))
    denominator = sum((x - mean_x) ** 2 for x in hours)
    if denominator == 0:
        return False
    slope = numerator / denominator
    return abs(slope) > threshold_per_hour


def evaluate_sensor_health(
    observation: ObservationV1,
    history: Iterable[ObservationV1],
) -> list[SensorHealthV1]:
    """Evaluate per-sensor health using recent history."""
    now = observation.timestamp
    history_list = list(history)
    if not history_list or history_list[-1] is not observation:
        history_list.append(observation)

    results: list[SensorHealthV1] = []
    for name, config in SENSOR_CONFIGS.items():
        current_value = _get_value(observation, name)

        if current_value is None:
            fault_state = FaultType.DISCONNECTED
            status = "failed" if not config.optional else "degraded"
            confidence = 0.3 if not config.optional else 0.5
            health = SensorHealthV1(
                schema_version="sensor_health_v1",
                timestamp=now,
                sensor_name=name,
                sensor_type=None,
                status=status,
                confidence=confidence,
                fault_state=fault_state,
                last_reading=None,
                readings_since_fault=0,
                consecutive_failures=1,
                voltage_mv=None,
                signal_quality=None,
                notes="Sensor reading missing",
            )
            results.append(health)
            continue

        recent_60 = _recent_window(history_list, now, 60)
        recent_values = [
            _get_value(obs, name)
            for obs in recent_60
            if _get_value(obs, name) is not None
        ]

        fault_state = FaultType.NONE
        status = "healthy"
        confidence = 1.0
        notes = None

        if _detect_stuck(recent_values, config.tolerance):
            fault_state = FaultType.STUCK
            status = "degraded"
            confidence = 0.5
            notes = "Reading unchanged beyond tolerance"

        if len(history_list) >= 2:
            prev = history_list[-2]
            prev_value = _get_value(prev, name)
            if prev_value is not None:
                delta_minutes = (
                    now - prev.timestamp
                ).total_seconds() / 60.0
                if _detect_jump(
                    prev_value,
                    current_value,
                    delta_minutes,
                    config.jump_rate_per_min,
                ):
                    fault_state = FaultType.JUMP
                    status = "failed" if not config.optional else "degraded"
                    confidence = 0.2
                    notes = "Unphysical jump detected"

        if config.drift_rate_per_hour is not None:
            recent_4h = _history_window(history_list, now, 4)
            drift_values = [
                _get_value(obs, name)
                for obs in recent_4h
                if _get_value(obs, name) is not None
            ]
            drift_times = [
                obs.timestamp
                for obs in recent_4h
                if _get_value(obs, name) is not None
            ]
            if _detect_drift(
                drift_values,
                drift_times,
                config.drift_rate_per_hour,
            ):
                if fault_state == FaultType.NONE:
                    fault_state = FaultType.DRIFT
                    status = "degraded"
                    confidence = 0.7
                    notes = "Slow drift detected"

        health = SensorHealthV1(
            schema_version="sensor_health_v1",
            timestamp=now,
            sensor_name=name,
            sensor_type=None,
            status=status,
            confidence=confidence,
            fault_state=fault_state,
            last_reading=current_value,
            readings_since_fault=0 if fault_state != FaultType.NONE else len(recent_values),
            consecutive_failures=0,
            voltage_mv=None,
            signal_quality=None,
            notes=notes,
        )
        results.append(health)

    return results
