# Planned Features and Stages

This file captures planned components and staged work that are not yet implemented in code. Keep it aligned with open TOMATO issues.

---

## Stage 1 (Foundations)

- TOMATO-15: Build estimator core pipeline (Observation -> StateV1 + AnomalyV1[] + SensorHealthV1)
- TOMATO-16: Create `scripts/simulate_day.py` for 24h accelerated simulation and log generation
- TOMATO-17: Implement virtual clock abstraction and scheduler with simulation time scaling
- TOMATO-18: Add integration test for deterministic 24h simulation using SimClock (MVP Quality Gate)

---

## Stage 2 (Control and Guardrails)

- Baseline control (water-only, deterministic policy) implemented
- Guardrails v1 runtime validation (hybrid clip/reject) implemented
- Mock executor (log-only dispatch stub for simulations) implemented
- Remaining Stage 2 expansion:
  - Add non-water action policies (light/fan/co2/circulate) in later stages
  - Add hardware executor integration in later stages

---

## Stage 3 (Weather Integration)

- Weather integration baseline implemented: `world_model/weather_client.py` + `forecast_36h_v1` normalization
- Weather adapter baseline implemented: scenario logic + `targets_v1`, `sampling_plan_v1`, `weather_adapter_log_v1`
- State schema alignment implemented for weather adapter inputs (mapping from current `StateV1`)
- Stage 3 runtime artifact wiring implemented in simulation + fixture pipeline
- Remaining Stage 3 expansion:
  - Replace deterministic weather stub with live provider adapter path
  - Add baseline world-model uncertainty host behavior beyond adapter routing

---

## Stage 4 (Vision Pipeline)

- Vision contracts baseline implemented: `vision_input_v1`, `vision_v1`, `vision_explanation_v1`
- Deterministic baseline vision analyzer implemented in `brain/vision/baseline_analyzer.py`
- Stage 4 runtime artifact wiring implemented in simulation (`vision.jsonl`, `vision_explanations.jsonl`)
- Remaining Stage 4 expansion:
  - Integrate external VLM/LLM inference runtime
  - Add temporal multi-frame reasoning and richer explanation provenance

---

## Stage 5 (Hardware Execution Foundation)

- Hardware execution foundation started:
  - pluggable executor backend selection in `scripts/simulate_day.py`
  - hardware adapter abstraction in `brain/executor/hardware_adapter.py`
  - deterministic hardware stub executor path in `brain/executor/hardware_executor.py`
- Remaining Stage 5 expansion:
  - production hardware adapter for actuator I/O
  - device state machine with fault and safe-mode transitions
  - retry/backoff strategy and execution idempotency keys

---

## Planned Agents (Not Yet Implemented)

- World Model Agent
- LLM Agent (Vision Analyzer)

Implemented in Stage 1:
- Observation Source Agent
- State Estimator Agent
- Storage Agent
- Virtual Clock & Scheduler Agent
- Integration Orchestrator foundation (`scripts/simulate_day.py`)

Implemented in Stage 2 (simulation baseline):
- Control Layer Agent (water-only policy)
- Guardrails Agent (runtime validation and reason codes)
- Mock Executor Agent (log-only execution path)

---

## Planned Capabilities (High Level)

- Multi-sensor fusion and VPD calculation in estimator
- 36h forecast for soil moisture and VPD with uncertainty bounds
- MPC-lite action selection with budget-aware guardrails
- Event-driven sampling during anomalies
- Simulation orchestration with deterministic replay and acceleration
- Forecast ingestion + normalization pipeline (GeoSphere Austria)
- Dynamic target/budget/sampling adaptation via Weather Adapter
- Advisory vision assessment and explanation stream for operator-facing context

---

## Planned Modules (Explicit)

- `brain/world_model/weather_client.py`
- `brain/world_model/weather_adapter.py`
- `brain/vision/baseline_analyzer.py`
