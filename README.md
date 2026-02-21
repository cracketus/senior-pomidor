# 🍅 Tomato Brain (Embodied AI)

An open, production-minded AI core for growing tomatoes in the real world.

This project is about building an **embodied AI system** that can:

* Read sensor data (real or synthetic)
* Estimate plant state
* Detect anomalies
* Make decisions (water, light)
* Run safely on a mini-PC next to a real plant

No hype. No magic. Just clean engineering.

---

# 🚀 Quick Start (< 10 minutes)

## Prerequisites
- Python 3.11 or later

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with dev dependencies
pip install -e ".[dev]"
```

## Common Commands

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=brain --cov-report=html

# Lint code
ruff check .

# Auto-fix lint issues
ruff check . --fix

# Simulate 24-hour day (accelerated time)
python scripts/simulate_day.py --seed 42 --duration-hours 24 --time-scale 120 --output-dir data/runs
```

Main loop (every 2 hours): observation → estimate → store → advance.

---

# 🚀 Philosophy

This is not a research notebook.
This is not a prototype that "might" go to prod.

This code **is production code from day one**.

Design principles:

* Deterministic
* Testable
* Observable
* Minimal dependencies
* Transparent and open to the community
* Hardware-independent core

We start simple and evolve carefully.

---

# 🧠 What Exists in MVP

The MVP focuses on the most independent and valuable core:

## 1️⃣ Contracts (Source of Truth)

Strict Pydantic models define:

* `state_v1`
* `action_v1`
* `anomaly_v1`
* `sensor_health_v1`

Schemas are versioned.
Everything written to disk must validate.

---

## 2️⃣ JSONL Storage (No Database Yet)

All data is stored as JSONL files.

Why?

* Simple
* Debuggable
* Git-friendly
* Works offline
* Zero infra

We will introduce a database only when:

* Query complexity grows
* We need indexing
* Multiple services write concurrently
* Data volume becomes painful

Until then, files win.

---

## 3️⃣ Synthetic + Replay Data

The system can run without hardware.

Data sources:

* Synthetic generator (noise + day cycle)
* Replay from previous JSONL logs

This means:

* CI works
* Development is fast
* Bugs are reproducible

---

## 4️⃣ State Estimator

Transforms raw observations into structured plant state.

Includes:

* VPD calculation
* Ring buffer smoothing
* Confidence score
* Anomaly detection

This is the heart of Tomato Brain.

---

## 5️⃣ Virtual Time

We support time scaling.

Example:

```
1 minute of real time = 2 hours of plant time
```

This allows us to simulate 24 hours in minutes.

---

# 📂 Project Structure (Simplified)

```
brain/
  contracts/
  storage/
  simulator/
  state_estimator/
  scheduler/

scripts/
  simulate_day.py

tests/
```

We keep it tight.
No premature abstraction.

---

# 🛠 Requirements

* **Python 3.11** (required)
* pytest
* pytest-cov (coverage reporting)
* ruff (linting)
* pydantic (strict validation)

All dependencies are configured in `pyproject.toml`.

Install development environment:

```bash
pip install -e ".[dev]"
```

Verify installation:

```bash
pytest --version
ruff --version
```

---

# 🌍 Open & Transparent

This project is designed to be:

* Publicly shareable
* Reproducible
* Inspectable

Runs generate datasets that can be exported to `data/public/`.

The goal is not just to grow tomatoes.
The goal is to build an open embodied AI system that the community can inspect and improve.

---

## Operational Documentation

- `docs/confidence_scoring.md`
- `docs/anomaly_thresholds.md`
- `docs/error_handling.md`
- `docs/state_v1_weather_adapter_mapping.md`
- `docs/codex_prompting_playbook.md`

---

# 🧪 What This Is NOT

* Not a web app (yet)
* Not connected to hardware (yet)
* Not an LLM decision system (yet)
* Not over-engineered

We build the foundation first.

---

# 🛣 Roadmap Direction

Next layers (not in MVP):

* Action executor (water + light control)
* Hardware adapters
* FastAPI interface
* Long-term analytics
* Optional SQLite layer
* Eventually Rust performance modules

But only when the core is stable.

---

# 🧑‍🌾 Why This Matters

Embodied AI is different.

If it fails:

* Plants die
* Hardware breaks
* Water leaks

So we build carefully.

Small. Deterministic. Observable.

---

# 🍅 Senior Pomidor

This repository is part of the larger vision:

An open, real-world, embodied AI that grows tomatoes autonomously.

We start with the brain.

Everything else comes later.

---

## Stage 2 Runtime Status

Current Stage 2 runtime in `scripts/simulate_day.py` includes:

* Baseline water-only control proposals (`ActionV1`)
* Guardrails validation with deterministic approve/reject/clip outcomes (`GuardrailResultV1`)
* Log-only mock executor events (`ExecutorEventV1`)

Additional Stage 2 artifacts per run:

* `actions.jsonl`
* `guardrail_results.jsonl`
* `executor_log.jsonl`

Scope note:

* Stage 2 intentionally emits only `ActionType.WATER`.
* `light`, `fan`, `co2`, and `circulate` control policies are deferred to later stages.

## Stage 3 Runtime Status

Current Stage 3 simulation baseline in `scripts/simulate_day.py` also includes:

* Deterministic 36h normalized forecast stream (`Forecast36hV1`)
* Deterministic weather-adapter targets stream (`TargetsV1`)
* Deterministic weather-adapter sampling plan stream (`SamplingPlanV1`)
* Deterministic weather-adapter decision log stream (`WeatherAdapterLogV1`)

Additional Stage 3 artifacts per run:

* `forecast_36h.jsonl`
* `targets.jsonl`
* `sampling_plan.jsonl`
* `weather_adapter_log.jsonl`

Scope note:

* Forecast input is a deterministic simulation stub (no live API key path in runtime).
* Non-water action policies and hardware actuator execution remain deferred.
