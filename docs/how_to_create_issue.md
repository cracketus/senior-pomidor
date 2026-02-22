# How to Create a GitHub Issue in `cracketus/senior-pomidor`

This guide is based on patterns used in closed issues in this repository (for example: #10, #11, #12, #52, #53, #59, #67, #74).

## Issue templates in this repository

Use the template that matches the work:

- `TOMATO Work Item` (`.github/ISSUE_TEMPLATE/tomato_work_item.yml`): roadmap implementation and stage tracking.
- `Enhancement Request` (`.github/ISSUE_TEMPLATE/enhancement_request.yml`): non-roadmap enhancements.
- `Bug report` (`.github/ISSUE_TEMPLATE/bug_report.md`): reproducible defects.
- `Feature request` (`.github/ISSUE_TEMPLATE/feature_request.md`): general feature proposals.

## 1. Decide the issue type first

Use one of these three types:

1. Implementation issue (most common)
2. Stage tracking issue (parent/coordinator issue)
3. General enhancement issue (non-TOMATO naming)

## 2. Title format (required)

### A) Implementation issue

Use:

`TOMATO-{N}: {Clear action-oriented title}`

Examples from closed issues:

- `TOMATO-54: Define Stage 4 vision contracts and schema exports`
- `TOMATO-50: Implement weather client and forecast_36h normalization contract`
- `TOMATO-15: Build estimator core pipeline: Observation -> StateV1 + AnomalyV1[] + SensorHealthV1`

Rules:

- Keep `TOMATO-{N}` at the beginning.
- Use imperative wording (`Implement`, `Add`, `Define`, `Integrate`, `Normalize`).
- Keep scope specific enough to finish in one PR.

### B) Stage tracking issue (parent)

Use:

`TOMATO-{N}: Stage {X} tracking - {short scope}`

Examples:

- `TOMATO-49: Stage 3 tracking - weather integration and world-model baseline`
- `TOMATO-53: Stage 4 tracking - vision pipeline and explanation baseline`

### C) General enhancement (non-roadmap/non-TOMATO)

Use:

`Enhancement: {short title}`

Example:

- `Enhancement: Codex Agent prompting standards and templates`

## 3. Labeling rules

Observed labels in this repo:

- `stage 1`
- `stage 2`
- `stage 3`
- `stage 4`
- `stage 5`
- `enhancement`
- `duplicate` (only when closing as duplicate)

Recommended labeling policy now:

1. Roadmap implementation/tracking issues: add stage label (`stage 1`/`stage 2`/`stage 3`/`stage 4`/`stage 5`).
2. Feature work: also add `enhancement`.
3. Only use `duplicate` when the issue is truly a duplicate and will be closed quickly.

Note: older closed issues use stage-only labels in some places; newer issues often use `enhancement + stage` together.

## 4. Body structure (standard implementation issue)

Use this section order:

1. `## Context / Why`
2. `## Scope`
3. `## Non-goals`
4. `## Acceptance Criteria`
5. `## Required Tests`
6. `## Definition of Done` (recommended)
7. `## Dependencies` (if any)

### Required quality for each section

- Context / Why: explain why this issue exists now.
- Scope: concrete deliverables (files/modules/contracts/tests).
- Non-goals: explicitly list what is out of scope.
- Acceptance Criteria: checkbox list, objectively verifiable.
- Required Tests: exact test paths and, when useful, exact test names.
- Definition of Done: completion conditions for PR/merge readiness.
- Dependencies: refer to issue numbers when relevant.

## 5. Body template (copy/paste)

```md
## Context / Why
<Why this work is needed now.>

## Scope
- <Deliverable 1>
- <Deliverable 2>
- <Deliverable 3>

## Non-goals
- <Explicitly out-of-scope item 1>
- <Explicitly out-of-scope item 2>

## Acceptance Criteria
- [ ] <Measurable outcome 1>
- [ ] <Measurable outcome 2>
- [ ] <Measurable outcome 3>

## Required Tests
- `<test path or node 1>`
- `<test path or node 2>`

## Definition of Done
- <Code merged + tests pass + docs aligned, etc.>

## Dependencies
- <Issue refs or `None`>
```

## 6. Stage tracking issue template (copy/paste)

Use this only for parent/coordinator issues.

```md
## Context / Why
<Why this stage-level tracker is needed.>

## Scope
- Coordinate Stage <X> domain issues.
- Track acceptance gates across contracts/runtime/tests/docs.

## Non-goals
- <Out of scope for this tracker>

## Acceptance Criteria
- [ ] Linked Stage <X> domain issues are closed.
- [ ] Stage <X> runtime/contracts/tests/docs are aligned.

## Linked Stage <X> Domain Issues
- [ ] #<child-issue-1>
- [ ] #<child-issue-2>
- [ ] #<child-issue-3>

## Definition of Done
- Parent checklist complete and all linked child issues closed.

## Dependencies
- <Prior stage/issues if relevant>
```

## 7. TOMATO number selection

`TOMATO-{N}` is a workstream identifier in issue titles, not the GitHub issue number.

Before creating a new issue:

1. Find latest used TOMATO number in closed issues.
2. Pick next unused `N`.
3. Confirm no duplicates by searching similar title text.

Helpful commands:

```powershell
gh issue list --state all --limit 200 --repo cracketus/senior-pomidor
gh issue list --state all --search "TOMATO-" --repo cracketus/senior-pomidor
```

## 8. Create issue via CLI

Preferred approach: create from a body file.

```powershell
gh issue create --repo cracketus/senior-pomidor `
  --title "TOMATO-76: <your title>" `
  --label "enhancement" `
  --label "stage 5" `
  --body-file .github/ISSUE_BODY.md
```

Or for a non-TOMATO enhancement:

```powershell
gh issue create --repo cracketus/senior-pomidor `
  --title "Enhancement: <your title>" `
  --label "enhancement" `
  --body-file .github/ISSUE_BODY.md
```

## 9. Final pre-submit checklist

- Title follows one of the approved formats.
- Correct stage label is applied.
- `enhancement` label is applied for feature work.
- Scope and non-goals are explicit and non-overlapping.
- Acceptance criteria are testable and complete.
- Required tests are named.
- Dependencies and linked issues are listed when applicable.
