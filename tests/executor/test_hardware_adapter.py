"""Tests for hardware adapter foundation."""

from datetime import datetime, timezone

from brain.contracts import ActionV1
from brain.contracts.action_v1 import ActionType
from brain.executor import HardwareStubAdapter


def test_dispatch_maps_action_to_expected_command():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    action = ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=12.0,
        intensity=0.7,
        reason="test",
    )
    adapter = HardwareStubAdapter()

    result = adapter.dispatch(action=action, now=now)

    assert result.accepted is True
    assert result.command == "WATER_PULSE"
    assert result.duration_seconds == 12.0
