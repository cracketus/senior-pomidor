"""Tests for canonical playground demo fixture generation."""

from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.generate_playground_demo_fixtures import (
    ARTIFACT_FILES,
    DEMO_FIXTURES,
    generate_fixtures,
)

FIXTURE_ROOT = Path("tests/fixtures/playground_demo_runs")


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def test_committed_playground_demo_fixtures_exist():
    for fixture in DEMO_FIXTURES:
        fixture_dir = FIXTURE_ROOT / fixture.name
        assert fixture_dir.exists(), f"Missing fixture directory: {fixture_dir}"
        for artifact in ARTIFACT_FILES:
            assert (fixture_dir / artifact).exists(), (
                f"Missing artifact {artifact} in fixture {fixture.name}"
            )
        assert (fixture_dir / "manifest.json").exists(), (
            f"Missing manifest for fixture {fixture.name}"
        )


def test_fixture_regeneration_is_byte_identical(tmp_path):
    generated_root_a = tmp_path / "generated_a"
    generated_root_b = tmp_path / "generated_b"

    generate_fixtures(
        output_root=generated_root_a,
        seed=42,
        duration_hours=24.0,
        time_scale=1_000_000.0,
    )
    generate_fixtures(
        output_root=generated_root_b,
        seed=42,
        duration_hours=24.0,
        time_scale=1_000_000.0,
    )

    for fixture in DEMO_FIXTURES:
        generated_dir_a = generated_root_a / fixture.name
        generated_dir_b = generated_root_b / fixture.name
        for artifact in ARTIFACT_FILES:
            generated_hash_a = _sha256_file(generated_dir_a / artifact)
            generated_hash_b = _sha256_file(generated_dir_b / artifact)
            assert generated_hash_a == generated_hash_b, (
                f"Artifact mismatch across deterministic reruns: "
                f"{fixture.name}/{artifact}"
            )
