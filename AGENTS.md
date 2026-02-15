# 🤖 Agents & Components

**Tomato Brain is not a monolithic application.**

It is a collection of autonomous, single-responsibility agents that cooperate to observe, reason, and act.

---

## Agent Architecture

Planned components and stages are summarized in `PLANNED_FEATURES.md`.

### 1️⃣ Observation Source Agent

**Status**: Current

**Responsibility**: Emit structured observations from sensors (real or simulated).

```
┌─────────────────────┐
│ Observation Source  │
│  (Synthetic/Replay) │
└──────────┬──────────┘
           │
           ▼
     Observation + DeviceStatus
```

**Two implementations**:

- **`SyntheticSource`**: Generates realistic sensor readings with noise, diurnal cycles, and scenario injection.
- **`ReplaySource`**: Reads historical observations from JSONL and plays them back deterministically.

**Interface**:
```python
def next_observation() -> tuple[ObservationV1, DeviceStatusV1] | None
```

**Guarantees**:
- Deterministic output (seeded synthetic source)
- Ordered emission
- Returns `None` at end-of-stream
- All sources emit `ObservationV1` + `DeviceStatusV1`

---

### 2️⃣ State Estimator Agent

**Status**: Planned

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

### 3️⃣ World Model Agent

**Status**: Planned

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

---

### 4️⃣ Control Layer Agent

**Status**: Planned

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

---

### 5️⃣ Guardrails Agent

**Status**: Planned

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

---

### 6️⃣ LLM Agent (Vision Analyzer)

**Status**: Planned

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

---

### 7️⃣ Storage Agent

**Status**: Current

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
```

---

### 8️⃣ Virtual Clock & Scheduler Agent

**Status**: Planned

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

---

### 9️⃣ Integration Orchestrator

**Status**: Planned

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

**Entry point**: `scripts/simulate_day.py` (planned; see issue TOMATO-16)

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
