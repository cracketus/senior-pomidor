"""ExecutorEventV1: execution-path observability for Stage 2 mock executor."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ExecutorStatus(str, Enum):
    """Execution outcome for a proposed action."""

    EXECUTED = "executed"
    SKIPPED = "skipped"


class ExecutorEventV1(BaseModel):
    """Event emitted by executor for each proposed action."""

    model_config = ConfigDict(
        use_enum_values=True,
        strict=True,
    )

    schema_version: str = Field(
        description="Schema version identifier. Must be 'executor_event_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when executor processed the action.",
    )
    status: ExecutorStatus = Field(
        description="Execution status: executed or skipped.",
    )
    action_type: str = Field(
        description="Action type from proposal (e.g., water).",
    )
    guardrail_decision: str = Field(
        description="Guardrail decision value (approved/rejected/clipped).",
    )
    reason_codes: list[str] = Field(
        default_factory=list,
        description="Guardrail reason codes propagated for observability.",
    )
    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Effective duration executed, if applicable.",
    )
    notes: str | None = Field(
        default=None,
        description="Optional operator-facing executor note.",
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
        """Ensure schema_version is exactly 'executor_event_v1'."""
        if v != "executor_event_v1":
            raise ValueError(
                f"schema_version must be 'executor_event_v1', got '{v}'"
            )
        return v
