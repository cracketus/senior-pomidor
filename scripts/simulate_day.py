"""Run a 24h simulated day using synthetic observations."""

from __future__ import annotations

import argparse
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from brain.clock import SimClock
from brain.control import BaselineWaterController
from brain.estimator import EstimatorPipeline
from brain.executor import MockExecutor
from brain.guardrails import GuardrailsValidator
from brain.sources import SyntheticConfig, SyntheticSource
from brain.storage.dataset import DatasetManager
from brain.storage.jsonl_writer import JSONLWriter
from brain.vision import BaselineVisionAnalyzer
from brain.world_model import (
    WeatherAdapter,
    WeatherClient,
    map_state_v1_to_weather_adapter_input,
)
from brain.contracts import VisionInputV1

DEFAULT_STEP_SECONDS = 2 * 60 * 60
EVENT_STEP_SECONDS = 15 * 60
EVENT_WINDOW_SECONDS = 2 * 60 * 60
SEEDED_START_TIME = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
FORECAST_HORIZON_HOURS = 36


def _clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


def _scenario_hooks(name: str | None) -> list[Callable]:
    if not name or name == "none":
        return []

    def heatwave(obs, device, _rng, _index):
        # Keep this strong enough to reliably trigger high-severity anomalies in tests.
        temp = obs.air_temperature + 16.0
        rh = _clamp(obs.air_humidity - 35.0, 0.0, 100.0)
        return obs.model_copy(update={"air_temperature": temp, "air_humidity": rh}), device

    def dry_inflow(obs, device, _rng, _index):
        temp = obs.air_temperature + 3.0
        rh = _clamp(obs.air_humidity - 15.0, 0.0, 100.0)
        return obs.model_copy(update={"air_temperature": temp, "air_humidity": rh}), device

    def wind_spike(obs, device, _rng, _index):
        rh = _clamp(obs.air_humidity - 5.0, 0.0, 100.0)
        return obs.model_copy(update={"air_humidity": rh}), device

    def cold_spell(obs, device, _rng, _index):
        temp = obs.air_temperature - 6.0
        rh = _clamp(obs.air_humidity + 10.0, 0.0, 100.0)
        return obs.model_copy(update={"air_temperature": temp, "air_humidity": rh}), device

    hooks = {
        "heatwave": heatwave,
        "dry_inflow": dry_inflow,
        "wind_spike": wind_spike,
        "cold_spell": cold_spell,
    }

    if name not in hooks:
        raise ValueError(f"Unsupported scenario '{name}'")
    return [hooks[name]]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a simulated day with synthetic observations.",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output-dir", type=str, default="data/runs")
    parser.add_argument("--duration-hours", type=float, default=24.0)
    parser.add_argument("--time-scale", type=float, default=120.0)
    parser.add_argument(
        "--scenario",
        type=str,
        default="none",
        choices=["none", "heatwave", "dry_inflow", "wind_spike", "cold_spell"],
    )
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def _is_high_severity(anomaly) -> bool:
    severity = (
        anomaly.severity.value
        if hasattr(anomaly.severity, "value")
        else str(anomaly.severity)
    ).lower()
    return severity in {"high", "critical"}


def _build_stub_forecast_payload(
    *,
    now: datetime,
    air_temp_c: float,
    rh_pct: float,
    scenario: str,
) -> list[dict[str, float | str]]:
    points: list[dict[str, float | str]] = []
    scenario_temp_shift = {
        "none": 0.0,
        "heatwave": 6.0,
        "dry_inflow": 3.0,
        "wind_spike": 1.0,
        "cold_spell": -8.0,
    }.get(scenario, 0.0)
    scenario_rh_shift = {
        "none": 0.0,
        "heatwave": -12.0,
        "dry_inflow": -20.0,
        "wind_spike": -6.0,
        "cold_spell": 10.0,
    }.get(scenario, 0.0)
    scenario_wind_shift = {
        "none": 0.0,
        "heatwave": 0.5,
        "dry_inflow": 1.2,
        "wind_spike": 6.0,
        "cold_spell": 1.0,
    }.get(scenario, 0.0)

    for hour in range(FORECAST_HORIZON_HOURS):
        ts = now + timedelta(hours=hour)
        phase = (ts.hour / 24.0) * 2.0 * math.pi
        temp = air_temp_c + 2.5 * math.sin(phase) + scenario_temp_shift
        rh = rh_pct - 8.0 * math.sin(phase) + scenario_rh_shift
        wind = 2.0 + 0.8 * math.cos(phase) + scenario_wind_shift
        cloud = 45.0 - 20.0 * math.sin(phase)
        solar = max(0.0, 700.0 * max(0.0, math.sin(phase)))
        points.append(
            {
                "timestamp": ts.isoformat(),
                "ext_temp_c": round(_clamp(temp, -30.0, 55.0), 3),
                "ext_rh_pct": round(_clamp(rh, 0.0, 100.0), 3),
                "ext_wind_mps": round(_clamp(wind, 0.0, 35.0), 3),
                "ext_cloud_cover_pct": round(_clamp(cloud, 0.0, 100.0), 3),
                "ext_solar_wm2": round(_clamp(solar, 0.0, 1200.0), 3),
            }
        )
    return points


def run_simulation(args: argparse.Namespace) -> Path:
    if args.duration_hours <= 0:
        raise ValueError("duration-hours must be positive")
    if args.time_scale <= 0:
        raise ValueError("time-scale must be positive")

    total_duration_seconds = int(args.duration_hours * 3600)
    if total_duration_seconds < DEFAULT_STEP_SECONDS:
        raise ValueError("duration-hours must be at least 2.0")

    start_time = SEEDED_START_TIME if args.seed is not None else datetime.now(timezone.utc)

    config = SyntheticConfig(
        seed=args.seed,
        start_time=start_time,
        step_seconds=DEFAULT_STEP_SECONDS,
        count=None,
        scenarios=_scenario_hooks(args.scenario),
    )
    source = SyntheticSource(config)
    pipeline = EstimatorPipeline()

    dataset = DatasetManager(args.output_dir)
    run_dir = dataset.create_run_dir(run_date=start_time.date())

    state_path = run_dir / "state.jsonl"
    anomalies_path = run_dir / "anomalies.jsonl"
    health_path = run_dir / "sensor_health.jsonl"
    observations_path = run_dir / "observations.jsonl"
    cadence_path = run_dir / "cadence.jsonl"
    actions_path = run_dir / "actions.jsonl"
    guardrail_results_path = run_dir / "guardrail_results.jsonl"
    executor_log_path = run_dir / "executor_log.jsonl"
    forecast_path = run_dir / "forecast_36h.jsonl"
    targets_path = run_dir / "targets.jsonl"
    sampling_plan_path = run_dir / "sampling_plan.jsonl"
    weather_adapter_log_path = run_dir / "weather_adapter_log.jsonl"
    vision_path = run_dir / "vision.jsonl"
    vision_explanations_path = run_dir / "vision_explanations.jsonl"

    _touch(anomalies_path)
    _touch(health_path)
    _touch(cadence_path)
    _touch(actions_path)
    _touch(guardrail_results_path)
    _touch(executor_log_path)
    _touch(forecast_path)
    _touch(targets_path)
    _touch(sampling_plan_path)
    _touch(weather_adapter_log_path)
    _touch(vision_path)
    _touch(vision_explanations_path)

    state_writer = JSONLWriter(str(state_path))
    anomaly_writer = JSONLWriter(str(anomalies_path))
    health_writer = JSONLWriter(str(health_path))
    observations_writer = JSONLWriter(str(observations_path))
    cadence_writer = JSONLWriter(str(cadence_path))
    actions_writer = JSONLWriter(str(actions_path))
    guardrail_results_writer = JSONLWriter(str(guardrail_results_path))
    executor_log_writer = JSONLWriter(str(executor_log_path))
    forecast_writer = JSONLWriter(str(forecast_path))
    targets_writer = JSONLWriter(str(targets_path))
    sampling_plan_writer = JSONLWriter(str(sampling_plan_path))
    weather_adapter_log_writer = JSONLWriter(str(weather_adapter_log_path))
    vision_writer = JSONLWriter(str(vision_path))
    vision_explanations_writer = JSONLWriter(str(vision_explanations_path))

    clock = SimClock(time_scale=1.0, start_time=start_time)
    controller = BaselineWaterController()
    guardrails = GuardrailsValidator()
    executor = MockExecutor()
    weather_client = WeatherClient()
    weather_adapter = WeatherAdapter()
    vision_analyzer = BaselineVisionAnalyzer()

    elapsed = 0
    event_mode_until: int | None = None
    cycle_no = 0

    # Main loop: obs -> estimate -> store -> optional event mode -> advance
    while elapsed < total_duration_seconds:
        now = clock.now()
        in_event_mode = event_mode_until is not None and elapsed <= event_mode_until
        interval_seconds = EVENT_STEP_SECONDS if in_event_mode else DEFAULT_STEP_SECONDS
        mode = "event" if in_event_mode else "baseline"

        item = source.next_observation()
        if item is None:
            break
        raw_observation, raw_device_status = item

        # Tie output timestamps to logical clock so cadence changes are observable in output.
        observation = raw_observation.model_copy(update={"timestamp": now})
        device_status = raw_device_status.model_copy(update={"timestamp": now})

        observations_writer.append(
            {
                "observation": observation.model_dump(mode="json"),
                "device_status": device_status.model_dump(mode="json"),
            }
        )

        state, anomalies, sensor_health = pipeline.process(
            observation, device_status
        )
        state_writer.append(state.model_dump(mode="json"))
        for anomaly in anomalies:
            anomaly_writer.append(anomaly.model_dump(mode="json"))
        for health in sensor_health:
            health_writer.append(health.model_dump(mode="json"))

        raw_forecast = _build_stub_forecast_payload(
            now=now,
            air_temp_c=observation.air_temperature,
            rh_pct=observation.air_humidity,
            scenario=args.scenario,
        )
        forecast = weather_client.normalize(
            raw_forecast,
            source="simulate_day_stub",
            timezone_name="UTC",
            freq_minutes=60,
            horizon_hours=FORECAST_HORIZON_HOURS,
            generated_at=now,
        )
        weather_state = map_state_v1_to_weather_adapter_input(state)
        weather_result = weather_adapter.apply(
            forecast=forecast,
            state=weather_state,
            now=now,
            forecast_ref="forecast_36h_v1:simulate_day_stub",
            state_ref="state_v1",
        )
        forecast_writer.append(forecast.model_dump(mode="json"))
        targets_writer.append(weather_result.targets.model_dump(mode="json"))
        sampling_plan_writer.append(weather_result.sampling_plan.model_dump(mode="json"))
        weather_adapter_log_writer.append(weather_result.log.model_dump(mode="json"))

        vision_input = VisionInputV1(
            schema_version="vision_input_v1",
            timestamp=now,
            image_ref=f"sim://{run_dir.name}/cycle_{cycle_no:04d}.jpg",
            state_ref=f"state_v1:{run_dir.name}:cycle_{cycle_no}",
            telemetry_summary=(
                f"vpd={state.vpd:.3f} "
                f"soil_avg_pct={state.soil_moisture_avg * 100.0:.2f} "
                f"conf={state.confidence:.3f}"
            ),
            camera_id="sim_cam_front",
        )
        vision, vision_explanation = vision_analyzer.analyze(vision_input)
        vision_writer.append(vision.model_dump(mode="json"))
        vision_explanations_writer.append(vision_explanation.model_dump(mode="json"))

        # Stage 2 scope: propose only WATER actions; other action types are deferred.
        proposed_action = controller.propose_action(state, now=now)
        if proposed_action is not None:
            effective_action, guardrail_result = guardrails.validate(
                proposed_action,
                state=state,
                device_status=device_status,
                anomalies=anomalies,
                now=now,
            )
            guardrail_results_writer.append(guardrail_result.model_dump(mode="json"))
            executor_event = executor.execute(
                proposed_action=proposed_action,
                effective_action=effective_action,
                guardrail_result=guardrail_result,
                now=now,
            )
            executor_log_writer.append(executor_event.model_dump(mode="json"))
            if effective_action is not None:
                actions_writer.append(effective_action.model_dump(mode="json"))

        if any(_is_high_severity(anomaly) for anomaly in anomalies):
            candidate_until = elapsed + EVENT_WINDOW_SECONDS
            event_mode_until = (
                candidate_until
                if event_mode_until is None
                else max(event_mode_until, candidate_until)
            )

        cadence_writer.append(
            {
                "timestamp": now.isoformat(),
                "cycle": cycle_no,
                "mode": mode,
                "interval_seconds": interval_seconds,
                "event_mode_active_until_seconds": event_mode_until,
            }
        )

        if args.verbose:
            print(
                f"{observation.timestamp.isoformat()} | "
                f"mode={mode} interval={interval_seconds}s "
                f"confidence={state.confidence:.2f} "
                f"anomalies={len(anomalies)}"
            )

        wall_sleep = interval_seconds / args.time_scale
        if wall_sleep > 0:
            time.sleep(wall_sleep)

        clock.sleep_for_logical(interval_seconds)
        elapsed += interval_seconds
        cycle_no += 1

    return run_dir


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        run_dir = run_simulation(args)
    except Exception as exc:  # noqa: BLE001
        print(f"simulate_day failed: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"Run output: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
