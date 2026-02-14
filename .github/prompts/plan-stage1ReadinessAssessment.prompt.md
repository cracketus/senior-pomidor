# Plan: Stage 1 Readiness Assessment & Roadmap

**TL;DR**: The 8 issues form a **solid foundation** but have **critical gaps** in contract definitions, algorithm specifications, and cross-module integration details. With additions, Stage 1 is achievable in ~4-6 weeks at Excellence quality. The issues need clarification before implementation to avoid rework.

---

## Key Findings

### ✅ Strengths of Current Issues

- Clear separation of concerns with distinct, testable components
- Well-scoped acceptance criteria with specific test names
- Good dependency ordering (Issues 1→2→3/4→5/6→7→8)
- Emphasis on determinism and schema validation

### ⚠️ Critical Gaps Identified

1. **Missing: Observation Contract** — Issue 4 assumes an `Observation` type for sources, but Issue 2 doesn't define it. Sources need a clear contract for what they emit.

2. **Incomplete: Sensor Health Diagnostics** — Issue 2 mentions `SensorHealthV1` output but doesn't specify required fields (fault types, confidence per sensor, etc.).

3. **Vague: Anomaly Detection Algorithm** — Issue 5 requires threshold-based detection but doesn't:
   - Define thresholds (soil moisture, VPD range, rate-of-change bounds, etc.)
   - Specify how thresholds are determined or customized
   - Detail fault detection rules (stuck-at, jump, drift, disconnect)

4. **Vague: Confidence Scoring Logic** — Issue 5 mentions confidence (0..1) but doesn't:
   - Define the scoring formula or algorithm
   - List inputs (sensor history, variance, missing data, etc.)
   - Show example calculation

5. **Missing: Ring Buffer API** — Issue 5 requires a 48h buffer but doesn't specify:
   - Storage structure (in-memory vs. disk)
   - Time indexing mechanism
   - Query interface (`.get_last_n_hours()`, etc.)

6. **Missing: Device Status Contract** — State Estimator needs device telemetry input, but no contract is defined for device status observations.

7. **Incomplete: VPD Algorithm Specification** — Issue 5 requires reference-validated VPD but doesn't:
   - Provide the precise formula
   - Give reference test cases
   - Document unit assumptions (kPa, °C, %)

8. **Missing: Orchestrator Integration** — No issue explicitly wires the components together or shows data flow in `simulate_day.py`.

9. **Missing: CLI Specification for simulate_day.py** — Issue 7 requires CLI but doesn't list all required/optional arguments (--seed, --time-scale, --output-dir, etc.).

10. **Missing: Error Handling & Edge Cases** — Issues mention "graceful" error handling but don't specify failure modes or recovery strategies (malformed observations, sensor disconnects, timestamp discontinuities).

---

## Recommendations Before Implementation

| Gap | Action | Priority | Effort |
|-----|--------|----------|--------|
| Add Observation contract | Define in Issue 2 or create Issue 2.5 | HIGH | Small |
| Clarify sensor health fields | Define SensorHealthV1 structure explicitly | HIGH | Small |
| Specify anomaly thresholds | Create sub-issue or technical doc | HIGH | Medium |
| Define confidence algorithm | Create technical annex with examples | HIGH | Medium |
| Detail ring buffer API | Add to Issue 5 spec | MEDIUM | Small |
| Add device status contract | Define in Issue 2 | MEDIUM | Small |
| Provide VPD reference cases | Create test fixture file with 5-10 cases | HIGH | Small |
| Document orchestrator flow | Add diagram to AGENTS.md or new issue | MEDIUM | Small |
| Specify CLI arguments | Define in Issue 7 | MEDIUM | Small |
| Define error modes | Create error handling guide | MEDIUM | Medium |

---

## Stage 1 Implementation Roadmap (Excellence Quality, ~6 weeks)

### Phase 1: Foundation (Week 1-2)
- Issue 1: Repository Bootstrap
- Issue 2: Contracts (with added Observation + SensorHealthV1 detail)
- Create reference docs: VPD algorithm, anomaly thresholds, confidence scoring

### Phase 2: Data Flow (Week 2-3)
- Issue 4: Sources (Observation contract now finalized)
- Issue 3: JSONL Storage

### Phase 3: Core Logic (Week 3-4)
- Issue 5: State Estimator (with detailed VPD cases, threshold rules, confidence algorithm)
- Parallel: Issue 6: Clock & Scheduler

### Phase 4: Integration (Week 5)
- Issue 7: Simulation Script (integrate all components with clear orchestrator)
- Document data flow in code

### Phase 5: Quality Gate (Week 5-6)
- Issue 8: Integration Tests (24h deterministic run)
- Achieve 90%+ coverage
- Polish docs, examples, troubleshooting guide

---

## What's Still Missing for Stage 2 Readiness

Once Stage 1 is complete, you'll need:
- Actions contract finalized (Issue 2 has skeleton, needs detail)
- Mock action executor (for testing without hardware)
- 2-hour decision cycle scaffold (orchestrator hooks)
- Then Stage 2 (Control, Guardrails) becomes possible

---

## Detailed Gap Analysis

### Gap 1: Observation Contract

**Problem**: Issue 4 (Sources) defines a `next_observation() -> Observation | None` interface, but Pydantic model for `Observation` is never defined in Issue 2 (Contracts).

**Impact**: Sources can't be implemented without knowing what structure to emit. Integration tests can't validate observation format.

**Solution**:
- Create `brain/contracts/observation_v1.py`
- Required fields: `ts` (ISO8601), `sensors` (dict), `device_status` (dict)
- Example:
```python
class ObservationV1(BaseModel):
    schema_version: str = "observation_v1"
    ts: datetime  # ISO8601 with timezone
    sensors: dict  # {probe_id: moisture_pct, "air_temp_c": 24.3, ...}
    device_status: dict  # {"mcu_connected": bool, "light": "ON"/"OFF", ...}
```

### Gap 2: SensorHealthV1 Structure

**Problem**: Technical Specification mentions sensor health diagnostics but doesn't define fields.

**Needed fields**:
- `fault_type`: stuck_at | jump | drift | disconnect | none
- `confidence_delta`: How much confidence dropped due to fault
- `last_valid_reading_ts`: When sensor last reported valid value
- `anomaly_count_24h`: How many anomalies detected in last 24h

### Gap 3: Anomaly Detection Algorithm

**Problem**: Issue 5 says "threshold-based MVP" but doesn't specify thresholds or logic.

**Specification needed**:
```
Soil moisture:
- Alert if P1 < 10% (severe water stress)
- Alert if P2 > 85% (waterlogging)
- Alert if P1/P2 differential > 40% (extreme zone pattern)

VPD:
- Alert if > 3.5 kPa (excessive transpiration stress)
- Alert if < 0.2 kPa (condensation risk, disease pressure)

Temperature:
- Alert if air_temp > 32°C or < 8°C (outside growth range)

Rate of change:
- Alert if soil_moisture drops > 5% in 30 minutes (pump malfunction or leak)
- Alert if temperature rise > 3°C in 10 minutes (equipment malfunction)
```

### Gap 4: Confidence Scoring Algorithm

**Problem**: "Confidence (0..1) reflects uncertainty" is vague and untestable.

**Specification needed**:
```
Base confidence: 1.0

Deductions:
- -0.1 per sensor reading beyond 48h old
- -0.2 if reading is at sensor range extreme (0% or 100%)
- -0.15 if rate of change exceeds expected variance
- -0.3 if cross-sensor disagreement (P1 and P2 diverge sharply)
- -0.5 if sensor appears stuck (same value > 3 readings)
- -0.25 if reading is anomaly-class (threshold exceeded)

Min: 0.0, Max: 1.0
```

### Gap 5: Ring Buffer API

**Problem**: "48-hour ring buffer" is undefined — no storage, indexing, or query interface.

**Specification needed**:
```python
class RingBuffer:
    def add(self, state: StateV1) -> None:
        """Append state, auto-rotate oldest if > 48h old"""
    
    def get_last_n_hours(self, n: int) -> List[StateV1]:
        """Return all states from last n hours"""
    
    def get_since(self, ts: datetime) -> List[StateV1]:
        """Return all states since timestamp"""
    
    def get_stats(self, metric: str, window_hours: int) -> dict:
        """Return min/max/mean/std for metric in window"""
```

### Gap 6: Device Status Contract

**Problem**: State Estimator needs device telemetry, but no contract exists.

**Specification needed** (add to Issue 2):
```python
class DeviceStatusV1(BaseModel):
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

### Gap 7: VPD Algorithm with Reference Cases

**Problem**: VPD formula is not provided; can't validate implementation.

**Specification** (Magnus approximation):
```
es(T) = 6.112 * exp((17.67 * T) / (T + 243.5))  # Saturation vapor pressure (hPa)
ea(T, RH) = (RH / 100) * es(T)  # Actual vapor pressure
VPD(kPa) = (es(T) - ea(T, RH)) / 10  # Convert hPa to kPa

Example:
T = 25°C, RH = 60%
es(25) = 6.112 * exp((17.67 * 25) / (25 + 243.5)) = 31.825 hPa
ea(25, 60) = 0.6 * 31.825 = 19.095 hPa
VPD = (31.825 - 19.095) / 10 = 1.273 kPa ✓
```

**Reference test cases** (add to `tests/fixtures/vpd_reference_cases.py`):
```python
[
    {"temp_c": 20, "rh_pct": 50, "expected_vpd_kpa": 1.01},
    {"temp_c": 25, "rh_pct": 60, "expected_vpd_kpa": 1.27},
    {"temp_c": 30, "rh_pct": 40, "expected_vpd_kpa": 2.48},
    {"temp_c": 15, "rh_pct": 80, "expected_vpd_kpa": 0.30},
    {"temp_c": 28, "rh_pct": 70, "expected_vpd_kpa": 0.82},
]
```

### Gap 8: Orchestrator Integration

**Problem**: No explicit issue details how components wire together in `simulate_day.py`.

**Specification needed**:
```
Main loop (every 2 hours):
  1. obs = source.next_observation()
  2. state, anomalies, health = estimator.estimate(obs)
  3. storage.write(state, anomalies, health)
  4. if anomalies: trigger event-driven mode (5-15 min cycles)
  5. clock.advance(2 hours)
```

### Gap 9: CLI Arguments for simulate_day.py

**Problem**: Required arguments and defaults are undefined.

**Specification** (Issue 7 should add):
```
python scripts/simulate_day.py \
  --time-scale 120 \           # Default: 120 (24h in 12 min)
  --seed 42 \                  # Default: random
  --output-dir ./data/runs \   # Default: ./data/runs
  --duration-hours 24 \        # Default: 24
  --scenario default \         # Default: default (others: high-wind, sensor-fault, etc.)
  --verbose true               # Default: false
```

### Gap 10: Error Handling & Edge Cases

**Problem**: Issues mention "graceful" handling but don't specify failure modes.

**Specification needed** (new `docs/error_handling.md`):
```
Malformed observation → skip, log ERROR, continue
Sensor disconnect (3+ readings missing) → emit ANOMALY, drop confidence to 0.2
Timestamp discontinuity (>12h gap) → reset ring buffer, emit ANOMALY
Invalid JSON in replay log → log WARN, skip line, continue
Storage write failure → raise exception, exit with code 1
```

---

## Success Criteria for Stage 1

✅ All 8 issues implemented with high test coverage (90%+)  
✅ All 10 gaps resolved with clear specifications  
✅ `pytest --cov=brain` shows 90%+ line coverage  
✅ `scripts/simulate_day.py` runs successfully for 24h at time_scale=120  
✅ Output JSONL is valid, readable, and replays correctly  
✅ No warnings or errors in `ruff check` and `ruff format`  
✅ Code is documented with clear docstrings and examples  
✅ Integration test (`tests/integration/test_24h_deterministic_run.py`) passes  
✅ README updated with working examples and troubleshooting  
✅ Gateway: "Ready for Stage 2 (Control & Guardrails)"

---

## All Gaps Fixed: Updated Issues Mapping

All 10 gaps have been systematically incorporated into an updated MVP_GITHUB_ISSUES specification. Here's the mapping:

| Gap | Original Issue | Now Addressed In | Change |
|-----|---|---|---|
| 1. Observation Contract | Issue 4 | Issue 2a (NEW) | New contract created with full specification |
| 2. SensorHealthV1 Structure | Issue 2 | Issue 2 + Issue 2b | SensorHealthV1 expanded w/ fault_type, confidence_delta, etc. |
| 3. Anomaly Thresholds | Issue 5 | Issue 2b (NEW) + Issue 5 | Detailed threshold spec in Issue 2b; Issue 5 references it |
| 4. Confidence Algorithm | Issue 5 | Issue 2b (NEW) + Issue 5 | Detailed algorithm in Issue 2b; Issue 5 implements it |
| 5. Ring Buffer API | Issue 5 | Issue 5 | API methods specified: add(), get_last_n_hours(), get_stats() |
| 6. Device Status Contract | Issue 2 | Issue 2a (NEW) | New DeviceStatusV1 contract with all device states |
| 7. VPD Algorithm + Ref Cases | Issue 5 | Issue 2b (NEW) + Issue 5 | Magnus formula + 5 reference test cases in Issue 2b |
| 8. Orchestrator Integration | Issue 7 | Issue 7 | Main loop algorithm specified in Issue 7 scope |
| 9. CLI Arguments | Issue 7 | Issue 7 | All arguments defined: --time-scale, --seed, --output-dir, etc. |
| 10. Error Handling | Issue 3, 4 | Issue 2b + Issue 3 + Issue 4 | Error modes specified; Issues 3/4 updated to handle them |

### New Issues Created
- **Issue 2a**: Observation & Device Status Contracts (Gap 1, 6)
- **Issue 2b**: Confidence Scoring & Anomaly Thresholds (Gap 3, 4, 7)

### Updated Issues
- **Issue 2**: SensorHealthV1 structure expanded
- **Issue 3**: Error handling added
- **Issue 4**: Error handling for malformed observations added
- **Issue 5**: Ring buffer API, VPD algorithm, confidence algorithm, anomaly thresholds specified
- **Issue 7**: CLI arguments and main loop algorithm specified

## Next Steps

1. **Review** `MVP_GITHUB_ISSUES_COMPLETE.md` (the comprehensive updated spec)
2. **Verify** all gaps are addressed to your satisfaction
3. **Create tickets** in GitHub using the issues from `MVP_GITHUB_ISSUES_COMPLETE.md`
4. **Draft supporting docs** (auto-generated from Issue 2b specs):
   - `docs/vpd_algorithm.md`
   - `docs/anomaly_thresholds.md`
   - `docs/confidence_scoring.md`
5. **Begin Phase 1** implementation

---

## Timeline Estimate (Excellence Quality)

| Phase | Weeks | Deliverables |
|-------|-------|--------------|
| 1: Foundation | 1-2 | Issue 1, Issue 2 + annexes |
| 2: Data Flow | 2-3 | Issue 3, Issue 4 |
| 3: Core Logic | 3-4 | Issue 5, Issue 6 (parallel) |
| 4: Integration | 5 | Issue 7 + orchestrator docs |
| 5: Quality Gate | 5-6 | Issue 8 + coverage + docs |
| **Total** | **~6 weeks** | **Stage 1 complete, Stage 2 ready** |
