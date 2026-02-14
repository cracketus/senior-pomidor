# Anomaly Detection Thresholds

## Overview

Anomaly detection identifies deviations from safe operating ranges and physical implausibilities.
Each anomaly includes a **severity level** used for control response and alerting.

**Principle**: Deterministic, rule-based detection with well-defined thresholds and escalation paths.

---

## Severity Levels

| Level    | Value | Description | Action |
|----------|-------|-------------|--------|
| **INFO** | 0     | Informational; normal operation variation | Log and track |
| **WARN** | 1     | Warning; approaching limits; operator should monitor | Reduce automation confidence; log |
| **ERROR** | 2    | Error; outside safe range; control adjustment needed | Reduce budget; tighten constraints |
| **CRIT**  | 3    | Critical; immediate intervention required; safety risk | Disable risky automation; manual override |

---

## Soil Moisture Anomalies

### Threshold: Soil Moisture Too Low (P1 < 10%)

| Property | Value |
|----------|-------|
| **Threshold** | P1 < 10% |
| **Severity** | ERROR (2) |
| **Trigger Duration** | 5 minutes sustained |
| **Reason** | Plant at imminent risk of wilting; immediate watering needed |
| **Recovery** | P1 >= 15% for 10 minutes |
| **Control Impact** | Increase pump budget; reduce VPD stress tolerance |

```python
if soil_moisture_p1 < 0.10:
    anomaly = AnomalyV1(
        type="soil_moisture_low",
        severity=2,
        measurement_name="soil_moisture_p1",
        measurement_value=soil_moisture_p1,
        threshold=0.10,
    )
```

---

### Threshold: Soil Moisture Too High (P1 > 85%)

| Property | Value |
|----------|-------|
| **Threshold** | P1 > 85% |
| **Severity** | WARN (1) |
| **Trigger Duration** | 10 minutes sustained |
| **Reason** | Root zone waterlogging risk; disease and O₂ depletion |
| **Recovery** | P1 <= 75% for 15 minutes |
| **Control Impact** | Reduce watering; increase ventilation (reduce humidity) |

```python
if soil_moisture_p1 > 0.85:
    anomaly = AnomalyV1(
        type="soil_moisture_high",
        severity=1,
        measurement_name="soil_moisture_p1",
        measurement_value=soil_moisture_p1,
        threshold=0.85,
    )
```

---

### Threshold: Soil Moisture Differential (Two-Zone Distribution)

| Property | Value |
|----------|-------|
| **Threshold** | \|P1 - P2\| > 0.40 (relative) |
| **Severity** | WARN (1) |
| **Trigger Duration** | 15 minutes sustained |
| **Reason** | Likely uneven watering or biased root growth; risk of local drying or waterlogging |
| **Recovery** | Differential <= 0.30 for 20 minutes |
| **Control Impact** | Adjust watering pattern; investigate probe placement or plant health |

```python
if soil_moisture_p2 is not None and abs(soil_moisture_p1 - soil_moisture_p2) > 0.40:
    anomaly = AnomalyV1(
        type="soil_moisture_differential",
        severity=1,
        measurement_name="soil_moisture_differential",
        measurement_value=abs(soil_moisture_p1 - soil_moisture_p2),
        threshold=0.40,
    )
```

---

## Vapor Pressure Deficit (VPD) Anomalies

### Threshold: VPD Too High (>3.5 kPa)

| Property | Value |
|----------|-------|
| **Threshold** | VPD > 3.5 kPa |
| **Severity** | ERROR (2) |
| **Trigger Duration** | 20 minutes sustained |
| **Reason** | Excessive transpiration stress; risk of tip burn, flower drop, fruit cracking |
| **Recovery** | VPD <= 3.2 kPa for 15 minutes |
| **Control Impact** | Increase humidity (close vents); improve shade; reduce air temperature |

```python
if vpd > 3.5:
    anomaly = AnomalyV1(
        type="vpd_high",
        severity=2,
        measurement_name="vpd",
        measurement_value=vpd,
        threshold=3.5,
    )
```

---

### Threshold: VPD Too Low (<0.2 kPa)

| Property | Value |
|----------|-------|
| **Threshold** | VPD < 0.2 kPa |
| **Severity** | WARN (1) |
| **Trigger Duration** | 30 minutes sustained |
| **Reason** | Excessive humidity; poor gas exchange; fungal disease risk (powdery mildew, etc.) |
| **Recovery** | VPD >= 0.3 kPa for 20 minutes |
| **Control Impact** | Increase ventilation; reduce humidity; improve air circulation |

```python
if vpd < 0.2:
    anomaly = AnomalyV1(
        type="vpd_low",
        severity=1,
        measurement_name="vpd",
        measurement_value=vpd,
        threshold=0.2,
    )
```

---

## Air Temperature Anomalies

### Threshold: Temperature Too Low (<8°C)

| Property | Value |
|----------|-------|
| **Threshold** | air_temp < 8°C |
| **Severity** | ERROR (2) |
| **Trigger Duration** | 30 minutes sustained |
| **Reason** | Growth stalls or stops; plant metabolic shutdown risk |
| **Recovery** | air_temp >= 12°C for 20 minutes |
| **Control Impact** | Activate heater; close vents; use thermal blankets |

```python
if air_temperature < 8.0:
    anomaly = AnomalyV1(
        type="temperature_low",
        severity=2,
        measurement_name="air_temperature",
        measurement_value=air_temperature,
        threshold=8.0,
    )
```

---

### Threshold: Temperature Too High (>32°C)

| Property | Value |
|----------|-------|
| **Threshold** | air_temp > 32°C |
| **Severity** | ERROR (2) |
| **Trigger Duration** | 20 minutes sustained |
| **Reason** | Heat stress; flower/pollen sterility; metabolic damage |
| **Recovery** | air_temp <= 28°C for 15 minutes |
| **Control Impact** | Open vents; increase evaporative cooling (misting); reduce light |

```python
if air_temperature > 32.0:
    anomaly = AnomalyV1(
        type="temperature_high",
        severity=2,
        measurement_name="air_temperature",
        measurement_value=air_temperature,
        threshold=32.0,
    )
```

---

### Threshold: Rapid Temperature Change (>3°C in 10 min)

| Property | Value |
|----------|-------|
| **Threshold** | \|ΔT\| > 3°C over 10 minutes |
| **Severity** | WARN (1) |
| **Trigger Duration** | Single occurrence |
| **Reason** | Sudden environment change; sensor malfunction possible; physiological shock risk |
| **Recovery** | Temperature stabilizes (slope < 0.3°C/min for 5 min) |
| **Control Impact** | Check sensors; investigate environment (door open?); gradual adjustment recommended |

```python
if abs(current_temp - temp_10min_ago) > 3.0:
    anomaly = AnomalyV1(
        type="temperature_rate_high",
        severity=1,
        measurement_name="air_temperature",
        measurement_value=abs(current_temp - temp_10min_ago),
        threshold=3.0,
    )
```

---

## Sensor Fault Detection

Faults degrade confidence and may trigger anomalies if critical.

### Stuck-At Fault

| Property | Value |
|----------|-------|
| **Detection** | Reading hasn't changed > ε for 60+ minutes |
| **Severity** | WARN (1) → ERROR (2) if critical sensor |
| **ε tolerance** | ±0.2% for soil; ±0.1°C for temp |
| **Recovery** | Value changes by > 2×ε |
| **Cause** | Sensor failure, loose connector, frozen electronics |

```python
def detect_stuck_at(history, sensor_name, tolerance, window_minutes=60):
    recent = history.get_since(now() - timedelta(minutes=window_minutes))
    if len(recent) < 2:
        return False
    values = [r[sensor_name] for r in recent]
    return max(values) - min(values) <= tolerance
```

---

### Jump Fault

| Property | Value |
|----------|-------|
| **Detection** | Unphysical spike: \|ΔV\| > max_reasonable change |
| **Severity** | ERROR (2) |
| **Single occurrence** | Immediate trigger |
| **Recovery** | Next reading within plausible range |
| **Cause** | Noise spike, glitch, EMI, sensor malfunction |
| **Reasonable Changes** | Soil: ±0.3/min; Temp: ±1°C/min; RH: ±5%/min |

```python
max_reasonable = {
    "soil_moisture": 0.3,
    "air_temperature": 1.0,
    "air_humidity": 5.0,
}
if abs(current_value - prev_value) > max_reasonable[sensor]:
    anomaly(type="sensor_jump", severity=2)
```

---

### Drift Fault

| Property | Value |
|----------|-------|
| **Detection** | Consistent bias over hours: slope > threshold |
| **Severity** | WARN (1) |
| **Detection Window** | 4+ hours |
| **Slope Threshold** | Soil: ±0.02/hour; Temp: ±0.5°C/hour |
| **Recovery** | Slope reverses or stabilizes |
| **Cause** | Calibration drift, sensor aging, temperature compensation failure |

```python
def detect_drift(history, sensor_name, window_hours=4, slope_threshold=0.02):
    recent = history.get_last_n_hours(window_hours)
    if len(recent) < 3:
        return False
    # Linear regression on (time, value)
    slope = compute_slope(recent)
    return abs(slope) > slope_threshold
```

---

### Sensor Disconnect

| Property | Value |
|----------|-------|
| **Detection** | Reading unavailable (None) or timeout |
| **Severity** | ERROR (2) if critical (P1, air_temp); WARN (1) if optional (CO₂, light) |
| **Trigger Duration** | 2 consecutive missing readings |
| **Recovery** | Valid reading received |
| **Cause** | Cable unplugged, radio link lost, I²C failure, sensor power loss |

```python
if observation.soil_moisture_p1 is None and prev_was_none:
    anomaly(type="sensor_disconnect", severity=2, measurement_name="soil_moisture_p1")
```

---

## Orchestration and Escalation

### Event-Driven Mode Triggers

The estimator enters **event-driven mode** (increase sampling frequency) when:

- **Any ERROR-level anomaly** (soil too low/high, VPD/temp extremes, sensor jump)
- **Multiple WARN anomalies** (≥ 3 simultaneous warnings)
- **Sensor disconnect** on critical sensor (P1, air_temp)

### Safe Mode Triggers

System enters **SAFE MODE** (disable risky control, manual override) when:

- **Critical-level anomaly** (if defined future severity=3)
- **Confidence < 0.3** due to sensor faults
- **MCU disconnected** for > 2 minutes
- **Unrecoverable error** (e.g., storage full)

---

## Reference Implementation

These thresholds are implemented in [issue #5 (State Estimator)](./issues.md#issue-5).

See also:
- [Confidence Scoring Algorithm](./confidence_scoring.md)
- Anomaly Scenarios: [tests/fixtures/anomaly_test_scenarios.py](../tests/fixtures/anomaly_test_scenarios.py)
