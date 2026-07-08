# Proof vs. Confidence

**Duration:** 10 minutes  
**Goal:** Learn the single most important distinction in the QWED ecosystem before writing any code

---

## The Core Rule

**Verified is not "very confident."**

In QWED, these are different categories:

- **VERIFIED:** A deterministic engine proved the claim within a supported domain. The result includes a `proof_ref` — a cryptographic hash binding the verdict to the evidence that justified it.
- **UNVERIFIABLE:** The claim could not be proved with the available deterministic machinery. `proof_ref` is `None`.
- **BLOCKED:** Verification could not even be attempted (parse error, configuration failure, security policy violation). `proof_ref` is `None`.

There are exactly three diagnostic states. `HEURISTIC` and `SIMPLIFIED` are not verification states — they are optional advisory signals carried in `developer_fields.advisory_checks`.

This distinction matters because future AI systems will often produce outputs that are:

- plausible
- useful
- well reasoned
- high confidence

and still **not verified**.

---

## What QWED Refuses to Blur

QWED treats these as separate concepts:

| Concept | Meaning | Is it proof? |
|--------|---------|--------------|
| Parsing | The input can be read into a structure | No |
| Validation | A format or rule check passed | Not necessarily |
| Simplification | An expression was transformed | No |
| Simulation | A model produced an estimate | No |
| Verification | A supported claim was checked deterministically | Yes |
| Proof | The strongest form of deterministic verification | Yes |
| Auditability | We can inspect how the result was produced | Useful, but not proof |

If a course example collapses these together, it is teaching the wrong trust model.

---

## Why Confidence Is Dangerous Here

Confidence is a **probabilistic belief signal**.

Verification is a **deterministic claim status**.

That means:

- `95% confidence` is not verification
- `100% confidence` is still not the right label for a proof
- a low-confidence answer is not automatically false
- an unsupported answer is not necessarily safe

In QWED, unsupported or unknown states must not silently become trusted outputs.

---

## Fail-Closed Means

When QWED cannot establish trust, the correct outcome is not:

- "try a softer fallback"
- "guess conservatively"
- "return the LLM answer with lower confidence"

The result states are `BLOCKED` or `UNVERIFIABLE`. Follow-up actions such as quarantine or human review are separate workflow steps, not verification states.

This is the core philosophy that protects future agent ecosystems from silent trust failures.

---

## Short Examples

All QWED operations return a `DiagnosticResult` with three layers. The trust model is the same across all domains: check the status first, then decide the workflow action.

### Example 1: Verified

```python
from qwed_new.core import DiagnosticStatus

query = "Solve x^2 - 4 = 0"
result = client.verify_math(query)

print(result.status)                    # DiagnosticStatus.VERIFIED
print(result.proof_ref)                 # "sha256:abcdef..."
print(result.developer_fields["value"])  # [-2, 2]
```

The claim is in a supported symbolic domain, and the engine can prove it. The `proof_ref` cryptographically binds the verdict to the evidence.

### Example 2: Blocked

```python
from qwed_new.core import DiagnosticStatus

query = "x + x"
result = client.verify_math(query)

print(result.status)          # DiagnosticStatus.BLOCKED
print(result.proof_ref)       # None
print(result.agent_message)   # "Expression could not be parsed as a claim"
```

The engine could not parse the query as a verifiable claim. No proof artifact exists.

### Example 3: Unverifiable

```python
from qwed_new.core import DiagnosticStatus

query = "Which startup strategy is safest in 2027?"
result = client.verify(query)

print(result.status)          # DiagnosticStatus.UNVERIFIABLE
print(result.proof_ref)       # None
```

The output may still be useful, but it is not deterministically provable. Without a `proof_ref`, this result is non-authoritative.

### Advisory Checks (Non-Status Signals)

```python
# Heuristic signals live in developer_fields, not the status enum
advisory = result.developer_fields.get("advisory_checks", [])
for check in advisory:
    print(check.name, check.outcome)  # e.g. "style_check" "PASS"
```

These are information, not proof. A BLOCKED or UNVERIFIABLE result can still carry useful advisory signals.

---

## The Mental Model to Keep

Use this rule throughout the course:

> **Unknown must not silently become trusted.**

That principle matters more than any single engine, API, or integration detail.

---

## Before You Continue

If you remember only one thing from this course, remember this:

> **Confidence is a guess about correctness. Verification is evidence of correctness.**

Now continue to the formal-methods primer with the right mental model.

---

## Principle 9: Diagnostics ≠ Explainability

A `DiagnosticResult` tells you what was checked and what was found. It does not tell you why an LLM chose a particular response. These are separate concerns:

| Concept | Purpose | Example |
|---------|---------|---------|
| **Diagnostics** | What was checked, what was found | `status: BLOCKED`, `proof_ref: None`, `agent_message: "Parse error"` |
| **Explainability** | Why the model gave that answer | Chain-of-thought, attention weights, rationale |

QWED enforces this separation through three structural layers:

- **Layer 1 (`agent_message`):** Agent-safe diagnostic text. No model internals.
- **Layer 2 (`developer_fields`):** Structured evidence for engineers. No confidence scores.
- **Layer 3 (`proof_ref`):** Cryptographic proof binding. Present only on `VERIFIED`.

### Why This Matters

If a downstream agent treats "the LLM explained its reasoning" as equivalent to "the claim was verified," the trust boundary is broken. An LLM's explanation can be fluent, persuasive, and wrong — just like its original answer.

**Rule of thumb:** Diagnostic output must never be overridden, softened, or replaced by an LLM's explanation or chain-of-thought reasoning. If `status` is `UNVERIFIABLE`, no amount of explainability makes it `VERIFIED`.

> **"A good explanation of a wrong answer is still a wrong answer."**

---

> **Optional:** After completing the core course, continue to [Module 14: Infrastructure Verification](../module-14-infrastructure-verification/README.md) to see how `InfraDiagnosticResult` applies the same three-state model to IaC verification — where `proof_ref` is the literal proof that trust requires evidence.

-> [Continue to formal methods for developers](01-formal-methods-intro.md)
