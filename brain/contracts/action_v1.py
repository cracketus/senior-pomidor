"""ActionV1: Control decisions made by the Control Layer Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ActionType(str, Enum):
    """Valid control action types."""

    WATER = "water"
    LIGHT = "light"
    FAN = "fan"
    CO2 = "co2"
    CIRCULATE = "circulate"


class ActionV1(BaseModel):
    """
    Control decision from Control Layer Agent.

    Represents a single action recommendation with justification and metrics.
    All actions are validated by Guardrails before execution.

    Example:
        ```python
        action = ActionV1(
            schema_version="action_v1",
            timestamp=datetime.now(timezone.utc),
            action_type=ActionType.WATER,
            duration_seconds=10,
            intensity=0.8,
            reason="Soil moisture p1 below target (0.45 < 0.55)",
            estimated_impact=0.15,
            budget_remaining_ml=80.0,
        )
        ```
    """

    model_config = ConfigDict(
        use_enum_values=True,
        strict=True,
    )

    # Contract metadata
    schema_version: str = Field(
        description="Schema version identifier. Must be 'action_v1'.",
    )
    timestamp: datetime = Field(
        description="ISO8601 timestamp (UTC) when action was decided."
    )

    # Action definition
    action_type: ActionType = Field(
        description="Type of control action (water, light, fan, co2, circulate)."
    )
    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Duration for this action in seconds. None if instantaneous.",
    )
    intensity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relative intensity (0.0=off, 1.0=max). None if not applicable.",
    )

    # Justification and metrics
    reason: str = Field(
        description="Human-readable explanation for this action decision."
    )
    estimated_impact: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Estimated improvement to objective (0.0=none, 1.0=max). "
        "Used for prioritization.",
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in this action (0.0=unreliable, 1.0=fully trusted).",
    )

    # Resource tracking
    budget_remaining_ml: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Remaining water budget in ml after this action. None if not tracked.",
    )
    budget_remaining_co2_seconds: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Remaining CO2 injection budget in seconds. None if not tracked.",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes or warnings about this action.",
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
        """Ensure schema_version is exactly 'action_v1'."""
        if v != "action_v1":
            raise ValueError(
                f"schema_version must be 'action_v1', got '{v}'"
            )
        return v
