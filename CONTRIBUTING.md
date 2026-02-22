# Contributing to Senior Pomidor

Thanks for contributing. This guide defines the baseline workflow for code, docs, and issue/PR quality.

## Local Setup

Prerequisite: Python 3.11+

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Quality Gates

Run before opening a pull request:

```bash
pytest
ruff check .
```

If you changed behavior, add or update tests in `tests/` and update relevant docs in `docs/` or `README.md`.

## Branch and Title Conventions

- Use focused branches for one issue/work item.
- For roadmap implementation issues, follow TOMATO title format:
  - `TOMATO-{N}: {Clear action-oriented title}`
- For non-roadmap improvements, use:
  - `Enhancement: {short title}`

## Commit and PR Expectations

- Keep commits atomic and scoped to one logical change.
- Reference issue IDs in PR body (`Fixes #...`) when applicable.
- Use `.github/PULL_REQUEST_TEMPLATE.md` and complete all checklist items.
- Avoid unrelated refactors in the same PR.

## Testing Expectations by Change Type

- Contracts/types: add or update schema/contract tests under `tests/contracts/`.
- Runtime behavior: add or update unit/integration coverage in relevant `tests/` modules.
- CLI/scripts: validate entrypoints and deterministic output expectations where applicable.
- Docs-only changes: run at least a quick sanity check (`pytest -q`) when feasible.

## Documentation Policy

When behavior, interfaces, or workflows change, update:

- `README.md` for user-facing usage
- `docs/` for operational details
- issue/PR templates if contribution flow changed

## Which Issue Template to Use

Use GitHub issue templates in `.github/ISSUE_TEMPLATE/`:

- `tomato_work_item.yml`: Roadmap implementation and stage tracking issues.
- `enhancement_request.yml`: Non-roadmap enhancements.
- `bug_report.md`: Reproducible defects.
- `feature_request.md`: General feature proposals.

See also: `docs/how_to_create_issue.md` for TOMATO naming, labels, and body structure.
