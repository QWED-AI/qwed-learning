# Module 11: The Legal Auditor ⚖️

**Building a Deterministic AI Paralegal**

In this module, we will tackle one of the highest-stakes domains for AI: **Law**. 

You will learn why "chatting with PDF contracts" is dangerous and how to build a **Deterministic Legal Auditor** that verifies deadlines, liabilities, and citations with mathematical precision.

---

## 🛑 The Crisis: The "Mata v. Avianca" Effect

Generative AI is an "Artist" — it loves creative writing. Law requires an "Accountant" — strict adherence to facts.

When you ask an LLM: *"Find all deadlines in this NDA"*, it often:
1.  **Misses dates** hidden in complex clauses ("3 business days after the last Friday...").
2.  **Invented citations** (Hallucinations), as seen in the infamous *Mata v. Avianca* case where ChatGPT cited non-existent court cases.
3.  **Fails math**, miscalculating liability caps (e.g., is "200% of fees" > "$5M"?).

We will solve this using **QWED-Legal**.

---

## 📚 Curriculum

### Lesson 1: Precision Date Verification (DeadlineGuard)
Learn to calculate rigid legal deadlines across different jurisdictions. "3 days" in New York is different from "3 days" in London due to bank holidays.

**Example Implementation:**
```python
from qwed_sdk.guards import DeadlineGuard

guard = DeadlineGuard(jurisdiction="UK", include_bank_holidays=True)
result = guard.verify_deadline(
    start_date="2026-03-31",   # Tuesday before Easter week
    duration_days=3, 
    ai_calculated_end_date="2026-04-03" # AI ignores Good Friday bank holiday
)

if not result["verified"]:
    print(f"Hallucination Blocked: {result['irac.issue']}")
```

### Lesson 2: Financial Risk Auditing (LiabilityGuard)
Learn to audit indemnification clauses. If your company policy says *"Max Liability: $1M"*, your AI must flag a contract saying *"Liability limited to 3x contract value ($500k)"* as **SAFE** but *"Unlimited liability"* as **BLOCKED**.

**Example Implementation:**
```python
from qwed_sdk.guards import LiabilityGuard

guard = LiabilityGuard(max_liability_usd=1_000_000, block_unlimited=True)
contract_clause = "The Vendor's total aggregate liability shall be unlimited."

result = guard.verify_liability_clause(contract_clause)
print(result["irac.conclusion"]) # Outputs: "Blocked: Unlimited liability detected."
```

### Lesson 3: Logic & Contradictions (ClauseGuard)
Use the Z3 Theorem Prover to find logical inconsistencies. 
*   *Clause A:* "Termination notice: 30 days."
*   *Clause B:* "Termination notice: 90 days."
*   **Result:** Logical Contradiction found.

### Lesson 4: The Fact Shield (CitationGuard)
Prevent the *Avianca* problem. We will build a guard that verifies every legal citation against a trusted allow-list or regex pattern before it goes into a brief.

---

## 🛠️ Hands-on Exercises

1.  **Hallucination Demo**: See an un-guarded LLM make up a fake case law.
2.  **Deadline Verifier**: Build a script that handles "London Business Days".
3.  **Liability Auditor**: Audit 5 contract clauses for financial risk.
4.  **Contradiction Hunter**: Use Logic to find conflicting terms.
5.  **Capstone**: Build `verify_contract.py` using **Claude Desktop** to audit a PDF in real-time.

---

## 🚀 Next Steps

Go to the `exercises/` folder and start with **Exercise 1**.
