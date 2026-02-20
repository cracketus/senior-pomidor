"""TargetsV1: weather-adapted target envelope for Stage 3."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TargetEnvelopeV1(BaseModel):
    """Environmental and soil target bounds."""

    model_config = ConfigDict(strict=True)

    vpd_min_kpa: float = Field(ge=0.0)
    vpd_max_kpa: float = Field(ge=0.0)
    soil_moisture_min_pct: float = Field(ge=0.0, le=100.0)
    soil_moisture_max_pct: float = Field(ge=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_bounds(self) -> "TargetEnvelopeV1":
        if self.vpd_min_kpa > self.vpd_max_kpa:
            raise ValueError("vpd_min_kpa must be <= vpd_max_kpa")
        if self.soil_moisture_min_pct > self.soil_moisture_max_pct:
            raise ValueError("soil_moisture_min_pct must be <= soil_moisture_max_pct")
        return self


class BudgetAdaptationV1(BaseModel):
    """Budget multipliers after weather adaptation."""

    model_config = ConfigDict(strict=True)

    water_budget_multiplier: float = Field(ge=0.5, le=2.0)
    co2_budget_multiplier: float = Field(ge=0.5, le=2.0)


class TargetsV1(BaseModel):
    """World-model output: base and adapted targets with active scenarios."""

    model_config = ConfigDict(strict=True)

    schema_version: Literal["targets_v1"]
    generated_at: datetime
    valid_until_ts: datetime
    base_targets: TargetEnvelopeV1
    adapted_targets: TargetEnvelopeV1
    adapted_budgets: BudgetAdaptationV1
    active_scenarios: list[str] = Field(default_factory=list)

    @field_validator("generated_at", "valid_until_ts")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamps must include timezone info")
        return value

    @model_validator(mode="after")
    def validate_window(self) -> "TargetsV1":
        if self.valid_until_ts <= self.generated_at:
            raise ValueError("valid_until_ts must be after generated_at")
        return self
