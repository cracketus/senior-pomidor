"""VPD calculation utilities."""

from __future__ import annotations

import math


def calculate_vpd(air_temperature_c: float, relative_humidity_percent: float) -> float:
    """Calculate vapor pressure deficit (kPa) using Magnus approximation.

    Formula:
      Es (kPa) = 0.6108 * exp((17.67 * T) / (T + 243.5))
      VPD = Es * (1 - RH/100)

    Args:
        air_temperature_c: Air temperature in Celsius.
        relative_humidity_percent: Relative humidity in percent (0-100).

    Returns:
        VPD in kPa.

    Raises:
        ValueError: If humidity is outside [0, 100] or temperature is implausible.
    """
    if relative_humidity_percent < 0.0 or relative_humidity_percent > 100.0:
        raise ValueError("relative_humidity_percent must be between 0 and 100")
    if air_temperature_c < -50.0 or air_temperature_c > 80.0:
        raise ValueError("air_temperature_c out of supported range")

    saturation_kpa = 0.6108 * math.exp(
        (17.67 * air_temperature_c) / (air_temperature_c + 243.5)
    )
    vpd = saturation_kpa * (1.0 - (relative_humidity_percent / 100.0))
    return max(0.0, vpd)
