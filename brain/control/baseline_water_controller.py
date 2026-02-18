"""Deterministic baseline controller for Stage 2 water-only actions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from brain.contracts import ActionV1, StateV1
from brain.contracts.action_v1 import ActionType


def _clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


@dataclass(frozen=True)
class BaselineWaterControlConfig:
    """Configuration for water-only baseline policy."""

    trigger_threshold: float = 0.42
    target_moisture: float = 0.55
    min_duration_seconds: float = 8.0
    max_duration_seconds: float = 40.0
    intensity: float = 0.8


class BaselineWaterController:
    """Propose deterministic water actions from StateV1 snapshots.

    Stage 2 intentionally emits only `ActionType.WATER`. All other action
    types are deferred to next stages.
    """

    def __init__(self, config: BaselineWaterControlConfig | None = None) -> None:
        self._config = config or BaselineWaterControlConfig()

    def propose_action(
        self,
        state: StateV1,
        *,
        now: datetime | None = None,
    ) -> ActionV1 | None:
        """Return a water action when p1 moisture is below trigger threshold."""
        if state.soil_moisture_p1 >= self._config.trigger_threshold:
            return None

        timestamp = now or state.timestamp
        moisture_deficit = max(0.0, self._config.target_moisture - state.soil_moisture_p1)
        normalized_deficit = _clamp(
            moisture_deficit / max(self._config.target_moisture, 1e-9), 0.0, 1.0
        )
        duration_seconds = self._config.min_duration_seconds + normalized_deficit * (
            self._config.max_duration_seconds - self._config.min_duration_seconds
        )

        return ActionV1(
            schema_version="action_v1",
            timestamp=timestamp,
            action_type=ActionType.WATER,
            duration_seconds=round(duration_seconds, 3),
            intensity=self._config.intensity,
            reason=(
                "Stage 2 water-only policy: soil_moisture_p1 "
                f"({state.soil_moisture_p1:.3f}) below trigger "
                f"({self._config.trigger_threshold:.3f})."
            ),
            estimated_impact=round(normalized_deficit, 3),
            confidence=state.confidence,
        )
