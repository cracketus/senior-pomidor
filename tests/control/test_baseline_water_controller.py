"""Unit tests for Stage 2 water-only baseline controller."""

from datetime import datetime, timezone

from brain.control import BaselineWaterController
from brain.contracts import StateV1


def _make_state(soil_moisture_p1: float) -> StateV1:
    return StateV1(
        schema_version="state_v1",
        timestamp=datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc),
        soil_moisture_p1=soil_moisture_p1,
        soil_moisture_p2=soil_moisture_p1,
        soil_moisture_avg=soil_moisture_p1,
        air_temperature=22.0,
        air_humidity=60.0,
        vpd=1.0,
        co2_ppm=420.0,
        light_intensity=400.0,
        confidence=0.9,
        notes=None,
    )


def test_no_action_when_soil_is_above_threshold():
    controller = BaselineWaterController()
    state = _make_state(soil_moisture_p1=0.60)

    assert controller.propose_action(state) is None


def test_water_action_when_soil_is_below_threshold():
    controller = BaselineWaterController()
    state = _make_state(soil_moisture_p1=0.20)

    action = controller.propose_action(state)

    assert action is not None
    assert action.action_type == "water"
    assert action.duration_seconds is not None
    assert action.duration_seconds > 0
    assert action.reason is not None
    assert "Stage 2 water-only policy" in action.reason


def test_action_output_is_deterministic_for_identical_inputs():
    controller = BaselineWaterController()
    state = _make_state(soil_moisture_p1=0.25)
    now = datetime(2026, 2, 15, 6, 0, tzinfo=timezone.utc)

    action_a = controller.propose_action(state, now=now)
    action_b = controller.propose_action(state, now=now)

    assert action_a is not None
    assert action_b is not None
    assert action_a.model_dump(mode="json") == action_b.model_dump(mode="json")


def test_duration_stays_within_configured_bounds():
    controller = BaselineWaterController()
    state = _make_state(soil_moisture_p1=0.0)

    action = controller.propose_action(state)

    assert action is not None
    assert action.duration_seconds is not None
    assert 8.0 <= action.duration_seconds <= 40.0
