# Issue 1 — Repository Bootstrap (Production Skeleton)

## Title
**Bootstrap production-ready Python 3.11 repository skeleton for Embodied AI Tomato Brain**

## Context / Why
We need a stable, reproducible baseline before implementing domain logic. A production-ready skeleton ensures consistent tooling, testing, linting, and packaging from day one, reducing rework and integration risk.

## Scope
- Configure Python 3.11 project metadata and dependencies in `pyproject.toml`
- Add and configure:
  - `pytest`
  - `pytest-cov` (coverage reporting)
  - `ruff`
- Create minimal package structure under `brain/`
- Add baseline `README.md` with setup, test, lint, and run instructions
- Add CI-ready local commands/scripts/config structure (no CI provider workflow yet)
- Add initial smoke test to validate package import and test harness

## Non-goals
- Implementing domain models, storage logic, clock/scheduler, or estimator logic
- Connecting to hardware, database, API server, or LLM
- Adding complex architecture beyond MVP skeleton

## Acceptance Criteria
- [ ] Project uses Python 3.11 in configuration and documentation
- [ ] `pyproject.toml` exists with dependencies and tool configuration
- [ ] `pytest` and coverage run successfully locally
- [ ] `ruff` runs successfully locally
- [ ] `brain/` package exists and is importable
- [ ] `README.md` includes quickstart, lint, test, and simulation command placeholders
- [ ] Repository structure is ready for future CI integration

## Required Tests
- `tests/test_smoke_import.py::test_import_brain_package`
- `tests/test_project_metadata.py::test_python_version_target_is_311`
- `tests/test_tooling_config.py::test_pyproject_contains_pytest_and_ruff_sections`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- Coverage command executes without errors
- Ruff command executes without errors
- Documentation is sufficient for a new engineer to bootstrap locally in <10 minutes

## Dependencies
- None

---

# Issue 2 — Contracts: Pydantic Models as Source of Truth

## Title
**Define strict Pydantic v2 contracts for state/action/anomaly/sensor health (v1 schemas)**

## Context / Why
Typed contracts are the source of truth for all pipeline boundaries and persisted records. Strong validation and schema generation reduce integration bugs and make JSONL data reliable for replay and analysis.

## Scope
- Implement strict Pydantic models:
  - `StateV1` (`state_v1`)
  - `ActionV1` (`action_v1`)
  - `AnomalyV1` (`anomaly_v1`)
  - `SensorHealthV1` (`sensor_health_v1`)
- Require `schema_version` field in each model
- Require ISO8601 timestamp field(s) with timezone awareness
- Enforce strict typing (no implicit coercion where unsafe)
- Support JSON Schema export for each model
- Add model-level docs/comments for field intent

## Non-goals
- Implementing storage, replay, scheduling, or estimator algorithms
- Designing version migration tooling beyond `schema_version` presence
- Supporting multiple schema versions in runtime logic

## Acceptance Criteria
- [ ] All four models are implemented with strict validation
- [ ] `schema_version` is mandatory and validated
- [ ] Timestamp fields validate ISO8601 with timezone info
- [ ] Invalid payloads fail validation deterministically
- [ ] JSON Schema can be generated for all models
- [ ] Model serialization/deserialization roundtrip is stable

## Required Tests
- `tests/contracts/test_state_v1.py::test_valid_state_payload_passes`
- `tests/contracts/test_state_v1.py::test_missing_schema_version_fails`
- `tests/contracts/test_action_v1.py::test_invalid_timestamp_fails`
- `tests/contracts/test_anomaly_v1.py::test_strict_types_reject_coercion`
- `tests/contracts/test_sensor_health_v1.py::test_roundtrip_dump_and_validate`
- `tests/contracts/test_json_schema_export.py::test_all_contracts_export_json_schema`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- JSON Schema artifacts are reproducible from code
- Contracts are referenced as canonical interfaces in module docs

## Dependencies
- Issue 1 (repository bootstrap and tooling)

---

# Issue 3 — JSONL Storage Layer

## Title
**Implement production JSONL storage layer with atomic writes, rotation, and dataset management**

## Context / Why
The MVP requires disk-backed, inspectable, replayable storage without databases. A robust JSONL layer must guarantee data integrity, predictable file layout, and operational safety for long-running simulations.

## Scope
- Implement append-capable JSONL writer with atomic write strategy
- Configurable `flush` and `fsync` behavior
- File rotation by:
  - day boundary
  - max size threshold
- Dataset manager with `run_YYYYMMDD` naming and directory lifecycle
- Public subset export (filtered/whitelisted fields and records)
- Clear storage module API for state/anomaly/action records

## Non-goals
- Introducing any SQL/NoSQL database
- Building remote storage backends (S3, GCS, etc.)
- Building analytics/query engine

## Acceptance Criteria
- [ ] JSONL append writes are atomic from caller perspective
- [ ] Flush and fsync behavior is configurable and tested
- [ ] Rotation works by day and by file size
- [ ] Dataset manager creates and resolves `run_YYYYMMDD` directories
- [ ] Public subset export creates sanitized JSONL output
- [ ] Storage API handles malformed input gracefully via explicit errors

## Required Tests
- `tests/storage/test_jsonl_writer.py::test_atomic_append_writes_valid_lines`
- `tests/storage/test_jsonl_writer.py::test_flush_and_fsync_modes`
- `tests/storage/test_rotation.py::test_rotate_on_day_change`
- `tests/storage/test_rotation.py::test_rotate_on_max_size`
- `tests/storage/test_dataset_manager.py::test_create_run_directory_naming`
- `tests/storage/test_export_public_subset.py::test_export_filters_private_fields`
- `tests/storage/test_error_handling.py::test_rejects_non_serializable_record`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- Manual inspection confirms JSONL readability and line-delimited validity
- Storage behavior is documented (config knobs + file layout)

## Dependencies
- Issue 1 (tooling)
- Issue 2 (contracts for stored records)

---

# Issue 4 — Synthetic and Replay Data Sources

## Title
**Implement unified observation source interface with synthetic and replay backends**

## Context / Why
A shared source interface enables the same estimator pipeline to run against generated data and historical logs. This is essential for deterministic testing, development without hardware, and reproducible experiments.

## Scope
- Define source interface:
  - `next_observation() -> Observation | None`
- Implement `synthetic_source` with:
  - noise
  - diurnal cycle
  - scenario injection hooks
- Implement `replay_source` reading observations from JSONL
- Ensure both implementations obey same observation contract and iteration semantics
- Add seed-based determinism support for synthetic source

## Non-goals
- Real hardware adapters
- Streaming/message-broker ingestion
- Complex scenario DSL beyond simple configurable scenarios

## Acceptance Criteria
- [ ] Unified source interface is documented and enforced
- [ ] Synthetic source emits realistic observation streams with configurable parameters
- [ ] Replay source consumes JSONL and yields ordered observations
- [ ] Both sources return `None` at end-of-stream
- [ ] Synthetic source is deterministic with fixed seed
- [ ] Replay source handles malformed lines with explicit strategy (fail-fast or skip+log)

## Required Tests
- `tests/sources/test_interface.py::test_sources_implement_next_observation_contract`
- `tests/sources/test_synthetic_source.py::test_seeded_generation_is_deterministic`
- `tests/sources/test_synthetic_source.py::test_diurnal_cycle_affects_output`
- `tests/sources/test_synthetic_source.py::test_scenario_injection_changes_signal`
- `tests/sources/test_replay_source.py::test_reads_jsonl_in_order`
- `tests/sources/test_replay_source.py::test_returns_none_after_eof`
- `tests/sources/test_replay_source.py::test_malformed_line_policy`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- Source modules are typed and lint-clean
- Interface is used by at least one consumer in codebase

## Dependencies
- Issue 1 (tooling and package layout)
- Issue 2 (observation/state contract types)
- Issue 3 (JSONL format alignment for replay)

---

# Issue 5 — State Estimator Core

## Title
**Build estimator core pipeline (Observation -> StateV1 + anomalies + sensor health)**

## Context / Why
The estimator is the core “brain” behavior in MVP: transforming raw observations into operational state, anomaly events, and sensor diagnostics. This enables downstream logging and simulation validation.

## Scope
- Implement VPD calculation utility (with documented units/assumptions)
- Implement ring buffer for recent observation/state context
- Implement confidence scoring logic
- Implement anomaly detection logic (threshold/rule-based MVP)
- Implement estimator pipeline returning:
  - `StateV1`
  - list of `AnomalyV1`
  - `SensorHealthV1`
- Ensure deterministic behavior for identical input sequences

## Non-goals
- ML training/inference pipelines
- Advanced probabilistic filtering (Kalman/particle filters)
- Adaptive self-learning logic

## Acceptance Criteria
- [ ] VPD calculation is implemented and validated against reference cases
- [ ] Ring buffer provides bounded memory behavior
- [ ] Confidence score is produced for each estimated state
- [ ] Anomaly detector emits structured `AnomalyV1` events
- [ ] Pipeline output conforms to contracts and handles edge cases
- [ ] Pipeline is deterministic for fixed input sequence

## Required Tests
- `tests/estimator/test_vpd.py::test_vpd_matches_reference_values`
- `tests/estimator/test_ring_buffer.py::test_ring_buffer_overwrites_oldest`
- `tests/estimator/test_confidence.py::test_confidence_with_missing_sensors_decreases`
- `tests/estimator/test_anomaly_detector.py::test_threshold_breach_emits_anomaly`
- `tests/estimator/test_pipeline.py::test_pipeline_returns_state_anomalies_sensor_health`
- `tests/estimator/test_pipeline.py::test_pipeline_is_deterministic_for_same_inputs`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- Public estimator API is documented
- No contract validation errors in nominal test scenarios

## Dependencies
- Issue 2 (contracts)
- Issue 4 (observation source compatibility)

---

# Issue 6 — Virtual Clock and Scheduler

## Title
**Implement virtual clock abstraction and scheduler with simulation time scaling**

## Context / Why
To run fast, deterministic simulations independent of wall-clock speed, the system needs a pluggable clock and scheduler. This is required for accelerated 24h runs and reproducible integration tests.

## Scope
- Implement clock abstraction
  - `RealClock`
  - `SimClock(scale)`
- Implement event loop / scheduler driven by clock abstraction
- Support configurable time acceleration (`time_scale`)
- Support a logical 2-hour cycle as configurable scheduler workload
- Provide deterministic tick progression in `SimClock`

## Non-goals
- Async distributed scheduler
- Cron-like DSL
- Real-time OS integration

## Acceptance Criteria
- [ ] `Clock` abstraction is implemented and documented
- [ ] `RealClock` and `SimClock` conform to same interface
- [ ] Scheduler executes periodic tasks using injected clock
- [ ] `SimClock(scale)` accelerates logical time relative to wall time
- [ ] 2-hour logical cycle runs correctly at different `time_scale` values
- [ ] Scheduler shutdown/termination is graceful

## Required Tests
- `tests/clock/test_sim_clock.py::test_sim_clock_advances_by_scale`
- `tests/clock/test_real_clock.py::test_real_clock_monotonicity`
- `tests/scheduler/test_event_loop.py::test_periodic_task_execution_order`
- `tests/scheduler/test_event_loop.py::test_two_hour_logical_cycle_completion`
- `tests/scheduler/test_event_loop.py::test_graceful_shutdown`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- Scheduler API is typed and documented
- Time-scale behavior is verified in both unit and integration-level checks

## Dependencies
- Issue 1 (project skeleton)

---

# Issue 7 — End-to-End Simulation Script

## Title
**Create `scripts/simulate_day.py` for 24h accelerated simulation and log generation**

## Context / Why
A single runnable script is needed for developers and CI to execute the MVP flow end-to-end: source -> estimator -> storage over a simulated day.

## Scope
- Add `scripts/simulate_day.py`
- Wire together:
  - observation source
  - estimator pipeline
  - storage output
  - virtual clock/scheduler
- Support 24-hour logical simulation run
- Configurable `time_scale`
- Persist `state` and `anomaly` logs to JSONL dataset
- Provide CLI arguments for output directory, seed, and scale

## Non-goals
- Web API/UI
- Hardware execution mode
- Complex scenario orchestration beyond simple flags

## Acceptance Criteria
- [ ] Script runs a full 24h logical simulation successfully
- [ ] `time_scale` parameter changes runtime speed without changing logical outcomes
- [ ] State and anomaly logs are written in expected JSONL locations
- [ ] Script exits with non-zero code on unrecoverable runtime errors
- [ ] CLI `--help` documents all parameters

## Required Tests
- `tests/scripts/test_simulate_day_cli.py::test_help_contains_required_arguments`
- `tests/scripts/test_simulate_day_run.py::test_generates_state_and_anomaly_logs`
- `tests/scripts/test_simulate_day_run.py::test_time_scale_does_not_change_logical_count`
- `tests/scripts/test_simulate_day_run.py::test_fixed_seed_produces_reproducible_outputs`

## Definition of Done
- All acceptance criteria are met
- Required tests are implemented and passing
- Script is documented in README with example command
- Output artifacts are compatible with replay source

## Dependencies
- Issue 3 (storage)
- Issue 4 (sources)
- Issue 5 (estimator)
- Issue 6 (clock/scheduler)

---

# Issue 8 — Integration Test: 24h Deterministic Run

## Title
**Add integration test for deterministic 24h simulation using SimClock**

## Context / Why
This test is the MVP quality gate proving the system can run a full-day simulation quickly, safely, and deterministically, while producing schema-valid outputs.

## Scope
- Implement integration test that runs 24h logical simulation using `SimClock`
- Validate:
  - expected number of state records
  - no unhandled exceptions
  - output schema validity
  - deterministic output for fixed seed
- Verify artifacts produced by simulation script/pipeline in temporary directory

## Non-goals
- Performance benchmarking across machines
- Multi-day soak testing
- Fault-injection matrix beyond core deterministic scenario

## Acceptance Criteria
- [ ] Integration test executes a 24h logical run via `SimClock`
- [ ] Record count assertions match configured cadence
- [ ] All output records validate against Pydantic contracts
- [ ] Two runs with same seed are byte-equivalent (or semantically equivalent if ordering metadata differs)
- [ ] Test fails clearly on any unhandled exception during simulation

## Required Tests
- `tests/integration/test_24h_deterministic_run.py::test_24h_simclock_run_produces_expected_state_count`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_has_no_unhandled_exceptions`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_outputs_validate_against_contracts`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_is_deterministic_with_fixed_seed`

## Definition of Done
- All acceptance criteria are met
- Required integration tests are implemented and passing in local test run
- Test runtime is practical for developer workflow (fast via simulation scale)
- This test is documented as MVP release gate

## Dependencies
- Issue 2 (contracts)
- Issue 6 (SimClock)
- Issue 7 (simulation script)
