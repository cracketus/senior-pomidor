"""Tests for hardware adapter foundation."""

from datetime import datetime, timezone

import pytest

from brain.contracts import ActionV1
from brain.contracts.action_v1 import ActionType
from brain.executor import (
    HardwareDispatchResult,
    HardwareStubAdapter,
    available_hardware_adapters,
    create_hardware_adapter,
    register_hardware_adapter,
)


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
    assert result.adapter_name == "hardware_stub"


def test_create_adapter_supports_production_scaffold():
    adapter = create_hardware_adapter("production_scaffold")
    assert adapter.adapter_name == "production_scaffold"


def test_registry_returns_known_adapters():
    adapters = available_hardware_adapters()
    assert "hardware_stub" in adapters
    assert "production_scaffold" in adapters


def test_register_hardware_adapter_allows_custom_factory():
    class _CustomAdapter:
        @property
        def adapter_name(self) -> str:
            return "custom_adapter"

        def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
            return HardwareDispatchResult(
                accepted=True,
                command="CUSTOM",
                duration_seconds=action.duration_seconds,
                adapter_name=self.adapter_name,
                details=now.isoformat(),
            )

    register_hardware_adapter("custom_adapter", _CustomAdapter)
    adapter = create_hardware_adapter("custom_adapter")
    assert adapter.adapter_name == "custom_adapter"


def test_dispatch_result_validates_required_fields():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    action = ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=10.0,
        intensity=0.8,
        reason="test",
    )
    adapter = HardwareStubAdapter()
    result = adapter.dispatch(action=action, now=now)
    assert isinstance(result, HardwareDispatchResult)


def test_unknown_adapter_name_raises_value_error():
    with pytest.raises(ValueError):
        create_hardware_adapter("missing_adapter")
