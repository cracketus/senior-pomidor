"""Integration-style tests for simulate_day outputs."""

import json
import subprocess
import sys
from pathlib import Path


def _run_simulate(output_dir: Path, extra_args: list[str]) -> subprocess.CompletedProcess:
    args = [
        sys.executable,
        "scripts/simulate_day.py",
        "--output-dir",
        str(output_dir),
    ] + extra_args
    return subprocess.run(args, cwd=Path.cwd(), capture_output=True, text=True)


def _find_run_dir(output_dir: Path) -> Path:
    runs = [p for p in output_dir.iterdir() if p.is_dir() and p.name.startswith("run_")]
    assert len(runs) == 1
    return runs[0]


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    return [] if not text else text.splitlines()


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in _read_lines(path)]


def test_generates_state_and_anomaly_logs(tmp_path):
    result = _run_simulate(
        tmp_path,
        ["--duration-hours", "2", "--seed", "123", "--time-scale", "1000000"],
    )
    assert result.returncode == 0

    run_dir = _find_run_dir(tmp_path)
    state_path = run_dir / "state.jsonl"
    anomaly_path = run_dir / "anomalies.jsonl"
    observations_path = run_dir / "observations.jsonl"

    assert state_path.exists()
    assert anomaly_path.exists()
    assert observations_path.exists()
    assert len(_read_lines(state_path)) >= 1


def test_time_scale_does_not_change_logical_count(tmp_path):
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"

    result_a = _run_simulate(
        out_a,
        ["--duration-hours", "4", "--seed", "7", "--time-scale", "1000000"],
    )
    result_b = _run_simulate(
        out_b,
        ["--duration-hours", "4", "--seed", "7", "--time-scale", "2000000"],
    )

    assert result_a.returncode == 0
    assert result_b.returncode == 0

    run_a = _find_run_dir(out_a)
    run_b = _find_run_dir(out_b)

    count_a = len(_read_lines(run_a / "state.jsonl"))
    count_b = len(_read_lines(run_b / "state.jsonl"))

    assert count_a == count_b


def test_fixed_seed_produces_reproducible_outputs(tmp_path):
    out_a = tmp_path / "run_a"
    out_b = tmp_path / "run_b"

    result_a = _run_simulate(
        out_a,
        ["--duration-hours", "4", "--seed", "42", "--time-scale", "1000000"],
    )
    result_b = _run_simulate(
        out_b,
        ["--duration-hours", "4", "--seed", "42", "--time-scale", "1000000"],
    )

    assert result_a.returncode == 0
    assert result_b.returncode == 0

    run_a = _find_run_dir(out_a)
    run_b = _find_run_dir(out_b)

    assert (run_a / "state.jsonl").read_text(encoding="utf-8") == (
        run_b / "state.jsonl"
    ).read_text(encoding="utf-8")


def test_event_driven_mode_increases_sampling_frequency(tmp_path):
    result = _run_simulate(
        tmp_path,
        ["--duration-hours", "8", "--seed", "123", "--time-scale", "1000000", "--scenario", "heatwave"],
    )
    assert result.returncode == 0

    run_dir = _find_run_dir(tmp_path)
    cadence_records = _load_jsonl(run_dir / "cadence.jsonl")

    assert cadence_records, "cadence.jsonl should contain cycle metadata"
    modes = {record["mode"] for record in cadence_records}
    intervals = {record["interval_seconds"] for record in cadence_records}

    assert "baseline" in modes
    assert "event" in modes
    assert 7200 in intervals
    assert 900 in intervals
