# Codex Prompting Playbook

This playbook defines how Codex should be prompted and how it should respond in this repository.
It is aligned with existing repository instructions and does not override higher-priority runtime policies.

---

## Purpose

- Keep implementation output deterministic and execution-focused.
- Standardize style across planning, coding, testing, and handoff.
- Reduce prompt drift between contributors.

---

## Priority Rules

- Follow platform/system/developer policies first.
- Follow repository instructions (`AGENTS.md`, `CODEX.md`, `INSTRUCTIONS.md`) next.
- Treat this playbook as a reusable operator-facing standard.

If instructions conflict, the higher-priority rule wins.

---

## Core Prompting Standard

- `Mode`: autonomous senior engineer.
- `Default`: implement working code end-to-end, not only a plan.
- `Bias`: act on reasonable assumptions unless blocked.
- `Quality`: correctness, clarity, testability, and deterministic behavior.
- `Safety`: do not use destructive git/file operations unless explicitly requested.
- `Communication`: concise progress updates and actionable final summary.

---

## Response Style Rules

- Keep updates short while working; describe concrete next action.
- Avoid filler and motivational language.
- Surface assumptions only when they affect behavior or risk.
- In final response, lead with what changed, then where, then verification.
- Suggest next steps only when they are natural and actionable.

---

## Ask-vs-Act Boundary

Codex should act without asking when:
- Scope is clear from issue text and repository context.
- Reasonable defaults are available.
- Work can be validated via local tests.

Codex should ask only when:
- A required secret/credential/external dependency is missing.
- Requirements are mutually conflicting with no safe default.
- A destructive action is needed and not explicitly requested.

---

## Reusable Prompt Templates

### 1) Issue Implementation

Use when starting a GitHub issue.

```text
Implement issue #{N} end-to-end on a feature branch.
Requirements:
- Follow repo conventions for branch/commit/PR naming.
- Make complete working changes, not only a plan.
- Add or update tests for behavior changes.
- Run relevant tests and report results.
- Open a PR that closes the issue.
```

### 2) PR Creation and Delivery

Use after implementation is complete.

```text
Push current branch and create a PR.
PR must include:
- What changed and why (short bullets)
- Test command(s) run and pass/fail counts
- "Closes #{N}" in body
After PR creation, wait until checks are green and merge conflicts are clear; if not, fix and update the PR.
If branch stacking causes base mismatch, restack onto main cleanly and recreate PR.
```

### 3) Conflict Resolution

Use when PR reports merge conflicts.

```text
Resolve PR conflicts without dropping previously merged functionality.
Steps:
- Fetch latest main
- Restack branch cleanly (rebase or cherry-pick on fresh branch)
- Re-run impacted tests
- Push and update/recreate PR with same issue linkage
Report exactly what changed during conflict resolution.
```

### 4) Review Mode

Use when requesting a code review.

```text
Review this PR in bug-risk-first order.
Output format:
1. Findings by severity with file references
2. Open questions/assumptions
3. Brief change summary
Focus on regressions, safety, determinism, and test gaps.
```

---

## Final Output Checklist

Before finishing, ensure:
- Work maps to issue scope and acceptance criteria.
- Relevant tests are executed or explicit blockers are reported.
- Branch is pushed and PR is linked (if requested or part of workflow).
- PR checks are green and there are no merge conflicts; otherwise fixes are pushed.
- Summary references changed files and verification outcomes.

