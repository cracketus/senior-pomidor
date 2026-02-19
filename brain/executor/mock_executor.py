"""Log-only mock executor for Stage 2."""

from __future__ import annotations

from datetime import datetime

from brain.contracts import ActionV1, ExecutorEventV1, GuardrailResultV1
from brain.contracts.executor_event_v1 import ExecutorStatus
from brain.contracts.guardrail_result_v1 import GuardrailDecision


class MockExecutor:
    """Record execution intent without affecting plant dynamics."""

    def execute(
        self,
        *,
        proposed_action: ActionV1,
        effective_action: ActionV1 | None,
        guardrail_result: GuardrailResultV1,
        now: datetime,
    ) -> ExecutorEventV1:
        """Return execution event from proposal/guardrail outcome."""
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

        return ExecutorEventV1(
            schema_version="executor_event_v1",
            timestamp=now,
            status=ExecutorStatus.EXECUTED,
            action_type=str(effective_action.action_type),
            guardrail_decision=guardrail_result.decision,
            reason_codes=guardrail_result.reason_codes,
            duration_seconds=effective_action.duration_seconds,
            notes=(
                "executed_mock_clipped"
                if guardrail_result.decision == GuardrailDecision.CLIPPED.value
                else "executed_mock"
            ),
        )
