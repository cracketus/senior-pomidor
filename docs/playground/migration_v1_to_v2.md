# Playground Contract Migration: v1 -> v2

This guide documents additive migration from the Stage 1 playground contract set (`v1`) to Stage 6 read-only observability contracts (`v2`).

## Compatibility Strategy
- `v1` files stay valid and are not modified.
- `v2` files add Stage 2-5 observability semantics.
- Consumers can migrate endpoint-by-endpoint.

## Contract Changes

### `capabilities_v1` -> `capabilities_v2`
Added capability flags:
- `supports_guardrail_log`
- `supports_executor_log`
- `supports_weather_adapter_logs`
- `supports_vision_logs`

Existing fields remain unchanged.

### `paginated_log_response_v1` -> `paginated_log_response_v2`
Extended `log_type` enum with:
- `guardrail_results`
- `executor_events`
- `forecast_36h`
- `targets`
- `sampling_plan`
- `weather_adapter`
- `vision`
- `vision_explanations`

Pagination contract and response envelope remain unchanged.

### `pipeline_current_v1` -> `pipeline_current_v2`
Adds optional references:
- `latest_guardrail_result`
- `latest_executor_event`
- `latest_forecast`
- `latest_vision`
- `latest_vision_explanation`

Core required fields from `v1` remain required.

## Mixed-Age Run Handling
- Required files (`state/anomalies/sensor_health/cadence/manifest`) must exist.
- Missing optional Stage 2-5 files are represented by:
  - empty `items` in log endpoints
  - `false` capability flags
- Consumers must not treat missing optional streams as fatal.

## Recommended Rollout
1. Parse `capabilities_v2` first and gate UI by capability booleans.
2. Upgrade log routing to `paginated_log_response_v2` enum set.
3. Read optional `pipeline_current_v2` references when present.
4. Keep fallback path for `v1` contracts during transition.
