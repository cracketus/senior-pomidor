"""Tests for targets_v1 contract."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from brain.contracts.targets_v1 import BudgetAdaptationV1, TargetEnvelopeV1, TargetsV1


def test_targets_v1_valid_payload():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    payload = TargetsV1(
        schema_version="targets_v1",
        generated_at=now,
        valid_until_ts=now + timedelta(hours=6),
        base_targets=TargetEnvelopeV1(
            vpd_min_kpa=0.8,
            vpd_max_kpa=1.5,
            soil_moisture_min_pct=35.0,
            soil_moisture_max_pct=75.0,
        ),
        adapted_targets=TargetEnvelopeV1(
            vpd_min_kpa=0.7,
            vpd_max_kpa=1.3,
            soil_moisture_min_pct=40.0,
            soil_moisture_max_pct=75.0,
        ),
        adapted_budgets=BudgetAdaptationV1(
            water_budget_multiplier=1.2,
            co2_budget_multiplier=0.9,
        ),
        active_scenarios=["heatwave"],
    )
    assert payload.schema_version == "targets_v1"


def test_targets_v1_rejects_invalid_ranges():
    with pytest.raises(ValidationError):
        TargetEnvelopeV1(
            vpd_min_kpa=1.5,
            vpd_max_kpa=0.8,
            soil_moisture_min_pct=35.0,
            soil_moisture_max_pct=75.0,
        )


def test_targets_v1_rejects_invalid_window():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        TargetsV1(
            schema_version="targets_v1",
            generated_at=now,
            valid_until_ts=now,
            base_targets=TargetEnvelopeV1(
                vpd_min_kpa=0.8,
                vpd_max_kpa=1.5,
                soil_moisture_min_pct=35.0,
                soil_moisture_max_pct=75.0,
            ),
            adapted_targets=TargetEnvelopeV1(
                vpd_min_kpa=0.7,
                vpd_max_kpa=1.3,
                soil_moisture_min_pct=40.0,
                soil_moisture_max_pct=75.0,
            ),
            adapted_budgets=BudgetAdaptationV1(
                water_budget_multiplier=1.1,
                co2_budget_multiplier=1.0,
            ),
        )
