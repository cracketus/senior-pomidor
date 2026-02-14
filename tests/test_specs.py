"""Tests for specification documents and fixtures."""

import os
from pathlib import Path

from tests.fixtures.anomaly_test_scenarios import (
    ANOMALY_TEST_SCENARIOS,
    get_scenario,
    get_scenarios_by_anomaly_type,
)
from tests.fixtures.vpd_reference_cases import (
    VPD_REFERENCE_CASES,
    get_all_reference_cases,
    get_reference_case,
)


class TestSpecificationDocuments:
    """Test that specification documents exist and are readable."""

    def test_confidence_scoring_docs_exist_and_are_readable(self):
        """Confidence scoring documentation should exist and be non-empty."""
        doc_path = Path("docs/confidence_scoring.md")
        assert doc_path.exists(), "docs/confidence_scoring.md not found"
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) > 500, "confidence_scoring.md too short"
        assert "Algorithm" in content
        assert "Example" in content
        assert "Interpretation" in content

    def test_anomaly_threshold_docs_exist_and_are_readable(self):
        """Anomaly threshold documentation should exist and be non-empty."""
        doc_path = Path("docs/anomaly_thresholds.md")
        assert doc_path.exists(), "docs/anomaly_thresholds.md not found"
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) > 500, "anomaly_thresholds.md too short"
        assert "Threshold" in content
        assert "Severity" in content
        assert "Fault Detection" in content


class TestVPDReferenceCases:
    """Test VPD reference case fixture."""

    def test_all_reference_cases_are_valid(self):
        """All reference cases should be valid and retrievable."""
        cases = get_all_reference_cases()
        assert len(cases) >= 5, "Should have at least 5 reference cases"

        for case in cases:
            # Validate structure
            assert case.case_id.startswith("vpd_")
            assert 0 <= case.air_temperature_celsius <= 40
            assert 0 <= case.relative_humidity_percent <= 100
            assert case.expected_vpd_kpa >= 0
            assert case.tolerance_kpa > 0
            # Validate retrievability
            retrieved = get_reference_case(case.case_id)
            assert retrieved.case_id == case.case_id

    def test_reference_case_retrieval(self):
        """Reference cases should be retrievable by ID."""
        case = get_reference_case("vpd_001")
        assert case.case_id == "vpd_001"
        assert case.air_temperature_celsius == 22.0
        assert case.relative_humidity_percent == 65.0

    def test_reference_case_not_found(self):
        """Non-existent reference case should raise."""
        with __import__("pytest").raises(ValueError):
            get_reference_case("vpd_999")

    def test_vpd_physical_constraints(self):
        """VPD should reflect physical relationships."""
        cases = get_all_reference_cases()

        # VPD increases with temperature (at constant RH)
        warm_case = next(c for c in cases if c.case_id == "vpd_005")  # 35°C, 25%
        cool_case = next(c for c in cases if c.case_id == "vpd_004")  # 5°C, 95%
        assert warm_case.expected_vpd_kpa > cool_case.expected_vpd_kpa

        # VPD goes to zero at saturation (100% RH)
        saturation = next(
            c for c in cases if c.case_id == "vpd_007"
        )  # 100% RH
        assert saturation.expected_vpd_kpa < 0.01  # Should be near zero


class TestAnomalyScenarios:
    """Test anomaly detection scenario fixture."""

    def test_all_scenarios_are_valid(self):
        """All scenarios should be valid and retrievable."""
        scenarios = ANOMALY_TEST_SCENARIOS
        assert len(scenarios) >= 10, "Should have at least 10 scenarios"

        for scenario in scenarios:
            # Validate structure
            assert scenario.scenario_id.startswith("anom_")
            assert isinstance(scenario.expected_anomalies, list)
            assert 0 <= scenario.soil_moisture_p1 <= 1.0
            assert 0 <= scenario.air_temperature <= 40
            assert 0 <= scenario.air_humidity <= 100
            assert scenario.vpd >= 0
            # Validate retrievability
            retrieved = get_scenario(scenario.scenario_id)
            assert retrieved.scenario_id == scenario.scenario_id

    def test_scenario_retrieval(self):
        """Scenarios should be retrievable by ID."""
        scenario = get_scenario("anom_001")
        assert scenario.scenario_id == "anom_001"
        assert len(scenario.expected_anomalies) == 0

    def test_scenario_not_found(self):
        """Non-existent scenario should raise."""
        with __import__("pytest").raises(ValueError):
            get_scenario("anom_999")

    def test_get_scenarios_by_anomaly_type(self):
        """Should retrieve scenarios by anomaly type."""
        low_soil_scenarios = get_scenarios_by_anomaly_type("soil_moisture_low")
        assert len(low_soil_scenarios) >= 1
        assert all(
            "soil_moisture_low" in s.expected_anomalies
            for s in low_soil_scenarios
        )

    def test_scenario_with_multiple_anomalies(self):
        """Scenario with multiple simultaneous anomalies should be defined."""
        multi_scenario = get_scenario("anom_009")
        assert len(multi_scenario.expected_anomalies) >= 3

    def test_normal_operation_scenario(self):
        """Should have a baseline normal scenario."""
        normal = get_scenario("anom_001")
        assert len(normal.expected_anomalies) == 0
        assert normal.soil_moisture_p1 > 0.3
        assert normal.soil_moisture_p1 < 0.8

    def test_anomaly_type_coverage(self):
        """Should cover major anomaly types."""
        all_anomalies = set()
        for scenario in ANOMALY_TEST_SCENARIOS:
            all_anomalies.update(scenario.expected_anomalies)

        required_types = {
            "soil_moisture_low",
            "soil_moisture_high",
            "vpd_high",
            "vpd_low",
            "temperature_high",
            "temperature_low",
        }
        assert required_types.issubset(all_anomalies)
