# Playground Demo Fixtures (Stage 3)

These fixtures are canonical deterministic runs for investor/demo playback.

## Fixtures
- `baseline_seed42_24h` (`scenario=none`)
- `heatwave_seed42_24h` (`scenario=heatwave`)

Each fixture contains:
- `state.jsonl`
- `anomalies.jsonl`
- `sensor_health.jsonl`
- `observations.jsonl`
- `cadence.jsonl`
- `actions.jsonl`
- `guardrail_results.jsonl`
- `executor_log.jsonl`
- `forecast_36h.jsonl`
- `targets.jsonl`
- `sampling_plan.jsonl`
- `weather_adapter_log.jsonl`
- `manifest.json` (hashes + summary metrics)

## Regeneration
Run from repository root:

```powershell
python scripts/generate_playground_demo_fixtures.py
```

Expected behavior:
- fixture directories are recreated deterministically
- artifact files remain byte-identical for identical seed/scenario/config
