"""Executor that routes validated actions through hardware adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from brain.contracts import ActionV1, DeviceStatusV1, ExecutorEventV1, GuardrailResultV1
from brain.contracts.executor_event_v1 import ExecutorStatus
from brain.contracts.guardrail_result_v1 import GuardrailDecision
from brain.executor.hardware_adapter import HardwareAdapter
from brain.executor.hardware_state_machine import (
    HardwareExecutionStateMachine,
    StateTransition,
)
from brain.executor.idempotency import IdempotencyConfig
from brain.executor.retry_policy import RetryPolicyConfig


@dataclass(frozen=True)
class _IdempotencyEntry:
    key: str
    first_seen_at: datetime
    expires_at: datetime


class HardwareExecutor:
    """Dispatch effective actions through a hardware adapter abstraction."""

    def __init__(
        self,
        adapter: HardwareAdapter,
        *,
        retry_policy: RetryPolicyConfig | None = None,
        idempotency: IdempotencyConfig | None = None,
    ) -> None:
        if not getattr(adapter, "adapter_name", ""):
            raise ValueError("adapter must define non-empty adapter_name")
        self._adapter = adapter
        self._retry_policy = retry_policy or RetryPolicyConfig()
        self._idempotency = idempotency or IdempotencyConfig()
        self._state_machine = HardwareExecutionStateMachine()
        self._pending_runtime_events: list[ExecutorEventV1] = []
        self._idempotency_cache: dict[str, _IdempotencyEntry] = {}

    def drain_runtime_events(self) -> list[ExecutorEventV1]:
        """Return and clear queued state-machine/runtime events."""
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

    def _append_runtime_event(
        self,
        *,
        timestamp: datetime,
        action_type: str,
        guardrail_decision: str,
        reason_codes: list[str],
        note: str,
    ) -> None:
        self._pending_runtime_events.append(
            ExecutorEventV1(
                schema_version="executor_event_v1",
                timestamp=timestamp,
                status=ExecutorStatus.SKIPPED,
                action_type=action_type,
                guardrail_decision=guardrail_decision,
                reason_codes=reason_codes,
                duration_seconds=None,
                notes=note,
            )
        )

    def _purge_expired_idempotency(self, *, now: datetime) -> None:
        expired = [key for key, entry in self._idempotency_cache.items() if entry.expires_at <= now]
        for key in expired:
            self._idempotency_cache.pop(key, None)

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

        key = effective_action.idempotency_key or proposed_action.idempotency_key
        self._purge_expired_idempotency(now=now)
        if key is not None and key in self._idempotency_cache:
            cached = self._idempotency_cache[key]
            self._append_runtime_event(
                timestamp=now,
                action_type=str(effective_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
                note=(
                    "idempotency_hit:"
                    f"key={cached.key}:"
                    f"first_seen_at={cached.first_seen_at.isoformat()}:"
                    f"expires_at={cached.expires_at.isoformat()}"
                ),
            )
            return ExecutorEventV1(
                schema_version="executor_event_v1",
                timestamp=now,
                status=ExecutorStatus.SKIPPED,
                action_type=str(effective_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes + ["idempotency_duplicate"],
                duration_seconds=None,
                notes=f"skipped_duplicate_idempotency_key:{key}",
            )

        attempt_no = 1
        dispatch_time = now
        dispatch_result = self._adapter.dispatch(action=effective_action, now=dispatch_time)
        while True:
            post_dispatch_transitions = self._state_machine.observe_dispatch_result(
                accepted=dispatch_result.accepted,
                now=dispatch_time,
            )
            self._queue_transition_events(
                transitions=post_dispatch_transitions,
                action_type=str(effective_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
            )
            if dispatch_result.accepted:
                break

            if not dispatch_result.retryable:
                return ExecutorEventV1(
                    schema_version="executor_event_v1",
                    timestamp=dispatch_time,
                    status=ExecutorStatus.SKIPPED,
                    action_type=str(effective_action.action_type),
                    guardrail_decision=guardrail_result.decision,
                    reason_codes=guardrail_result.reason_codes + ["non_retryable_dispatch"],
                    duration_seconds=None,
                    notes=(
                        "adapter_rejected_non_retryable:"
                        f"{dispatch_result.adapter_name}:{dispatch_result.command}:"
                        f"{dispatch_result.error_class or 'unknown_error'}"
                    ),
                )

            if not self._retry_policy.is_retryable_error_class(dispatch_result.error_class):
                return ExecutorEventV1(
                    schema_version="executor_event_v1",
                    timestamp=dispatch_time,
                    status=ExecutorStatus.SKIPPED,
                    action_type=str(effective_action.action_type),
                    guardrail_decision=guardrail_result.decision,
                    reason_codes=guardrail_result.reason_codes + ["retry_class_not_allowed"],
                    duration_seconds=None,
                    notes=(
                        "adapter_rejected_class_blocked:"
                        f"{dispatch_result.adapter_name}:{dispatch_result.command}:"
                        f"{dispatch_result.error_class or 'unknown_error'}"
                    ),
                )

            if attempt_no >= self._retry_policy.max_attempts:
                return ExecutorEventV1(
                    schema_version="executor_event_v1",
                    timestamp=dispatch_time,
                    status=ExecutorStatus.SKIPPED,
                    action_type=str(effective_action.action_type),
                    guardrail_decision=guardrail_result.decision,
                    reason_codes=guardrail_result.reason_codes + ["retry_exhausted"],
                    duration_seconds=None,
                    notes=(
                        "adapter_rejected_retry_exhausted:"
                        f"{dispatch_result.adapter_name}:{dispatch_result.command}:"
                        f"attempts={attempt_no}"
                    ),
                )

            retry_no = attempt_no
            backoff_seconds = self._retry_policy.backoff_seconds_for_retry(retry_no)
            retry_at = dispatch_time + timedelta(seconds=backoff_seconds)
            self._append_runtime_event(
                timestamp=dispatch_time,
                action_type=str(effective_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
                note=(
                    "retry_scheduled:"
                    f"adapter={dispatch_result.adapter_name}:"
                    f"attempt={retry_no + 1}:"
                    f"backoff_seconds={backoff_seconds:.3f}:"
                    f"execute_at={retry_at.isoformat()}"
                ),
            )

            attempt_no += 1
            dispatch_time = retry_at
            dispatch_result = self._adapter.dispatch(action=effective_action, now=dispatch_time)

        clipped = guardrail_result.decision == GuardrailDecision.CLIPPED.value
        if clipped:
            note = (
                "executed_after_retry_"
                f"{dispatch_result.adapter_name}_clipped:"
                f"{dispatch_result.command}:attempts={attempt_no}"
                if attempt_no > 1
                else f"executed_{dispatch_result.adapter_name}_clipped:{dispatch_result.command}"
            )
        else:
            note = (
                "executed_after_retry_"
                f"{dispatch_result.adapter_name}:"
                f"{dispatch_result.command}:attempts={attempt_no}"
                if attempt_no > 1
                else f"executed_{dispatch_result.adapter_name}:{dispatch_result.command}"
            )

        if key is not None:
            if len(self._idempotency_cache) >= self._idempotency.max_entries:
                oldest_key = min(
                    self._idempotency_cache,
                    key=lambda k: self._idempotency_cache[k].first_seen_at,
                )
                self._idempotency_cache.pop(oldest_key, None)
            expires_at = dispatch_time + timedelta(seconds=self._idempotency.ttl_seconds)
            self._idempotency_cache[key] = _IdempotencyEntry(
                key=key,
                first_seen_at=dispatch_time,
                expires_at=expires_at,
            )
            self._append_runtime_event(
                timestamp=dispatch_time,
                action_type=str(effective_action.action_type),
                guardrail_decision=guardrail_result.decision,
                reason_codes=guardrail_result.reason_codes,
                note=f"idempotency_stored:key={key}:expires_at={expires_at.isoformat()}",
            )

        return ExecutorEventV1(
            schema_version="executor_event_v1",
            timestamp=dispatch_time,
            status=ExecutorStatus.EXECUTED,
            action_type=str(effective_action.action_type),
            guardrail_decision=guardrail_result.decision,
            reason_codes=guardrail_result.reason_codes,
            duration_seconds=dispatch_result.duration_seconds,
            notes=note,
        )
