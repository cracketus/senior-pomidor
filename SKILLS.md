# 🎯 Skills & Capabilities Roadmap

A clear inventory of what Tomato Brain can do now, and what's planned for the future.

---

## ✅ MVP Capabilities (Current)

### Observation & Sensing

- ✅ **Synthetic sensor data generation**
  - Configurable noise models
  - Simulated diurnal (day/night) cycles
  - Temperature, humidity, light, soil moisture simulation
  - Deterministic emission (seeded RNG)

- ✅ **Historical data replay**
  - Load observations from JSONL logs
  - Deterministic playback in chronological order
  - Graceful handling of malformed records

### State Estimation

- ✅ **VPD (Vapor Pressure Deficit) calculation**
  - Physics-based vapor pressure computation
  - Plant-relevant diagnostics
  - Reference-validated

- ✅ **Ring buffer for temporal context**
  - Sliding window of recent observations
  - Memory-bounded history
  - Support for trend detection

- ✅ **Confidence scoring**
  - Quantify estimation uncertainty
  - Drop confidence when sensors are missing/failing
  - Feed into decision confidence

- ✅ **Anomaly detection (threshold-based MVP)**
  - Rule-based detectors for out-of-range conditions
  - Emit structured `AnomalyV1` events
  - No false positive filtering (yet)

### Contracts & Schema

- ✅ **Versioned Pydantic models**
  - `StateV1`: Plant state with confidence
  - `ActionV1`: Control decisions (water, light)
  - `AnomalyV1`: Anomaly events with severity
  - `SensorHealthV1`: Sensor diagnostics
  - Strict validation on serialization/deserialization

- ✅ **JSON Schema export**
  - Auto-generated schemas from Pydantic models
  - Available for data documentation and integration

### Storage

- ✅ **JSONL file storage**
  - Line-delimited JSON for durability and debuggability
  - Atomic append writes
  - Configurable flush/fsync behavior

- ✅ **File rotation**
  - By day boundary
  - By max file size
  - Automatic directory creation for runs

- ✅ **Dataset management**
  - `run_YYYYMMDD` naming convention
  - Organized directory layout
  - Lifecycle management (creation, archival)

- ✅ **Public data export**
  - Filter sensitive fields
  - Generate safe JSONL subsets for sharing
  - Whitelisted record selection

### Virtual Time & Simulation

- ✅ **Clock abstraction**
  - `RealClock` for wall-clock time
  - `SimClock(scale)` for accelerated logical time
  - Pluggable for testing

- ✅ **Configurable time scaling**
  - `time_scale=1`: Real-time (1 second = 1 second)
  - `time_scale=120`: Fast sim (1 second = 2 minutes)
  - Scale affects logical progression, not determinism

- ✅ **Event loop & scheduler**
  - Periodic task execution
  - Graceful shutdown
  - Clock-driven dispatch

### End-to-End Execution

- ✅ **Full 24-hour simulation**
  - Single script orchestration
  - Configurable time acceleration
  - Reproducible with fixed seeds
  - Persists all state/anomaly logs

- ✅ **Integration testing**
  - 24h deterministic validation
  - Schema conformance checks
  - Record count assertions
  - Reproducibility verification

### Development & Operations

- ✅ **Production-ready Python structure**
  - `pyproject.toml` configuration
  - Clean package layout
  - Dependency pinning

- ✅ **Comprehensive test suite**
  - Unit tests for all modules
  - Integration tests for full pipeline
  - Coverage reporting
  - Determinism validation

- ✅ **Code quality tools**
  - `pytest` for testing
  - `pytest-cov` for coverage
  - `ruff` for linting and formatting

---

## 🔜 Planned Capabilities (Roadmap)

The system evolves in deliberate stages, each building on the previous.

### Stage 1: Core Foundation (MVP - Current & Immediate)

**Focus**: State Estimator, Contracts, Storage, Simulation

- ✅ Versioned Pydantic contracts (StateV1, ActionV1, AnomalyV1, SensorHealthV1)
- ✅ JSONL storage with atomic writes and rotation
- ✅ State Estimator (VPD, confidence, anomaly detection, 48h ring buffer)
- ✅ Synthetic and replay data sources
- ✅ Virtual clock with time scaling
- ✅ Full 24h simulation script
- ✅ Unit and integration tests

### Stage 2: Control & Safety (Foundation for Actions)

**Focus**: Decision logic, constraints validation, safe execution

- [ ] Control Layer Agent (MPC-lite, 36h horizon planning)
- [ ] Guardrails Agent (budget validation, safety constraints, safe mode)
- [ ] Basic rule-based control policy (threshold-based watering/light)
- [ ] Decision cycle formalization (every 2 hours + event-driven)
- [ ] Event-driven mode implementation (anomaly response, tighter sampling)
- [ ] Mock action executor for testing
- [ ] Acceptance tests for control correctness

### Stage 3: Forecasting & Adaptation

**Focus**: World Model, weather integration, adaptive planning

- [ ] World Model Agent (36h soil moisture / VPD forecast)
- [ ] Hybrid physics-empirical forecasting
- [ ] Weather forecast integration
- [ ] Nightly model rebuild (coefficient update via RLS/OLS)
- [ ] Uncertainty quantification and calibration
- [ ] Budget allocation during high-stress windows
- [ ] Backtesting suite for forecast validation

### Stage 4: Vision & LLM Integration

**Focus**: Plant analysis, explanations, human-level insights

- [ ] LLM Agent (Qwen2.5-VL 7B CPU-only)
- [ ] Vision contract (VisionV1 JSON schema)
- [ ] Plant health classification (leaf color, wilting, stress score)
- [ ] Episodic memory (per wake-cycle)
- [ ] Semantic memory (seasonal aggregations)
- [ ] Public log integration (no secrets, transparent reasoning)

---

## 🔜 Phase 5+: Extended Capabilities

Once Stages 1–4 are stable:

### Phase 5: Real Hardware & Execution

- [ ] Hardware adapter interface (water, light, fans, CO2)
- [ ] Action Executor Agent
- [ ] Device state machine (ready, fault, safe mode)
- [ ] Graceful degradation on hardware failure

### Phase 6: Data & Analytics

- [ ] SQLite optional backend (JSONL remains append log)
- [ ] Analytics Agent (daily summaries, trends)
- [ ] SQL queries for seasonal analysis
- [ ] Data visualization (time-series, anomaly timeline)

### Phase 7: APIs & Interfaces

- [ ] FastAPI server (current state, historical queries)
- [ ] Web dashboard (plant visualization, alerts, manual override)
- [ ] CLI tools (JSONL inspection, export, health checks)

### Phase 8: Multi-Plant & Distributed

- [ ] Multiple plant instances on one mini-PC
- [ ] Shared analytics database
- [ ] Comparative health metrics
- [ ] Central logging and orchestration

---

## 📊 Capability Matrix

| Feature | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Phase 5 | Phase 6+ |
|---------|---------|---------|---------|---------|---------|----------|
| Contracts & versioning | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| JSONL storage | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Synthetic observations | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Historical replay | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| State Estimator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| VPD calculation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Anomaly detection | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 48h ring buffer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Virtual clock | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2h decision cycle | | ✅ | ✅ | ✅ | ✅ | ✅ |
| Event-driven mode | | ✅ | ✅ | ✅ | ✅ | ✅ |
| Control Layer (MPC) | | ✅ | ✅ | ✅ | ✅ | ✅ |
| Guardrails Agent | | ✅ | ✅ | ✅ | ✅ | ✅ |
| Rule-based control | | ✅ | ✅ | ✅ | ✅ | ✅ |
| World Model (forecast) | | | ✅ | ✅ | ✅ | ✅ |
| Weather integration | | | ✅ | ✅ | ✅ | ✅ |
| Adaptive coefficients | | | ✅ | ✅ | ✅ | ✅ |
| Vision analysis (LLM) | | | | ✅ | ✅ | ✅ |
| Crop health scoring | | | | ✅ | ✅ | ✅ |
| Hardware execution | | | | | ✅ | ✅ |
| Action Executor | | | | | ✅ | ✅ |
| SQLite backend | | | | | | ✅ |
| Analytics queries | | | | | | ✅ |
| Web API | | | | | | ✅ |
| Dashboard UI | | | | | | ✅ |
| CLI tools | | | | | | ✅ |
| Multi-plant support | | | | | | ✅ |

---

## 🎓 What Tomato Brain IS

- ✅ Production-ready code from day one
- ✅ Deterministic and testable
- ✅ Observable (all data persisted and replayable)
- ✅ Hardware-independent core (simulation ready)
- ✅ Multi-agent architecture with clear responsibilities
- ✅ Versioned data contracts for transparency
- ✅ Safe-first design (Guardrails before execution)
- ✅ Simple enough to understand, modify, and extend
- ✅ Open source and community-driven
- ✅ Staged roadmap (build one layer at a time)

---

## ❌ What Tomato Brain IS NOT (Yet)

- ❌ Connected to real hardware (Stage 1 is simulation + contracts)
- ❌ Making autonomous watering decisions (Stage 2 adds Control Layer)
- ❌ Forecasting long-term trends (Stage 3 adds World Model)
- ❌ Analyzing plant photos (Stage 4 adds LLM Agent)
- ❌ Web application (Phase 7+)
- ❌ Distributed or clustered (Phase 8+)
- ❌ Over-engineered for features not yet needed

---

## 🌱 Design Philosophy

**Start simple. Stay observable. Evolve deliberately.**

We don't add features until:
1. The core is stable
2. There's a clear use case
3. The addition doesn't compromise safety or simplicity
4. We have tests ready

This keeps the codebase lean and the system trustworthy.

---

## 🔗 Related Documentation

- [README.md](README.md) — Project philosophy and MVP overview
- [AGENTS.md](AGENTS.md) — Agent architecture and data flow
- [INSTRUCTIONS.md](INSTRUCTIONS.md) — Developer setup and workflow
- [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) — Detailed design requirements
- [MVP_GITHUB_ISSUES.md](MVP_GITHUB_ISSUES.md) — Component acceptance criteria for first iteration

---

## 📞 Questions?

- **How do I use a specific feature?** → See [INSTRUCTIONS.md](INSTRUCTIONS.md)
- **How does the system work?** → See [AGENTS.md](AGENTS.md)
- **What are the technical details?** → See [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)
- **What's the development roadmap?** → This file (SKILLS.md)
- **What are the acceptance criteria for first iteration?** → See [MVP_GITHUB_ISSUES.md](MVP_GITHUB_ISSUES.md)
