# 📋 Stage 1 Gap Fixes: File Navigation

**Quick start**: All gaps have been fixed. Here's where to find everything.

---

## 📍 Key Files

### 1. Main Implementation Spec
**File**: `MVP_GITHUB_ISSUES_COMPLETE.md` ⭐ START HERE
- **What**: Updated 8 issues + 2 new issues with all gap fixes integrated
- **Status**: Ready to create GitHub issues from this
- **Contains**:
  - Issue 1: Repository Bootstrap
  - Issue 2: Core Contracts (StateV1, ActionV1, AnomalyV1, SensorHealthV1)
  - **Issue 2a (NEW)**: Observation & DeviceStatus Contracts
  - **Issue 2b (NEW)**: Confidence Scoring & Anomaly Thresholds (WITH ALGORITHMS)
  - Issue 3: JSONL Storage (+ error handling)
  - Issue 4: Sources (+ error handling)
  - Issue 5: State Estimator (+ VPD algorithm, ring buffer API, confidence scoring, anomaly detection)
  - Issue 6: Clock & Scheduler
  - Issue 7: Simulation Script (+ CLI arguments, main loop specification)
  - Issue 8: Integration Tests

### 2. Gap Fixes Mapping
**File**: `STAGE1_GAP_FIXES_SUMMARY.md`
- **What**: Summary of all 10 gaps and how each was fixed
- **Status**: Reference document
- **Contains**:
  - ✅ Gap #1 → Issue 2a (Observation Contract)
  - ✅ Gap #2 → Issue 2 (SensorHealthV1 structure)
  - ✅ Gap #3 → Issue 2b + Issue 5 (Anomaly thresholds)
  - ✅ Gap #4 → Issue 2b + Issue 5 (Confidence algorithm)
  - ✅ Gap #5 → Issue 5 (Ring buffer API)
  - ✅ Gap #6 → Issue 2a (DeviceStatus contract)
  - ✅ Gap #7 → Issue 2b + Issue 5 (VPD algorithm + reference cases)
  - ✅ Gap #8 → Issue 7 + Issue 5 (Orchestrator integration)
  - ✅ Gap #9 → Issue 7 (CLI arguments)
  - ✅ Gap #10 → Issue 2b + Issue 3 + Issue 4 (Error handling)

### 3. Updated Plan Document
**File**: `.github/prompts/plan-stage1ReadinessAssessment.prompt.md`
- **What**: Original Stage 1 readiness assessment + gap fixes update
- **Status**: Updated with section linking gaps to fixed issues
- **Contains**:
  - Original 10 gap analysis (detail)
  - Gap → Issue mapping (new section)
  - Implementation roadmap (phases and timeline)

### 4. Original Reference
**File**: `MVP_GITHUB_ISSUES.md` (unchanged)
- **What**: Original 8 issues (for reference/comparison)
- **Status**: Kept as baseline reference
- **Note**: `MVP_GITHUB_ISSUES_COMPLETE.md` is the updated version to use

---

## 🎯 How to Use These Files

### For Project Managers / Planning
1. Read `STAGE1_GAP_FIXES_SUMMARY.md` (overview)
2. Check `.github/prompts/plan-stage1ReadinessAssessment.prompt.md` (timeline)
3. Review roadmap table

### For Developers / Implementation
1. Read `MVP_GITHUB_ISSUES_COMPLETE.md` (detailed specs)
2. Start with **Issue 1** (Repository Bootstrap)
3. Priority path: Issue 1 → 2 → 2a → 2b → 3/4 → 5/6 → 7 → 8

### For QA / Testing
1. Review issue acceptance criteria in `MVP_GITHUB_ISSUES_COMPLETE.md`
2. Check required tests for each issue
3. Reference algorithms in Issue 2b for edge cases

### For Tech Leads / Architecture
1. Read `AGENTS.md` (system design, unchanged)
2. Review Issue 2b specifications (algorithms locked in)
3. Check Issue 7 main loop (orchestration, locked in)

---

## 📊 What Each Issue Requires

### Phase 1: Foundation (Weeks 1-2)
| Issue | Deliverable | Depends On |
|-------|-----|-----------|
| **Issue 1** | `pyproject.toml`, tests, package structure | None |
| **Issue 2** | 4 Pydantic models (State, Action, Anomaly, SensorHealth) | Issue 1 |
| **Issue 2a** | 2 Pydantic models (Observation, DeviceStatus) | Issue 1 |
| **Issue 2b** | 3 docs (VPD, anomaly, confidence) + reference fixtures | Issue 2 |

### Phase 2: Data Flow (Weeks 2-3)
| Issue | Deliverable | Depends On |
|-------|-----|-----------|
| **Issue 4** | Synthetic + Replay sources | Issue 2a |
| **Issue 3** | JSONL storage + rotation | Issue 2 |

### Phase 3: Core Logic (Weeks 3-4)
| Issue | Deliverable | Depends On |
|-------|-----|-----------|
| **Issue 5** | State estimator pipeline (VPD, ring buffer, confidence, anomaly, health) | Issue 2, 2a, 2b, 4 |
| **Issue 6** | Clock abstraction + scheduler | Issue 1 |

### Phase 4: Integration (Week 5)
| Issue | Deliverable | Depends On |
|-------|-----|-----------|
| **Issue 7** | `scripts/simulate_day.py` orchestrator | Issue 3, 4, 5, 6 |

### Phase 5: Quality Gate (Weeks 5-6)
| Issue | Deliverable | Depends On |
|-------|-----|-----------|
| **Issue 8** | 24h deterministic integration test + 90% coverage | All Phase 1-4 |

---

## 🔍 Key Specifications Inside `MVP_GITHUB_ISSUES_COMPLETE.md`

### Algorithms You'll Implement
- **VPD**: Magnus approximation formula (Issue 5 section)
- **Confidence**: Cumulative deduction algorithm (Issue 2b section)
- **Anomaly**: Threshold rules for soil, VPD, temp, rates (Issue 2b section)
- **Ring Buffer**: auto-rotate 48h history (Issue 5 section)

### Reference Test Cases
- **VPD**: 5 cases (20°C/50% → 1.01 kPa, etc.) in Issue 5
- **Anomaly**: Thresholds in Issue 2b (e.g., P1 < 10%, VPD > 3.5)

### CLI Arguments
- `--time-scale 120` (Issue 7)
- `--seed` (Issue 7)
- `--output-dir ./data/runs` (Issue 7)
- `--duration-hours 24` (Issue 7)
- `--scenario default` (Issue 7)
- `--verbose false` (Issue 7)

---

## ✅ Checklist for Implementation

- [ ] Review `MVP_GITHUB_ISSUES_COMPLETE.md` end-to-end
- [ ] Verify all gaps addressed (check `STAGE1_GAP_FIXES_SUMMARY.md`)
- [ ] Confirm Phase 1 issues are concrete and testable
- [ ] Create GitHub issues from `MVP_GITHUB_ISSUES_COMPLETE.md`
- [ ] Link issues: Issue 2 → 2a → 2b, then 3/4, then 5/6, then 7, then 8
- [ ] Assign developers to Phase 1 (can work in parallel: 1, 2, 2a, 2b)
- [ ] Set up project board with 5 phases
- [ ] Track progress against timeline

---

## 📌 Key Takeaways

✅ **All 10 gaps fixed**  
✅ **Specs lock in-ready**  
✅ **Algorithms & thresholds detailed**  
✅ **Reference cases provided**  
✅ **Error handling specified**  
✅ **CLI defined**  
✅ **8 core + 2 new issues ready**  
✅ **~6 weeks to complete Stage 1**

**Next action**: Create GitHub issues from `MVP_GITHUB_ISSUES_COMPLETE.md` and start Phase 1.

---

Questions? Check files in this order:
1. Quick overview → `STAGE1_GAP_FIXES_SUMMARY.md`
2. Detailed specs → `MVP_GITHUB_ISSUES_COMPLETE.md`
3. Algorithms → Issue 2b section in `MVP_GITHUB_ISSUES_COMPLETE.md`
4. Timeline → `.github/prompts/plan-stage1ReadinessAssessment.prompt.md`
