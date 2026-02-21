"""Executor that routes validated actions through a hardware adapter."""

from __future__ import annotations

from datetime import datetime

from brain.contracts import ActionV1, DeviceStatusV1, ExecutorEventV1, GuardrailResultV1
from brain.contracts.executor_event_v1 import ExecutorStatus
from brain.contracts.guardrail_result_v1 import GuardrailDecision
from brain.executor.hardware_adapter import HardwareAdapter
from brain.executor.hardware_state_machine import (
    HardwareExecutionStateMachine,
    StateTransition,
)


class HardwareExecutor:
    """Dispatch effective actions through a hardware adapter abstraction."""

    def __init__(self, adapter: HardwareAdapter) -> None:
        if not getattr(adapter, "adapter_name", ""):
            raise ValueError("adapter must define non-empty adapter_name")
        self._adapter = adapter
        self._state_machine = HardwareExecutionStateMachine()
        self._pending_runtime_events: list[ExecutorEventV1] = []

    def drain_runtime_events(self) -> list[ExecutorEventV1]:
        """Return and clear queued state-machine runtime events."""
        drained = self._pending_runtime_events[:]
        self._pending_runtime_events.clear()
        return drained

    def _queue_transition_events(
        self,
        *,
        transitions: list[StateTransition],
        action_type: str,
        guardrail_decision: str,
        reason_codes: list[str],
    ) -> None:
        for transition in transitions:
            self._pending_runtime_events.append(
                ExecutorEventV1(
                    schema_version="executor_event_v1",
                    timestamp=transition.timestamp,
                    status=ExecutorStatus.SKIPPED,
                    action_type=action_type,
                    guardrail_decision=guardrail_decision,
                    reason_codes=reason_codes,
                    duration_seconds=None,
                    notes=(
                        "state_transition:"
                        f"{transition.previous_state.value}"
                        f"->{transition.next_state.value}:{transition.reason}"
                    ),
                )
            )

    def execute(
        self,
        *,
        proposed_action: ActionV1,
        effective_action: ActionV1 | None,
        guardrail_result: GuardrailResultV1,
        now: datetime,
        device_status: DeviceStatusV1 | None = None,
    ) -> ExecutorEventV1:
        pre_dispatch_transitions = self._state_machine.observe_telemetry(
            now=now,
            device_status=device_status,
        )
        self._queue_transition_events(
            transitions=pre_dispatch_transitions,
            action_type=str(proposed_action.action_type),
            guardrail_decision=guardrail_result.decision,
            reason_codes=guardrail_result.reason_codes,
        )

        if not self._state_machine.can_execute():
            return ExecutorEventV1(
                schema_version="executor_event_v1",
                timestamp=now,
                status=ExecutorStatus.SKIPPED,
                action_type=str(proposed_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
                duration_seconds=None,
                notes=f"blocked_by_state:{self._state_machine.state.value}",
            )

        if effective_action is None:
            return ExecutorEventV1(
                schema_version="executor_event_v1",
                timestamp=now,
                status=ExecutorStatus.SKIPPED,
                action_type=str(proposed_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
                duration_seconds=None,
                notes="skipped_by_guardrails_v1",
            )

        dispatch_result = self._adapter.dispatch(action=effective_action, now=now)
        post_dispatch_transitions = self._state_machine.observe_dispatch_result(
            accepted=dispatch_result.accepted,
            now=now,
        )
        self._queue_transition_events(
            transitions=post_dispatch_transitions,
            action_type=str(effective_action.action_type),
            guardrail_decision=guardrail_result.decision,
            reason_codes=guardrail_result.reason_codes,
        )

        if not dispatch_result.accepted:
            return ExecutorEventV1(
                schema_version="executor_event_v1",
                timestamp=now,
                status=ExecutorStatus.SKIPPED,
                action_type=str(effective_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
                duration_seconds=None,
                notes=(
                    "adapter_rejected:"
                    f"{dispatch_result.adapter_name}:{dispatch_result.command}"
                ),
            )

        clipped = guardrail_result.decision == GuardrailDecision.CLIPPED.value
        return ExecutorEventV1(
            schema_version="executor_event_v1",
            timestamp=now,
            status=ExecutorStatus.EXECUTED,
            action_type=str(effective_action.action_type),
            guardrail_decision=guardrail_result.decision,
            reason_codes=guardrail_result.reason_codes,
            duration_seconds=dispatch_result.duration_seconds,
            notes=(
                f"executed_{dispatch_result.adapter_name}_clipped:{dispatch_result.command}"
                if clipped
                else f"executed_{dispatch_result.adapter_name}:{dispatch_result.command}"
            ),
        )
