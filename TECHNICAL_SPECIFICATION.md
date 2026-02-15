# Technical Specification: “Brain” of the Embodied Tomato System
Version: v1.0  
Date: February 2026  
Context: CPU-only (Windows/Linux), 1–2 plants (Season 1)

---

## Purpose of the Document

This document defines the requirements and interfaces of the software “brain” of the plant control system: State Estimator, World Model, Control Layer, Guardrails, and LLM Agent (Qwen). It is written so that development can begin immediately, in parallel with hardware assembly and further clarifications.

---

## Key Principles

- Autonomous 24/7 operation; the human receives clear anomaly alerts and can perform a manual override.
- Planning horizon: 24–36 hours (realistic with an empirical model + weather forecast).
- Combined optimization: yield (priority) + stress minimization, under resource budgets.
- Decision cycle every 2 hours + event-driven anomaly handling (wind/overheat/sensor disconnect).
- Data and decisions are logged for publication (transparency) and training (dataset).
- The LLM has no direct actuator control: all actions pass through Guardrails and contract validation.

---

## System Scope and Responsibilities

The “brain” operates on top of a low-level execution layer (MCU/relays/pump/fans/light), which exposes safe commands (e.g., WATER_PULSE(ml), CO2_INJECT(seconds), SET_LIGHT(on/off)).  
This specification covers only the software decision logic and its interfaces.

---

## Definitions

**State** – Normalized system state at a specific time (sensors + derived metrics + device statuses).  
**Observation** – Raw sensor/camera measurements before filtering and fusion.  
**Action** – Command to the execution layer (watering, light, fan, CO2, etc.).  
**Episode** – One wake-cycle (every 2 hours): read → estimate → plan → act → log.  
**Anomaly** – Event outside expected range or failure (wind spike, overheating, sensor drift, disconnect).

---

# 1. Data Contracts and Versioning

## 1.1 Schema Versioning

All data structures include a `schema_version` field (e.g., `state_v1`).  
Schema changes must preserve backward compatibility: new fields are optional; deprecated fields remain available for at least one season.

## 1.2 Core Structures (JSON)

### State (normalized state)

```json
{
  "schema_version": "state_v1",
  "ts": "2026-02-14T10:00:00+01:00",
  "env": {"air_temp_c": 24.3, "rh_pct": 61.7, "co2_ppm": 439.0, "vpd_kpa": 1.15},
  "plant": {
    "leaf_temp_c": 23.7,
    "leaf_air_delta_c": 0.6,
    "vision": {
      "source": "camera_main",
      "summary": "dense canopy, no wilting",
      "stress_score": 0.10,
      "fruit_count_est": 3,
      "confidence": 0.65
    }
  },
  "soil": {
    "temp_c": 19.7,
    "probes": [
      {"id": "P1", "moisture_pct": 15.6, "confidence": 0.55},
      {"id": "P2", "moisture_pct": 49.2, "confidence": 0.85}
    ],
    "avg_moisture_pct": 32.4,
    "zone_pattern": "two_zone"
  },
  "devices": {
    "light": "ON",
    "circulation_fan": "ON",
    "exhaust_fan": "OFF",
    "humidifier": "OFF",
    "heater_mat": "OFF",
    "water_pump": "OFF",
    "co2_solenoid": "OFF",
    "mcu_connected": true,
    "last_reset_ts": "2026-02-14T06:02:10+01:00"
  },
  "budgets": {
    "water_ml_used_today": 1600,
    "water_ml_budget_today": 2200,
    "co2_seconds_used_today": 120,
    "co2_seconds_budget_today": 600
  }
}
```

### Action (command to execution layer)

```json
{
  "schema_version": "action_v1",
  "ts": "2026-02-14T10:00:05+01:00",
  "type": "WATER",
  "params": {"ml": 200, "pulses": 1},
  "why": {
    "rules_fired": ["soil.P1 < 18%"],
    "objective_hint": "reduce_water_stress"
  },
  "safety": {
    "validated": true,
    "guardrails": ["daily_water_budget", "max_pulse_ml", "min_interval"]
  }
}
```

### Anomaly (event/anomaly)

```json
{
  "schema_version": "anomaly_v1",
  "ts": "2026-02-14T13:17:00+01:00",
  "severity": "HIGH",
  "type": "WIND_SPIKE",
  "signals": {"wind_gust_mps": 18.0, "window_open_sensor": true},
  "expected_effects": ["rapid_VPD_increase", "leaf_temp_delta_change"],
  "required_response": ["increase_sampling", "check_fan_modes", "notify"]
}
```

### Weather Integration Contracts (planned)

The following contracts are required for forecast ingestion and Weather Adapter integration:

- `forecast_36h_v1`: normalized external forecast (temperature, humidity, wind, cloud/solar) for the next 36 hours.
- `targets_v1`: base targets + adapted targets with active scenario list and validity window.
- `sampling_plan_v1`: base sampling cadence plus override windows.
- `weather_adapter_log_v1`: explainable log record of applied scenario changes and guardrail clipping.

These are planned and will be added alongside the World Model implementation.

---

# 2. State Estimator

## Purpose

Transforms raw observations (sensors, device statuses, photos) into a stable, physically meaningful `State`: filters noise, detects sensor failures, computes derived metrics (VPD, leaf-air delta), evaluates confidence, and normalizes data into a versioned schema.

## Inputs

- Raw sensor readings (soil probes, air temp/RH, CO2, soil temp, light proxy)
- Device telemetry (ON/OFF, MCU connected, resets)
- Vision summary from LLM Agent (JSON, not the image itself)
- Calendar context: day/night, season stage, local time (Europe/Vienna)

## Outputs

- `State (state_vN)`
- `sensor_health_vN`
- `Anomaly (anomaly_vN)` when thresholds are exceeded or failures suspected

## Functional Requirements

- Support at least 2 soil probes, extensible to N without API changes.
- Confidence (0..1) per sensor based on range, rate of change, cross-consistency, and history.
- Detect common faults: stuck-at (flat line), sudden jump, drift, out-of-range, disconnect.
- Compute VPD (kPa) from air_temp and RH. Algorithm fixed and documented.
- Detect soil patterns (e.g., two-zone: P1 low, P2 high) and store `zone_pattern`.
- Maintain 48-hour ring buffer of state history.
- Event-driven mode: increase sensor frequency (e.g., from 2h to 5–15 min) during anomalies.

## Interfaces

Recommended: local event bus (Redis streams / NATS / MQTT) + JSONL file logging.  
State Estimator publishes `state_vN` and `anomaly_vN` and writes to storage.

## Testing and Acceptance Criteria

- Unit tests for VPD and derived metrics.
- Tests for stuck-at/jump detection on synthetic data.
- Integration test: replay 24h logs → identical state snapshots.
- Acceptance: if one probe disconnects, confidence drops and no unsafe conclusions are made.

---

# 3. World Model

## Purpose

Forecasts environmental and soil dynamics for 24–36 hours: soil moisture (by zones), VPD, stress risk. Must run on CPU and be trainable from seasonal logs.

## Recommended Approach (Hybrid)

Base physical-empirical model (drying rate as function of VPD/light/ventilation) + lightweight ML correction (regression/boosting), trained offline/daily on CPU.

## Inputs

- State history (at least 48 hours)
- Planned regimes (light cycle, fans)
- Weather forecast (temperature, humidity, wind, cloudiness/sun)

## Outputs

- 36-hour hourly forecast `{soil(P1,P2,avg), VPD, stress_risk}`
- Uncertainty + explanation
- Scheduling recommendations (risk windows for budget allocation)

## Weather Forecast Integration (planned)

Forecasts are sourced from GeoSphere Austria and normalized into `forecast_36h_v1`.
Normalization requirements include:

- hourly (or native) cadence with explicit `freq_minutes`
- timestamps stored at minute precision in `Europe/Vienna` timezone
- fields: `ext_temp_c`, `ext_rh_pct`, `ext_wind_mps`, and either `ext_cloud_cover_pct` or `ext_solar_wm2`
- caching metadata for 24 hours, forecast TTL 120 minutes
- rate limit compliance (5 req/s, 240 req/hour)

## Weather Adapter (planned)

WeatherAdapter lives under `brain/world_model/weather_adapter.py` as a policy layer on top of the forecast.
Inputs: `forecast_36h_v1` + `StateV1` + context (growth stage, mode).
Outputs:

- `targets_v1` (base + adapted targets)
- `sampling_plan_v1` (base cadence + overrides)
- adapted budgets and explanations

Scenarios (initial set):
- dry inflow
- heatwave
- wind spike
- cold spell

## State Schema Reconciliation (planned)

Weather Adapter expects nested state fields (env/soil/probes), while current `StateV1` is flat.
Until contracts are aligned, apply a mapping:

- `env.air_temp_c` ← `StateV1.air_temperature`
- `env.rh_pct` ← `StateV1.air_humidity`
- `env.vpd_kpa` ← `StateV1.vpd`
- `soil.avg_moisture_pct` ← `StateV1.soil_moisture_avg` * 100
- `soil.probes` ← `StateV1.soil_moisture_p1/p2` (as available)

This mapping should be documented and replaced with a unified schema once the contracts are updated.

## Nightly Rebuild

Every night (e.g., 00:10), fetch weather forecast and rebuild wake-cycle schedule and constraints.  
Increase monitoring frequency and tighten stress constraints if strong wind or fluctuations expected.

## Minimal v1 Implementation

- Soil moisture forecast as exponential decay (per zone) using last 48h.
- Drying rate: `dM/dt = a*VPD + b*light + c*fan + d`.
- Daily coefficient update (RLS/OLS) on CPU.
- VPD forecast from weather + regimes.
- `stress_risk = f(VPD, leaf-air delta, soil(P1), drop rate)`.

## Testing

- Backtesting on logs: 24h ahead MAE for soil_avg and VPD.
- Uncertainty calibration.
- Acceptance: forecast warns about drying risk during wind.

---

# 4. Control Layer

## Purpose

Selects actions (watering, CO2, ventilation/light modes) to maximize combined objective (yield priority + stress minimization) under budgets and constraints.  
Runs every 2 hours + event-driven mode.

## Objective (v1)

`J = w_yield*YieldProxy + w_stress*(-Stress) + w_resource*(-ResourceUse) + w_smooth*(-ActionChurn)`

- YieldProxy: stable VPD in target range, sufficient CO2 in light hours, no water stress.
- Stress: soil(P1) below threshold, VPD out of range, increasing vision.stress_score.
- ResourceUse: water/CO2 consumption.
- ActionChurn: penalty for frequent switching.

## Controller (MPC-lite)

24–36h horizon, 1h step. Evaluate limited plan set (beam search), select max J, recompute every 2h.

## Minimal v1

Hybrid rule-policy + budget planner. Thresholds adapt to forecast and stress risk. Remaining budget allocated to high-risk windows.

## Testing

- Offline simulation (7 days logs).
- Compare with rule-only baseline.
- Acceptance: fewer stress events with equal or less water; more stable VPD; reduced churn.

---

# 5. Guardrails

## Purpose

Single entry point for all actions. Validates safety, budgets, intervals, device state, and data freshness. Constraints adapt: stricter during anomalies, relaxed during stability.

## Constraint Categories

- Budget limits: water_ml_per_day, co2_seconds_per_day, max_actions_per_hour.
- Per-action limits: max_pulse_ml, min_interval_between_water, max_CO2_injection_seconds.
- Environmental constraints (VPD/RH thresholds, etc.).
- Device and connectivity checks (MCU disconnected, device OFF).
- Data validity (stale state, low confidence → safe policy).

## Safe Mode

In critical conditions: disable potentially dangerous devices (CO2/pump), keep safe ones (circulation), increase monitoring frequency, notify, and switch to conservative policy until trust restored.

---

# 6. LLM Agent (Qwen)

## Purpose

The LLM Agent is the “analyst and chronicler”: analyzes plant photos, summarizes telemetry, produces explanations, hypotheses, and human-level plans. No direct actuator control.

## Model and Mode

Target model: Qwen2.5-VL 7B Instruct (GGUF, CPU-only).  
1–2 photos per wake-cycle; output: strict JSON (`vision_summary`) + textual reasoning for logs.

## Vision Contract

Task: analyze plant photo and return ONLY JSON.

```json
{
  "schema_version": "vision_v1",
  "ts": "...",
  "leaf_color": "green|yellowing|spots|unknown",
  "wilting": true,
  "pest_signs": "none|possible|likely",
  "fruit_count_est": 0,
  "flower_count_est": 0,
  "stress_score": 0.0,
  "notes": "short",
  "confidence": 0.0
}
```

## Memory

Two levels:
- Episodic (per wake-cycle)
- Semantic (aggregated seasonal facts)

Public log: no secrets, but sufficient detail of state/action/anomaly and reasoning.

---

# 7. Logging, Dataset, and Public Transparency

## Architecture

Two tracks:
- Private full-fidelity dataset (raw + state/action/anomaly + images + versions)
- Public dataset (state/action/anomaly + edited images + reports)

Format: JSONL + media folders by date.  
Frequency: state every 30 minutes + event-driven records.

## Minimal File Structure

```
/data/
  /private/
    states_YYYY-MM.jsonl
    actions_YYYY-MM.jsonl
    anomalies_YYYY-MM.jsonl
    sensors_raw_YYYY-MM.jsonl
    /images/YYYY-MM-DD/*.jpg
  /public/
    states_public_YYYY-MM.jsonl
    actions_public_YYYY-MM.jsonl
    anomalies_public_YYYY-MM.jsonl
    /images/YYYY-MM-DD/*.jpg
  metadata.json
  /schema/
```

## Public Guarantees

- Each public action references a specific state snapshot and reasoning.
- Publish failures (resets, disconnects).
- Publish baseline (rule-only) for comparison.
- Do not publish secrets (API keys, exact address, external cameras).

---

# 8. Work Plan (Start Now)

**Stage 1**  
Schemas (state/action/anomaly), JSONL logging, State Estimator (VPD, confidence, anomaly detector).

**Stage 2**  
Baseline Control (threshold + budget), Guardrails v1, mock executor.

**Stage 3**  
World Model v1 (hybrid + backtesting), weather integration.

**Stage 4**  
LLM Agent (vision → JSON), integration with baseline, MVP.
