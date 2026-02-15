"""Generate canonical Stage 1 playground demo fixtures for investor demos.

This script creates two deterministic 24h runs:
- baseline_seed42_24h (scenario=none)
- heatwave_seed42_24h (scenario=heatwave)

Artifacts are written under tests/fixtures/playground_demo_runs by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from simulate_day import run_simulation

ARTIFACT_FILES = [
    "state.jsonl",
    "anomalies.jsonl",
    "sensor_health.jsonl",
    "observations.jsonl",
    "cadence.jsonl",
]


@dataclass(frozen=True)
class DemoFixture:
    name: str
    scenario: str


DEMO_FIXTURES = [
    DemoFixture(name="baseline_seed42_24h", scenario="none"),
    DemoFixture(name="heatwave_seed42_24h", scenario="heatwave"),
]


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def _count_jsonl_records(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _collect_metrics(run_dir: Path) -> dict[str, Any]:
    cadence_records = _load_jsonl(run_dir / "cadence.jsonl")
    anomaly_records = _load_jsonl(run_dir / "anomalies.jsonl")

    anomalies_by_severity: dict[str, int] = {}
    anomalies_by_type: dict[str, int] = {}
    for record in anomaly_records:
        severity = str(record.get("severity", "unknown"))
        anomaly_type = str(record.get("anomaly_type", "unknown"))
        anomalies_by_severity[severity] = anomalies_by_severity.get(severity, 0) + 1
        anomalies_by_type[anomaly_type] = anomalies_by_type.get(anomaly_type, 0) + 1

    cadence_by_mode: dict[str, int] = {}
    interval_counts: dict[str, int] = {}
    for record in cadence_records:
        mode = str(record.get("mode", "unknown"))
        interval = str(record.get("interval_seconds", "unknown"))
        cadence_by_mode[mode] = cadence_by_mode.get(mode, 0) + 1
        interval_counts[interval] = interval_counts.get(interval, 0) + 1

    return {
        "state_records": _count_jsonl_records(run_dir / "state.jsonl"),
        "anomaly_records": len(anomaly_records),
        "sensor_health_records": _count_jsonl_records(run_dir / "sensor_health.jsonl"),
        "observation_records": _count_jsonl_records(run_dir / "observations.jsonl"),
        "cadence_records": len(cadence_records),
        "cadence_by_mode": cadence_by_mode,
        "interval_counts": interval_counts,
        "anomalies_by_severity": anomalies_by_severity,
        "anomalies_by_type": anomalies_by_type,
    }


def _copy_artifacts(run_dir: Path, fixture_dir: Path) -> None:
    fixture_dir.mkdir(parents=True, exist_ok=True)
    for name in ARTIFACT_FILES:
        source = run_dir / name
        target = fixture_dir / name
        if not source.exists():
            raise FileNotFoundError(f"Missing artifact: {source}")
        shutil.copy2(source, target)


def _write_manifest(
    fixture_dir: Path,
    seed: int,
    duration_hours: float,
    time_scale: float,
    scenario: str,
) -> None:
    hashes = {name: _sha256_file(fixture_dir / name) for name in ARTIFACT_FILES}
    metrics = _collect_metrics(fixture_dir)
    manifest = {
        "schema_version": "playground_demo_manifest_v1",
        "fixture_name": fixture_dir.name,
        "seed": seed,
        "duration_hours": duration_hours,
        "time_scale": time_scale,
        "scenario": scenario,
        "artifacts": ARTIFACT_FILES,
        "file_hashes_sha256": hashes,
        "metrics": metrics,
    }
    (fixture_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _run_single_fixture(
    output_root: Path,
    fixture: DemoFixture,
    seed: int,
    duration_hours: float,
    time_scale: float,
) -> Path:
    temp_out = output_root / "_tmp" / fixture.name
    if temp_out.exists():
        shutil.rmtree(temp_out)
    temp_out.mkdir(parents=True, exist_ok=True)

    args = SimpleNamespace(
        seed=seed,
        output_dir=str(temp_out),
        duration_hours=duration_hours,
        time_scale=time_scale,
        scenario=fixture.scenario,
        verbose=False,
    )
    run_dir = run_simulation(args)

    final_dir = output_root / fixture.name
    if final_dir.exists():
        shutil.rmtree(final_dir)
    _copy_artifacts(run_dir, final_dir)
    _write_manifest(
        final_dir,
        seed=seed,
        duration_hours=duration_hours,
        time_scale=time_scale,
        scenario=fixture.scenario,
    )
    return final_dir


def generate_fixtures(
    output_root: Path,
    seed: int = 42,
    duration_hours: float = 24.0,
    time_scale: float = 1_000_000.0,
) -> list[Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for fixture in DEMO_FIXTURES:
        generated.append(
            _run_single_fixture(
                output_root=output_root,
                fixture=fixture,
                seed=seed,
                duration_hours=duration_hours,
                time_scale=time_scale,
            )
        )
    tmp_root = output_root / "_tmp"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    return generated


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic Stage 1 demo fixtures for playground.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("tests/fixtures/playground_demo_runs"),
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--duration-hours", type=float, default=24.0)
    parser.add_argument("--time-scale", type=float, default=1_000_000.0)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    generated = generate_fixtures(
        output_root=args.output_root,
        seed=args.seed,
        duration_hours=args.duration_hours,
        time_scale=args.time_scale,
    )
    print("Generated demo fixtures:")
    for path in generated:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
