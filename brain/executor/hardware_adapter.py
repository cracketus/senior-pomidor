"""Hardware adapter interface and deterministic stub implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from brain.contracts import ActionV1
from brain.contracts.action_v1 import ActionType


@dataclass(frozen=True)
class HardwareDispatchResult:
    """Result from dispatching a validated action to an actuator backend."""

    accepted: bool
    command: str
    duration_seconds: float | None
    details: str | None = None


class HardwareAdapter(Protocol):
    """Abstraction for actuator command dispatch backends."""

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        """Dispatch an action and return deterministic execution metadata."""


class HardwareStubAdapter:
    """Deterministic no-op adapter that mimics hardware command routing."""

    _COMMAND_MAP = {
        ActionType.WATER.value: "WATER_PULSE",
        ActionType.LIGHT.value: "SET_LIGHT",
        ActionType.FAN.value: "SET_FAN",
        ActionType.CO2.value: "CO2_INJECT",
        ActionType.CIRCULATE.value: "SET_CIRCULATION",
    }

    def dispatch(self, *, action: ActionV1, now: datetime) -> HardwareDispatchResult:
        command = self._COMMAND_MAP.get(str(action.action_type), "UNKNOWN")
        return HardwareDispatchResult(
            accepted=True,
            command=command,
            duration_seconds=action.duration_seconds,
            details=f"hardware_stub_dispatched_at={now.isoformat()}",
        )
