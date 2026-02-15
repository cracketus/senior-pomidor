# Planned Features and Stages

This file captures planned components and staged work that are not yet implemented in code. Keep it aligned with open TOMATO issues.

---

## Stage 1 (Foundations)

- TOMATO-15: Build estimator core pipeline (Observation -> StateV1 + AnomalyV1[] + SensorHealthV1)
- TOMATO-16: Create `scripts/simulate_day.py` for 24h accelerated simulation and log generation
- TOMATO-17: Implement virtual clock abstraction and scheduler with simulation time scaling
- TOMATO-18: Add integration test for deterministic 24h simulation using SimClock (MVP Quality Gate)

---

## Planned Agents (Not Yet Implemented)

- State Estimator Agent
- World Model Agent
- Control Layer Agent
- Guardrails Agent
- LLM Agent (Vision Analyzer)
- Virtual Clock & Scheduler Agent
- Integration Orchestrator

---

## Planned Capabilities (High Level)

- Multi-sensor fusion and VPD calculation in estimator
- 36h forecast for soil moisture and VPD with uncertainty bounds
- MPC-lite action selection with budget-aware guardrails
- Event-driven sampling during anomalies
- Simulation orchestration with deterministic replay and acceleration
