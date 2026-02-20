"""Baseline deterministic weather adapter for Stage 3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from brain.contracts import Forecast36hV1
from brain.contracts.sampling_plan_v1 import SamplingOverrideV1
from brain.contracts.targets_v1 import BudgetAdaptationV1, TargetEnvelopeV1, TargetsV1
from brain.contracts.weather_adapter_log_v1 import WeatherAdapterLogV1
from brain.contracts import SamplingPlanV1
from brain.world_model.state_v1_weather_adapter_mapper import WeatherAdapterStateInputV1

SCENARIO_HEATWAVE = "heatwave"
SCENARIO_DRY_INFLOW = "dry_inflow"
SCENARIO_WIND_SPIKE = "wind_spike"
SCENARIO_COLD_SPELL = "cold_spell"


@dataclass(frozen=True)
class WeatherAdapterConfig:
    """Baseline adapter configuration with deterministic thresholds."""

    base_sampling_minutes: int = 120
    heatwave_temp_c: float = 32.0
    dry_inflow_rh_pct: float = 35.0
    wind_spike_mps: float = 10.0
    cold_spell_temp_c: float = 8.0


@dataclass(frozen=True)
class WeatherAdapterResult:
    """Grouped weather-adapter outputs."""

    targets: TargetsV1
    sampling_plan: SamplingPlanV1
    log: WeatherAdapterLogV1


class WeatherAdapter:
    """Apply forecast-driven scenario adjustments to targets and cadence."""

    def __init__(self, config: WeatherAdapterConfig | None = None) -> None:
        self._config = config or WeatherAdapterConfig()

    def apply(
        self,
        forecast: Forecast36hV1,
        state: WeatherAdapterStateInputV1,
        *,
        now: datetime | None = None,
        forecast_ref: str = "forecast_36h_v1",
        state_ref: str = "state_v1",
    ) -> WeatherAdapterResult:
        ts = now or forecast.generated_at
        scenarios = self._detect_scenarios(forecast)

        base_targets = TargetEnvelopeV1(
            vpd_min_kpa=0.8,
            vpd_max_kpa=1.5,
            soil_moisture_min_pct=35.0,
            soil_moisture_max_pct=75.0,
        )
        adapted_targets, target_changes = self._adapt_targets(base_targets, scenarios)
        adapted_budgets, budget_changes = self._adapt_budgets(scenarios)
        sampling_plan, sampling_changes = self._build_sampling_plan(forecast, ts, scenarios)

        targets = TargetsV1(
            schema_version="targets_v1",
            generated_at=ts,
            valid_until_ts=ts + timedelta(hours=forecast.horizon_hours),
            base_targets=base_targets,
            adapted_targets=adapted_targets,
            adapted_budgets=adapted_budgets,
            active_scenarios=scenarios,
        )

        log = WeatherAdapterLogV1(
            schema_version="weather_adapter_log_v1",
            timestamp=ts,
            forecast_ref=forecast_ref,
            state_ref=state_ref,
            matched_scenarios=scenarios,
            applied_changes=target_changes + budget_changes + sampling_changes,
            guardrail_clips=[],
            final_targets=adapted_targets,
        )

        return WeatherAdapterResult(targets=targets, sampling_plan=sampling_plan, log=log)

    def _detect_scenarios(self, forecast: Forecast36hV1) -> list[str]:
        scenarios: list[str] = []
        if any(point.ext_temp_c >= self._config.heatwave_temp_c for point in forecast.points):
            scenarios.append(SCENARIO_HEATWAVE)
        if any(point.ext_rh_pct <= self._config.dry_inflow_rh_pct for point in forecast.points):
            scenarios.append(SCENARIO_DRY_INFLOW)
        if any(point.ext_wind_mps >= self._config.wind_spike_mps for point in forecast.points):
            scenarios.append(SCENARIO_WIND_SPIKE)
        if any(point.ext_temp_c <= self._config.cold_spell_temp_c for point in forecast.points):
            scenarios.append(SCENARIO_COLD_SPELL)
        return scenarios

    def _adapt_targets(
        self,
        base: TargetEnvelopeV1,
        scenarios: list[str],
    ) -> tuple[TargetEnvelopeV1, list[str]]:
        changes: list[str] = []
        vpd_min = base.vpd_min_kpa
        vpd_max = base.vpd_max_kpa
        soil_min = base.soil_moisture_min_pct
        soil_max = base.soil_moisture_max_pct

        if SCENARIO_HEATWAVE in scenarios:
            vpd_max -= 0.2
            soil_min += 5.0
            changes.append("heatwave:lower_vpd_max_raise_soil_min")
        if SCENARIO_DRY_INFLOW in scenarios:
            vpd_max -= 0.1
            soil_min += 3.0
            changes.append("dry_inflow:lower_vpd_max_raise_soil_min")
        if SCENARIO_WIND_SPIKE in scenarios:
            vpd_max -= 0.15
            changes.append("wind_spike:lower_vpd_max")
        if SCENARIO_COLD_SPELL in scenarios:
            vpd_min -= 0.2
            vpd_max -= 0.2
            changes.append("cold_spell:shift_vpd_window_lower")

        # Deterministic clipping to safe bounds.
        vpd_min = max(0.2, min(vpd_min, 2.5))
        vpd_max = max(vpd_min + 0.1, min(vpd_max, 3.5))
        soil_min = max(15.0, min(soil_min, 80.0))
        soil_max = max(soil_min + 5.0, min(soil_max, 95.0))

        return (
            TargetEnvelopeV1(
                vpd_min_kpa=round(vpd_min, 3),
                vpd_max_kpa=round(vpd_max, 3),
                soil_moisture_min_pct=round(soil_min, 3),
                soil_moisture_max_pct=round(soil_max, 3),
            ),
            changes,
        )

    def _adapt_budgets(self, scenarios: list[str]) -> tuple[BudgetAdaptationV1, list[str]]:
        water_multiplier = 1.0
        co2_multiplier = 1.0
        changes: list[str] = []

        if SCENARIO_HEATWAVE in scenarios:
            water_multiplier += 0.3
            changes.append("heatwave:raise_water_budget")
        if SCENARIO_DRY_INFLOW in scenarios:
            water_multiplier += 0.2
            changes.append("dry_inflow:raise_water_budget")
        if SCENARIO_COLD_SPELL in scenarios:
            co2_multiplier -= 0.1
            changes.append("cold_spell:lower_co2_budget")

        water_multiplier = max(0.5, min(water_multiplier, 2.0))
        co2_multiplier = max(0.5, min(co2_multiplier, 2.0))

        return (
            BudgetAdaptationV1(
                water_budget_multiplier=round(water_multiplier, 3),
                co2_budget_multiplier=round(co2_multiplier, 3),
            ),
            changes,
        )

    def _build_sampling_plan(
        self,
        forecast: Forecast36hV1,
        now: datetime,
        scenarios: list[str],
    ) -> tuple[SamplingPlanV1, list[str]]:
        overrides: list[SamplingOverrideV1] = []
        changes: list[str] = []

        scenario_to_minutes = {
            SCENARIO_HEATWAVE: 15,
            SCENARIO_DRY_INFLOW: 30,
            SCENARIO_WIND_SPIKE: 15,
            SCENARIO_COLD_SPELL: 45,
        }

        for scenario in scenarios:
            minutes = scenario_to_minutes[scenario]
            first_match = next(
                (
                    point.timestamp
                    for point in forecast.points
                    if self._scenario_matches_point(scenario, point.ext_temp_c, point.ext_rh_pct, point.ext_wind_mps)
                ),
                None,
            )
            if first_match is None:
                continue
            overrides.append(
                SamplingOverrideV1(
                    start_ts=first_match,
                    end_ts=first_match + timedelta(hours=2),
                    sampling_minutes=minutes,
                    scenario=scenario,
                    reason=f"{scenario}:risk_window",
                )
            )
            changes.append(f"{scenario}:sampling_override_{minutes}m")

        overrides.sort(key=lambda item: (item.start_ts, item.scenario))
        return (
            SamplingPlanV1(
                schema_version="sampling_plan_v1",
                generated_at=now,
                base_sampling_minutes=self._config.base_sampling_minutes,
                active_scenarios=scenarios,
                overrides=overrides,
            ),
            changes,
        )

    def _scenario_matches_point(
        self,
        scenario: str,
        temp_c: float,
        rh_pct: float,
        wind_mps: float,
    ) -> bool:
        if scenario == SCENARIO_HEATWAVE:
            return temp_c >= self._config.heatwave_temp_c
        if scenario == SCENARIO_DRY_INFLOW:
            return rh_pct <= self._config.dry_inflow_rh_pct
        if scenario == SCENARIO_WIND_SPIKE:
            return wind_mps >= self._config.wind_spike_mps
        if scenario == SCENARIO_COLD_SPELL:
            return temp_c <= self._config.cold_spell_temp_c
        return False
