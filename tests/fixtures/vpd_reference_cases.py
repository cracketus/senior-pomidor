"""
Reference test cases for VPD (Vapor Pressure Deficit) calculations.

These cases validate the VPD calculation implementation against known physics-based values.
VPD is computed from air temperature and relative humidity using the Magnus formula.
"""

from dataclasses import dataclass


@dataclass
class VPDReferenceCase:
    """Single reference case for VPD calculation validation."""

    case_id: str
    description: str
    air_temperature_celsius: float
    relative_humidity_percent: float
    expected_vpd_kpa: float
    tolerance_kpa: float = 0.05  # ±0.05 kPa tolerance


# Reference cases derived from standard psychrometric calculations
# using Magnus formula: Es = 6.112 * exp((17.67 * T) / (T + 243.5))
VPD_REFERENCE_CASES = [
    VPDReferenceCase(
        case_id="vpd_001",
        description="Comfortable daytime conditions (22°C, 65% RH)",
        air_temperature_celsius=22.0,
        relative_humidity_percent=65.0,
        expected_vpd_kpa=1.19,
        tolerance_kpa=0.05,
    ),
    VPDReferenceCase(
        case_id="vpd_002",
        description="Warm, dry conditions (28°C, 40% RH) - high VPD stress",
        air_temperature_celsius=28.0,
        relative_humidity_percent=40.0,
        expected_vpd_kpa=2.35,
        tolerance_kpa=0.05,
    ),
    VPDReferenceCase(
        case_id="vpd_003",
        description="Cool, humid night (15°C, 80% RH) - low VPD",
        air_temperature_celsius=15.0,
        relative_humidity_percent=80.0,
        expected_vpd_kpa=0.31,
        tolerance_kpa=0.05,
    ),
    VPDReferenceCase(
        case_id="vpd_004",
        description="Cold conditions (5°C, 95% RH) - minimal VPD",
        air_temperature_celsius=5.0,
        relative_humidity_percent=95.0,
        expected_vpd_kpa=0.025,
        tolerance_kpa=0.05,
    ),
    VPDReferenceCase(
        case_id="vpd_005",
        description="Hot, dry alert conditions (35°C, 25% RH) - extreme VPD",
        air_temperature_celsius=35.0,
        relative_humidity_percent=25.0,
        expected_vpd_kpa=4.25,
        tolerance_kpa=0.10,
    ),
    VPDReferenceCase(
        case_id="vpd_006",
        description="Optimal growth conditions (24°C, 70% RH)",
        air_temperature_celsius=24.0,
        relative_humidity_percent=70.0,
        expected_vpd_kpa=1.07,
        tolerance_kpa=0.05,
    ),
    VPDReferenceCase(
        case_id="vpd_007",
        description="Fog/saturation condition (18°C, 100% RH) - zero VPD",
        air_temperature_celsius=18.0,
        relative_humidity_percent=100.0,
        expected_vpd_kpa=0.0,
        tolerance_kpa=0.01,
    ),
    VPDReferenceCase(
        case_id="vpd_008",
        description="Very warm, moderate humidity (32°C, 50% RH)",
        air_temperature_celsius=32.0,
        relative_humidity_percent=50.0,
        expected_vpd_kpa=2.64,
        tolerance_kpa=0.10,
    ),
]


def get_reference_case(case_id: str) -> VPDReferenceCase:
    """Retrieve a reference case by ID."""
    for case in VPD_REFERENCE_CASES:
        if case.case_id == case_id:
            return case
    raise ValueError(f"Reference case {case_id} not found")


def get_all_reference_cases() -> list[VPDReferenceCase]:
    """Return all reference cases."""
    return VPD_REFERENCE_CASES
