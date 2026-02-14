# 🎯 CREATE GITHUB ISSUES: Visual Quick-Start

Choose your path. Takes 30 seconds to 20 minutes.

---

## 🚀 Path 1: FAST (30 seconds) ⭐ RECOMMENDED

### Prerequisites
- GitHub CLI installed: https://cli.github.com/
- Authenticated: `gh auth login` (one-time)

### Command
```powershell
cd C:\MyProjects\senior-pomidor
python scripts\create_github_issues.py
```

### Result
✅ All 10 issues created automatically on GitHub
✅ Correct titles with `TOMATO-N:` prefix
✅ Correct descriptions, labels, dependencies
✅ Ready for implementation

### Time: 30 seconds

---

## 👀 Path 2: SAFE (2 minutes) - Dry-Run First

### Prerequisites
- Python installed
- In correct directory

### Command
```powershell
python scripts\create_github_issues.py --dry-run
```

### Result
✅ See exactly what will be created
✅ Preview without modifying anything
✅ Build confidence

### Then
```powershell
python scripts\create_github_issues.py
```

### Time: 2 minutes

---

## 📋 Path 3: MANUAL (20 minutes) - Copy-Paste

### Prerequisites
- Python installed
- GitHub web access

### Step 1: Generate Export
```powershell
python scripts\export_issues_for_manual_creation.py
```

Creates: `GITHUB_ISSUES_EXPORT.md`

### Step 2: Copy Content
Open `GITHUB_ISSUES_EXPORT.md`
```markdown
## Issue 1: Bootstrap production-ready Python 3.11 repository skeleton...

### GitHub UI - Title Field
```
Bootstrap production-ready Python 3.11 repository skeleton...
```

### GitHub UI - Body Field
```markdown
## Context / Why
...
## Scope
...
```
```

### Step 3: Create Issues on GitHub
1. Go to: https://github.com/your-org/senior-pomidor/issues
2. Click **New Issue**
3. Copy **Title** from export
4. Paste into GitHub title field
5. Copy **Body** from export
6. Paste into GitHub body field
7. Add labels: `stage-1`, `issue-1`
8. Click **Create Issue**

### Repeat for All 10 Issues
~2 minutes per issue × 10 = 20 minutes total

### Time: 20 minutes

---

## 📚 Documentation Files (Optional Reading)

| If You Want | Read This | Time |
|---|---|---|
| Just do it | Nothing, run command | 30 sec |
| Understand what's being created | `GITHUB_ISSUES_SETUP_COMPLETE.md` | 5 min |
| Step-by-step instructions | `GITHUB_ISSUES_QUICK_START.md` | 3 min |
| Detailed guide for all methods | `CREATE_GITHUB_ISSUES_GUIDE.md` | 10 min |
| Full issue specifications | `MVP_GITHUB_ISSUES_COMPLETE.md` | 30 min |
| Understand gap fixes | `STAGE1_GAP_FIXES_SUMMARY.md` | 5 min |
| Timeline & phases | `plan-stage1ReadinessAssessment.prompt.md` | 10 min |

---

## ⚡ Decision Matrix

| Situation | Method | Command |
|---|---|---|
| I have GitHub CLI | **Fast (30 sec)** | `python scripts\create_github_issues.py` |
| I want to preview first | **Safe (2 min)** | `python scripts\create_github_issues.py --dry-run` |
| I don't have GitHub CLI | **Manual (20 min)** | `python scripts\export_issues_for_manual_creation.py` |
| I'm not sure | **Read** `GITHUB_ISSUES_QUICK_START.md` | Then pick method |

---

## ✅ Verification

After running your chosen method:

### Check on GitHub
Go to: https://github.com/your-org/senior-pomidor/issues

You should see:
- ✅ 10 issues listed
- ✅ Titles are readable
- ✅ Each has `stage-1` label
- ✅ Each has `issue-N` label

### Issues Summary
- Issue 1: Repository Bootstrap
- Issue 2: Core Pydantic Contracts
- Issue 2a: Observation & Device Status (⭐ NEW)
- Issue 2b: Confidence Scoring & Thresholds (⭐ NEW)
- Issue 3: JSONL Storage
- Issue 4: Data Sources
- Issue 5: State Estimator
- Issue 6: Clock & Scheduler
- Issue 7: Simulation Script
- Issue 8: Integration Tests

---

## 🐛 If Something Goes Wrong

### "gh: command not found"
→ Install GitHub CLI: https://cli.github.com/

### "Not authenticated"
→ Run: `gh auth login`

### "Error creating issues"
→ Check: `gh auth status`

### Script doesn't work
→ See: `CREATE_GITHUB_ISSUES_GUIDE.md` troubleshooting

---

## 🎉 You're Done When

✅ All 10 issues appear on GitHub  
✅ Each issue has correct title & description  
✅ Each issue has labels: `stage-1`, `issue-N`  
✅ You can click & read each issue  

---

## 🚀 Next: Start Implementation

After issues are created:

1. **Organize by Phase** (optional)
   - Create GitHub project board
   - Organize by: Foundation → DataFlow → Logic → Integration → Done

2. **Start Phase 1 (Week 1)**
   - Issue 1: Repository Bootstrap
   - Issues 2, 2a, 2b: Contracts & specifications (parallel)

3. **Follow Timeline** (~6 weeks total)
   - Phase 1: Weeks 1-2 (foundation)
   - Phase 2: Weeks 2-3 (data flow)
   - Phase 3: Weeks 3-4 (core logic)
   - Phase 4: Week 5 (integration)
   - Phase 5: Week 5-6 (QA & coverage)

---

## 📊 The 10 Issues Overview

```
Phase 1: FOUNDATION (Weeks 1-2)
  ✓ Issue 1:  Bootstrap
  ✓ Issue 2:  Contracts
  ✓ Issue 2a: Observation (NEW)
  ✓ Issue 2b: Specs (NEW)

Phase 2: DATA FLOW (Weeks 2-3)
  ✓ Issue 3:  Storage
  ✓ Issue 4:  Sources

Phase 3: CORE LOGIC (Weeks 3-4)
  ✓ Issue 5:  Estimator
  ✓ Issue 6:  Clock

Phase 4: INTEGRATION (Week 5)
  ✓ Issue 7:  Simulation

Phase 5: QUALITY (Weeks 5-6)
  ✓ Issue 8:  Integration Test
```

---

## 🎯 You Have 3 Paths

### 🏃 Path 1: Fast (I have GitHub CLI)
```powershell
python scripts\create_github_issues.py
```
**Done in 30 seconds**

### 🚶 Path 2: Safe (I want to preview)
```powershell
python scripts\create_github_issues.py --dry-run
python scripts\create_github_issues.py
```
**Done in 2 minutes**

### 📝 Path 3: Manual (I prefer UI)
```powershell
python scripts\export_issues_for_manual_creation.py
```
Then copy-paste each issue into GitHub UI
**Done in 20 minutes**

---

## ✨ That's It!

Pick your path above and follow the command.

### Questions?
- **How do I do this?** → `GITHUB_ISSUES_QUICK_START.md`
- **What will be created?** → `GITHUB_ISSUES_SETUP_COMPLETE.md`
- **I need help** → `CREATE_GITHUB_ISSUES_GUIDE.md`

### Ready?
→ Run your chosen command above
→ Go to GitHub to verify
→ Done! ✅

---

**30 seconds until your 10 issues are on GitHub.** 🚀
