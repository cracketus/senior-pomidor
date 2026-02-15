"""Synthetic observation source with noise, diurnal cycle, and scenarios."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from brain.contracts import DeviceStatusV1, ObservationV1

ScenarioHook = Callable[
    [ObservationV1, DeviceStatusV1, random.Random, int],
    tuple[ObservationV1, DeviceStatusV1],
]


def _clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


@dataclass
class SyntheticConfig:
    """Configuration for SyntheticSource generation."""

    seed: Optional[int] = None
    start_time: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    step_seconds: int = 600
    count: Optional[int] = None

    # Base means
    base_air_temperature: float = 22.0
    base_air_humidity: float = 60.0
    base_soil_moisture_p1: float = 0.55
    base_soil_moisture_p2: float = 0.52
    base_co2_ppm: float = 420.0
    base_light_intensity: float = 500.0

    # Noise amplitudes (std-like scale)
    noise_air_temperature: float = 0.4
    noise_air_humidity: float = 2.0
    noise_soil_moisture: float = 0.01
    noise_co2_ppm: float = 10.0
    noise_light_intensity: float = 15.0

    # Diurnal cycle (sinusoidal) configuration
    diurnal_temp_amp: float = 3.0
    diurnal_humidity_amp: float = -6.0
    diurnal_light_amp: float = 1.0
    diurnal_phase_hours: float = 6.0  # peak around noon

    scenarios: list[ScenarioHook] = field(default_factory=list)


class SyntheticSource:
    """Generate synthetic observations with noise and diurnal cycles."""

    def __init__(self, config: SyntheticConfig) -> None:
        if config.start_time.tzinfo is None:
            raise ValueError("start_time must be timezone-aware")
        if config.step_seconds <= 0:
            raise ValueError("step_seconds must be positive")
        if config.count is not None and config.count < 0:
            raise ValueError("count must be non-negative or None")
        self._config = config
        self._rng = random.Random(config.seed)
        self._index = 0
        self._current_time = config.start_time

    def next_observation(
        self,
    ) -> tuple[ObservationV1, DeviceStatusV1] | None:
        if self._config.count is not None and self._index >= self._config.count:
            return None

        hour_fraction = (
            self._current_time.hour
            + self._current_time.minute / 60.0
            + self._current_time.second / 3600.0
        )
        angle = 2.0 * math.pi * (
            (hour_fraction - self._config.diurnal_phase_hours) / 24.0
        )
        diurnal = math.sin(angle)

        temp = (
            self._config.base_air_temperature
            + self._config.diurnal_temp_amp * diurnal
            + self._rng.gauss(0.0, self._config.noise_air_temperature)
        )
        humidity = (
            self._config.base_air_humidity
            + self._config.diurnal_humidity_amp * diurnal
            + self._rng.gauss(0.0, self._config.noise_air_humidity)
        )
        soil_p1 = (
            self._config.base_soil_moisture_p1
            + self._rng.gauss(0.0, self._config.noise_soil_moisture)
        )
        soil_p2 = (
            self._config.base_soil_moisture_p2
            + self._rng.gauss(0.0, self._config.noise_soil_moisture)
        )
        co2 = (
            self._config.base_co2_ppm
            + self._rng.gauss(0.0, self._config.noise_co2_ppm)
        )

        light_day_factor = max(0.0, diurnal) * self._config.diurnal_light_amp
        light = (
            self._config.base_light_intensity * light_day_factor
            + self._rng.gauss(0.0, self._config.noise_light_intensity)
        )

        observation = ObservationV1(
            schema_version="observation_v1",
            timestamp=self._current_time,
            soil_moisture_p1=_clamp(soil_p1, 0.0, 1.0),
            soil_moisture_p2=_clamp(soil_p2, 0.0, 1.0),
            air_temperature=temp,
            air_humidity=_clamp(humidity, 0.0, 100.0),
            co2_ppm=max(0.0, co2),
            light_intensity=max(0.0, light),
        )

        device_status = DeviceStatusV1(
            schema_version="device_status_v1",
            timestamp=self._current_time,
            light_on=observation.light_intensity is not None
            and observation.light_intensity > 0.0,
            fans_on=observation.air_temperature >= 26.0,
            heater_on=observation.air_temperature <= 18.0,
            pump_on=False,
            co2_on=observation.co2_ppm is not None
            and observation.co2_ppm < 380.0,
            mcu_connected=True,
            mcu_uptime_seconds=self._index * self._config.step_seconds,
            mcu_reset_count=0,
            light_intensity_setpoint=observation.light_intensity,
            pump_pulse_count=0,
        )

        for hook in self._config.scenarios:
            observation, device_status = hook(
                observation, device_status, self._rng, self._index
            )

        self._index += 1
        self._current_time = self._current_time + timedelta(
            seconds=self._config.step_seconds
        )
        return observation, device_status
