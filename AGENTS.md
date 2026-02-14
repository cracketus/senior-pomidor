# 🤖 Agents & Components

**Tomato Brain is not a monolithic application.**

It is a collection of autonomous, single-responsibility agents that cooperate to observe, reason, and act.

---

## Agent Architecture

### 1️⃣ **Observation Source Agent**

**Responsibility**: Emit structured observations from sensors (real or simulated).

```
┌─────────────────────┐
│ Observation Source  │
│  (Synthetic/Replay) │
└──────────┬──────────┘
           │
           ▼
        Observation
```

**Two implementations**:

- **`SyntheticSource`**: Generates realistic sensor readings with noise, diurnal cycles, and scenario injection.
- **`ReplaySource`**: Reads historical observations from JSONL and plays them back deterministically.

**Interface**:
```python
def next_observation() -> Observation | None
```

**Guarantees**:
- Deterministic output (seeded synthetic source)
- Ordered emission
- Returns `None` at end-of-stream

---

### 2️⃣ **State Estimator Agent**

**Responsibility**: Transform raw observations into structured plant state, anomaly events, and sensor health. Fuses sensor data, detects failures, computes derived metrics (VPD, leaf-air delta), and evaluates confidence.

```
┌──────────────────┐   ┌──────────────────┐
│   Observations   │   │  Device Status   │
└────────┬─────────┘   └───────┬──────────┘
         └──────────┬──────────┘
                    │
                    ▼
┌──────────────────────────┐
│  State Estimator Agent   │
│ • Multi-sensor fusion    │
│ • VPD calculation        │
│ • Confidence scoring     │
│ • Sensor fault detection │
│ • 48h ring buffer        │
│ • Anomaly detection      │
└────────┬─────────────────┘
         │
     ┌───┴──────────┬──────────────┐
     ▼              ▼              ▼
  StateV1      AnomalyV1    SensorHealthV1
```

**Inputs**:
- Raw sensor readings (soil probes, air temp/RH, CO2, light, soil temp)
- Device telemetry (ON/OFF, MCU connected, resets)
- Calendar context (day/night, local time)

**Outputs**:
- `StateV1`: Estimated plant state with per-sensor confidence
- `AnomalyV1[]`: Detected anomaly events with severity
- `SensorHealthV1`: Sensor diagnostics and fault indicators

**Capabilities**:
- Support multiple soil probes (at least 2, extensible)
- Detect sensor faults: stuck-at, jumps, drift, disconnect
- Compute VPD from air_temp and RH (physics-based, documented)
- Detect soil patterns (e.g., two-zone moisture distribution)
- Maintain 48-hour ring buffer of state history
- Event-driven mode: increase sampling frequency during anomalies

**Guarantees**:
- Deterministic for identical input sequences
- Confidence (0..1) reflects uncertainty from sensor state and history
- All outputs validate against Pydantic contracts

---

### 3️⃣ **World Model Agent**

**Responsibility**: Forecast environmental and soil dynamics 24–36 hours ahead to inform planning and budget allocation.

```
┌─────────────────┐
│  State History  │  ┌─────────────────┐
│  (48+ hours)    │  │ Weather Forecast│
└────────┬────────┘  └────────┬────────┘
         └──────────┬─────────┘
                    │
                    ▼
   ┌────────────────────────────┐
   │   World Model Agent        │
   │ • Hybrid physics+ML        │
   │ • Soil moisture forecast   │
   │ • VPD forecast             │
   │ • Stress risk assessment   │
   │ • Nightly model rebuild    │
   └────────┬───────────────────┘
            │
        ┌───┴─────────┬──────────────┐
        ▼             ▼              ▼
   36h Forecast  Uncertainty  Schedule Hints
```

**Inputs**:
- State history (at least 48 hours)
- Planned control regimes (light cycle, fans)
- Weather forecast (temperature, humidity, wind, cloudiness)

**Outputs**:
- 36-hour hourly forecast `{soil(P1,P2,avg), VPD, stress_risk}`
- Uncertainty bounds and confidence
- Scheduling recommendations (risk windows for budget allocation)

**Approach (v1)**:
- Base physical-empirical model (soil drying as function of VPD/light/ventilation)
- Lightweight ML correction (regression/boosting on CPU)
- Daily coefficient update (RLS/OLS) on seasonal logs
- Nightly rebuild: fetch weather, rebuild schedule, tighten constraints if high wind/stress expected

**Guarantees**:
- Runs on CPU-only hardware
- Deterministic outputs for fixed inputs
- Trainable from seasonal logs
- Uncertainty calibrated via backtesting

---

### 4️⃣ **Control Layer Agent**

**Responsibility**: Select actions (watering, CO2, ventilation/light modes) to maximize combined objective under budgets and constraints. Runs every 2 hours + event-driven.

```
┌──────────────┐   ┌──────────────┐
│  StateV1     │   │ World Model  │
│              │   │ Forecast     │
└────────┬─────┘   └──────┬───────┘
         └───────┬────────┘
                 │
                 ▼
   ┌─────────────────────────────────┐
   │   Control Layer (MPC-lite)      │
   │ • 24–36h horizon, 1h step       │
   │ • Combined objective function   │
   │ • Beam search plan selection    │
   │ • Recompute every 2 hours       │
   │ • Adapt thresholds to forecast  │
   └────────┬────────────────────────┘
            │
        ┌───┴─────────────┐
        ▼                 ▼
    ActionV1          Guardrails
```

**Objective (v1)**:
```
J = w_yield * YieldProxy
  + w_stress * (-Stress)
  + w_resource * (-ResourceUse)
  + w_smooth * (-ActionChurn)
```

- **YieldProxy**: Stable VPD in target, sufficient CO2, no water stress
- **Stress**: Soil(P1) below threshold, VPD out of range, vision stress increase
- **ResourceUse**: Water/CO2 consumption vs. budget
- **ActionChurn**: Penalty for frequent device switching

**Implementation**:
- MPC-lite: evaluate limited plan set (beam search), select max J
- Hybrid rule-policy + budget planner
- Thresholds adapt to forecast and stress risk
- Remaining budget allocated to high-risk windows

**Guarantees**:
- Decisions backed by multi-hour forecast
- All actions passed to Guardrails for safety check
- Repeatable behavior for fixed state + forecast

---

### 5️⃣ **Guardrails Agent**

**Responsibility**: Single entry point for all actions. Validates safety, budgets, intervals, device state, and data freshness. Constraints adapt based on system state.

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  ActionV1    │  │  StateV1     │  │  Constants   │
│ (proposed)   │  │              │  │  (limits)    │
└────────┬─────┘  └────────┬─────┘  └────────┬─────┘
         └──────────┬────────────────────────┘
                    │
                    ▼
    ┌──────────────────────────────────┐
    │  Guardrails Agent                │
    │ • Budget validation              │
    │ • Per-action limits              │
    │ • Environmental constraints      │
    │ • Device state checks            │
    │ • Data freshness validation      │
    │ • Adaptive constraint tightening │
    └────────┬─────────────────────────┘
             │
         ┌───┴────────┐
         ▼            ▼
   Validated      Safe Mode
   or Rejected    (if critical)
```

**Constraint Categories**:
- **Budget limits**: water_ml/day, co2_seconds/day, max_actions/hour
- **Per-action limits**: max_pulse_ml, min_interval_between_water, max_co2_injection_seconds
- **Environmental**: VPD/RH thresholds, safe operating ranges
- **Device checks**: MCU connected, device ready, etc.
- **Data validity**: state freshness, confidence thresholds

**Safe Mode**:
- Triggered on critical failures (MCU disconnect, stale data, severe anomaly)
- Disables risky devices (CO2, pump); keeps safe ones (circulation)
- Increases monitoring frequency
- Switches to conservative policy until trust restored

**Guarantees**:
- No action executes without passing guardrails
- Safety constraints are hard limits (never relaxed)
- Budget constraints adapt: stricter during anomalies, baseline during stability

---

### 6️⃣ **LLM Agent (Vision Analyzer)**

**Responsibility**: Analyze plant photos and telemetry summaries, produce structured vision insights and explanations. No direct actuator control.

```
┌──────────────┐  ┌──────────────┐
│ Plant Photo  │  │  Telemetry   │
│ (1–2 per     │  │  Summary     │
│  wake-cycle) │  │              │
└────────┬─────┘  └────────┬─────┘
         └──────────┬──────┘
                    │
                    ▼
  ┌────────────────────────────┐
  │  LLM Agent (Qwen2.5-VL 7B) │
  │  • Vision analysis         │
  │  • Structured JSON output  │
  │  • Plant health assessment │
  │  • Reasoning log           │
  └────────┬───────────────────┘
           │
       ┌───┴──────────┬──────────┐
       ▼              ▼          ▼
  VisionV1      TextualNote  SemantLogs
   (JSON)       (for human)  (memory)
```

**Vision Contract**:
Strict JSON output:
```json
{
  "schema_version": "vision_v1",
  "leaf_color": "green|yellowing|spots|unknown",
  "wilting": true,
  "pest_signs": "none|possible|likely",
  "fruit_count_est": 0,
  "flower_count_est": 0,
  "stress_score": 0.0,
  "notes": "short descriptive text",
  "confidence": 0.0
}
```

**Memory Levels**:
- **Episodic**: Per wake-cycle structured observations
- **Semantic**: Aggregated seasonal facts (growth stage, typical patterns)

**Guarantees**:
- CPU-only execution (GGUF quantization)
- Deterministic for same image input
- Output validates against `VisionV1` schema
- No secrets in public logs

---

### 7️⃣ **Storage Agent**

**Responsibility**: Persist state, anomalies, and actions to JSONL with atomic writes, rotation, and export.

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  StateV1     │  │  AnomalyV1   │  │  ActionV1    │
└────────┬─────┘  └────────┬─────┘  └─────────┬────┘
         └──────────┬─────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │  Storage Agent (JSONL)  │
        │ • Atomic append         │
        │ • Rotation by day/size  │
        │ • Public export         │
        └─────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   run_YYYYMMDD/          data/public/
   (raw records)          (filtered export)
```

**Inputs**:
- Contracts (StateV1, AnomalyV1, ActionV1, SensorHealthV1)

**Outputs**:
- JSONL files organized by dataset/run
- Public-safe export (filtered fields)

**Guarantees**:
- Atomic writes (append-safe from concurrent readers)
- File rotation by day and size threshold
- Full line-delimited JSON validity

---

### 8️⃣ **Virtual Clock & Scheduler Agent**

**Responsibility**: Drive simulation at configurable speeds and schedule periodic tasks.

```
┌──────────────────────────┐
│  Clock Abstraction       │
│  • RealClock             │
│  • SimClock(time_scale)  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Scheduler / Event Loop  │
│ • Periodic task queue    │
│ • Time-driven dispatch   │
│ • Graceful shutdown      │
└──────────────────────────┘
```

**Clock Implementations**:

- **`RealClock`**: Wall-clock time, for production hardware execution.
- **`SimClock(scale)`**: Logical time, accelerated by `scale` factor for fast development.

**Example**: `SimClock(scale=120)` means 1 wall-second = 120 logical seconds (a 24-hour day in 12 minutes).

**Guarantees**:
- Monotonic time progression
- Deterministic tick ordering (SimClock)
- Pluggable for testing and simulation

---

### 9️⃣ **Integration Orchestrator**

**Responsibility**: Wire all agents together and run end-to-end workflows.

```
Observation Source
       │
       ▼
State Estimator ──→ Storage Agent
       │                │
       └────────────────┘
            │
        Virtual Clock
        & Scheduler
```

**Entry point**: `scripts/simulate_day.py`

**Decision Cycle** (every 2 hours + event-driven):
1. Read observations + device state
2. Estimate state (State Estimator)
3. Detect anomalies → trigger event-driven mode if critical
4. Generate 36h forecast (World Model)
5. Compute optimal actions (Control Layer)
6. Validate safety (Guardrails)
7. Analyze plant photo if available (LLM Agent)
8. Persist all records (Storage)

**Event-Driven Mode**:
- Triggered by: wind spike, severe anomaly, sensor disconnect, overheating
- Increases sampling frequency from 2h → 5–15 min
- Tightens constraints, switches to conservative policy
- Notifies human operator

---

## Agent Communication Contract

All agents communicate via immutable, versioned Pydantic contracts:

- **`StateV1`**: Estimated plant state
- **`ActionV1`**: Control decisions (water, light)
- **`AnomalyV1`**: Detected anomalies
- **`SensorHealthV1`**: Sensor diagnostics

**Principle**: Every message on disk must validate against its schema.

---

## Why Agents?

1. **Testability**: Each agent can be tested in isolation or integrated incrementally.
2. **Replaceability**: A storage agent can be swapped from JSONL → database without affecting sources or estimator.
3. **Clarity**: Single-responsibility design makes the data flow transparent.
4. **Observability**: Passing messages between agents means all signals are recorded and replayable.

---

## Future Extensions

As the system grows, new agents may be added:

- **Action Executor Agent**: Dispatch control signals to hardware (water valve, lights, fans, CO2).
- **Database Agent**: Optional SQLite backend for efficient querying (JSONL stays as append log).
- **Analytics Agent**: Query and analyze stored records; daily summaries and trends.
- **ML Training Agent**: Adapt model coefficients from seasonal logs; learn per-plant profiles.
- **Weather Integration Agent**: Fetch forecasts and integrate into World Model.
- **Human Interface Agent**: Export public data; web API or CLI for monitoring and overrides.

Each will follow the same messaging discipline, versioned Pydantic contracts, and safety-first principles.
