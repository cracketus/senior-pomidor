# Playground API Compatibility Policy (Stage 6 Read-Only Observability)

This policy maps the playground API surface to the current Stage 6 target for read-only observability over Stage 2-5 runtime artifacts.

## Status Definitions
- `implemented`: endpoint can be backed by canonical deterministic fixture artifacts.
- `deferred`: endpoint requires mutable runtime orchestration or not-yet-shipped production integrations.

## Route Mapping
| Route | Spec Area | Stage 6 Status | Notes |
|---|---|---|---|
| `GET /api/capabilities` | General | implemented | Exposes read-only mode and stream-level support flags (`capabilities_v2`). |
| `GET /api/runs` | Simulation/Logs | implemented | Enumerates available run fixtures and metadata. |
| `GET /api/sim/status` | Simulation | implemented | Derived from selected run manifest and latest cadence/state records. |
| `GET /api/pipeline/current` | Pipeline | implemented | Latest state + anomaly summary + cadence, with optional Stage 2-5 summary refs (`pipeline_current_v2`). |
| `GET /api/logs/states` | Logs | implemented | Serves `StateV1` records from JSONL. |
| `GET /api/logs/anomalies` | Logs | implemented | Serves `AnomalyV1` records from JSONL. |
| `GET /api/logs/sensor_health` | Logs | implemented | Serves `SensorHealthV1` records from JSONL. |
| `GET /api/logs/cadence` | Logs | implemented | Serves cadence records from JSONL. |
| `GET /api/logs/actions` | Logs | implemented | Serves `ActionV1` records from `actions.jsonl` when present. |
| `GET /api/logs/guardrail_results` | Logs | implemented | Serves `GuardrailResultV1` records from `guardrail_results.jsonl` when present. |
| `GET /api/logs/executor_events` | Logs | implemented | Serves `ExecutorEventV1` records from `executor_log.jsonl` when present. |
| `GET /api/logs/forecast_36h` | Logs | implemented | Serves `Forecast36hV1` records from `forecast_36h.jsonl` when present. |
| `GET /api/logs/targets` | Logs | implemented | Serves `TargetsV1` records from `targets.jsonl` when present. |
| `GET /api/logs/sampling_plan` | Logs | implemented | Serves `SamplingPlanV1` records from `sampling_plan.jsonl` when present. |
| `GET /api/logs/weather_adapter` | Logs | implemented | Serves `WeatherAdapterLogV1` records from `weather_adapter_log.jsonl` when present. |
| `GET /api/logs/vision` | Logs | implemented | Serves `VisionV1` records from `vision.jsonl` when present. |
| `GET /api/logs/vision_explanations` | Logs | implemented | Serves `VisionExplanationV1` records from `vision_explanations.jsonl` when present. |
| `GET /api/logs/export_public` | Logs | implemented | Uses public subset export behavior. |
| `POST /api/sim/start` | Simulation Controls | deferred | Mutable runtime control is out of Stage 6 scope. |
| `POST /api/sim/pause` | Simulation Controls | deferred | Mutable runtime control is out of Stage 6 scope. |
| `POST /api/sim/step` | Simulation Controls | deferred | Mutable runtime control is out of Stage 6 scope. |
| `POST /api/sim/speed` | Simulation Controls | deferred | Mutable runtime control is out of Stage 6 scope. |
| `POST /api/sim/jump` | Simulation Controls | deferred | Mutable runtime control is out of Stage 6 scope. |
| `POST /api/pipeline/run_once` | Pipeline Controls | deferred | Runtime control/execution mutation is out of scope. |
| `POST /api/vision/analyze` | Vision | deferred | External model runtime is not implemented here. |
| `POST /api/vision/attach` | Vision | deferred | Media ingestion pipeline is not implemented here. |

## Fixture Ingestion Contract

Required run files:
- `state.jsonl`
- `anomalies.jsonl`
- `sensor_health.jsonl`
- `cadence.jsonl`
- `manifest.json`

Optional but supported run files:
- `actions.jsonl`
- `guardrail_results.jsonl`
- `executor_log.jsonl`
- `forecast_36h.jsonl`
- `targets.jsonl`
- `sampling_plan.jsonl`
- `weather_adapter_log.jsonl`
- `vision.jsonl`
- `vision_explanations.jsonl`

Fallback behavior for optional files:
- Missing optional file -> endpoint returns empty `items`.
- Related capability flag in `capabilities_v2` should be `false`.
- Endpoint remains stable; no hard failure for mixed-age run directories.

## Non-Negotiable Rule
Playground remains read-only in Stage 6. UI must derive availability from capabilities and never present deferred mutation features as active.
