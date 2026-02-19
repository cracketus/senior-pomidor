# Investor Brief — Current State Snapshot (February 15, 2026)

## Positioning
This is an engineering evidence snapshot, not a full product launch. Claims below are limited to implemented and test-verified functionality in the current repository state.

## What Is Demonstrated Today
- Deterministic simulation and replay for reproducible pipeline runs.
- Structured state estimation with versioned contracts:
  - `StateV1`
  - `AnomalyV1`
  - `SensorHealthV1`
- Stage 2 water-only control proposals and guardrails outcomes:
  - `ActionV1` logs (`actions.jsonl`)
  - `GuardrailResultV1` logs (`guardrail_results.jsonl`)
  - mock executor observability (`executor_log.jsonl`)
- Event-aware sampling behavior: cadence tightens under high-severity anomalies.
- Transparent JSONL logs suitable for audit, replay, and investor-facing demos.

## Verification Signals
- Repository test status (February 15, 2026): `157 passed`.
- Coverage status: `87.97%`.
- Two deterministic canonical demo datasets are stored for repeatable walkthroughs:
  - `baseline_seed42_24h`
  - `heatwave_seed42_24h`

## Demo Message for Investors
- Baseline run shows stable periodic operation and contract-valid state emission.
- Heatwave run shows stress injection, anomaly detection, and adaptive sampling response.
- Both runs are transparent and reproducible from the same commands and artifacts.

## What Is Explicitly Not Shipped Yet
- Runtime autonomous control decisions.
- Non-water control policy runtime (`light`, `fan`, `co2`, `circulate`).
- Actuator execution loop on real hardware (current executor is log-only).
- Runtime world-model forecasting and weather adaptation.
- Runtime vision/LLM analysis loop.

## Near-Term Build Path
- Stage 2 expansion: broaden control beyond water-only and integrate hardware executor.
- Stage 3: weather integration and forecast-hosted adaptation.
- Stage 4: vision analysis integration.
- Separate `senior-pomidor-playground` repo: read-only observability frontend backed by Stage 1 JSONL artifacts.
