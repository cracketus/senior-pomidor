# MVP GitHub Issues: Stage 1 Complete Specification

This document contains all 8 core issues + 2 new contract specification issues, with all 10 gaps identified in the Stage 1 Readiness Plan fully integrated.

---

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

# Issue 2 — Contracts: Core Pydantic Models (State, Action, Anomaly, Sensor Health)

## Title
**Define strict Pydantic v2 contracts for core messaging: state/action/anomaly/sensor health (v1 schemas)**

## Context / Why
Typed contracts are the source of truth for all pipeline boundaries and persisted records. Strong validation and schema generation reduce integration bugs and make JSONL data reliable for replay and analysis.

## Scope
- Implement 4 strict Pydantic v2 models:
  - `StateV1`: Estimated plant state with confidence scores
  - `ActionV1`: Control decisions and their justification
  - `AnomalyV1`: Detected anomalies with severity
  - `SensorHealthV1`: Per-sensor diagnostics and fault detection

### StateV1 Required Fields
```python
schema_version: str = "state_v1"
ts: datetime  # ISO8601 with timezone
env: dict  # {air_temp_c, rh_pct, co2_ppm, vpd_kpa}
plant: dict  # {leaf_temp_c, leaf_air_delta_c, vision (optional)}
soil: dict  # {temp_c, probes: [{id, moisture_pct, confidence}], avg_moisture_pct, zone_pattern}
devices: dict  # {light, circulation_fan, exhaust_fan, humidifier, heater_mat, water_pump, co2_solenoid, mcu_connected, last_reset_ts}
budgets: dict  # {water_ml_used_today, water_ml_budget_today, co2_seconds_used_today, co2_seconds_budget_today}
confidence: float  # 0.0-1.0 overall state confidence (see Issue 2a for algorithm)
```

### ActionV1 Required Fields
```python
schema_version: str = "action_v1"
ts: datetime  # ISO8601 with timezone
type: str  # WATER | CO2 | LIGHT | FAN | HEATER
params: dict  # Action-specific parameters (ml, pulses, seconds, on/off, etc.)
why: dict  # {rules_fired: list, objective_hint: str}
safety: dict  # {validated: bool, guardrails: list}
```

### AnomalyV1 Required Fields
```python
schema_version: str = "anomaly_v1"
ts: datetime  # ISO8601 with timezone
severity: str  # INFO | WARN | HIGH | CRITICAL
type: str  # SOIL_STRESS | VPD_OUT_OF_RANGE | SENSOR_FAULT | EQUIPMENT_MALFUNCTION | etc.
signals: dict  # Sensor readings that triggered anomaly
expected_effects: list  # Predicted consequences
required_response: list  # Suggested actions
```

### SensorHealthV1 Required Fields (NEW SPECIFICATION)
```python
schema_version: str = "sensor_health_v1"
ts: datetime  # ISO8601 with timezone
sensors: dict  # {sensor_id: {
  #   fault_type: "none" | "stuck_at" | "jump" | "drift" | "disconnect",
  #   confidence_delta: float,  # How much confidence dropped (0.0-1.0)
  #   last_valid_reading_ts: datetime,
  #   anomaly_count_24h: int,
  #   diagnostics: str  # Human-readable note
  # }}
overall_health: str  # "healthy" | "degraded" | "failing"
```

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

# Issue 2a — Observation & Device Status Contracts (NEW)

## Title
**Define Observation and DeviceStatus Pydantic contracts for sensor/device input streams**

## Context / Why
Sources (synthetic and replay) emit Observation records; device telemetry comes via DeviceStatus. Without explicit contracts, sources and estimators have no clear interface. This issue codifies the input layer contracts.

## Scope
- Implement `ObservationV1`: Raw sensor readings and metadata
- Implement `DeviceStatusV1`: Device ON/OFF states and telemetry
- Both must be used by Issue 4 (Sources) and Issue 5 (Estimator)

### ObservationV1 Required Fields (NEW SPECIFICATION)
```python
schema_version: str = "observation_v1"
ts: datetime  # ISO8601 with timezone
sensors: dict  # Raw sensor readings: {
  #   "air_temp_c": float,
  #   "rh_pct": float,
  #   "co2_ppm": float,
  #   "soil_temp_c": float,
  #   "probe_P1_moisture_pct": float,
  #   "probe_P2_moisture_pct": float,
  #   "light_intensity_lux": float,
  # }
device_status: DeviceStatusV1  # See below
```

### DeviceStatusV1 Required Fields (NEW SPECIFICATION)
```python
schema_version: str = "device_status_v1"
ts: datetime  # ISO8601 with timezone
mcu_connected: bool
light_on: bool
circulation_fan_on: bool
exhaust_fan_on: bool
humidifier_on: bool
heater_mat_on: bool
water_pump_on: bool
co2_solenoid_on: bool
last_reset_ts: Optional[datetime]
uptime_seconds: int
```

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

# Issue 2b — Confidence Scoring & Anomaly Threshold Specifications (NEW)

## Title
**Document confidence scoring algorithm and anomaly detection thresholds for reference implementation**

## Context / Why
Issue 5 (State Estimator) requires a "confidence score" and "threshold-based anomaly detection," but the spec is vague. This technical specification issue codifies the algorithms to enable deterministic, testable implementations.

## Scope
- Create `docs/confidence_scoring.md` with algorithm and examples
- Create `docs/anomaly_thresholds.md` with all threshold rules
- Create `tests/fixtures/vpd_reference_cases.py` with 5-10 reference cases
- Create `tests/fixtures/anomaly_test_scenarios.py` with test scenarios

### Confidence Scoring Algorithm Specification

**Base confidence**: 1.0

**Deductions (cumulative, min 0.0)**:
- -0.1 per sensor reading older than 48 hours
- -0.2 if reading is at sensor range extreme (0% or 100% for moisture)
- -0.15 if rate of change exceeds expected variance (e.g., > 10% moisture in 30 min)
- -0.3 if cross-sensor disagreement detected (e.g., P1 and P2 diverge > 40%)
- -0.5 if sensor appears stuck (same value in 3+ consecutive readings)
- -0.25 if reading triggers anomaly threshold (see threshold spec below)
- -0.1 per missing sensor reading

**Example**:
- Reading 30 hours old: no deduction (< 48h)
- Reading 70 hours old: -0.1 confidence
- Reading at 100% moisture + stale + triggers anomaly: -0.2 - 0.25 = -0.45, final: 0.55

### Anomaly Detection Threshold Rules Specification

**Soil Moisture Thresholds**:
- P1 < 10%: CRITICAL water stress
- P1 < 15%: HIGH water stress
- P2 > 85%: HIGH waterlogging risk
- P1/P2 differential > 40%: WARN zone pattern anomaly
- Moisture drop > 5% in 30 min: HIGH rapid dry-down (pump leak?)

**VPD Thresholds**:
- VPD > 3.5 kPa: HIGH transpiration stress
- VPD < 0.2 kPa: HIGH condensation/disease risk

**Temperature Thresholds**:
- Air temp > 32°C: HIGH overheating
- Air temp < 8°C: HIGH chilling stress
- Temperature rise > 3°C in 10 minutes: HIGH equipment malfunction
- Soil temp < 16°C: WARN cold stress

**Sensor Fault Detection Rules**:
- Stuck-at (same value > 3 readings): WARN sensor fault
- Jump (> 20% change in 1 reading): WARN sensor malfunction
- Drift (steady 2-3% change per hour): WARN calibration drift
- Disconnect (no reading > 1 hour): HIGH sensor disconnect

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

# Issue 4 — Synthetic and Replay Data Sources

## Title
**Implement unified observation source interface with synthetic and replay backends**

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

# Issue 5 — State Estimator Core (Comprehensive)

## Title
**Build estimator core pipeline: Observation -> StateV1 + AnomalyV1[] + SensorHealthV1**

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

### VPD Algorithm Specification (Reference-Validated)

**Formula** (Magnus approximation):
```
es(T) = 6.112 * exp((17.67 * T) / (T + 243.5))  # Saturation vapor pressure (hPa)
ea(T, RH) = (RH / 100) * es(T)  # Actual vapor pressure (hPa)
VPD(kPa) = (es(T) - ea(T, RH)) / 10  # Convert hPa to kPa
```

**Reference Test Cases**:
```python
[
    {"temp_c": 20, "rh_pct": 50, "expected_vpd_kpa": 1.01},
    {"temp_c": 25, "rh_pct": 60, "expected_vpd_kpa": 1.27},
    {"temp_c": 30, "rh_pct": 40, "expected_vpd_kpa": 2.48},
    {"temp_c": 15, "rh_pct": 80, "expected_vpd_kpa": 0.30},
    {"temp_c": 28, "rh_pct": 70, "expected_vpd_kpa": 0.82},
]
```

### Ring Buffer API Specification

```python
class RingBuffer:
    def add(self, state: StateV1) -> None:
        """Append state, auto-rotate oldest if > 48h old"""
    
    def get_last_n_hours(self, n: int) -> List[StateV1]:
        """Return all states from last n hours"""
    
    def get_since(self, ts: datetime) -> List[StateV1]:
        """Return all states since timestamp"""
    
    def get_stats(self, metric: str, window_hours: int = 24) -> dict:
        """Return min/max/mean/std for metric (e.g. 'soil_moisture_avg') in window"""
```

### Confidence Scoring Algorithm (Issue 2b)
- Implemented per specs in `docs/confidence_scoring.md`
- Ranges 0.0 to 1.0
- Reflects sensor age, range, variance, cross-sensor agreement

### Anomaly Detection Thresholds (Issue 2b)
- All thresholds implemented per `docs/anomaly_thresholds.md`
- Soil moisture, VPD, temperature, rate-of-change thresholds
- Severity levels: INFO, WARN, HIGH, CRITICAL

### Sensor Health Diagnostics
- Fault detection: stuck-at, jump, drift, disconnect
- Per-sensor confidence delta tracking
- Last valid reading timestamp
- 24-hour anomaly count

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

# Issue 6 — Virtual Clock and Scheduler

## Title
**Implement virtual clock abstraction and scheduler with simulation time scaling**

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

# Issue 7 — End-to-End Simulation Script with Clear Orchestration

## Title
**Create `scripts/simulate_day.py` for 24h accelerated simulation and log generation**

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

### Main Loop Specification
```
For each 2-hour cycle:
  1. Fetch next observation from source
  2. Estimate state: estimator.estimate(obs) → StateV1, AnomalyV1[], SensorHealthV1
  3. Store records: storage.write(state), storage.write(anomalies), storage.write(health)
  4. If anomalies triggered: enter event-driven mode (5-15 min cycles until stabilized)
  5. Advance clock by 2 hours
  6. Repeat until end-of-stream or duration reached
```

### CLI Arguments Specification (NEW)

```bash
python scripts/simulate_day.py \
  --time-scale 120 \           # Default: 120 (1 wall-sec = 120 logical secs)
  --seed 42 \                  # Default: random
  --output-dir ./data/runs \   # Default: ./data/runs
  --duration-hours 24 \        # Default: 24
  --scenario default \         # Default: default (others: high-wind, sensor-fault, etc.)
  --verbose false              # Default: false
```

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

# Issue 8 — Integration Test: 24h Deterministic Run Quality Gate

## Title
**Add integration test for deterministic 24h simulation using SimClock (MVP Quality Gate)**

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

## Summary: Issues 1-8 + New Issues 2a-2b

### Mapping of Issues to Gaps

| Issue | Gaps Addressed |
|-------|---|
| Issue 1 | Repository setup |
| Issue 2 | (Core contracts) → Gaps 2, 3 (SensorHealthV1) |
| Issue 2a (NEW) | Gaps 1, 6 (Observation, DeviceStatus contracts) |
| Issue 2b (NEW) | Gaps 3, 4, 7 (Anomaly thresholds, confidence algorithm, VPD) |
| Issue 3 | Gap 10 (Error handling) |
| Issue 4 | Gap 10 (Error handling for malformed observations) |
| Issue 5 | Gaps 5, 7, 8 (Ring buffer API, VPD algorithm, orchestrator skeleton) |
| Issue 6 | Virtual clock/scheduler |
| Issue 7 | Gaps 8, 9 (Orchestrator integration, CLI specification) |
| Issue 8 | Integration testing |

All 10 gaps are now addressed across issues 1-8 + new issues 2a-2b.

