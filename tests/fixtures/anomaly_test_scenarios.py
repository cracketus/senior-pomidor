"""
Test scenarios for anomaly detection validation.

These scenarios define realistic situations where anomalies should or should not be triggered.
Each scenario includes observation setup, expected anomalies, and rationale.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class AnomalyScenario:
    """Single test scenario for anomaly detection."""

    scenario_id: str
    description: str
    # Observation inputs
    soil_moisture_p1: float
    soil_moisture_p2: Optional[float] = None
    air_temperature: float = 22.0
    air_humidity: float = 65.0
    vpd: float = 1.2
    # Expected anomalies (list of anomaly type strings expected)
    expected_anomalies: list[str] = field(default_factory=list)
    # Context
    observation_age_minutes: int = 5
    notes: str = ""


# Test scenarios covering various anomaly conditions
ANOMALY_TEST_SCENARIOS = [
    AnomalyScenario(
        scenario_id="anom_001",
        description="Normal operation: all metrics in range",
        soil_moisture_p1=0.55,
        soil_moisture_p2=0.54,
        air_temperature=22.0,
        air_humidity=65.0,
        vpd=1.2,
        expected_anomalies=[],
        notes="Baseline healthy state; no anomalies",
    ),
    AnomalyScenario(
        scenario_id="anom_002",
        description="Soil moisture critically low (P1 < 10%)",
        soil_moisture_p1=0.08,
        soil_moisture_p2=0.10,
        air_temperature=24.0,
        air_humidity=55.0,
        vpd=1.85,
        expected_anomalies=["soil_moisture_low"],
        notes="Plant at immediate wilting risk; watering required",
    ),
    AnomalyScenario(
        scenario_id="anom_003",
        description="Soil moisture high (P1 > 85%)",
        soil_moisture_p1=0.92,
        soil_moisture_p2=0.88,
        air_temperature=20.0,
        air_humidity=78.0,
        vpd=0.65,
        expected_anomalies=["soil_moisture_high"],
        notes="Waterlogging risk; reduce watering; increase ventilation",
    ),
    AnomalyScenario(
        scenario_id="anom_004",
        description="High soil differential (P1 vs P2 > 40%)",
        soil_moisture_p1=0.72,
        soil_moisture_p2=0.25,
        air_temperature=23.0,
        air_humidity=60.0,
        vpd=1.35,
        expected_anomalies=["soil_moisture_differential"],
        notes="Uneven watering or root distribution issue",
    ),
    AnomalyScenario(
        scenario_id="anom_005",
        description="VPD critically high (> 3.5 kPa)",
        soil_moisture_p1=0.45,
        soil_moisture_p2=0.48,
        air_temperature=36.0,
        air_humidity=18.0,
        vpd=3.8,
        expected_anomalies=["vpd_high"],
        notes="Extreme transpiration stress; close vents; reduce light",
    ),
    AnomalyScenario(
        scenario_id="anom_006",
        description="VPD critically low (< 0.2 kPa)",
        soil_moisture_p1=0.62,
        soil_moisture_p2=0.60,
        air_temperature=16.0,
        air_humidity=99.0,
        vpd=0.12,
        expected_anomalies=["vpd_low"],
        notes="Excessive humidity; fungal disease risk; increase ventilation",
    ),
    AnomalyScenario(
        scenario_id="anom_007",
        description="Temperature too cold (< 8°C)",
        soil_moisture_p1=0.55,
        soil_moisture_p2=0.54,
        air_temperature=5.0,
        air_humidity=75.0,
        vpd=1.05,
        expected_anomalies=["temperature_low"],
        notes="Growth stalls; activate heater",
    ),
    AnomalyScenario(
        scenario_id="anom_008",
        description="Temperature too hot (> 32°C)",
        soil_moisture_p1=0.48,
        soil_moisture_p2=0.50,
        air_temperature=35.5,
        air_humidity=35.0,
        vpd=3.72,
        expected_anomalies=["temperature_high", "vpd_high"],
        notes="Heat stress; flower sterility risk; open vents; provide shade",
    ),
    AnomalyScenario(
        scenario_id="anom_009",
        description="Multiple simultaneous anomalies",
        soil_moisture_p1=0.08,
        soil_moisture_p2=0.92,
        air_temperature=38.0,
        air_humidity=22.0,
        vpd=4.1,
        expected_anomalies=[
            "soil_moisture_low",
            "soil_moisture_high",
            "soil_moisture_differential",
            "temperature_high",
            "vpd_high",
        ],
        notes="Complex emergency; system should escalate to SAFE MODE",
    ),
    AnomalyScenario(
        scenario_id="anom_010",
        description="Borderline soil moisture (just above threshold)",
        soil_moisture_p1=0.105,
        soil_moisture_p2=0.12,
        air_temperature=23.0,
        air_humidity=62.0,
        vpd=1.28,
        expected_anomalies=[],
        notes="Just above 10% threshold; no anomaly yet (margin for noise)",
    ),
    AnomalyScenario(
        scenario_id="anom_011",
        description="Borderline soil moisture (just below threshold)",
        soil_moisture_p1=0.095,
        soil_moisture_p2=0.11,
        air_temperature=23.0,
        air_humidity=62.0,
        vpd=1.28,
        expected_anomalies=["soil_moisture_low"],
        notes="Just below 10% threshold; anomaly triggered",
    ),
    AnomalyScenario(
        scenario_id="anom_012",
        description="Night conditions with low VPD",
        soil_moisture_p1=0.61,
        soil_moisture_p2=0.59,
        air_temperature=14.0,
        air_humidity=92.0,
        vpd=0.28,
        expected_anomalies=[],
        notes="Normal night condition; high humidity not anomalous if below 0.2 kPa threshold",
    ),
    AnomalyScenario(
        scenario_id="anom_013",
        description="One probe missing (P2=None) with P1 normal",
        soil_moisture_p1=0.55,
        soil_moisture_p2=None,
        air_temperature=22.0,
        air_humidity=65.0,
        vpd=1.2,
        expected_anomalies=[],
        notes="Single probe is normal; no differential anomaly if P2=None",
    ),
    AnomalyScenario(
        scenario_id="anom_014",
        description="Stale observation (90 minutes old)",
        soil_moisture_p1=0.55,
        soil_moisture_p2=0.54,
        air_temperature=22.0,
        air_humidity=65.0,
        vpd=1.2,
        expected_anomalies=[],
        observation_age_minutes=90,
        notes="Anomalies depend on sensor health checks, not age alone",
    ),
]


def get_scenario(scenario_id: str) -> AnomalyScenario:
    """Retrieve a scenario by ID."""
    for scenario in ANOMALY_TEST_SCENARIOS:
        if scenario.scenario_id == scenario_id:
            return scenario
    raise ValueError(f"Scenario {scenario_id} not found")


def get_all_scenarios() -> list[AnomalyScenario]:
    """Return all anomaly scenarios."""
    return ANOMALY_TEST_SCENARIOS


def get_scenarios_by_anomaly_type(anomaly_type: str) -> list[AnomalyScenario]:
    """Get all scenarios that trigger a specific anomaly type."""
    return [
        s for s in ANOMALY_TEST_SCENARIOS if anomaly_type in s.expected_anomalies
    ]
