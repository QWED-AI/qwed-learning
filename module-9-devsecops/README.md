# Module 9: DevSecOps - CI/CD Verification

> **"Shift left. Catch hallucinations in the PR, not in production."**

⏱️ **Duration:** 45 minutes  
📊 **Level:** Advanced  
🎯 **Goal:** Automate AI verification in your CI/CD pipeline using GitHub Actions.

---

## 🧠 What You'll Learn

After this module, you'll understand:

- ✅ Shift-Left Verification philosophy
- ✅ Setting up QWED GitHub Action
- ✅ Blocking PRs that fail verification
- ✅ Generating verification artifacts

---

## 📚 Table of Contents

| Lesson | Topic | Time |
|--------|-------|------|
| 9.1 | [Shift-Left Philosophy](#91-shift-left-verification) | 10 min |
| 9.2 | [GitHub Action Setup](#92-github-action-setup) | 20 min |
| 9.3 | [Branch Protection](#93-branch-protection) | 10 min |
| 9.4 | [v4.0.0 CI/CD Infrastructure](#94-v400-cicd-infrastructure) | 15 min |

---

## 9.1: Shift-Left Verification

### The Problem

Most teams catch AI errors in production:

```
Developer → Code → Deploy → Production → 🔥 Error → Hotfix
                                              ↑
                                        Too late!
```

### The Solution: Shift Left

Move verification earlier in the pipeline:

```
Developer → Code → PR → CI/CD Verification → ✅ Merge
                              ↑
                        Caught early!
```

### Why This Matters

| When Caught | Cost to Fix |
|-------------|-------------|
| During coding | $1 |
| In PR review | $10 |
| In staging | $100 |
| In production | $1,000+ |
| After customer impact | $10,000+ |

### The QWED Approach

```mermaid
graph LR
    A[Developer Push] --> B[GitHub Action]
    B --> C[QWED Verification]
    C --> D{All Tests Pass?}
    D -->|✅ Yes| E[Allow Merge]
    D -->|❌ No| F[Block PR]
    F --> G[Developer Fixes]
    G --> A
    
    style C fill:#4caf50
    style F fill:#f44336
```

---

## 9.2: GitHub Action Setup

### The QWED Finance Action

QWED provides a ready-to-use GitHub Action for financial AI verification.

**Marketplace:** [QWED Finance Verify](https://github.com/marketplace/actions/qwed-finance-verify)

### Quick Setup

#### Step 1: Create Workflow File

Create `.github/workflows/qwed-verify.yml`:

```yaml
name: QWED Finance Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: QWED-AI/qwed-finance@v1.2.0
        with:
          file-path: 'tests/transactions.csv'
```

#### Step 2: Create Test CSV

Create `tests/transactions.csv` (Simulate a "Bad Data" trap):

```csv
transaction_id,amount,customer_region,llm_flagged
TXN_001,500,US,False
TXN_002,15000,US,False
```

> ⚠️ **Note:** `TXN_002` is $15,000 but NOT flagged. This is an AML violation.

#### Step 3: Push and Watch

```bash
git add .
git commit -m "Add QWED verification to CI/CD"
git push
```

#### Step 3: Push and Watch

```bash
git add .
git commit -m "Add QWED verification to CI/CD"
git push
```

### Action Inputs

| Input | Description | Default |
|-------|-------------|---------|
| `file-path` | Path to your CSV/JSON file to verify | Required |
| `python-version` | Python version to use | `3.11` |
| `fail-on-violation` | Fail workflow if verification fails | `true` |

### Action Outputs

| Output | Description |
|--------|-------------|
| `verified` | Whether all verifications passed |
| `receipt-count` | Number of verification receipts generated |
| `violations` | JSON array of violations found |

---

## 9.3: Branch Protection

### Block Failing PRs

Configure GitHub to require QWED verification before merge:

1. Go to **Settings → Branches → Add Rule**
2. Enter branch name pattern: `main`
3. Enable **"Require status checks to pass before merging"**
4. Select **"verify"** from the list
5. Save changes

### Result

Now when a PR fails QWED verification:

```
❌ QWED Finance Verification
   └── verify: Failed
       └── Error: AML verification failed!
       
🚫 Merge blocked - Fix required
```

### Verified Badge

Once your workflow passes, add the badge to your README:

```markdown
[![Verified by QWED](https://img.shields.io/badge/Verified_by-QWED-00C853?style=flat&logo=checkmarx)](https://github.com/QWED-AI/qwed-finance)
```

---

## 🧪 Hands-On Lab: The "Senior Citizen" Trap

**Scenario:** Ideally, Senior Citizens get +0.50% interest. Claude 4.5 hallucinates the math.

### Lab Goal
Blocking a "Bad PR" that would underpay customers.

### Step 1: Create The Trap

Create a file `rates_update.csv`:

```csv
product,base_rate,senior_margin,claude_output
Senior_FD,7.00,0.50,7.035
```

> **The Error:** Claude did `7.00 * 1.005 = 7.035`.
> **The Truth:** `7.00 + 0.50 = 7.50`.

### Step 2: Push and Watch Fail

Your pipeline will fail because QWED calculates `7.50` but sees `7.035`.

**Result in Actions tab:**
```
❌ Verification Failed: Interest Rate Mismatch
   Expected: 7.50%
   Found: 7.035%
   Error: Multiplicative logic applied to additive spread.
```

### Step 3: Fix the Bug

Update `rates_update.csv`:

```diff
- Senior_FD,7.00,0.50,7.035
+ Senior_FD,7.00,0.50,7.50
```

### Step 4: Push and Watch Pass

**Result:**
```
✅ QWED Finance Verification
   └── verify: Passed
   └── Audited 1 row(s). No hallucinations found.
   
🟢 Ready to merge!
```

---

## 📋 DevSecOps Checklist

| Item | Status |
|------|--------|
| Workflow file created | ☐ |
| Test script written | ☐ |
| Branch protection enabled | ☐ |
| Badge added to README | ☐ |
| Team trained on fixing failures | ☐ |

---

## 9.4: v4.0.0 CI/CD Infrastructure

🆕 *New in QWED v4.0.0 Sentinel Edition*

v4.0.0 introduced enterprise-grade CI/CD tooling beyond GitHub Actions:

### The Stack

| Tool | Purpose | Integration |
|------|---------|-------------|
| **Sentry** | Real-time error tracking | `sentry-sdk` in Python |
| **CircleCI** | Matrix testing (Python 3.10–3.12) | `.circleci/config.yml` |
| **SonarCloud** | Code quality + coverage analysis | GitHub App |
| **Snyk** | Security vulnerability scanning (SARIF) | `snyk test` / `snyk monitor` |
| **pip-audit** | Python dependency CVE scanning | `pip-audit --strict` |
| **Docker Scout** | Container vulnerability scanning | Docker Hub integration |
| **SBOM** | Software Bill of Materials (SPDX) | `anchore/sbom-action` |

### Docker Auto-Publish Pipeline

```yaml
# Automated on every GitHub Release
# 1. Build multi-platform image
# 2. Sign with pinned base image digests
# 3. Generate SBOM (SPDX format)
# 4. Push to Docker Hub with version tags
# 5. Run Docker Scout vulnerability scan
```

### Key Practices from v4.0.0

1. **pip-audit with exclusions** — Exclude local packages from audit (`--exclude qwed`)
2. **Non-root Docker** — All containers run as non-root user via `gosu`/`runuser`
3. **Hash-verified requirements** — `pip install --require-hashes` in Docker builds
4. **SARIF output** — Snyk results exported as SARIF for GitHub Security tab

### 🎯 Key Takeaway

> **"One scanner is hope. Five scanners in CI/CD is infrastructure."**

---

## 📝 Summary

| Concept | Implementation |
|---------|----------------|
| **Shift-Left** | Catch errors in PRs, not production |
| **GitHub Action** | `QWED-AI/qwed-finance@v1.2.0` |
| **Branch Protection** | Require "verify" status to merge |
| **Artifacts** | Verification receipts uploaded |
| **Sentry** | Error tracking in production |
| **Snyk + pip-audit** | Dependency CVE scanning |
| **SBOM** | Software supply chain transparency |

---

## ➡️ Next: Advanced Patterns

Learn the advanced verification engines — Fact Checker, Consensus, and Reasoning:

**[→ Continue to Module 10: Advanced Patterns](../module-10-advanced-patterns/README.md)**

---

*"Production is not a test environment. Verify before you ship."*
