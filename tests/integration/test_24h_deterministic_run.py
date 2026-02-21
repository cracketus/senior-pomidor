"""Integration test for 24h deterministic simulation run."""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from brain.contracts import (
    ActionV1,
    AnomalyV1,
    DeviceStatusV1,
    ExecutorEventV1,
    Forecast36hV1,
    GuardrailResultV1,
    ObservationV1,
    SamplingPlanV1,
    SensorHealthV1,
    StateV1,
    TargetsV1,
    VisionExplanationV1,
    VisionV1,
    WeatherAdapterLogV1,
)
from brain.contracts.action_v1 import ActionType
from brain.contracts.guardrail_result_v1 import GuardrailDecision
from brain.executor import HardwareExecutor, HardwareStubAdapter, IdempotencyConfig


def _run_simulate(
    output_dir: Path,
    seed: int,
    scenario: str = "none",
    duration_hours: int = 24,
) -> subprocess.CompletedProcess:
    args = [
        sys.executable,
        "scripts/simulate_day.py",
        "--output-dir",
        str(output_dir),
        "--duration-hours",
        str(duration_hours),
        "--seed",
        str(seed),
        "--time-scale",
        "1000000",
        "--scenario",
        scenario,
    ]
    return subprocess.run(args, cwd=Path.cwd(), capture_output=True, text=True)


def _find_run_dir(output_dir: Path) -> Path:
    runs = [p for p in output_dir.iterdir() if p.is_dir() and p.name.startswith("run_")]
    assert len(runs) == 1
    return runs[0]


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8").strip()
    return [] if not content else content.splitlines()


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in _read_lines(path)]


def test_24h_simclock_run_produces_expected_state_count(tmp_path):
    result = _run_simulate(tmp_path, seed=42)
    assert result.returncode == 0, result.stderr

    run_dir = _find_run_dir(tmp_path)
    state_records = _load_jsonl(run_dir / "state.jsonl")

    assert len(state_records) >= 12


def test_24h_run_has_no_unhandled_exceptions(tmp_path):
    result = _run_simulate(tmp_path, seed=123)
    assert result.returncode == 0, result.stderr


def test_24h_run_outputs_validate_against_contracts(tmp_path):
    result = _run_simulate(tmp_path, seed=7)
    assert result.returncode == 0, result.stderr

    run_dir = _find_run_dir(tmp_path)

    for payload in _load_jsonl(run_dir / "state.jsonl"):
        StateV1.model_validate(payload, strict=False)

    for payload in _load_jsonl(run_dir / "anomalies.jsonl"):
        AnomalyV1.model_validate(payload, strict=False)

    for payload in _load_jsonl(run_dir / "sensor_health.jsonl"):
        SensorHealthV1.model_validate(payload, strict=False)

    for payload in _load_jsonl(run_dir / "observations.jsonl"):
        ObservationV1.model_validate(payload["observation"], strict=False)
        DeviceStatusV1.model_validate(payload["device_status"], strict=False)

    for payload in _load_jsonl(run_dir / "actions.jsonl"):
        ActionV1.model_validate(payload, strict=False)

    for payload in _load_jsonl(run_dir / "guardrail_results.jsonl"):
        GuardrailResultV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "executor_log.jsonl"):
        ExecutorEventV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "forecast_36h.jsonl"):
        Forecast36hV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "targets.jsonl"):
        TargetsV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "sampling_plan.jsonl"):
        SamplingPlanV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "weather_adapter_log.jsonl"):
        WeatherAdapterLogV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "vision.jsonl"):
        VisionV1.model_validate(payload, strict=False)
    for payload in _load_jsonl(run_dir / "vision_explanations.jsonl"):
        VisionExplanationV1.model_validate(payload, strict=False)

def test_24h_run_is_deterministic_with_fixed_seed(tmp_path):
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"

    result_a = _run_simulate(out_a, seed=99)
    result_b = _run_simulate(out_b, seed=99)

    assert result_a.returncode == 0, result_a.stderr
    assert result_b.returncode == 0, result_b.stderr

    run_a = _find_run_dir(out_a)
    run_b = _find_run_dir(out_b)

    assert (run_a / "state.jsonl").read_text(encoding="utf-8") == (
        run_b / "state.jsonl"
    ).read_text(encoding="utf-8")


def test_24h_run_jsonl_files_are_readable(tmp_path):
    result = _run_simulate(tmp_path, seed=55)
    assert result.returncode == 0, result.stderr

    run_dir = _find_run_dir(tmp_path)

    for name in [
        "state.jsonl",
        "anomalies.jsonl",
        "sensor_health.jsonl",
        "observations.jsonl",
        "cadence.jsonl",
        "actions.jsonl",
        "guardrail_results.jsonl",
        "executor_log.jsonl",
        "forecast_36h.jsonl",
        "targets.jsonl",
        "sampling_plan.jsonl",
        "weather_adapter_log.jsonl",
        "vision.jsonl",
        "vision_explanations.jsonl",
    ]:
        path = run_dir / name
        for line in _read_lines(path):
            json.loads(line)


def test_24h_run_all_artifacts_are_deterministic(tmp_path):
    out_a = tmp_path / "a_all"
    out_b = tmp_path / "b_all"

    result_a = _run_simulate(out_a, seed=31415)
    result_b = _run_simulate(out_b, seed=31415)

    assert result_a.returncode == 0, result_a.stderr
    assert result_b.returncode == 0, result_b.stderr

    run_a = _find_run_dir(out_a)
    run_b = _find_run_dir(out_b)

    for artifact in [
        "state.jsonl",
        "anomalies.jsonl",
        "sensor_health.jsonl",
        "observations.jsonl",
        "actions.jsonl",
        "guardrail_results.jsonl",
        "executor_log.jsonl",
        "forecast_36h.jsonl",
        "targets.jsonl",
        "sampling_plan.jsonl",
        "weather_adapter_log.jsonl",
        "vision.jsonl",
        "vision_explanations.jsonl",
    ]:
        left = (run_a / artifact).read_text(encoding="utf-8")
        right = (run_b / artifact).read_text(encoding="utf-8")
        assert left == right, f"Mismatch in deterministic artifact: {artifact}"


def test_event_driven_window_is_deterministic(tmp_path):
    out_a = tmp_path / "event_a"
    out_b = tmp_path / "event_b"

    result_a = _run_simulate(out_a, seed=2026, scenario="heatwave", duration_hours=8)
    result_b = _run_simulate(out_b, seed=2026, scenario="heatwave", duration_hours=8)

    assert result_a.returncode == 0, result_a.stderr
    assert result_b.returncode == 0, result_b.stderr

    run_a = _find_run_dir(out_a)
    run_b = _find_run_dir(out_b)

    cadence_a = (run_a / "cadence.jsonl").read_text(encoding="utf-8")
    cadence_b = (run_b / "cadence.jsonl").read_text(encoding="utf-8")
    assert cadence_a == cadence_b

    records = _load_jsonl(run_a / "cadence.jsonl")
    assert any(record["mode"] == "event" for record in records)


def test_executor_state_transition_events_validate_contracts():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(HardwareStubAdapter())
    action = ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=5.0,
        intensity=0.5,
        reason="integration_test",
    )
    guardrail = GuardrailResultV1(
        schema_version="guardrail_result_v1",
        timestamp=now,
        decision=GuardrailDecision.APPROVED,
        reason_codes=[],
    )

    event = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now,
        device_status=None,
    )
    transitions = executor.drain_runtime_events()

    assert event.status == "skipped"
    assert event.notes == "blocked_by_state:faulted"
    assert transitions
    for payload in [item.model_dump(mode="json") for item in transitions]:
        ExecutorEventV1.model_validate(payload, strict=False)


def test_executor_idempotency_events_validate_contracts():
    now = datetime(2026, 2, 15, 0, 0, tzinfo=timezone.utc)
    executor = HardwareExecutor(
        HardwareStubAdapter(),
        idempotency=IdempotencyConfig(ttl_seconds=60 * 60),
    )
    action = ActionV1(
        schema_version="action_v1",
        timestamp=now,
        action_type=ActionType.WATER,
        duration_seconds=5.0,
        intensity=0.5,
        reason="integration_test",
        idempotency_key="integration-idem-0001",
    )
    guardrail = GuardrailResultV1(
        schema_version="guardrail_result_v1",
        timestamp=now,
        decision=GuardrailDecision.APPROVED,
        reason_codes=[],
    )
    device = DeviceStatusV1(
        schema_version="device_status_v1",
        timestamp=now,
        light_on=False,
        fans_on=True,
        heater_on=False,
        pump_on=False,
        co2_on=False,
        mcu_connected=True,
        mcu_uptime_seconds=100,
        mcu_reset_count=0,
    )

    first = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now,
        device_status=device,
    )
    _ = executor.drain_runtime_events()
    second = executor.execute(
        proposed_action=action,
        effective_action=action,
        guardrail_result=guardrail,
        now=now + timedelta(minutes=1),
        device_status=device.model_copy(update={"timestamp": now + timedelta(minutes=1)}),
    )
    runtime = executor.drain_runtime_events()

    assert first.status == "executed"
    assert second.status == "skipped"
    assert "idempotency_duplicate" in second.reason_codes
    for payload in [item.model_dump(mode="json") for item in runtime]:
        ExecutorEventV1.model_validate(payload, strict=False)
