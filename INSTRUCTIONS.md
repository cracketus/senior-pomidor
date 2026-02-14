# 📖 Development Instructions

A quick start and reference guide for developers working on Tomato Brain.

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

- Python 3.11 or higher
- `pip` and `venv`
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/senior-pomidor
cd senior-pomidor

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the project in development mode with all dependencies
pip install -e .

# Verify installation
python -c "import brain; print('✓ brain package imported successfully')"
```

---

## 🧪 Running Tests

### All tests

```bash
pytest
```

### With coverage report

```bash
pytest --cov=brain --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Specific test file

```bash
pytest tests/estimator/test_vpd.py -v
```

### Run only tests matching a pattern

```bash
pytest -k "deterministic" -v
```

### Run integration tests

```bash
pytest tests/integration/ -v
```

---

## 🔍 Linting and Code Quality

### Run ruff checker

```bash
ruff check brain/ tests/
```

### Run ruff formatter

```bash
ruff format brain/ tests/
```

### Both at once

```bash
ruff check brain/ tests/ && ruff format brain/ tests/
```

---

## ⚡ Running Simulations

### Understanding the Decision Cycle

The brain operates on a **2-hour decision cycle**:
1. Read current observations and device state
2. Estimate plant state (State Estimator)
3. Forecast 36 hours ahead (World Model)
4. Compute optimal actions (Control Layer)
5. Validate safety constraints (Guardrails)
6. Analyze plant photo if available (LLM Agent)
7. Persist all state/action/anomaly records (Storage)

In **event-driven mode** (anomaly detected), the cycle tightens to **5–15 minutes** to respond quickly to:
- Wind spikes
- Severe anomalies (disconnects, overheating)
- Sensor failures

### Quick 24-hour simulation (accelerated)

Run with default settings (logs saved to `data/runs/`):

```bash
python scripts/simulate_day.py
```

This executes 12 decision cycles (24h ÷ 2h) plus any event-driven cycles.

### Custom time scale (speeds up or slows down)

```bash
# Run a 24-hour day in 10 wall-clock minutes (time_scale=144)
python scripts/simulate_day.py --time-scale 144

# Run at near real-time (time_scale=1)
python scripts/simulate_day.py --time-scale 1
```

### Custom output directory

```bash
python scripts/simulate_day.py --output-dir ./my_results
```

### Reproducible with fixed seed

```bash
# Same seed = same observations = same state logs
python scripts/simulate_day.py --seed 42
```

### All options

```bash
python scripts/simulate_day.py --help
```

---

## 📁 Project Structure Reference

```
senior-pomidor/
├── brain/                  # Main package
│   ├── __init__.py
│   ├── contracts/          # Pydantic models (source of truth)
│   │   ├── state_v1.py
│   │   ├── action_v1.py
│   │   ├── anomaly_v1.py
│   │   ├── sensor_health_v1.py
│   │   └── vision_v1.py          # LLM vision output
│   ├── storage/            # JSONL storage and dataset management
│   │   ├── jsonl_writer.py
│   │   ├── rotation.py
│   │   └── dataset_manager.py
│   ├── sources/            # Observation sensors (real or synthetic)
│   │   ├── interface.py
│   │   ├── synthetic_source.py
│   │   └── replay_source.py
│   ├── estimator/          # State estimation pipeline (Agent #2)
│   │   ├── vpd.py
│   │   ├── ring_buffer.py
│   │   ├── confidence.py
│   │   ├── anomaly_detector.py
│   │   └── pipeline.py
│   ├── world_model/        # 36h forecasting engine (Agent #3)
│   │   ├── hybrid_forecast.py
│   │   ├── soil_dynamics.py
│   │   └── stress_assessment.py
│   ├── control/            # MPC-lite decision layer (Agent #4)
│   │   ├── objective.py
│   │   ├── beam_search.py
│   │   └── budget_planner.py
│   ├── guardrails/         # Safety validation (Agent #5)
│   │   ├── constraints.py
│   │   └── safe_mode.py
│   ├── llm_agent/          # Vision analysis (Agent #6)
│   │   ├── qwen_local.py
│   │   └── vision_contract.py
│   ├── clock/              # Virtual and real clock (Agent #8)
│   │   ├── clock.py        # Abstract Clock interface
│   │   ├── real_clock.py
│   │   └── sim_clock.py
│   └── scheduler/          # Event loop and 2h cycle (Agent #8)
│       ├── event_loop.py
│       └── scheduler.py
├── scripts/
│   └── simulate_day.py     # End-to-end 24h simulation (Orchestrator)
├── tests/                  # Test suite
│   ├── test_smoke_import.py
│   ├── contracts/
│   ├── storage/
│   ├── sources/
│   ├── estimator/
│   ├── world_model/
│   ├── control/
│   ├── guardrails/
│   ├── llm_agent/
│   ├── clock/
│   ├── scheduler/
│   ├── scripts/
│   └── integration/
├── data/                   # Data artifacts (generated by scripts)
│   ├── private/            # Full-fidelity dataset (all fields)
│   │   ├── states_YYYY-MM.jsonl
│   │   ├── actions_YYYY-MM.jsonl
│   │   ├── anomalies_YYYY-MM.jsonl
│   │   └── images/
│   ├── public/             # Public-safe exports (filtered)
│   │   ├── states_public_YYYY-MM.jsonl
│   │   ├── actions_public_YYYY-MM.jsonl
│   │   └── anomalies_public_YYYY-MM.jsonl
│   └── schema/             # JSON schema documentation
├── pyproject.toml          # Python project metadata and dependencies
├── README.md
├── AGENTS.md               # System architecture and agent descriptions
├── INSTRUCTIONS.md         # Developer guide
├── SKILLS.md               # Capability inventory and roadmap
└── TECHNICAL_SPECIFICATION.md  # Detailed requirements
```

---

## 🛠 Common Development Tasks

### Adding a new contract

1. Create model in `brain/contracts/my_contract_v1.py`
2. Use Pydantic v2 with strict validation
3. Include `schema_version` and ISO8601 timestamp fields
4. Add tests in `tests/contracts/test_my_contract_v1.py`
5. Verify JSON Schema export works: `model.model_json_schema()`

### Adding a new test

1. Create file under appropriate `tests/` subdirectory
2. Name it `test_*.py` (pytest discovery convention)
3. Use descriptive test names: `test_<system>_<scenario>_<expected_outcome>`
4. Use fixtures for shared setup
5. Run: `pytest tests/path/test_file.py -v`

### Running a subset of the codebase

**Import a specific module**:
```python
from brain.estimator.vpd import calculate_vpd
from brain.storage.jsonl_writer import JSONLWriter
```

**Check if it works**:
```bash
python -c "from brain.estimator.vpd import calculate_vpd; print(calculate_vpd(20, 50))"
```

### Inspecting JSONL output

After running a simulation, inspect the generated data:

```bash
# List dataset runs
ls data/runs/

# View a state log
head -5 data/runs/run_20260214/state.jsonl

# Parse and pretty-print a JSON record
jq . data/runs/run_20260214/state.jsonl | head -1
```

---

## 🐛 Debugging & Troubleshooting

### Tests fail with import error

Make sure the package is installed in development mode:
```bash
pip install -e .
```

### Simulation script complains about missing modules

Verify all dependencies are installed:
```bash
pip list | grep -E "pytest|pydantic|ruff"
```

### JSONL files are unreadable

Validate the JSONL format (should be line-delimited JSON):
```bash
python -c "
import json
with open('data/runs/run_20260214/state.jsonl') as f:
    for i, line in enumerate(f):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f'Line {i+1} invalid: {e}')
"
```

### Code is formatted differently after `ruff format`

That's expected. Commit the changes and move on—ruff enforces consistent style.

---

## 📝 Code Guidelines

### Naming Conventions

- **Contracts**: PascalCase with `V<N>` suffix (e.g., `StateV1`, `ActionV1`)
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: prefix with `_`

### Typing

Always include type hints:

```python
from brain.contracts import StateV1, AnomalyV1
from typing import Optional

def estimate_state(
    observation: Observation,
) -> tuple[StateV1, list[AnomalyV1]]:
    # Implementation
    pass
```

### Docstrings

Use clear, concise docstrings:

```python
def calculate_vpd(temp_c: float, rh_percent: float) -> float:
    """
    Calculate vapor pressure deficit.
    
    Args:
        temp_c: Temperature in Celsius
        rh_percent: Relative humidity as percentage (0-100)
    
    Returns:
        VPD in kilopascals (kPa)
    
    Raises:
        ValueError: If inputs are out of realistic plant range
    """
```

### Testing

- Aim for high coverage (70%+)
- Test happy path, edge cases, and error conditions
- Use descriptive assertion messages
- Avoid test interdependencies

---

## 🔄 Workflow: Adding a Feature

1. **Create a branch**: `git checkout -b feature/my-feature`
2. **Write tests first** (or alongside): `tests/my_module/test_new_feature.py`
3. **Implement**: Add code to `brain/my_module/`
4. **Check imports**: `ruff check brain/ tests/`
5. **Format**: `ruff format brain/ tests/`
6. **Test**: `pytest tests/my_module/ -v`
7. **Run full suite**: `pytest --cov=brain`
8. **Commit**: `git add . && git commit -m "feat: describe your feature"`

---

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Overview, philosophy, and MVP scope |
| [AGENTS.md](AGENTS.md) | Agent architecture and data flow |
| [INSTRUCTIONS.md](INSTRUCTIONS.md) | This file—how to develop |
| [SKILLS.md](SKILLS.md) | Current capabilities and roadmap |
| [TECHNICAL_SPECIFICATION.md.md](TECHNICAL_SPECIFICATION.md.md) | Detailed acceptance criteria for each module |

---

## ❓ Getting Help

- **Understanding architecture**: See [AGENTS.md](AGENTS.md)
- **Understanding capabilities**: See [SKILLS.md](SKILLS.md)
- **Understanding requirements**: See [TECHNICAL_SPECIFICATION.md.md](TECHNICAL_SPECIFICATION.md.md)
- **Understanding contracts**: Look at docstrings in `brain/contracts/`
- **Understanding estimator logic**: Look at unit tests in `tests/estimator/`

---

## ✅ Before Committing

Checklist:

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `ruff format brain/ tests/`
- [ ] No linting errors: `ruff check brain/ tests/`
- [ ] Commit message is clear and follows conventions
- [ ] Related tests are added/updated
- [ ] No unrelated changes are included

---

## 🚀 Submitting a PR

1. Push your feature branch
2. Open a pull request against `main`
3. Link related GitHub issues if applicable
4. Ensure all CI checks pass
5. Request review from team

---

Good luck! 🌱
