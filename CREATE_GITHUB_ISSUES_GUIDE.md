# Creating GitHub Issues: Quick Start Guide

Choose your preferred method below to create the 10 Stage 1 issues.

---

## ⚡ Method 1: Automatic (Recommended)

### Prerequisites
1. **Install GitHub CLI**  
   https://cli.github.com/

2. **Authenticate**  
   ```bash
   gh auth login
   ```
   Follow prompts to authenticate with your GitHub account.

3. **Verify authentication**
   ```bash
   gh auth status
   ```

### Create All Issues at Once

```bash
cd senior-pomidor
python scripts/create_github_issues.py
```

**Options:**
```bash
# Dry run (preview without creating)
python scripts/create_github_issues.py --dry-run

# See help
python scripts/create_github_issues.py --help
```

**Output:**
- ✅ 10 issues created with correct titles, descriptions, and labels
- Each issue labeled with `stage-1` and `issue-N`
- Dependencies documented in issue bodies

---

## 📋 Method 2: Manual (Copy-Paste)

If you prefer to create issues manually, see `GITHUB_ISSUES_EXPORT.md` in this directory. Contains:
- Issue titles (copy-paste ready)
- Issue bodies (markdown formatted)
- Dependencies (for linking)

Open each issue in GitHub UI and fill in the template.

---

## 📊 Method 3: Import Script (Alternative)

If GitHub CLI doesn't work, use this Python script to generate a formatted export:

```bash
python scripts/export_issues_for_manual_creation.py
```

This generates a `GITHUB_ISSUES_EXPORT.md` file that you can copy-paste into GitHub.

---

## ✨ What Gets Created

Running `create_github_issues.py` creates:

### Phase 1: Foundation (Weeks 1-2)
- **Issue 1**: Repository Bootstrap
- **Issue 2**: Core Pydantic Contracts (State, Action, Anomaly, SensorHealth)
- **Issue 2a** ⭐ NEW: Observation & Device Status Contracts
- **Issue 2b** ⭐ NEW: Confidence Scoring & Anomaly Thresholds Specs

### Phase 2: Data Flow (Weeks 2-3)
- **Issue 3**: JSONL Storage Layer
- **Issue 4**: Synthetic and Replay Data Sources

### Phase 3: Core Logic (Weeks 3-4)
- **Issue 5**: State Estimator Core (VPD, ring buffer, confidence, anomaly, health)
- **Issue 6**: Virtual Clock and Scheduler

### Phase 4 & 5: Integration & QA
- **Issue 7**: End-to-End Simulation Script
- **Issue 8**: Integration Test (24h Deterministic Run)

---

## 🔍 Post-Creation Checklist

After issues are created:

- [ ] All 10 issues appear in your GitHub repository
- [ ] Each issue has the correct title and description
- [ ] Issues are labeled with `stage-1` and `issue-N`
- [ ] Dependencies are documented in issue bodies
- [ ] Issues reference each other (e.g., Issue 2 → Issue 3 dependency)
- [ ] Create GitHub Project board (optional):
  - Create 5 columns: Backlog, Phase 1, Phase 2, Phase 3, Done
  - Assign issues to columns by phase

---

## 🐛 Troubleshooting

### "gh command not found"
- Install GitHub CLI: https://cli.github.com/
- Verify: `gh --version`

### "Authentication failed"
- Run: `gh auth login`
- Choose web-based auth
- Follow prompts

### "Error creating issue"
- Check:
  - Are you authenticated? `gh auth status`
  - Are you in the repository? `pwd` should show `.../senior-pomidor`
  - Do you have push access to the repo?

### Script doesn't parse issues correctly
- Verify `MVP_GITHUB_ISSUES_COMPLETE.md` exists
- Check markdown format is valid
- Try dry-run first: `python scripts/create_github_issues.py --dry-run`

---

## 📌 What's in Each Issue

Each issue in GitHub will contain:
- ✅ **Title**: Descriptive, action-oriented
- ✅ **Context / Why**: Background and motivation
- ✅ **Scope**: Exact deliverables
- ✅ **Non-goals**: What's explicitly NOT included
- ✅ **Acceptance Criteria**: Testable checklist
- ✅ **Required Tests**: Specific test names
- ✅ **Definition of Done**: What "complete" means
- ✅ **Dependencies**: Which issues must be done first

---

## 🎯 Next Steps (After Creating Issues)

1. **Set up project board** (optional but recommended)
   - `gh project create --title "Stage 1" --format table`
   - Organize by phase

2. **Assign issues to team members**
   - Phase 1 (Issues 1-2b) can be parallelized

3. **Create milestones** (optional)
   - Milestone: "Stage 1 - Core Foundation"
   - Assign issues 1-8

4. **Start Phase 1 immediately**
   - Issue 1: Repository Bootstrap
   - Issues 2, 2a, 2b: Contracts & Specs (parallel)

---

## 💡 Pro Tips

- **First time**: Run `--dry-run` to preview
- **GitHub CLI**: Faster and more reliable than UI
- **Batch creation**: Creates all 10 issues in seconds
- **Labels**: Auto-added for tracking in project board
- **Reference**: Each issue body is fully self-contained

---

## ❓ Questions?

- **Issue content**: Check `MVP_GITHUB_ISSUES_COMPLETE.md`
- **Dependencies**: See issue body sections
- **Timeline**: Check `.github/prompts/plan-stage1ReadinessAssessment.prompt.md`
- **Gaps**: See `STAGE1_GAP_FIXES_SUMMARY.md`

---

**Ready?** Run: `python scripts/create_github_issues.py`
