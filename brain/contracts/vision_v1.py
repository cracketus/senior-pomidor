"""VisionV1: structured baseline output from vision analyzer."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VisionV1(BaseModel):
    """Structured vision assessment for one image/cycle."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["vision_v1"]
    timestamp: datetime = Field(
        description="ISO8601 timestamp for vision assessment.",
    )
    image_ref: str = Field(
        min_length=1,
        description="Image identifier or path reference.",
    )
    source: str = Field(
        min_length=1,
        description="Analyzer source name.",
    )
    plant_status: Literal["healthy", "watch", "stress", "unknown"]
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Assessment confidence in [0,1].",
    )
    findings: list[str] = Field(
        default_factory=list,
        description="Detected visual findings.",
    )
    stress_signals: list[str] = Field(
        default_factory=list,
        description="Subset of findings interpreted as stress signals.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone info")
        return value
