# Stage 6 Issue Backlog (Playground Read-Only Observability)

This backlog is capped at 8 issues and aligned to Stage 6 scope.

## 1. TOMATO-76: Stage 6 tracking - playground observability expansion
- Parent tracker for Stage 6 playground observability work.
- Tracks closure of TOMATO-77..TOMATO-83 and acceptance gates.
- GitHub issue: #88

## 2. TOMATO-77: Define playground capabilities_v2 for Stage 2-5 stream flags
- Add `capabilities_v2` schema with additive booleans for guardrail/executor/weather/vision stream support.
- Keep `capabilities_v1` unchanged.
- GitHub issue: #81

## 3. TOMATO-78: Define paginated_log_response_v2 with expanded log_type enum
- Add Stage 2-5 log stream identifiers to `log_type`.
- Preserve response envelope and pagination semantics.
- GitHub issue: #82

## 4. TOMATO-79: Define pipeline_current_v2 with optional Stage 2-5 summary references
- Add optional latest references for guardrail, executor, forecast, vision, and vision explanation payloads.
- Preserve required Stage 1 core fields.
- GitHub issue: #83

## 5. TOMATO-80: Update docs/playground compatibility policy to Stage 6 read-only matrix
- Add Stage 6 route mapping for new GET log endpoints.
- Keep all POST mutation routes deferred.
- GitHub issue: #84

## 6. TOMATO-81: Add fixture-ingestion contract note for required vs optional streams
- Document required files and optional Stage 2-5 streams.
- Define fallback behavior for missing optional streams.
- GitHub issue: #85

## 7. TOMATO-82: Add tests validating new playground contract files and route matrix
- Extend docs/contract tests for new `v2` schemas.
- Validate Stage 6 route matrix includes all new log endpoints.
- Keep Stage 1 legacy docs/tests intact.
- GitHub issue: #86

## 8. TOMATO-83: Add migration notes (v1 -> v2) for senior-pomidor-playground implementers
- Provide additive migration guide and mixed-age run compatibility behavior.
- GitHub issue: #87
