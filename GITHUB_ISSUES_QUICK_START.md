# GitHub Issues Creation: Step-by-Step Instructions

All Stage 1 GitHub issues have been prepared. Choose one method below to create them.

---

## 🚀 Quick Start (60 seconds)

**If you have GitHub CLI installed:**

```powershell
cd C:\MyProjects\senior-pomidor
python scripts/create_github_issues.py
```

**That's it.** 10 issues created automatically. ✅

---

## 📋 Method Comparison

| Method | Time | Ease | Prerequisites | Notes |
|--------|------|------|---------------|-------|
| **Automatic (CLI)** | 30 sec | ⭐⭐⭐ | GitHub CLI | **Recommended.** Fastest, no errors. |
| **Manual (UI)** | 10 min | ⭐⭐ | GitHub web access | Copy-paste each issue one-by-one. |
| **Export (Hybrid)** | 2 min | ⭐⭐⭐ | Python only | Generate export file, then copy-paste. |

---

## ✅ Method 1: Automatic with GitHub CLI (RECOMMENDED)

### Step 1: Install GitHub CLI (if not already installed)
https://cli.github.com/

**Verify installation:**
```powershell
gh --version
```

### Step 2: Authenticate
```powershell
gh auth login
```

Choose:
- Platform: **GitHub.com**
- Protocol: **HTTPS**
- Authenticate: **Y** (web browser opens)
- Follow prompts to authorize

**Verify auth:**
```powershell
gh auth status
```

### Step 3: Run the script
```powershell
cd C:\MyProjects\senior-pomidor
python scripts\create_github_issues.py
```

### Expected Output
```
Stage 1 GitHub Issues Creator

Reading issues from MVP_GITHUB_ISSUES_COMPLETE.md...
Found 10 issues

[1/10] Processing Issue 1...
✓ Created: Bootstrap production-ready Python 3.11 repository skeleton for Embodied AI Tomato Brain
  https://github.com/your-org/senior-pomidor/issues/1

[2/10] Processing Issue 2...
✓ Created: Define strict Pydantic v2 contracts for core messaging: state/action/anomaly/sensor health (v1 schemas)
  https://github.com/your-org/senior-pomidor/issues/2

... (8 more issues)

Summary:
  Successful: 10
  Failed: 0

All issues created!
```

### ✅ Done!
All 10 issues have been created with:
- Correct titles and descriptions
- Acceptance criteria and tests
- Labels: `stage-1`, `issue-N`
- Dependencies documented

---

## 📝 Method 2: Manual Creation (Copy-Paste via GitHub UI)

### Step 1: Generate Export File
```powershell
python scripts\export_issues_for_manual_creation.py
```

Creates: `GITHUB_ISSUES_EXPORT.md` (formatted for copy-paste)

### Step 2: Open GitHub Repository
Go to: `https://github.com/your-org/senior-pomidor`

### Step 3: For Each Issue

**3a. Click "New Issue"**

**3b. Copy Title from Export File**
Look for: `### GitHub UI - Title Field`
```
Copy: Bootstrap production-ready Python 3.11 repository skeleton...
```
Paste into GitHub **Title** field

**3c. Copy Body from Export File**
Look for: `### GitHub UI - Body Field`
```markdown
## Context / Why
...
## Scope
...
(etc.)
```
Select all, copy, paste into GitHub **Body** field

**3d. Add Labels**
In GitHub UI, find "Labels" section:
- Add: `stage-1`
- Add: `issue-1` (or `issue-2`, etc. for each issue)

**3e. Click "Submit new issue"**

### ⏱️ Repeat for All 10 Issues
- Issue 1: Bootstrap (3 min)
- Issue 2: Core Contracts (3 min)
- Issue 2a: Observation Contracts (2 min)
- Issue 2b: Thresholds & Specs (2 min)
- Issue 3: Storage (2 min)
- Issue 4: Sources (2 min)
- Issue 5: Estimator (3 min)
- Issue 6: Clock (2 min)
- Issue 7: Simulation (2 min)
- Issue 8: Integration Tests (2 min)

**Total: ~25 minutes**

---

## 🔧 Method 3: Preview Before Creating (Dry-Run)

To see what will be created without actually creating:

```powershell
python scripts\create_github_issues.py --dry-run
```

Output shows:
```
[DRY RUN MODE] Issues will NOT be created.

[1/10] Processing Issue 1...
[DRY RUN] Would create issue:
  Title: Bootstrap production-ready Python 3.11 repository skeleton...
  Body length: 1250 chars
  Labels: stage-1, issue-1

... (etc. for all 10)

Dry run complete. Run without --dry-run to create issues.
```

No actual issues created, just preview.

---

## 📊 What Gets Created

### Phase 1: Foundation (Weeks 1-2) ← Start here
- **Issue 1**: Repository Bootstrap
- **Issue 2**: Core Pydantic Contracts
- **Issue 2a**: Observation & Device Status Contracts ⭐ NEW
- **Issue 2b**: Confidence Scoring & Anomaly Thresholds ⭐ NEW

### Phase 2: Data Flow (Weeks 2-3)
- **Issue 3**: JSONL Storage Layer
- **Issue 4**: Synthetic and Replay Data Sources

### Phase 3: Core Logic (Weeks 3-4)
- **Issue 5**: State Estimator Core
- **Issue 6**: Virtual Clock and Scheduler

### Phase 4-5: Integration & QA (Weeks 5-6)
- **Issue 7**: End-to-End Simulation Script
- **Issue 8**: Integration Test (24h Run - Quality Gate)

---

## ✨ Each Issue Contains

Every created GitHub issue includes:
- ✅ Clear context and motivation
- ✅ Detailed scope (what's included)
- ✅ Non-goals (what's NOT included)
- ✅ Acceptance criteria (checklist)
- ✅ Required test names
- ✅ Definition of done (how to verify completion)
- ✅ Dependencies (which issues to do first)

---

## 🎯 After Issues Are Created

1. **View Issues**: https://github.com/your-org/senior-pomidor/issues

2. **Create Project Board** (optional):
   ```powershell
   gh project create --title "Stage 1 - Core Foundation"
   ```

3. **Organize by Phase**: Backlog → Foundation → Data Flow → Core Logic → Integration → Done

4. **Start Implementation**: Begin with Issue 1 in Phase 1

---

## 🐛 Troubleshooting

### "gh: command not found"
**Fix**: Install GitHub CLI from https://cli.github.com/

### "Not authenticated"
**Fix**: Run `gh auth login` and follow prompts

### "Error creating issue"
**Fix**: 
- Make sure you're authenticated: `gh auth status`
- Are you in the repo directory? `cd senior-pomidor`
- Do you have push access?

### Scripts doesn't work
**Fix**:
- Ensure `MVP_GITHUB_ISSUES_COMPLETE.md` exists
- Try dry-run first: `python scripts\create_github_issues.py --dry-run`

---

## 💡 Tips & Tricks

| Tip | Command |
|-----|---------|
| Dry run (preview) | `python scripts\create_github_issues.py --dry-run` |
| Export for manual creation | `python scripts\export_issues_for_manual_creation.py` |
| Check authentication | `gh auth status` |
| View created issues | `gh issue list --limit 20` |
| Open issue in browser | `gh issue view 1 --web` |

---

## 📌 Key Files

| File | Purpose |
|------|---------|
| `MVP_GITHUB_ISSUES_COMPLETE.md` | Source specification for all 10 issues |
| `scripts/create_github_issues.py` | Script to create all issues at once |
| `scripts/export_issues_for_manual_creation.py` | Export for manual copy-paste |
| `GITHUB_ISSUES_EXPORT.md` | Generated export file (optional) |
| `CREATE_GITHUB_ISSUES_GUIDE.md` | Detailed guide |
| `FILE_NAVIGATION.md` | Document navigation reference |

---

## ✅ Verification Checklist

After creating issues:

- [ ] All 10 issues appear in GitHub Issues page
- [ ] Each issue has correct title and description
- [ ] Issues are labeled with `stage-1`
- [ ] Issues are labeled with `issue-N`
- [ ] Phase 1 issues (1, 2, 2a, 2b) visible
- [ ] Can click through issues and read content
- [ ] Dependencies are documented in issue bodies

---

## 🚀 Ready?

**Automatic creation (recommended):**
```powershell
python scripts/create_github_issues.py
```

**Or generate export for manual creation:**
```powershell
python scripts/export_issues_for_manual_creation.py
```

---

## ❓ Need Help?

- **GitHub CLI issues?** See https://cli.github.com/manual/
- **Issue content?** See `MVP_GITHUB_ISSUES_COMPLETE.md`
- **Stage 1 roadmap?** See `.github/prompts/plan-stage1ReadinessAssessment.prompt.md`
- **Gap documentation?** See `STAGE1_GAP_FIXES_SUMMARY.md`

---

**Let's go! 🍅**
