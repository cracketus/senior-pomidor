"""Deterministic Guardrails v1 validator with hybrid clip/reject behavior."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from brain.contracts import ActionV1, AnomalyV1, DeviceStatusV1, GuardrailResultV1, StateV1
from brain.contracts.action_v1 import ActionType
from brain.contracts.anomaly_v1 import SeverityLevel
from brain.contracts.guardrail_result_v1 import (
    GuardrailDecision,
    GuardrailReasonCode,
)


@dataclass
class GuardrailsConfig:
    """Configurable Stage 2 guardrail limits."""

    max_state_age: timedelta = timedelta(minutes=30)
    min_confidence: float = 0.40
    min_water_interval: timedelta = timedelta(minutes=15)
    daily_water_budget_ml: float = 2200.0
    water_ml_per_second: float = 8.0
    max_water_duration_seconds: float = 30.0


class GuardrailsValidator:
    """Validate proposed actions and return effective action + guardrail result."""

    def __init__(self, config: GuardrailsConfig | None = None) -> None:
        self._config = config or GuardrailsConfig()
        self._last_water_approved_at: datetime | None = None
        self._water_used_ml: float = 0.0

    def validate(
        self,
        action: ActionV1,
        *,
        state: StateV1,
        device_status: DeviceStatusV1,
        anomalies: list[AnomalyV1],
        now: datetime,
    ) -> tuple[ActionV1 | None, GuardrailResultV1]:
        """Return effective action (or None) and guardrail validation result."""
        reject_codes: list[GuardrailReasonCode] = []
        clip_codes: list[GuardrailReasonCode] = []
        clipped_fields: list[str] = []
        effective = action

        if action.action_type != ActionType.WATER.value:
            reject_codes.append(GuardrailReasonCode.ACTION_INVALID)

        if action.duration_seconds is None or action.duration_seconds <= 0:
            reject_codes.append(GuardrailReasonCode.ACTION_INVALID)

        if not device_status.mcu_connected:
            reject_codes.append(GuardrailReasonCode.DEVICE_OFFLINE)

        if state.confidence < self._config.min_confidence:
            reject_codes.append(GuardrailReasonCode.LOW_CONFIDENCE)

        if (now - state.timestamp) > self._config.max_state_age:
            reject_codes.append(GuardrailReasonCode.STALE_DATA)

        if any(
            anomaly.severity == SeverityLevel.CRITICAL.value
            or anomaly.requires_safe_mode
            for anomaly in anomalies
        ):
            reject_codes.append(GuardrailReasonCode.ENVIRONMENT_LIMIT)

        if (
            self._last_water_approved_at is not None
            and (now - self._last_water_approved_at) < self._config.min_water_interval
        ):
            reject_codes.append(GuardrailReasonCode.INTERVAL_VIOLATION)

        duration = float(action.duration_seconds or 0.0)
        if duration > self._config.max_water_duration_seconds:
            duration = self._config.max_water_duration_seconds
            clip_codes.extend(
                [GuardrailReasonCode.ACTION_CLIPPED, GuardrailReasonCode.ENVIRONMENT_LIMIT]
            )
            clipped_fields.append("duration_seconds")

        intensity = float(action.intensity if action.intensity is not None else 1.0)
        proposed_ml = duration * self._config.water_ml_per_second * intensity
        remaining_budget = max(0.0, self._config.daily_water_budget_ml - self._water_used_ml)

        if remaining_budget <= 0.0:
            reject_codes.append(GuardrailReasonCode.BUDGET_EXCEEDED)
        elif proposed_ml > remaining_budget:
            if intensity <= 0.0 or self._config.water_ml_per_second <= 0.0:
                reject_codes.append(GuardrailReasonCode.BUDGET_EXCEEDED)
            else:
                duration = remaining_budget / (self._config.water_ml_per_second * intensity)
                if duration <= 0.0:
                    reject_codes.append(GuardrailReasonCode.BUDGET_EXCEEDED)
                else:
                    clip_codes.extend(
                        [GuardrailReasonCode.ACTION_CLIPPED, GuardrailReasonCode.BUDGET_EXCEEDED]
                    )
                    if "duration_seconds" not in clipped_fields:
                        clipped_fields.append("duration_seconds")

        if reject_codes:
            result = GuardrailResultV1(
                schema_version="guardrail_result_v1",
                timestamp=now,
                decision=GuardrailDecision.REJECTED,
                reason_codes=self._dedupe_codes(reject_codes),
                clipped_fields=None,
            )
            return None, result

        if clip_codes:
            updated_budget = max(
                0.0, remaining_budget - duration * self._config.water_ml_per_second * intensity
            )
            effective = action.model_copy(
                update={
                    "duration_seconds": round(duration, 3),
                    "budget_remaining_ml": round(updated_budget, 3),
                    "notes": "clipped_by_guardrails_v1",
                }
            )
            self._water_used_ml += duration * self._config.water_ml_per_second * intensity
            self._last_water_approved_at = now
            result = GuardrailResultV1(
                schema_version="guardrail_result_v1",
                timestamp=now,
                decision=GuardrailDecision.CLIPPED,
                reason_codes=self._dedupe_codes(clip_codes),
                clipped_fields=clipped_fields,
            )
            return effective, result

        budget_remaining_ml = max(0.0, remaining_budget - proposed_ml)
        effective = action.model_copy(
            update={"duration_seconds": round(duration, 3), "budget_remaining_ml": round(budget_remaining_ml, 3)}
        )
        self._water_used_ml += proposed_ml
        self._last_water_approved_at = now
        result = GuardrailResultV1(
            schema_version="guardrail_result_v1",
            timestamp=now,
            decision=GuardrailDecision.APPROVED,
        )
        return effective, result

    @staticmethod
    def _dedupe_codes(codes: list[GuardrailReasonCode]) -> list[GuardrailReasonCode]:
        seen: set[GuardrailReasonCode] = set()
        ordered: list[GuardrailReasonCode] = []
        for code in codes:
            if code in seen:
                continue
            seen.add(code)
            ordered.append(code)
        return ordered
