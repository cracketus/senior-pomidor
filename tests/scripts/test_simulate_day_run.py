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
    actions_path = run_dir / "actions.jsonl"
    guardrail_results_path = run_dir / "guardrail_results.jsonl"
    executor_log_path = run_dir / "executor_log.jsonl"
    forecast_path = run_dir / "forecast_36h.jsonl"
    targets_path = run_dir / "targets.jsonl"
    sampling_plan_path = run_dir / "sampling_plan.jsonl"
    weather_adapter_log_path = run_dir / "weather_adapter_log.jsonl"
    vision_path = run_dir / "vision.jsonl"
    vision_explanations_path = run_dir / "vision_explanations.jsonl"

    assert state_path.exists()
    assert anomaly_path.exists()
    assert observations_path.exists()
    assert actions_path.exists()
    assert guardrail_results_path.exists()
    assert executor_log_path.exists()
    assert forecast_path.exists()
    assert targets_path.exists()
    assert sampling_plan_path.exists()
    assert weather_adapter_log_path.exists()
    assert vision_path.exists()
    assert vision_explanations_path.exists()
    assert len(_read_lines(state_path)) >= 1

    action_records = _load_jsonl(actions_path)
    for record in action_records:
        assert record["schema_version"] == "action_v1"
        assert record["action_type"] == "water"

    guardrail_records = _load_jsonl(guardrail_results_path)
    for record in guardrail_records:
        assert record["schema_version"] == "guardrail_result_v1"
        assert record["decision"] in {"approved", "rejected", "clipped"}

    executor_records = _load_jsonl(executor_log_path)
    for record in executor_records:
        assert record["schema_version"] == "executor_event_v1"
        assert record["status"] in {"executed", "skipped"}

    for record in _load_jsonl(forecast_path):
        assert record["schema_version"] == "forecast_36h_v1"
    for record in _load_jsonl(targets_path):
        assert record["schema_version"] == "targets_v1"
    for record in _load_jsonl(sampling_plan_path):
        assert record["schema_version"] == "sampling_plan_v1"
    for record in _load_jsonl(weather_adapter_log_path):
        assert record["schema_version"] == "weather_adapter_log_v1"
    for record in _load_jsonl(vision_path):
        assert record["schema_version"] == "vision_v1"
    for record in _load_jsonl(vision_explanations_path):
        assert record["schema_version"] == "vision_explanation_v1"

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
        [
            "--duration-hours",
            "8",
            "--seed",
            "123",
            "--time-scale",
            "1000000",
            "--scenario",
            "heatwave",
        ],
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


def test_hardware_backend_uses_selected_driver_in_executor_notes(tmp_path):
    result = _run_simulate(
        tmp_path,
        [
            "--duration-hours",
            "2",
            "--seed",
            "123",
            "--time-scale",
            "1000000",
            "--executor-backend",
            "hardware",
            "--hardware-driver",
            "production_scaffold",
        ],
    )
    assert result.returncode == 0

    run_dir = _find_run_dir(tmp_path)
    records = _load_jsonl(run_dir / "executor_log.jsonl")
    executed = [record for record in records if record["status"] == "executed"]
    assert all(
        record["notes"].startswith("executed_production_scaffold:")
        for record in executed
    )


def test_flaky_hardware_driver_emits_retry_events(tmp_path):
    result = _run_simulate(
        tmp_path,
        [
            "--duration-hours",
            "8",
            "--seed",
            "42",
            "--time-scale",
            "1000000",
            "--executor-backend",
            "hardware",
            "--hardware-driver",
            "flaky_stub",
            "--force-water-action",
        ],
    )
    assert result.returncode == 0

    run_dir = _find_run_dir(tmp_path)
    records = _load_jsonl(run_dir / "executor_log.jsonl")
    retry_records = [
        record for record in records if (record.get("notes") or "").startswith("retry_scheduled:")
    ]
    assert retry_records, "expected deterministic retry scheduling events in executor_log.jsonl"


def test_forced_idempotency_key_emits_duplicate_skip_events(tmp_path):
    result = _run_simulate(
        tmp_path,
        [
            "--duration-hours",
            "8",
            "--seed",
            "42",
            "--time-scale",
            "1000000",
            "--executor-backend",
            "hardware",
            "--hardware-driver",
            "flaky_stub",
            "--force-water-action",
            "--force-idempotency-key",
            "stage5-runtime-idem",
        ],
    )
    assert result.returncode == 0

    run_dir = _find_run_dir(tmp_path)
    records = _load_jsonl(run_dir / "executor_log.jsonl")
    assert any(
        (record.get("notes") or "").startswith("idempotency_stored:key=stage5-runtime-idem")
        for record in records
    )
    assert any(
        (record.get("notes") or "").startswith("idempotency_hit:key=stage5-runtime-idem")
        for record in records
    )
    assert any(
        record.get("notes") == "skipped_duplicate_idempotency_key:stage5-runtime-idem"
        for record in records
    )
