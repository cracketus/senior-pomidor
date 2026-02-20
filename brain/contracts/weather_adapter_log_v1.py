"""WeatherAdapterLogV1: explainable log for weather adapter decisions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .targets_v1 import TargetEnvelopeV1


class WeatherAdapterLogV1(BaseModel):
    """Traceable log entry for one weather-adapter evaluation cycle."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["weather_adapter_log_v1"]
    timestamp: datetime
    forecast_ref: str = Field(min_length=1)
    state_ref: str = Field(min_length=1)
    matched_scenarios: list[str] = Field(default_factory=list)
    applied_changes: list[str] = Field(default_factory=list)
    guardrail_clips: list[str] = Field(default_factory=list)
    final_targets: TargetEnvelopeV1

    @field_validator("timestamp")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must include timezone info")
        return value
