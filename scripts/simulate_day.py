"""Run a 24h simulated day using synthetic observations."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from brain.clock import SimClock
from brain.control import BaselineWaterController
from brain.estimator import EstimatorPipeline
from brain.sources import SyntheticConfig, SyntheticSource
from brain.storage.dataset import DatasetManager
from brain.storage.jsonl_writer import JSONLWriter

DEFAULT_STEP_SECONDS = 2 * 60 * 60
EVENT_STEP_SECONDS = 15 * 60
EVENT_WINDOW_SECONDS = 2 * 60 * 60
SEEDED_START_TIME = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)


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

    _touch(anomalies_path)
    _touch(health_path)
    _touch(cadence_path)
    _touch(actions_path)

    state_writer = JSONLWriter(str(state_path))
    anomaly_writer = JSONLWriter(str(anomalies_path))
    health_writer = JSONLWriter(str(health_path))
    observations_writer = JSONLWriter(str(observations_path))
    cadence_writer = JSONLWriter(str(cadence_path))
    actions_writer = JSONLWriter(str(actions_path))

    clock = SimClock(time_scale=1.0, start_time=start_time)
    controller = BaselineWaterController()

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

        # Stage 2 scope: propose only WATER actions; other action types are deferred.
        action = controller.propose_action(state, now=now)
        if action is not None:
            actions_writer.append(action.model_dump(mode="json"))

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
