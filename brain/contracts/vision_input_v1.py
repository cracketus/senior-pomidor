"""VisionInputV1: deterministic vision analyzer input envelope."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VisionInputV1(BaseModel):
    """Vision analyzer input metadata for one evaluation cycle."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["vision_input_v1"]
    timestamp: datetime = Field(
        description="ISO8601 timestamp for this vision input message.",
    )
    image_ref: str = Field(
        min_length=1,
        description="Image identifier or path reference.",
    )
    state_ref: str = Field(
        min_length=1,
        description="Reference to associated StateV1 record.",
    )
    telemetry_summary: str = Field(
        min_length=1,
        description="Short deterministic telemetry summary for context.",
    )
    camera_id: str | None = Field(
        default=None,
        description="Optional camera identifier.",
    )

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_has_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone info")
        return value
