# Module 9: DevSecOps & The CI/CD Gatekeeper 🛡️

**"The Accountant stops the Artist from bankrupting the company."**

---

## 🎯 The Goal

In this module, you will stop running verification manually. You will build a **CI/CD Gatekeeper** that automatically blocks any Pull Request (PR) containing hallucinated financial data.

You will use the official **[QWED Finance Guard Action](https://github.com/marketplace/actions/qwed-finance-guard)** which we released in `v1.2.0`.

---

## 📖 The Story: "The 0.50% Premium Error"

You are the Lead Engineer at **Hypothetical Bank**.
Your Junior Developer (using Claude 4.5) just pushed a CSV file updating the interest rates for "Senior Citizen Fixed Deposits".

**The Policy:** Senior Citizens get **0.50% extra** interest.
**The Context:**
*   Base Rate: 7.00%
*   Expected Senior Rate: 7.50%

**The AI's Mistake:**
Claude saw "0.50% premium" and calculated: `7.00 * 1.005 = 7.035%`.
It failed to understand that "premium" in banking means **additive** (+0.50%), not multiplicative.

If this code merges, your bank will underpay grandmothers by 0.465%. **This is a lawsuit waiting to happen.**

---

## 🛠️ The Lab: Build the Wall

### Step 1: The Trap (Simulate the Error)

Create a file named `rates_update.csv` in your repository:

```csv
product_name,base_rate,senior_margin,claude_generated_final_rate
Standard FD,7.00,0.00,7.00
Senior FD,7.00,0.50,7.035
```

> ⚠️ **Note:** `7.035` is WRONG. It should be `7.50`.

### Step 2: The Gatekeeper (Deploy the Action)

Create a workflow file at `.github/workflows/financial_audit.yml`:

```yaml
name: Financial Compliance Audit

on: [pull_request]

jobs:
  audit_numbers:
    runs-on: ubuntu-latest
    name: 🛡️ QWED Accountant
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Run Finance Guard
        uses: QWED-AI/qwed-finance@v1.2.0
        with:
          file-path: 'rates_update.csv'
```

### Step 3: The Block

Commit and push these files. Open a Pull Request.

**What happens?**
1.  GitHub Actions triggers.
2.  QWED downloads the Docker container.
3.  It recalculates the math deterministically.
4.  It finds the error: `Expected 7.50, Found 7.035`.
5.  **THE PIPELINE FAILS ❌.**

GitHub will turn red. The "Merge" button will be blocked (if you have branch protection).

### Step 4: The Fix

Update `rates_update.csv` with the correct value:

```diff
- Senior FD,7.00,0.50,7.035
+ Senior FD,7.00,0.50,7.50
```

Push the change.
**Result:** The pipeline turns **Green ✅**.

---

## 🧠 Why This Matters

This is **Shift-Left Verification**.
Instead of finding errors in production (expensive), you find them in the Pull Request (cheap).

**Homework:**
Apply this to your own project. Never let an LLM merge code without an Accountant checking it first.

[← Previous Module](../module-8-agentic-workflows/README.md) | [Next Module (Advanced Patterns) →](../module-10-advanced-patterns/README.md)
