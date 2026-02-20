"""VisionExplanationV1: human-readable explanation for vision output."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VisionExplanationV1(BaseModel):
    """Explanation payload paired with one VisionV1 result."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["vision_explanation_v1"]
    timestamp: datetime = Field(
        description="ISO8601 timestamp of explanation generation.",
    )
    image_ref: str = Field(
        min_length=1,
        description="Image identifier or path reference.",
    )
    vision_ref: str = Field(
        min_length=1,
        description="Reference key linking back to the VisionV1 record.",
    )
    summary: str = Field(
        min_length=1,
        description="Short operator-facing explanation.",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Concrete evidence statements supporting the summary.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Known limitations for this inference cycle.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone info")
        return value
