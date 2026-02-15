"""Tests for VPD calculation."""

import math
import pytest

from brain.estimator.vpd import calculate_vpd
from tests.fixtures.vpd_reference_cases import get_all_reference_cases


def test_vpd_matches_reference_values():
    for case in get_all_reference_cases():
        vpd = calculate_vpd(
            case.air_temperature_celsius, case.relative_humidity_percent
        )
        assert math.isclose(
            vpd, case.expected_vpd_kpa, abs_tol=case.tolerance_kpa
        ), f"{case.case_id} out of tolerance"


def test_vpd_handles_edge_cases():
    assert calculate_vpd(20.0, 100.0) == 0.0
    assert calculate_vpd(20.0, 0.0) > 0.0
    with pytest.raises(ValueError):
        calculate_vpd(20.0, -1.0)
    with pytest.raises(ValueError):
        calculate_vpd(20.0, 101.0)
