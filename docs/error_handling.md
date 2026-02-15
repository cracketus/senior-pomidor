# Error Handling Policy

This document defines runtime error handling behavior for Stage 1 components:

- `brain/sources/*`
- `brain/estimator/*`
- `brain/storage/*`
- `scripts/simulate_day.py`

Policy goals:

- deterministic behavior for identical inputs
- explicit fail-fast boundaries
- clear log severity by failure class

## Policy Table

| Component | Error case | Level | Behavior | Notes |
|---|---|---|---|---|
| Replay source | malformed JSONL line | WARNING | skip line and continue (`skip` policy) | `fail_fast` mode raises `ValueError` |
| Replay source | invalid schema payload | WARNING | skip line and continue (`skip` policy) | `fail_fast` mode raises `ValueError` |
| Synthetic source | invalid config (negative step/count, naive datetime) | ERROR | raise `ValueError` and stop startup | deterministic startup validation |
| Estimator (VPD) | invalid RH (<0 or >100), unsupported temperature range | ERROR | raise `ValueError` for invalid observation | caller decides retry/stop |
| Estimator pipeline | contract validation failure | ERROR | raise exception and stop current run | prevents silent data corruption |
| Storage writer | JSON serialization failure | ERROR | raise exception | caller handles termination |
| Storage writer | fsync unsupported | WARNING | write succeeds, fsync error swallowed | durability best-effort fallback |
| Simulation script | invalid CLI arguments | ERROR | raise `ValueError`, exit code `1` | validated before run starts |
| Simulation script | unhandled runtime exception | ERROR | print error to stderr, exit code `1` | no silent partial success |

## Source-Level Rules

### Replay source

- `malformed_policy="skip"`: malformed lines are logged and ignored.
- `malformed_policy="fail_fast"`: first malformed line raises and aborts replay.
- end-of-stream returns `None`.

### Synthetic source

- invalid configuration is rejected at construction.
- deterministic output depends on a valid seed + config.

## Estimator Rules

- input contracts are strict and timezone-aware.
- impossible physical input for VPD calculation is rejected.
- anomaly and confidence outputs must remain deterministic.

## Storage Rules

- append writes must produce line-delimited JSON.
- serialization failures are fatal for the append call.
- rotation failures return `None` and do not corrupt existing data.

## Script Rules (`scripts/simulate_day.py`)

- invalid `--duration-hours` or `--time-scale` fails fast.
- unsupported scenario name fails fast.
- any unhandled exception results in:
  - message: `simulate_day failed: <error>`
  - process exit code `1`

## Operational Guidance

- Use `fail_fast` mode when preparing golden datasets.
- Use `skip` mode when replaying noisy external logs.
- Treat storage exceptions as run-stopping events.
- Keep log records and contracts in sync with these policies.
