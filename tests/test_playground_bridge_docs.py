"""Validation tests for Stage 1 + Stage 6 playground bridge documentation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

BRIEF_DOC_STAGE1 = Path("docs/playground/stage1_bridge_implementation_brief.md")
BRIEF_DOC_STAGE6 = Path("docs/playground/stage6_bridge_observability_brief.md")
COMPAT_DOC_STAGE1 = Path("docs/playground/compatibility_policy_stage1.md")
COMPAT_DOC_STAGE6 = Path("docs/playground/compatibility_policy_stage6.md")
MIGRATION_DOC = Path("docs/playground/migration_v1_to_v2.md")
BACKLOG_DOC = Path("docs/playground/stage6_issue_backlog.md")
CONTRACT_DIR = Path("docs/playground/contracts")

CONTRACT_FILES_V1 = {
    "capabilities_v1.json": "capabilities_v1",
    "run_summary_v1.json": "run_summary_v1",
    "pipeline_current_v1.json": "pipeline_current_v1",
    "paginated_log_response_v1.json": "paginated_log_response_v1",
    "api_error_v1.json": "api_error_v1",
}

CONTRACT_FILES_V2 = {
    "capabilities_v2.json": "capabilities_v2",
    "pipeline_current_v2.json": "pipeline_current_v2",
    "paginated_log_response_v2.json": "paginated_log_response_v2",
}


def test_playground_docs_exist():
    assert BRIEF_DOC_STAGE1.exists()
    assert BRIEF_DOC_STAGE6.exists()
    assert COMPAT_DOC_STAGE1.exists()
    assert COMPAT_DOC_STAGE6.exists()
    assert MIGRATION_DOC.exists()
    assert BACKLOG_DOC.exists()
    assert CONTRACT_DIR.exists()


def test_contract_files_are_valid_json_and_named_versions():
    for filename, version in {**CONTRACT_FILES_V1, **CONTRACT_FILES_V2}.items():
        path = CONTRACT_DIR / filename
        assert path.exists(), f"Missing contract file: {path}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["title"] == version
        assert payload["properties"]["schema_version"]["const"] == version


def test_legacy_stage1_policy_keeps_status_classes():
    content = COMPAT_DOC_STAGE1.read_text(encoding="utf-8")
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


def test_stage6_policy_includes_expanded_read_only_routes():
    content = COMPAT_DOC_STAGE6.read_text(encoding="utf-8")
    assert "implemented" in content
    assert "deferred" in content
    assert "read-only" in content.lower()

    required_routes = [
        "GET /api/logs/guardrail_results",
        "GET /api/logs/executor_events",
        "GET /api/logs/forecast_36h",
        "GET /api/logs/targets",
        "GET /api/logs/sampling_plan",
        "GET /api/logs/weather_adapter",
        "GET /api/logs/vision",
        "GET /api/logs/vision_explanations",
        "POST /api/sim/start",
    ]
    for route in required_routes:
        assert route in content


def test_v2_contracts_define_stage6_fields():
    capabilities = json.loads((CONTRACT_DIR / "capabilities_v2.json").read_text(encoding="utf-8"))
    required_caps = capabilities["properties"]["capabilities"]["required"]
    assert "supports_guardrail_log" in required_caps
    assert "supports_executor_log" in required_caps
    assert "supports_weather_adapter_logs" in required_caps
    assert "supports_vision_logs" in required_caps

    logs = json.loads((CONTRACT_DIR / "paginated_log_response_v2.json").read_text(encoding="utf-8"))
    enum_values = logs["properties"]["log_type"]["enum"]
    assert "guardrail_results" in enum_values
    assert "executor_events" in enum_values
    assert "forecast_36h" in enum_values
    assert "targets" in enum_values
    assert "sampling_plan" in enum_values
    assert "weather_adapter" in enum_values
    assert "vision" in enum_values
    assert "vision_explanations" in enum_values

    pipeline = json.loads((CONTRACT_DIR / "pipeline_current_v2.json").read_text(encoding="utf-8"))
    assert "latest_guardrail_result" in pipeline["properties"]
    assert "latest_executor_event" in pipeline["properties"]
    assert "latest_forecast" in pipeline["properties"]
    assert "latest_vision" in pipeline["properties"]
    assert "latest_vision_explanation" in pipeline["properties"]
