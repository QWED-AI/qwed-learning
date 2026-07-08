# Module 11: The Legal Auditor ⚖️

**Building a Deterministic AI Paralegal**

In this module, we will tackle one of the highest-stakes domains for AI: **Law**. 

You will learn why "chatting with PDF contracts" is dangerous and how to build a **Deterministic Legal Auditor** that verifies deadlines, liabilities, and citations with mathematical precision.

---

## 🛑 The Crisis: The "Mata v. Avianca" Effect

Generative AI is a persuasive draft generator. Law requires verified dates, grounded citations, and explicit non-pass states when proof is unavailable.

When you ask an LLM: *"Find all deadlines in this NDA"*, it often:
1.  **Misses dates** hidden in complex clauses ("3 business days after the last Friday...").
2.  **Invented citations** (Hallucinations), as seen in the infamous *Mata v. Avianca* case where ChatGPT cited non-existent court cases.
3.  **Fails math**, miscalculating liability caps (e.g., is "200% of fees" > "$5M"?).

We will solve this using **QWED-Legal**.

---

## 📚 Curriculum

### Lesson 1: Precision Date Verification (DeadlineGuard)
Learn to calculate rigid legal deadlines across different jurisdictions. "3 days" in New York is different from "3 days" in London due to bank holidays.

**Example Implementation (see `exercises/ex2_deadline_guard.py`):**
```python
# The mock used in this course lives in exercises/ex2_deadline_guard.py
from exercises.ex2_deadline_guard import MockDeadlineGuard

guard = MockDeadlineGuard()
valid, msg = guard.verify(
    start_date="2024-01-01",
    days=3,
    jurisdiction="UK",
    expected_end_date="2024-01-04"
)
print(msg)  # Detects the holiday mismatch
```

### Lesson 2: Financial Risk Auditing (LiabilityGuard)
Learn to audit indemnification clauses. If your company policy says *"Max Liability: $1M"*, your AI must flag a contract saying *"Liability limited to 3x contract value ($500k)"* as **SAFE** but *"Unlimited liability"* as **BLOCKED**.

**Core QWED approach:** Use `client.verify_logic()` with policy rules to audit liability caps deterministically:

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="openai")
result = client.verify_logic(
    "Liability cap of $500k is under $1M policy max. Is this compliant?"
)
print(result.agent_message)
```

### Lesson 3: Logic & Contradictions (ContradictionGuard)
Use the Z3 Theorem Prover (via `client.verify_logic()`) to formally prove logical inconsistencies in contracts. 
*   *Clause A:* "Termination notice: 30 days."
*   *Clause B:* "Termination notice: 90 days."
*   **Result:** Logical Contradiction found.

### Lesson 4: The Fact Shield (CitationGuard)
Prevent the *Avianca* problem. Use `client.verify_fact()` to verify every legal citation against a trusted source list before it goes into a brief.

### Lesson 5: Bias & Counterfactual Testing (FairnessGuard)
Teach your AI to detect implicit bias. Use `client.verify_logic()` with counterfactual prompts: swap protected attributes and check if the outcome changes deterministically.

### Lesson 6: Structuring Legal Reasoning (IRACGuard)
Enforce predictable outputs by requiring the AI's reasoning to follow the IRAC (Issue, Rule, Application, Conclusion) structure. The `ProcessVerifier` in `qwed_new.guards.process_guard` validates structured reasoning paths.

### Lesson 7: Architecture Compliance (SACProcessor)
Learn how to map chunks to specific legal contexts securely before passing them to the AI for evaluation.

---

## 🛠️ Hands-on Exercises

1.  **Hallucination Demo**: See an un-guarded LLM make up a fake case law.
2.  **Deadline Verifier**: Build a script that handles "London Business Days".
3.  **Liability Auditor**: Audit 5 contract clauses for financial risk.
4.  **Contradiction Hunter**: Use Logic to find conflicting terms.
5.  **Bias Detection**: Use `FairnessGuard` to evaluate a settlement offer.
6.  **IRAC Audit**: Verify that an AI-generated memo follows IRAC structure.
7.  **Capstone**: Build `verify_contract.py` behind a governed execution gateway or audited MCP host.

---

## 🚀 Next Steps

Go to the `exercises/` folder and start with **Exercise 1**.
