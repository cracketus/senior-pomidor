"""Tests for sampling_plan_v1 contract."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from brain.contracts.sampling_plan_v1 import SamplingOverrideV1, SamplingPlanV1


def test_sampling_plan_valid_payload():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    plan = SamplingPlanV1(
        schema_version="sampling_plan_v1",
        generated_at=now,
        base_sampling_minutes=120,
        active_scenarios=["heatwave"],
        overrides=[
            SamplingOverrideV1(
                start_ts=now + timedelta(hours=1),
                end_ts=now + timedelta(hours=3),
                sampling_minutes=15,
                scenario="heatwave",
                reason="risk_window",
            )
        ],
    )
    assert plan.schema_version == "sampling_plan_v1"


def test_sampling_override_rejects_invalid_window():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        SamplingOverrideV1(
            start_ts=now + timedelta(hours=1),
            end_ts=now,
            sampling_minutes=15,
            scenario="heatwave",
            reason="risk_window",
        )
