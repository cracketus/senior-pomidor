"""Anomaly detection based on deterministic threshold rules."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable

from brain.contracts import AnomalyV1, DeviceStatusV1, ObservationV1, SensorHealthV1
from brain.contracts.anomaly_v1 import AnomalyType, SeverityLevel
from brain.contracts.sensor_health_v1 import FaultType

THRESHOLDS = {
    "soil_moisture_low": 0.10,
    "soil_moisture_high": 0.85,
    "soil_moisture_differential": 0.40,
    "vpd_high": 3.5,
    "vpd_low": 0.2,
    "temperature_low": 8.0,
    "temperature_high": 32.0,
    "temperature_rate_10m": 3.0,
    "moisture_drop_30m": 0.05,
}


def _severity_for_fault(fault: FaultType) -> SeverityLevel:
    if fault == FaultType.JUMP:
        return SeverityLevel.HIGH
    if fault == FaultType.DISCONNECTED:
        return SeverityLevel.HIGH
    if fault == FaultType.STUCK:
        return SeverityLevel.MEDIUM
    if fault == FaultType.DRIFT:
        return SeverityLevel.MEDIUM
    return SeverityLevel.LOW


def _make_anomaly(
    timestamp: datetime,
    anomaly_type: AnomalyType,
    severity: SeverityLevel,
    description: str,
    affected_sensor: str | None = None,
    detection_mode: str = "instant",
) -> AnomalyV1:
    return AnomalyV1(
        schema_version="anomaly_v1",
        timestamp=timestamp,
        anomaly_type=anomaly_type,
        severity=severity,
        affected_sensor=affected_sensor,
        description=description,
        confidence=0.9,
        action_recommended=severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL),
        expected_duration_seconds=None,
        requires_safe_mode=severity == SeverityLevel.CRITICAL,
        notes=f"detection_mode={detection_mode}",
    )


def _recent_breach_count(
    history: list[ObservationV1],
    now: datetime,
    minutes: int,
    predicate,
) -> int:
    cutoff = now - timedelta(minutes=minutes)
    return sum(1 for obs in history if obs.timestamp >= cutoff and predicate(obs))


def detect_anomalies(
    observation: ObservationV1,
    vpd_kpa: float,
    sensor_health: Iterable[SensorHealthV1],
    device_status: DeviceStatusV1,
    history: Iterable[ObservationV1] | None = None,
) -> list[AnomalyV1]:
    """Detect anomalies using deterministic threshold + temporal checks."""
    anomalies: list[AnomalyV1] = []
    now = observation.timestamp
    history_list = list(history or [])
    if not history_list or history_list[-1] is not observation:
        history_list.append(observation)
    previous = history_list[-2] if len(history_list) >= 2 else None

    # Soil moisture thresholds (instant + sustained)
    if observation.soil_moisture_p1 < THRESHOLDS["soil_moisture_low"]:
        mode = "instant"
        if _recent_breach_count(
            history_list,
            now,
            minutes=30,
            predicate=lambda obs: obs.soil_moisture_p1 < THRESHOLDS["soil_moisture_low"],
        ) >= 2:
            mode = "sustained"
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.MOISTURE_STRESS,
                SeverityLevel.HIGH,
                "Soil moisture below minimum threshold",
                affected_sensor="soil_moisture_p1",
                detection_mode=mode,
            )
        )
    if observation.soil_moisture_p1 > THRESHOLDS["soil_moisture_high"]:
        mode = "instant"
        if _recent_breach_count(
            history_list,
            now,
            minutes=30,
            predicate=lambda obs: obs.soil_moisture_p1 > THRESHOLDS["soil_moisture_high"],
        ) >= 2:
            mode = "sustained"
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.MOISTURE_STRESS,
                SeverityLevel.MEDIUM,
                "Soil moisture above maximum threshold",
                affected_sensor="soil_moisture_p1",
                detection_mode=mode,
            )
        )
    if observation.soil_moisture_p2 is not None:
        diff = abs(observation.soil_moisture_p1 - observation.soil_moisture_p2)
        if diff > THRESHOLDS["soil_moisture_differential"]:
            anomalies.append(
                _make_anomaly(
                    now,
                    AnomalyType.MOISTURE_STRESS,
                    SeverityLevel.MEDIUM,
                    "Soil moisture probes diverge beyond threshold",
                    affected_sensor="soil_moisture_differential",
                    detection_mode="instant",
                )
            )

    # VPD thresholds
    if vpd_kpa > THRESHOLDS["vpd_high"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.VPD_OUT_OF_RANGE,
                SeverityLevel.HIGH,
                "VPD above maximum threshold",
                affected_sensor="vpd",
                detection_mode="instant",
            )
        )
    if vpd_kpa < THRESHOLDS["vpd_low"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.VPD_OUT_OF_RANGE,
                SeverityLevel.MEDIUM,
                "VPD below minimum threshold",
                affected_sensor="vpd",
                detection_mode="instant",
            )
        )

    # Temperature thresholds (instant + sustained)
    if observation.air_temperature < THRESHOLDS["temperature_low"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.TEMPERATURE_STRESS,
                SeverityLevel.HIGH,
                "Air temperature below minimum threshold",
                affected_sensor="air_temperature",
                detection_mode="instant",
            )
        )
    if observation.air_temperature > THRESHOLDS["temperature_high"]:
        mode = "instant"
        if _recent_breach_count(
            history_list,
            now,
            minutes=20,
            predicate=lambda obs: obs.air_temperature > THRESHOLDS["temperature_high"],
        ) >= 2:
            mode = "sustained"
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.TEMPERATURE_STRESS,
                SeverityLevel.HIGH,
                "Air temperature above maximum threshold",
                affected_sensor="air_temperature",
                detection_mode=mode,
            )
        )

    # Rate-based checks
    if previous is not None:
        delta_minutes = (now - previous.timestamp).total_seconds() / 60.0
        if 0 < delta_minutes <= 10:
            temp_delta = abs(observation.air_temperature - previous.air_temperature)
            if temp_delta > THRESHOLDS["temperature_rate_10m"]:
                anomalies.append(
                    _make_anomaly(
                        now,
                        AnomalyType.TEMPERATURE_STRESS,
                        SeverityLevel.HIGH,
                        "Rapid temperature change detected",
                        affected_sensor="air_temperature",
                        detection_mode="rate",
                    )
                )
        if 0 < delta_minutes <= 30:
            moisture_drop = previous.soil_moisture_p1 - observation.soil_moisture_p1
            if moisture_drop > THRESHOLDS["moisture_drop_30m"]:
                anomalies.append(
                    _make_anomaly(
                        now,
                        AnomalyType.MOISTURE_STRESS,
                        SeverityLevel.MEDIUM,
                        "Rapid soil moisture drop detected",
                        affected_sensor="soil_moisture_p1",
                        detection_mode="rate",
                    )
                )

    # Sensor faults
    for health in sensor_health:
        if health.fault_state == FaultType.NONE:
            continue
        if health.fault_state == FaultType.STUCK:
            anomaly_type = AnomalyType.SENSOR_STUCK
        elif health.fault_state == FaultType.JUMP:
            anomaly_type = AnomalyType.SENSOR_JUMP
        elif health.fault_state == FaultType.DRIFT:
            anomaly_type = AnomalyType.SENSOR_DRIFT
        elif health.fault_state == FaultType.DISCONNECTED:
            anomaly_type = AnomalyType.SENSOR_DISCONNECT
        else:
            anomaly_type = AnomalyType.UNKNOWN
        fault_label = (
            health.fault_state.value
            if hasattr(health.fault_state, "value")
            else str(health.fault_state)
        )
        anomalies.append(
            _make_anomaly(
                now,
                anomaly_type,
                _severity_for_fault(health.fault_state),
                f"Sensor fault detected: {fault_label}",
                affected_sensor=health.sensor_name,
                detection_mode="instant",
            )
        )

    # Device offline
    if not device_status.mcu_connected:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.DEVICE_OFFLINE,
                SeverityLevel.HIGH,
                "MCU disconnected",
                affected_sensor="mcu",
                detection_mode="instant",
            )
        )

    return anomalies
