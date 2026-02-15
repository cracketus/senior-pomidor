"""Anomaly detection based on threshold rules."""

from __future__ import annotations

from datetime import datetime
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
        notes=None,
    )


def detect_anomalies(
    observation: ObservationV1,
    vpd_kpa: float,
    sensor_health: Iterable[SensorHealthV1],
    device_status: DeviceStatusV1,
) -> list[AnomalyV1]:
    """Detect anomalies using deterministic thresholds."""
    anomalies: list[AnomalyV1] = []
    now = observation.timestamp

    # Soil moisture thresholds
    if observation.soil_moisture_p1 < THRESHOLDS["soil_moisture_low"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.MOISTURE_STRESS,
                SeverityLevel.HIGH,
                "Soil moisture below minimum threshold",
                affected_sensor="soil_moisture_p1",
            )
        )
    if observation.soil_moisture_p1 > THRESHOLDS["soil_moisture_high"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.MOISTURE_STRESS,
                SeverityLevel.MEDIUM,
                "Soil moisture above maximum threshold",
                affected_sensor="soil_moisture_p1",
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
            )
        )

    # Temperature thresholds
    if observation.air_temperature < THRESHOLDS["temperature_low"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.TEMPERATURE_STRESS,
                SeverityLevel.HIGH,
                "Air temperature below minimum threshold",
                affected_sensor="air_temperature",
            )
        )
    if observation.air_temperature > THRESHOLDS["temperature_high"]:
        anomalies.append(
            _make_anomaly(
                now,
                AnomalyType.TEMPERATURE_STRESS,
                SeverityLevel.HIGH,
                "Air temperature above maximum threshold",
                affected_sensor="air_temperature",
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
        anomalies.append(
            _make_anomaly(
                now,
                anomaly_type,
                _severity_for_fault(health.fault_state),
                f"Sensor fault detected: {health.fault_state.value}",
                affected_sensor=health.sensor_name,
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
            )
        )

    return anomalies
