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
pytest tests/sources/test_synthetic_source.py -v
```

### Run only tests matching a pattern

```bash
pytest -k "deterministic" -v
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

## 🌿 Branch and Commit Conventions

All work must be tracked against GitHub issues using the `TOMATO-N` prefix system.

### Branch Naming Convention

Create branches using the issue prefix and a short description:

```bash
git checkout -b TOMATO-1/bootstrap-repository
git checkout -b TOMATO-2/pydantic-contracts
git checkout -b TOMATO-5/state-estimator-vpd
```

**Format**: `TOMATO-{number}/{short-description}`

- Use lowercase
- Use hyphens to separate words
- Keep description short (3-5 words)
- Do NOT use issue numbers in addition to the prefix

### Commit Message Convention

Every commit message must start with the issue prefix:

```bash
git commit -m "TOMATO-1: Bootstrap repository with pytest and ruff"
git commit -m "TOMATO-2: Add StateV1 Pydantic contract with validation"
git commit -m "TOMATO-5: Implement VPD calculation with reference cases"
```

**Format**: `TOMATO-{number}: {description}`

- Capitalize first word after colon
- Be concise but descriptive
- Reference what was changed or added
- Can include multiple commits per issue if logical units warrant it

### Pull Request Naming Convention

When creating a PR, use the issue prefix in the title:

```bash
gh pr create --title="TOMATO-1: Bootstrap production-ready repository skeleton" \
  --body="Implements requirements from Issue TOMATO-1"
```

**Format**: `TOMATO-{number}: {Title with proper capitalization}`

---

## ⚡ Running Simulations (Planned)

Simulation workflow will be added in TOMATO-16. When `scripts/simulate_day.py` exists, this section will be updated with runnable commands.

---

## 📁 Project Structure Reference

### Current

```
senior-pomidor/
├── brain/                  # Main package
│   ├── __init__.py
│   ├── contracts/          # Pydantic models (source of truth)
│   │   ├── state_v1.py
│   │   ├── action_v1.py
│   │   ├── anomaly_v1.py
│   │   ├── sensor_health_v1.py
│   │   ├── observation_v1.py
│   │   └── device_status_v1.py
│   ├── sources/            # Observation sources (real or synthetic)
│   │   ├── interface.py
│   │   ├── synthetic_source.py
│   │   └── replay_source.py
│   └── storage/            # JSONL storage and dataset management
│       ├── jsonl_writer.py
│       ├── dataset.py
│       └── export.py
├── docs/
│   ├── anomaly_thresholds.md
│   └── confidence_scoring.md
├── scripts/
├── tests/                  # Test suite
│   ├── contracts/
│   ├── sources/
│   ├── storage/
│   └── fixtures/
├── README.md
├── AGENTS.md
├── INSTRUCTIONS.md
├── SKILLS.md
└── TECHNICAL_SPECIFICATION.md
```

### Planned

- `brain/estimator/`
- `brain/world_model/`
- `brain/control/`
- `brain/guardrails/`
- `brain/llm_agent/`
- `brain/clock/`
- `brain/scheduler/`
- `scripts/simulate_day.py`
- `tests/estimator/`, `tests/world_model/`, `tests/control/`, `tests/guardrails/`, `tests/llm_agent/`, `tests/clock/`, `tests/scheduler/`, `tests/integration/`
- `PLANNED_FEATURES.md`

---

## Stage Kickoff Workflow (Starting a New Stage)

Before implementing any issue in a new stage, follow this process.

### Step 0: Check whether stage issues already exist

Use GitHub CLI to confirm whether the stage already has open or closed issues:

```bash
gh issue list --state all --repo cracketus/senior-pomidor --search "stage 3"
gh issue list --state all --repo cracketus/senior-pomidor --search "TOMATO-"
```

If stage issues already exist, continue with normal issue implementation workflow below.

### Step 1: If no stage issues exist, define stage requirements first

Before creating issues, write down:

1. Stage goals and scope boundaries
2. Acceptance criteria for the stage
3. Non-goals (explicitly out of scope)

Each planned issue for the stage must map to these requirements and acceptance criteria.

### Step 2: Create stage issues (maximum 10)

Create a focused issue set for the stage using the repository issue format:

- Use `TOMATO-{N}: ...` naming
- Apply the correct stage label (`stage 1`, `stage 2`, `stage 3`, `stage 4`, etc.)
- Use structured body sections (`Context / Why`, `Scope`, `Non-goals`, `Acceptance Criteria`, `Required Tests`, `Dependencies`)

Hard limit:

- Do not create more than 10 issues for a single stage.

If the stage is too large for 10 issues, split scope and defer remaining work to a later stage.

## Issue Implementation Workflow

When implementing a GitHub issue, follow this workflow:

### Step 1: View the issue details

```bash
gh issue view TOMATO-1
```

### Step 2: Create a feature branch

Use the `TOMATO-N/description` naming convention (see conventions above):

```bash
git checkout -b TOMATO-1/bootstrap-repository
git checkout -b TOMATO-2/pydantic-contracts
```

### Step 3: Implement the issue

- Work in the feature branch
- Commit frequently with clear messages following the `TOMATO-N:` convention
- Run tests: `pytest`
- Run linter: `ruff check . && ruff format .`

### Step 4: Create a Pull Request

Once the issue is complete and all tests pass:

```bash
gh pr create --title="TOMATO-1: Bootstrap production-ready repository skeleton" \
  --body="Implements requirements from TOMATO-1"
```

Or let GitHub prompt you interactively:

```bash
gh pr create
```

### Step 4.5: Squash all commits into one

**Before merging, all commits in the PR must be squashed into a single commit.**

This ensures a clean, linear history and one commit per issue.

```bash
# Count commits on current branch vs main
git log main..HEAD --oneline

# If more than 1 commit, squash them
git rebase -i HEAD~<number-of-commits>

# In the editor, keep the first commit as 'pick' and change the rest to 'squash' (or 's')
# Save and exit

# Force push to update the PR
git push --force-with-lease origin TOMATO-1/bootstrap-repository
```

**Verify** the PR now shows 1 commit in the GitHub UI.

### Step 5: Verify and merge

- Ensure all CI checks pass
- Verify PR shows **exactly 1 commit** before merging
- Review the PR description
- Merge via GitHub UI or CLI:

```bash
gh pr merge <pr-number> --merge
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
from brain.sources.synthetic_source import SyntheticSource
```

**Check if it works**:
```bash
python -c "from brain.sources.synthetic_source import SyntheticSource; print(SyntheticSource)"
```

---

## 🐛 Debugging & Troubleshooting

### Tests fail with import error

Make sure the package is installed in development mode:

```bash
pip install -e .
```

### Simulation script complains about missing modules

Simulation entrypoint is planned in TOMATO-16. If you see missing modules, verify dependencies are installed and check the issue status.

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

- Coverage gate: keep total coverage at or above 80% (`--cov-fail-under=80`)
- Test happy path, edge cases, and error conditions
- Use descriptive assertion messages
- Avoid test interdependencies

---

### Coverage Escalation Process

When a change cannot keep coverage >= 80%:
1. Add targeted tests where feasible in the same PR.
2. If still below threshold, do not merge silently: document the gap in the PR and open a follow-up TOMATO issue with an owner and due milestone.
3. Raise the follow-up priority if production-critical modules are affected.
## 🔁 Workflow: Adding a Feature

1. Create a branch: `git checkout -b TOMATO-19/short-description`
2. Write or update tests under `tests/`
3. Implement changes under `brain/` or `scripts/`
4. Run checks: `ruff check brain/ tests/ && ruff format brain/ tests/`
5. Run tests: `pytest tests/ -v`
6. Commit: `git add . && git commit -m "TOMATO-19: Describe your feature"`

---

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Overview, philosophy, and MVP scope |
| `AGENTS.md` | Agent architecture and data flow |
| `INSTRUCTIONS.md` | This file—how to develop |
| `SKILLS.md` | Current capabilities and roadmap |
| `TECHNICAL_SPECIFICATION.md` | Detailed requirements for each module |
| `PLANNED_FEATURES.md` | Planned stages and not-yet-implemented components |

---

## ❓ Getting Help

- **Understanding architecture**: See `AGENTS.md`
- **Understanding capabilities**: See `SKILLS.md`
- **Understanding requirements**: See `TECHNICAL_SPECIFICATION.md`
- **Understanding contracts**: Look at docstrings in `brain/contracts/`
- **Understanding storage logic**: Look at unit tests in `tests/storage/`

---

## ✅ Before Committing

Checklist:

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `ruff format brain/ tests/`
- [ ] No linting errors: `ruff check brain/ tests/`
- [ ] Commit message is clear and follows conventions
- [ ] Related tests are added or updated
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

