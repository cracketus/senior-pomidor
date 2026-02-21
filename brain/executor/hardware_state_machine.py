"""Deterministic runtime state machine for hardware execution lifecycle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from brain.contracts import DeviceStatusV1


class ExecutorRuntimeState(str, Enum):
    """Executor runtime states for hardware dispatch lifecycle."""

    NOMINAL = "nominal"
    DEGRADED = "degraded"
    FAULTED = "faulted"
    SAFE_MODE = "safe_mode"


@dataclass(frozen=True)
class StateTransition:
    """Single state transition event."""

    previous_state: ExecutorRuntimeState
    next_state: ExecutorRuntimeState
    reason: str
    timestamp: datetime


@dataclass(frozen=True)
class StateMachineConfig:
    """Thresholds for deterministic state transitions."""

    stale_after_seconds: int = 15 * 60
    fault_after_seconds: int = 45 * 60
    adapter_errors_for_fault: int = 2
    adapter_errors_for_safe_mode: int = 3
    healthy_cycles_for_recovery: int = 2


class HardwareExecutionStateMachine:
    """Tracks runtime health state from telemetry and dispatch outcomes."""

    def __init__(self, config: StateMachineConfig | None = None) -> None:
        self._config = config or StateMachineConfig()
        self._state = ExecutorRuntimeState.NOMINAL
        self._consecutive_adapter_errors = 0
        self._consecutive_healthy_cycles = 0

    @property
    def state(self) -> ExecutorRuntimeState:
        return self._state

    def can_execute(self) -> bool:
        return self._state in {
            ExecutorRuntimeState.NOMINAL,
            ExecutorRuntimeState.DEGRADED,
        }

    def observe_telemetry(
        self,
        *,
        now: datetime,
        device_status: DeviceStatusV1 | None,
    ) -> list[StateTransition]:
        transitions: list[StateTransition] = []
        if device_status is None:
            self._consecutive_healthy_cycles = 0
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.FAULTED,
                    reason="telemetry_missing",
                    timestamp=now,
                )
            )
            return transitions

        age_seconds = max(0.0, (now - device_status.timestamp).total_seconds())
        telemetry_fault = (not device_status.mcu_connected) or (
            age_seconds > self._config.fault_after_seconds
        )
        telemetry_degraded = age_seconds > self._config.stale_after_seconds

        if telemetry_fault:
            self._consecutive_healthy_cycles = 0
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.FAULTED,
                    reason=(
                        "mcu_disconnected"
                        if not device_status.mcu_connected
                        else "telemetry_stale_fault"
                    ),
                    timestamp=now,
                )
            )
            return transitions

        if telemetry_degraded:
            self._consecutive_healthy_cycles = 0
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.DEGRADED,
                    reason="telemetry_stale_degraded",
                    timestamp=now,
                )
            )
            return transitions

        self._consecutive_healthy_cycles += 1
        if (
            self._state == ExecutorRuntimeState.SAFE_MODE
            and self._consecutive_adapter_errors == 0
            and self._consecutive_healthy_cycles >= self._config.healthy_cycles_for_recovery
        ):
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.DEGRADED,
                    reason="safe_mode_recovery_window",
                    timestamp=now,
                )
            )
            return transitions

        if (
            self._state in {ExecutorRuntimeState.DEGRADED, ExecutorRuntimeState.FAULTED}
            and self._consecutive_adapter_errors == 0
            and self._consecutive_healthy_cycles >= self._config.healthy_cycles_for_recovery
        ):
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.NOMINAL,
                    reason="telemetry_recovered",
                    timestamp=now,
                )
            )
        return transitions

    def observe_dispatch_result(
        self,
        *,
        accepted: bool,
        now: datetime,
    ) -> list[StateTransition]:
        transitions: list[StateTransition] = []
        if accepted:
            self._consecutive_adapter_errors = 0
            return transitions

        self._consecutive_adapter_errors += 1
        self._consecutive_healthy_cycles = 0
        if self._consecutive_adapter_errors >= self._config.adapter_errors_for_safe_mode:
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.SAFE_MODE,
                    reason="adapter_errors_safe_mode",
                    timestamp=now,
                )
            )
        elif self._consecutive_adapter_errors >= self._config.adapter_errors_for_fault:
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.FAULTED,
                    reason="adapter_errors_faulted",
                    timestamp=now,
                )
            )
        else:
            transitions.extend(
                self._transition_to(
                    ExecutorRuntimeState.DEGRADED,
                    reason="adapter_error_degraded",
                    timestamp=now,
                )
            )
        return transitions

    def _transition_to(
        self,
        next_state: ExecutorRuntimeState,
        *,
        reason: str,
        timestamp: datetime,
    ) -> list[StateTransition]:
        if self._state == next_state:
            return []
        previous_state = self._state
        self._state = next_state
        return [
            StateTransition(
                previous_state=previous_state,
                next_state=next_state,
                reason=reason,
                timestamp=timestamp,
            )
        ]
