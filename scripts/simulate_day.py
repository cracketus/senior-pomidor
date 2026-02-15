"""Run a 24h simulated day using synthetic observations."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from brain.clock import SimClock
from brain.estimator import EstimatorPipeline
from brain.scheduler import Scheduler
from brain.sources import SyntheticConfig, SyntheticSource
from brain.storage.dataset import DatasetManager
from brain.storage.jsonl_writer import JSONLWriter

DEFAULT_STEP_SECONDS = 2 * 60 * 60
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
        temp = obs.air_temperature + 6.0
        rh = _clamp(obs.air_humidity - 10.0, 0.0, 100.0)
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


def run_simulation(args: argparse.Namespace) -> Path:
    if args.duration_hours <= 0:
        raise ValueError("duration-hours must be positive")
    if args.time_scale <= 0:
        raise ValueError("time-scale must be positive")

    steps = int((args.duration_hours * 3600) // DEFAULT_STEP_SECONDS)
    if steps < 1:
        raise ValueError("duration-hours must be at least 2.0")

    start_time = SEEDED_START_TIME if args.seed is not None else datetime.now(timezone.utc)

    config = SyntheticConfig(
        seed=args.seed,
        start_time=start_time,
        step_seconds=DEFAULT_STEP_SECONDS,
        count=steps,
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

    _touch(anomalies_path)
    _touch(health_path)

    state_writer = JSONLWriter(str(state_path))
    anomaly_writer = JSONLWriter(str(anomalies_path))
    health_writer = JSONLWriter(str(health_path))
    observations_writer = JSONLWriter(str(observations_path))

    clock = SimClock(time_scale=1.0, start_time=start_time)
    scheduler = Scheduler(clock)

    # Main loop (every 2 hours): obs -> estimate -> store -> advance
    def cycle(_now):
        item = source.next_observation()
        if item is None:
            scheduler.shutdown()
            return
        observation, device_status = item

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

        if args.verbose:
            print(
                f"{observation.timestamp.isoformat()} | "
                f"confidence={state.confidence:.2f} "
                f"anomalies={len(anomalies)}"
            )

        wall_sleep = DEFAULT_STEP_SECONDS / args.time_scale
        if wall_sleep > 0:
            time.sleep(wall_sleep)

    scheduler.schedule_every(DEFAULT_STEP_SECONDS, cycle, name="decision_cycle")
    scheduler.run(duration_seconds=steps * DEFAULT_STEP_SECONDS)

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
