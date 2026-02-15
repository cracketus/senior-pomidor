# Stage 1 Playground Bridge Implementation Brief

## Purpose
Implement a separate `senior-pomidor-playground` repository that exposes Stage 1 data from this repository (`senior-pomidor`) through a read-only API and frontend.

This brief is intentionally scoped to currently implemented functionality only.

## Architecture
- Engine producer: `senior-pomidor` (simulation + JSONL artifacts).
- Playground bridge: FastAPI service reading run directories and serving typed API responses.
- Frontend: React + TypeScript (strict mode), no backend business logic duplication.

## Stage 1 API Surface
- `GET /api/capabilities`
- `GET /api/runs`
- `GET /api/sim/status` (derived from selected run metadata)
- `GET /api/pipeline/current`
- `GET /api/logs/states`
- `GET /api/logs/anomalies`
- `GET /api/logs/sensor_health`
- `GET /api/logs/cadence`
- `GET /api/logs/actions` (returns empty list + `unsupported_in_stage1=true`)
- `GET /api/logs/export_public`

## API Contract Files
Contract payload definitions for the playground bridge are provided in:
- `docs/playground/contracts/capabilities_v1.json`
- `docs/playground/contracts/run_summary_v1.json`
- `docs/playground/contracts/pipeline_current_v1.json`
- `docs/playground/contracts/paginated_log_response_v1.json`
- `docs/playground/contracts/api_error_v1.json`

## Frontend Page Mapping
- Dashboard:
  - latest `StateV1` snapshot
  - confidence badge
  - anomaly counters
  - current cadence mode
- Charts:
  - time series from `state.jsonl`, `anomalies.jsonl`, `cadence.jsonl`
- Scenario Studio:
  - run selector and scenario metadata only
  - no live start/pause/step controls in Stage 1 bridge
- Vision:
  - planned-state panel (feature unavailable indicator)
- Logs:
  - JSONL-backed log browser with schema badges

## UI Capability Rule
Unavailable features must be rendered from capability flags and shown as unavailable. They must never appear as active or simulated.

## Data Source Expectations
The bridge reads canonical artifacts created by:
```powershell
python scripts/generate_playground_demo_fixtures.py
```

Expected per-run files:
- `state.jsonl`
- `anomalies.jsonl`
- `sensor_health.jsonl`
- `observations.jsonl`
- `cadence.jsonl`
- `manifest.json`

## Acceptance Scenarios (Bridge Repo)
- Endpoint payloads include declared `schema_version`.
- Invalid run identifier returns `api_error_v1`.
- Contract validation for records proxied from core logs.
- Dashboard renders without actions/world-model data.
- Capability flags hide unsupported controls.
- Heatwave run shows event-mode cadence and anomaly spike behavior.
