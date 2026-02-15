# CODEX

Pragmatic guide for Codex agents working in this repo.

---

## Conventions

- Branches: `TOMATO-{N}/short-description`
- Commits: `TOMATO-{N}: Short description`
- PR titles: `TOMATO-{N}: Title`

---

## Fast Commands

```bash
# Tests
pytest
pytest tests/sources -v

# Lint / format
ruff check brain/ tests/
ruff format brain/ tests/
```

---

## Where Things Live

- Contracts: `brain/contracts/`
- Observation sources: `brain/sources/`
- Storage: `brain/storage/`
- Tests: `tests/`
- Architecture: `AGENTS.md`
- Dev guide: `INSTRUCTIONS.md`
- Spec: `TECHNICAL_SPECIFICATION.md`

---

## Current vs Planned (Short)

Current code implements contracts, observation sources, and storage. Estimator, world model, control, guardrails, clock/scheduler, and simulation scripts are planned and tracked as TOMATO issues.

---

## Read These First

1. `README.md`
2. `AGENTS.md`
3. `INSTRUCTIONS.md`
4. `TECHNICAL_SPECIFICATION.md`
