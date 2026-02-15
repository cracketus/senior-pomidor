"""Validation tests for investor snapshot release notes."""

from __future__ import annotations

import re
from pathlib import Path


SNAPSHOT_NOTES = Path("docs/releases/2026-02-15_snapshot_release_notes.md")
INVESTOR_BRIEF = Path("docs/releases/2026-02-15_investor_brief.md")


def test_release_docs_exist():
    assert SNAPSHOT_NOTES.exists()
    assert INVESTOR_BRIEF.exists()


def test_snapshot_release_notes_required_sections_present():
    content = SNAPSHOT_NOTES.read_text(encoding="utf-8")
    required_sections = [
        "## Scope",
        "## What Works Now",
        "## Proof Points",
        "## Demo Story (Baseline vs Heatwave)",
        "## Known Gaps",
        "## Next Milestones",
        "## Risk Controls",
        "## Do Not Claim Yet",
        "## Fact-Check Matrix",
    ]
    for section in required_sections:
        assert section in content


def test_fact_check_matrix_references_existing_files_and_tests():
    content = SNAPSHOT_NOTES.read_text(encoding="utf-8")
    rows = [
        line
        for line in content.splitlines()
        if re.match(r"^\| C\d+\s*\|", line)
    ]
    assert rows, "Expected at least one fact-check matrix row."

    for row in rows:
        refs = re.findall(r"`([^`]+)`", row)
        assert len(refs) == 2, f"Expected code+test refs in row: {row}"
        code_ref, test_ref = refs
        assert Path(code_ref).exists(), f"Missing code evidence path: {code_ref}"
        assert Path(test_ref).exists(), f"Missing test evidence path: {test_ref}"


def test_do_not_claim_yet_explicit_boundaries():
    content = SNAPSHOT_NOTES.read_text(encoding="utf-8").lower()
    required_markers = [
        "autonomous control decisions",
        "actuator execution",
        "forecast-driven",
        "vision",
        "weather-adaptive",
    ]
    for marker in required_markers:
        assert marker in content
