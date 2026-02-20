"""SamplingPlanV1: weather-adapted sampling cadence plan for Stage 3."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SamplingOverrideV1(BaseModel):
    """Time-window override for sampling frequency."""

    model_config = ConfigDict(strict=True)

    start_ts: datetime
    end_ts: datetime
    sampling_minutes: int = Field(ge=1, le=180)
    scenario: str
    reason: str

    @field_validator("start_ts", "end_ts")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamps must include timezone info")
        return value

    @model_validator(mode="after")
    def validate_range(self) -> "SamplingOverrideV1":
        if self.end_ts <= self.start_ts:
            raise ValueError("end_ts must be after start_ts")
        return self


class SamplingPlanV1(BaseModel):
    """Sampling plan emitted by weather adapter for scheduler consumption."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["sampling_plan_v1"]
    generated_at: datetime
    base_sampling_minutes: int = Field(ge=1, le=240)
    active_scenarios: list[str] = Field(default_factory=list)
    overrides: list[SamplingOverrideV1] = Field(default_factory=list)

    @field_validator("generated_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("generated_at must include timezone info")
        return value
