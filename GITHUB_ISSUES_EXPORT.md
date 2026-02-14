# GitHub Issues Export - Stage 1 Complete Specification

This file contains all 10 Stage 1 issues formatted for manual GitHub creation.

## How to Use

1. For each issue below, click **New Issue** on GitHub
2. Copy the **Title** text
3. Paste into GitHub's Title field
4. Copy the **Body** text
5. Paste into GitHub's Body/Description field
6. Add labels: `stage-1`, `issue-N` (e.g., `issue-1`)
7. Click **Submit new issue**

---

## Issue 1: TOMATO-1: Repository Bootstrap (Production Skeleton)

### GitHub UI - Title Field
```
TOMATO-1: Repository Bootstrap (Production Skeleton)
```

### GitHub UI - Body Field
```markdown
## Context / Why

We need a stable, reproducible baseline before implementing domain logic. A production-ready skeleton ensures consistent tooling, testing, linting, and packaging from day one, reducing rework and integration risk.

## Scope

- Configure Python 3.11 project metadata and dependencies in `pyproject.toml`
- Add and configure:
  - `pytest`
  - `pytest-cov` (coverage reporting)
  - `ruff`
- Create minimal package structure under `brain/`
- Create `docs/` directory for technical specifications
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
- [ ] `docs/` directory created (for technical specifications)
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

```

### Labels to Add
- `stage-1`
- `issue-1`

---

## Issue 2: TOMATO-2: Contracts: Core Pydantic Models (State, Action, Anomaly, Sensor Health)

### GitHub UI - Title Field
```
TOMATO-2: Contracts: Core Pydantic Models (State, Action, Anomaly, Sensor Health)
```

### GitHub UI - Body Field
```markdown
## Context / Why

Typed contracts are the source of truth for all pipeline boundaries and persisted records. Strong validation and schema generation reduce integration bugs and make JSONL data reliable for replay and analysis.

## Scope

- Implement 4 strict Pydantic v2 models:
  - `StateV1`: Estimated plant state with confidence scores
  - `ActionV1`: Control decisions and their justification
  - `AnomalyV1`: Detected anomalies with severity
  - `SensorHealthV1`: Per-sensor diagnostics and fault detection

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
- [ ] All fields documented with type hints and docstrings
- [ ] StateV1 confidence field matches algorithm in Issue 2a

## Required Tests

- `tests/contracts/test_state_v1.py::test_valid_state_payload_passes`
- `tests/contracts/test_state_v1.py::test_missing_schema_version_fails`
- `tests/contracts/test_state_v1.py::test_confidence_field_is_float_0_to_1`
- `tests/contracts/test_action_v1.py::test_invalid_timestamp_fails`
- `tests/contracts/test_action_v1.py::test_action_types_are_valid_enum`
- `tests/contracts/test_anomaly_v1.py::test_strict_types_reject_coercion`
- `tests/contracts/test_anomaly_v1.py::test_severity_levels_are_valid`
- `tests/contracts/test_sensor_health_v1.py::test_fault_types_are_valid_enum`
- `tests/contracts/test_sensor_health_v1.py::test_roundtrip_dump_and_validate`
- `tests/contracts/test_json_schema_export.py::test_all_contracts_export_json_schema`

## Definition of Done

- All acceptance criteria are met
- Required tests are implemented and passing
- JSON Schema artifacts are reproducible from code
- Contracts are referenced as canonical interfaces in module docs
- Example payloads provided in docstrings

## Dependencies

- Issue 1 (repository bootstrap and tooling)

---

```

### Labels to Add
- `stage-1`
- `issue-2`

---

## Issue 2a: TOMATO-2a: Observation & Device Status Contracts (NEW)

### GitHub UI - Title Field
```
TOMATO-2a: Observation & Device Status Contracts (NEW)
```

### GitHub UI - Body Field
```markdown
## Context / Why

Sources (synthetic and replay) emit Observation records; device telemetry comes via DeviceStatus. Without explicit contracts, sources and estimators have no clear interface. This issue codifies the input layer contracts.

## Scope

- Implement `ObservationV1`: Raw sensor readings and metadata
- Implement `DeviceStatusV1`: Device ON/OFF states and telemetry
- Both must be used by Issue 4 (Sources) and Issue 5 (Estimator)

## Acceptance Criteria

- [ ] `ObservationV1` model defined with all required sensor fields
- [ ] `DeviceStatusV1` model defined with all device states
- [ ] Timestamp validation works for both
- [ ] Strict validation rejects missing sensors
- [ ] Both models have JSON Schema export
- [ ] ObservationV1 used by Issue 4 (Sources)
- [ ] DeviceStatusV1 integrated into StateV1 (Issue 2)

## Required Tests

- `tests/contracts/test_observation_v1.py::test_valid_observation_passes`
- `tests/contracts/test_observation_v1.py::test_missing_sensor_fails`
- `tests/contracts/test_device_status_v1.py::test_valid_device_status_passes`
- `tests/contracts/test_device_status_v1.py::test_timestamp_validation_works`

## Definition of Done

- Both contracts are stable and tested
- No changes to existing StateV1/ActionV1 (Issue 2)
- Sources use ObservationV1 (Issue 4)
- Estimator consumes ObservationV1 + DeviceStatusV1 (Issue 5)

## Dependencies

- Issue 1 (tooling)
- Issue 2 (core contracts already defined)

---

```

### Labels to Add
- `stage-1`
- `issue-2a`
- `new-issue`

---

## Issue 2b: TOMATO-2b: Confidence Scoring & Anomaly Threshold Specifications (NEW)

### GitHub UI - Title Field
```
TOMATO-2b: Confidence Scoring & Anomaly Threshold Specifications (NEW)
```

### GitHub UI - Body Field
```markdown
## Context / Why

Issue 5 (State Estimator) requires a "confidence score" and "threshold-based anomaly detection," but the spec is vague. This technical specification issue codifies the algorithms to enable deterministic, testable implementations.

## Scope

- Create `docs/confidence_scoring.md` with algorithm and examples
- Create `docs/anomaly_thresholds.md` with all threshold rules
- Create `tests/fixtures/vpd_reference_cases.py` with 5-10 reference cases
- Create `tests/fixtures/anomaly_test_scenarios.py` with test scenarios

## Acceptance Criteria

- [ ] `docs/confidence_scoring.md` specifies algorithm with 3+ examples
- [ ] `docs/anomaly_thresholds.md` lists all thresholds with severity levels
- [ ] Reference test cases provided in `tests/fixtures/vpd_reference_cases.py`
- [ ] Anomaly scenarios provided in `tests/fixtures/anomaly_test_scenarios.py`
- [ ] Issue 5 (Estimator) references these specs in code

## Required Tests

- `tests/test_specs.py::test_confidence_scoring_docs_exist_and_are_readable`
- `tests/test_specs.py::test_anomaly_threshold_docs_exist_and_are_readable`
- `tests/fixtures/test_vpd_reference_cases.py::test_all_reference_cases_are_valid`

## Definition of Done

- All specifications documented and reviewed
- Specs referenced in Issue 5 (State Estimator)
- No gaps between spec and implementation

## Dependencies

- Issue 2 (core contracts)
- Issue 5 (State Estimator implementation uses these specs)

---

```

### Labels to Add
- `stage-1`
- `issue-2b`
- `new-issue`

---

## Issue 3: TOMATO-3: JSONL Storage Layer

### GitHub UI - Title Field
```
TOMATO-3: JSONL Storage Layer
```

### GitHub UI - Body Field
```markdown
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
- **NEW**: Error handling strategy for malformed inputs (see Issue 2b)

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
- [ ] Storage API handles malformed input gracefully (logs error, skips record or raises exception per policy)
- [ ] Storage logs errors for non-serializable records

## Required Tests

- `tests/storage/test_jsonl_writer.py::test_atomic_append_writes_valid_lines`
- `tests/storage/test_jsonl_writer.py::test_flush_and_fsync_modes`
- `tests/storage/test_rotation.py::test_rotate_on_day_change`
- `tests/storage/test_rotation.py::test_rotate_on_max_size`
- `tests/storage/test_dataset_manager.py::test_create_run_directory_naming`
- `tests/storage/test_export_public_subset.py::test_export_filters_private_fields`
- `tests/storage/test_error_handling.py::test_rejects_non_serializable_record`
- `tests/storage/test_error_handling.py::test_malformed_observation_handling` (NEW)

## Definition of Done

- All acceptance criteria are met
- Required tests are implemented and passing
- Manual inspection confirms JSONL readability and line-delimited validity
- Storage behavior is documented (config knobs + file layout)

## Dependencies

- Issue 1 (tooling)
- Issue 2 (contracts for stored records)

---

```

### Labels to Add
- `stage-1`
- `issue-3`

---

## Issue 4: TOMATO-4: Synthetic and Replay Data Sources

### GitHub UI - Title Field
```
TOMATO-4: Synthetic and Replay Data Sources
```

### GitHub UI - Body Field
```markdown
## Context / Why

A shared source interface enables the same estimator pipeline to run against generated data and historical logs. This is essential for deterministic testing, development without hardware, and reproducible experiments.

## Scope

- Define source interface: `next_observation() -> ObservationV1 | None` **(uses Issue 2a contract)**
- Implement `SyntheticSource` with:
  - noise modeling
  - diurnal cycle
  - scenario injection hooks
  - seed-based determinism
- Implement `ReplaySource` reading observations from JSONL
- Ensure both implementations obey same observation contract and iteration semantics
- **NEW**: Error handling for malformed observations (skip + log or fail-fast per policy)

## Non-goals

- Real hardware adapters
- Streaming/message-broker ingestion
- Complex scenario DSL beyond simple configurable scenarios

## Acceptance Criteria

- [ ] Unified source interface is documented and enforced
- [ ] Synthetic source emits realistic observation streams (ObservationV1 contract)
- [ ] Replay source consumes JSONL and yields ordered observations
- [ ] Both sources return `None` at end-of-stream
- [ ] Synthetic source is deterministic with fixed seed
- [ ] Replay source handles malformed lines with explicit strategy (skip + log or fail-fast)
- [ ] Both sources produce DeviceStatusV1 objects (Issue 2a contract)

## Required Tests

- `tests/sources/test_interface.py::test_sources_implement_next_observation_contract`
- `tests/sources/test_synthetic_source.py::test_seeded_generation_is_deterministic`
- `tests/sources/test_synthetic_source.py::test_diurnal_cycle_affects_output`
- `tests/sources/test_synthetic_source.py::test_scenario_injection_changes_signal`
- `tests/sources/test_synthetic_source.py::test_observations_match_observation_v1_schema`
- `tests/sources/test_replay_source.py::test_reads_jsonl_in_order`
- `tests/sources/test_replay_source.py::test_returns_none_after_eof`
- `tests/sources/test_replay_source.py::test_malformed_line_policy` (NEW)

## Definition of Done

- All acceptance criteria are met
- Required tests are implemented and passing
- Source modules are typed and lint-clean
- Interface is used by at least one consumer in codebase (Issue 5)

## Dependencies

- Issue 1 (tooling and package layout)
- Issue 2a (ObservationV1 + DeviceStatusV1 contracts)
- Issue 3 (JSONL format alignment for replay)

---

```

### Labels to Add
- `stage-1`
- `issue-4`

---

## Issue 5: TOMATO-5: State Estimator Core (Comprehensive)

### GitHub UI - Title Field
```
TOMATO-5: State Estimator Core (Comprehensive)
```

### GitHub UI - Body Field
```markdown
## Context / Why

The estimator is the core "brain" behavior in MVP: transforming raw observations into operational state, anomaly events, and sensor diagnostics. This enables downstream logging and simulation validation.

## Scope

- **Project**: Implement VPD calculation with reference-validated formula (Magnus approximation)
- **Implement**: Ring buffer for 48-hour state history with query API
- **Implement**: Confidence scoring logic per Issue 2b specifications
- **Implement**: Anomaly detection logic per Issue 2b threshold specifications
- **Implement**: Sensor health diagnostics with fault detection (stuck-at, jump, drift, disconnect)
- **Implement**: Estimator pipeline returning StateV1, list of AnomalyV1, and SensorHealthV1
- **Ensure**: Deterministic behavior for identical input sequences

## Non-goals

- ML training/inference pipelines
- Advanced probabilistic filtering (Kalman/particle filters)
- Adaptive self-learning logic

## Acceptance Criteria

- [ ] VPD calculation matches reference cases (all 5+ test cases pass)
- [ ] Ring buffer provides bounded memory behavior (48h capacity auto-rotates)
- [ ] Confidence score is produced for each estimated state (0.0-1.0)
- [ ] Confidence algorithm documented and matches Issue 2b spec
- [ ] Anomaly detector emits structured AnomalyV1 events
- [ ] Anomaly thresholds documented and match Issue 2b spec
- [ ] Pipeline output conforms to StateV1/AnomalyV1/SensorHealthV1 contracts
- [ ] Pipeline handles edge cases (missing sensors, stale data, disconnects)
- [ ] Pipeline is deterministic for fixed input sequence

## Required Tests

- `tests/estimator/test_vpd.py::test_vpd_matches_reference_values`
- `tests/estimator/test_vpd.py::test_vpd_handles_edge_cases` (NEW)
- `tests/estimator/test_ring_buffer.py::test_ring_buffer_overwrites_oldest`
- `tests/estimator/test_ring_buffer.py::test_get_last_n_hours` (NEW)
- `tests/estimator/test_ring_buffer.py::test_get_stats` (NEW)
- `tests/estimator/test_confidence.py::test_confidence_with_missing_sensors_decreases`
- `tests/estimator/test_confidence.py::test_confidence_algorithm_matches_spec` (NEW)
- `tests/estimator/test_anomaly_detector.py::test_threshold_breach_emits_anomaly`
- `tests/estimator/test_anomaly_detector.py::test_all_thresholds_specified_in_spec` (NEW)
- `tests/estimator/test_sensor_health.py::test_fault_detection_stuck_at` (NEW)
- `tests/estimator/test_sensor_health.py::test_fault_detection_jump` (NEW)
- `tests/estimator/test_sensor_health.py::test_fault_detection_drift` (NEW)
- `tests/estimator/test_pipeline.py::test_pipeline_returns_state_anomalies_sensor_health`
- `tests/estimator/test_pipeline.py::test_pipeline_is_deterministic_for_same_inputs`

## Definition of Done

- All acceptance criteria are met
- Required tests are implemented and passing
- Public estimator API is documented
- No contract validation errors in nominal test scenarios
- VPD reference cases all pass
- Anomaly and confidence algorithms match Issue 2b specs

## Dependencies

- Issue 2 (StateV1, AnomalyV1, SensorHealthV1 contracts)
- Issue 2a (ObservationV1, DeviceStatusV1 contracts)
- Issue 2b (confidence and anomaly threshold specs)
- Issue 4 (observation source compatibility)

---

```

### Labels to Add
- `stage-1`
- `issue-5`

---

## Issue 6: TOMATO-6: Virtual Clock and Scheduler

### GitHub UI - Title Field
```
TOMATO-6: Virtual Clock and Scheduler
```

### GitHub UI - Body Field
```markdown
## Context / Why

To run fast, deterministic simulations independent of wall-clock speed, the system needs a pluggable clock and scheduler. This is required for accelerated 24h runs and reproducible integration tests.

## Scope

- Implement clock abstraction with two implementations:
  - `RealClock`: Returns actual wall-clock time
  - `SimClock(time_scale)`: Returns logical time accelerated by scale factor
- Implement event loop / scheduler driven by clock abstraction
- Support configurable time acceleration (`time_scale` parameter)
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

```

### Labels to Add
- `stage-1`
- `issue-6`

---

## Issue 7: TOMATO-7: End-to-End Simulation Script with Clear Orchestration

### GitHub UI - Title Field
```
TOMATO-7: End-to-End Simulation Script with Clear Orchestration
```

### GitHub UI - Body Field
```markdown
## Context / Why

A single runnable script is needed for developers and CI to execute the MVP flow end-to-end: source -> estimator -> storage over a simulated day. Must clearly show how all components wire together.

## Scope

- Add `scripts/simulate_day.py` with clear orchestration
- Wire together:
  - observation source (Issue 4)
  - estimator pipeline (Issue 5)
  - storage output (Issue 3)
  - virtual clock/scheduler (Issue 6)
- Support 24-hour logical simulation run
- **NEW**: Configurable `time_scale` parameter (default: 120, so 24h runs in ~12 minutes wall time)
- **NEW**: Configurable CLI arguments (--seed, --output-dir, --duration-hours, --scenario, --verbose)
- Persist `state` and `anomaly` logs to JSONL dataset
- Document data flow: "Main loop (every 2 hours): obs → estimate → store → advance"

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
- [ ] Main loop documented in code with clear comment
- [ ] Data flow shown in README with example command
- [ ] All CLI arguments are typed and validated

## Required Tests

- `tests/scripts/test_simulate_day_cli.py::test_help_contains_required_arguments`
- `tests/scripts/test_simulate_day_cli.py::test_all_cli_arguments_are_valid` (NEW)
- `tests/scripts/test_simulate_day_run.py::test_generates_state_and_anomaly_logs`
- `tests/scripts/test_simulate_day_run.py::test_time_scale_does_not_change_logical_count`
- `tests/scripts/test_simulate_day_run.py::test_fixed_seed_produces_reproducible_outputs`

## Definition of Done

- All acceptance criteria are met
- Required tests are implemented and passing
- Script is documented in README with example command
- Output artifacts are compatible with replay source (Issue 4)
- Main loop commented and clear to new developers

## Dependencies

- Issue 3 (storage)
- Issue 4 (sources)
- Issue 5 (estimator)
- Issue 6 (clock/scheduler)

---

```

### Labels to Add
- `stage-1`
- `issue-7`

---

## Issue 8: TOMATO-8: Integration Test: 24h Deterministic Run Quality Gate

### GitHub UI - Title Field
```
TOMATO-8: Integration Test: 24h Deterministic Run Quality Gate
```

### GitHub UI - Body Field
```markdown
## Context / Why

This test is the MVP quality gate proving the system can run a full-day simulation quickly, safely, and deterministically, while producing schema-valid outputs.

## Scope

- Implement integration test that runs 24h logical simulation using `SimClock`
- Validate:
  - expected number of state records (12 base cycles + event-driven)
  - no unhandled exceptions
  - output schema validity (all records match contracts)
  - deterministic output for fixed seed
  - JSONL file format and readability
- Verify artifacts produced by simulation script/pipeline in temporary directory

## Non-goals

- Performance benchmarking across machines
- Multi-day soak testing
- Fault-injection matrix beyond core deterministic scenario

## Acceptance Criteria

- [ ] Integration test executes a 24h logical run via `SimClock`
- [ ] Record count assertions match configured cadence (≥12 base state records)
- [ ] All output records validate against Pydantic contracts
- [ ] Two runs with same seed are byte-equivalent (or semantically equivalent if ordering metadata differs)
- [ ] Test fails clearly on any unhandled exception during simulation
- [ ] JSONL files are line-delimited and parseable

## Required Tests

- `tests/integration/test_24h_deterministic_run.py::test_24h_simclock_run_produces_expected_state_count`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_has_no_unhandled_exceptions`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_outputs_validate_against_contracts`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_is_deterministic_with_fixed_seed`
- `tests/integration/test_24h_deterministic_run.py::test_24h_run_jsonl_files_are_readable`

## Definition of Done

- All acceptance criteria are met
- Required integration tests are implemented and passing in local test run
- Test runtime is practical for developer workflow (fast via simulation scale)
- This test is documented as MVP release gate
- Coverage is 90%+: `pytest --cov=brain --cov-threshold=90`

## Dependencies

- Issue 2 (contracts)
- Issue 6 (SimClock)
- Issue 7 (simulation script)

---

```

### Labels to Add
- `stage-1`
- `issue-8`

---
