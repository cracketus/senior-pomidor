"""Executor that routes validated actions through a hardware adapter."""

from __future__ import annotations

from datetime import datetime

from brain.contracts import ActionV1, ExecutorEventV1, GuardrailResultV1
from brain.contracts.executor_event_v1 import ExecutorStatus
from brain.contracts.guardrail_result_v1 import GuardrailDecision
from brain.executor.hardware_adapter import HardwareAdapter


class HardwareExecutor:
    """Dispatch effective actions through a hardware adapter abstraction."""

    def __init__(self, adapter: HardwareAdapter) -> None:
        if not getattr(adapter, "adapter_name", ""):
            raise ValueError("adapter must define non-empty adapter_name")
        self._adapter = adapter

    def execute(
        self,
        *,
        proposed_action: ActionV1,
        effective_action: ActionV1 | None,
        guardrail_result: GuardrailResultV1,
        now: datetime,
    ) -> ExecutorEventV1:
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
