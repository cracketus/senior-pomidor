"""Estimator pipeline: Observation -> StateV1 + AnomalyV1[] + SensorHealthV1[]."""

from __future__ import annotations

from typing import Iterable

from brain.contracts import AnomalyV1, DeviceStatusV1, ObservationV1, SensorHealthV1, StateV1
from brain.estimator.anomaly_detector import detect_anomalies
from brain.estimator.confidence import compute_confidence
from brain.estimator.ring_buffer import TimeRingBuffer
from brain.estimator.sensor_health import evaluate_sensor_health
from brain.estimator.vpd import calculate_vpd


class EstimatorPipeline:
    """Core estimator pipeline with bounded observation history."""

    def __init__(self, history_hours: float = 48.0) -> None:
        self._history = TimeRingBuffer(history_hours, lambda obs: obs.timestamp)

    def history(self) -> list[ObservationV1]:
        return self._history.items()

    def process(
        self,
        observation: ObservationV1,
        device_status: DeviceStatusV1,
    ) -> tuple[StateV1, list[AnomalyV1], list[SensorHealthV1]]:
        """Process an observation and emit state, anomalies, and sensor health."""
        self._history.append(observation)
        history = self._history.items()

        vpd_kpa = calculate_vpd(
            observation.air_temperature, observation.air_humidity
        )

        soil_values = [observation.soil_moisture_p1]
        if observation.soil_moisture_p2 is not None:
            soil_values.append(observation.soil_moisture_p2)
        soil_avg = sum(soil_values) / len(soil_values)

        sensor_health = evaluate_sensor_health(observation, history)
        anomalies = detect_anomalies(
            observation, vpd_kpa, sensor_health, device_status, history=history
        )
        confidence = compute_confidence(
            observation,
            vpd_kpa,
            history,
            sensor_health,
            anomalies,
            now=observation.timestamp,
        )

        state = StateV1(
            schema_version="state_v1",
            timestamp=observation.timestamp,
            soil_moisture_p1=observation.soil_moisture_p1,
            soil_moisture_p2=observation.soil_moisture_p2,
            soil_moisture_avg=soil_avg,
            air_temperature=observation.air_temperature,
            air_humidity=observation.air_humidity,
            vpd=vpd_kpa,
            co2_ppm=observation.co2_ppm,
            light_intensity=observation.light_intensity,
            confidence=confidence,
            notes=None,
        )

        return state, anomalies, sensor_health
