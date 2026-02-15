"""GuardrailResultV1: validation outcome for proposed control actions."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GuardrailDecision(str, Enum):
    """Decision returned by guardrails."""

    APPROVED = "approved"
    REJECTED = "rejected"
    CLIPPED = "clipped"


class GuardrailReasonCode(str, Enum):
    """Standardized machine-readable reason codes for guardrail outcomes."""

    BUDGET_EXCEEDED = "budget_exceeded"
    INTERVAL_VIOLATION = "interval_violation"
    STALE_DATA = "stale_data"
    LOW_CONFIDENCE = "low_confidence"
    DEVICE_OFFLINE = "device_offline"
    ENVIRONMENT_LIMIT = "environment_limit"
    ACTION_INVALID = "action_invalid"
    ACTION_CLIPPED = "action_clipped"


class GuardrailResultV1(BaseModel):
    """Validation result for a proposed action before execution."""

    model_config = ConfigDict(
        use_enum_values=True,
        strict=True,
    )

    schema_version: str = Field(
        description="Schema version identifier. Must be 'guardrail_result_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when guardrail validation completed.",
    )
    decision: GuardrailDecision = Field(
        description="Outcome of guardrail validation: approved, rejected, or clipped.",
    )
    reason_codes: list[GuardrailReasonCode] = Field(
        default_factory=list,
        description="Machine-readable reason codes explaining rejection or clipping.",
    )
    clipped_fields: list[str] | None = Field(
        default=None,
        description="Field names clipped by guardrails when decision is clipped.",
    )
    notes: str | None = Field(
        default=None,
        description="Optional operator-facing context for logs or debugging.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, v: datetime) -> datetime:
        """Ensure timestamp has timezone info (must be aware)."""
        if v.tzinfo is None:
            raise ValueError(
                "timestamp must include timezone info. Use datetime.now(timezone.utc)"
            )
        return v

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        """Ensure schema_version is exactly 'guardrail_result_v1'."""
        if v != "guardrail_result_v1":
            raise ValueError(
                f"schema_version must be 'guardrail_result_v1', got '{v}'"
            )
        return v

    @model_validator(mode="after")
    def validate_reason_codes_for_decision(self) -> "GuardrailResultV1":
        """Rejected/clipped outcomes must include at least one reason code."""
        if self.decision in {
            GuardrailDecision.REJECTED,
            GuardrailDecision.CLIPPED,
        } and not self.reason_codes:
            raise ValueError(
                "reason_codes must be provided when decision is rejected or clipped"
            )
        return self
