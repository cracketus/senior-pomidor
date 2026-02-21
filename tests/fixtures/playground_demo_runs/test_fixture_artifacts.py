"""Assertions for committed Stage 5 fixture execution-path artifacts."""

from __future__ import annotations

import json
from pathlib import Path

FIXTURE_ROOT = Path("tests/fixtures/playground_demo_runs")
FIXTURES = ("baseline_seed42_24h", "heatwave_seed42_24h")


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def test_stage5_executor_log_contains_runtime_signals():
    all_notes: list[str] = []
    for fixture in FIXTURES:
        executor_log = _load_jsonl(FIXTURE_ROOT / fixture / "executor_log.jsonl")
        notes = [str(record.get("notes") or "") for record in executor_log]
        all_notes.extend(notes)

    assert any(note.startswith("state_transition:") for note in all_notes)
    assert any(note.startswith("retry_scheduled:") for note in all_notes)
    assert any(note.startswith("idempotency_stored:") for note in all_notes)
    assert any(note.startswith("idempotency_hit:") for note in all_notes)
    assert any(note.startswith("skipped_duplicate_idempotency_key:") for note in all_notes)
