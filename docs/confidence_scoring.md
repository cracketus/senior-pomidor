# Confidence Scoring Algorithm

## Overview

The confidence score represents the reliability and trustworthiness of an estimated `StateV1` snapshot.
A confidence of 1.0 means fully trusted; 0.0 means unreliable.

**Principle**: Confidence degrades when sensors are old, noisy, extreme, inconsistent, or faulty.

---

## Algorithm

### Base Confidence
Every state estimate starts with a base confidence:

$$\text{confidence} = 1.0$$

### Deductions

Deductions are applied for various risk factors. Each deduction is subtracted from the base:

#### 1. **Age Deduction** (Age of most recent sensor observation)
- **0–5 minutes**: 0.0 deduction (fresh)
- **5–15 minutes**: 0.05 deduction (acceptable)
- **15–30 minutes**: 0.10 deduction (stale)
- **30–60 minutes**: 0.20 deduction (very stale)
- **> 60 minutes**: 0.50 deduction (unreliable)

#### 2. **Extreme Value Deduction** (Sensor reading is outside normal operating range)
- Soil moisture < 10% **or** > 90%: 0.20 deduction
- Air temp < 8°C **or** > 32°C: 0.20 deduction
- Humidity < 10% **or** > 95%: 0.15 deduction
- VPD > 3.5 kPa **or** < 0.2 kPa: 0.15 deduction

#### 3. **High Variance Deduction** (Sensor noise or instability)
- Standard deviation of last N readings (typically 10) exceeds expected range:
  - Soil moisture std > 0.15: 0.15 deduction
  - Air temp std > 2.0°C: 0.15 deduction
  - Humidity std > 10%: 0.10 deduction

#### 4. **Cross-Sensor Disagreement Deduction** (Multiple sensors conflict)
- Soil probe P1 and P2 differ by > 40% **relative**: 0.30 deduction
- Air temp and soil temp disagree by > 8°C: 0.20 deduction

#### 5. **Sensor Fault Deduction** (Sensor has known fault)
- **Stuck-at** (reading hasn't changed in 60+ minutes): 0.50 deduction
- **Jump** (sudden unphysical spike): 0.30 deduction
- **Drift** (slow systematic error over hours): 0.25 deduction
- **Disconnect** (sensor offline/missing): 0.70 deduction

#### 6. **Anomaly Present Deduction** (Another detected anomaly exists)
- Minor anomaly (warning-level): 0.10 deduction
- Major anomaly (error-level): 0.25 deduction
- Critical anomaly (failure): 0.50 deduction

### Final Calculation

$$\text{confidence} = \max(0.0, 1.0 - \sum \text{deductions})$$

**Constraint**: Confidence is clamped to [0.0, 1.0].

---

## Examples

### Example 1: Fresh, Normal Conditions
- Age: 2 minutes → 0.0 deduction
- Soil P1: 55% (normal) → 0.0 deduction
- Air temp: 22°C (normal) → 0.0 deduction
- Humidity: 65% (normal) → 0.0 deduction
- Variance: all low → 0.0 deduction
- Cross-sensor: P1=55%, P2=54% (close) → 0.0 deduction
- No faults → 0.0 deduction
- No anomalies → 0.0 deduction

**Result**: $1.0 - 0.0 = \boxed{1.0}$ (fully trusted)

---

### Example 2: Stale Data with Slight Disagreement
- Age: 25 minutes → 0.10 deduction
- Soil P1: 48% (normal) → 0.0 deduction
- Air temp: 21°C (normal) → 0.0 deduction
- Humidity: 68% (normal) → 0.0 deduction
- Variance: low → 0.0 deduction
- Cross-sensor: P1=48%, P2=62% (diff=14%, <40%) → 0.0 deduction
- Soil P1 sensor shows minor drift → 0.25 deduction
- Minor anomaly detected (humidity slightly high) → 0.10 deduction

**Result**: $1.0 - (0.10 + 0.25 + 0.10) = \boxed{0.55}$ (moderately trusted, requires caution)

---

### Example 3: Extreme Conditions + Sensor Fault
- Age: 8 minutes → 0.05 deduction
- Soil P1: 8% (very dry, <10%) → 0.20 deduction
- Air temp: 35°C (>32°C) → 0.20 deduction
- Humidity: 25% (<10%+tolerance, edge case) → 0.15 deduction
- Variance: high due to oscillating pump cycles → 0.15 deduction
- Cross-sensor: P1=8%, P2=offline → 0.70 deduction (disconnect)
- No additional faults → 0.0 deduction
- Major anomaly: critical drought stress detected → 0.25 deduction

**Result**: $1.0 - (0.05 + 0.20 + 0.20 + 0.15 + 0.15 + 0.70 + 0.25) = \max(0.0, -0.70) = \boxed{0.0}$ (unreliable)

---

### Example 4: Degraded but Operational
- Age: 12 minutes → 0.05 deduction
- Soil P1: 62% (normal) → 0.0 deduction
- Air temp: 18°C (normal) → 0.0 deduction
- Humidity: 72% (normal) → 0.0 deduction
- Variance: moderate → 0.10 deduction
- Cross-sensor: P1=62%, P2=58% (diff=4%, <40%) → 0.0 deduction
- Soil P2 showing slow drift → 0.25 deduction
- No anomalies → 0.0 deduction

**Result**: $1.0 - (0.05 + 0.10 + 0.25) = \boxed{0.60}$ (moderately trusted)

---

## Interpretation

| Confidence Range | Status           | Recommendation |
|------------------|------------------|----------------|
| 0.9–1.0          | ✅ Excellent     | Use for critical decisions; full reliance |
| 0.75–0.89        | ✅ Good          | Use for normal operations; minor caution |
| 0.60–0.74        | ⚠️ Fair          | Use with judgement; consider secondary sources |
| 0.40–0.59        | ⚠️ Poor          | Use with caution; recommend human review |
| 0.0–0.39         | ❌ Very Poor     | Do not rely on for critical control decisions |
| 0.0              | ❌ Unreliable    | Disable automated control; manual mode only |

---

## Implementation Notes

1. **Accumulation**: Deductions are additive. Multiple faults compound.
2. **Clamping**: Result is always in [0.0, 1.0].
3. **Determinism**: For fixed input sequences, confidence must be reproducible.
4. **Hysteresis** (optional): To avoid control jitter, apply a small deadband:
   - If confidence changes by < 0.05, ignore the change unless crossing a critical threshold (0.0 or 0.75).
5. **Logging**: Every confidence score calculation should log deductions for debugging.

---

## Future Refinements

- **Adaptive ranges**: Adjust thresholds based on plant growth stage (seedling, veg, flowering).
- **Seasonal calibration**: VPD thresholds may vary by climate region.
- **ML-based scoring**: Replace rule-based deductions with learned confidence models.
