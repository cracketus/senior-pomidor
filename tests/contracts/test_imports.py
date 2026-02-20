"""Tests for __init__.py of contracts module."""

import pytest

from brain.contracts import (
    ActionV1,
    AnomalyV1,
    ExecutorEventV1,
    Forecast36hV1,
    GuardrailResultV1,
    SamplingPlanV1,
    SensorHealthV1,
    StateV1,
    TargetsV1,
    VisionExplanationV1,
    VisionInputV1,
    VisionV1,
    WeatherAdapterLogV1,
)


def test_all_contracts_are_importable():
    """Verify all contract models can be imported from brain.contracts."""
    assert StateV1 is not None
    assert ActionV1 is not None
    assert AnomalyV1 is not None
    assert ExecutorEventV1 is not None
    assert Forecast36hV1 is not None
    assert GuardrailResultV1 is not None
    assert TargetsV1 is not None
    assert SamplingPlanV1 is not None
    assert WeatherAdapterLogV1 is not None
    assert VisionInputV1 is not None
    assert VisionV1 is not None
    assert VisionExplanationV1 is not None
    assert SensorHealthV1 is not None
