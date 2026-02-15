"""CLI tests for simulate_day script."""

import subprocess
import sys
from pathlib import Path


def _run(args, cwd: Path):
    return subprocess.run(
        [sys.executable, "scripts/simulate_day.py", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_help_contains_required_arguments(tmp_path):
    result = _run(["--help"], cwd=Path.cwd())
    assert result.returncode == 0
    for flag in [
        "--seed",
        "--output-dir",
        "--duration-hours",
        "--time-scale",
        "--scenario",
        "--verbose",
    ]:
        assert flag in result.stdout


def test_all_cli_arguments_are_valid(tmp_path):
    result = _run(
        [
            "--seed",
            "123",
            "--output-dir",
            str(tmp_path),
            "--duration-hours",
            "2",
            "--time-scale",
            "1000000",
            "--scenario",
            "none",
            "--verbose",
        ],
        cwd=Path.cwd(),
    )
    assert result.returncode == 0
