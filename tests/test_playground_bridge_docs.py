"""Validation tests for Stage 1 playground bridge documentation artifacts."""

from __future__ import annotations

import json
from pathlib import Path


BRIEF_DOC = Path("docs/playground/stage1_bridge_implementation_brief.md")
COMPAT_DOC = Path("docs/playground/compatibility_policy_stage1.md")
CONTRACT_DIR = Path("docs/playground/contracts")

CONTRACT_FILES = {
    "capabilities_v1.json": "capabilities_v1",
    "run_summary_v1.json": "run_summary_v1",
    "pipeline_current_v1.json": "pipeline_current_v1",
    "paginated_log_response_v1.json": "paginated_log_response_v1",
    "api_error_v1.json": "api_error_v1",
}


def test_stage1_playground_docs_exist():
    assert BRIEF_DOC.exists()
    assert COMPAT_DOC.exists()
    assert CONTRACT_DIR.exists()


def test_contract_files_are_valid_json_and_named_versions():
    for filename, version in CONTRACT_FILES.items():
        path = CONTRACT_DIR / filename
        assert path.exists(), f"Missing contract file: {path}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["title"] == version
        assert payload["properties"]["schema_version"]["const"] == version


def test_compatibility_policy_has_all_status_classes():
    content = COMPAT_DOC.read_text(encoding="utf-8")
    assert "implemented" in content
    assert "read_only_stub" in content
    assert "deferred" in content

    required_routes = [
        "GET /api/capabilities",
        "GET /api/runs",
        "GET /api/pipeline/current",
        "GET /api/logs/actions",
        "POST /api/sim/start",
    ]
    for route in required_routes:
        assert route in content
