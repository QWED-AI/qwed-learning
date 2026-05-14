# Proof vs. Confidence

**Duration:** 10 minutes  
**Goal:** Learn the single most important distinction in the QWED ecosystem before writing any code

---

## The Core Rule

**Verified is not "very confident."**

In QWED, these are different categories:

- **Verified:** A deterministic engine proved the claim within a supported domain.
- **Invalid:** A deterministic engine checked the claim and found it false.
- **Unverifiable:** The claim could not be proved with the available deterministic machinery.
- **Heuristic:** A system produced a useful signal, but not a proof.

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

The correct outcome is one of:

- `BLOCKED`
- `UNVERIFIABLE`
- `QUARANTINED`
- `HUMAN_REVIEW_REQUIRED`

This is the core philosophy that protects future agent ecosystems from silent trust failures.

---

## Short Examples

These examples intentionally show different surfaces of the QWED ecosystem.
Some APIs return an object (`result.verified`, `result.value`), while others return
structured dictionaries (`status`, `is_valid`, `simplified`). The trust model is the
same across all of them: interpret the result category first, then decide the workflow action.

### Example 1: Verified

```python
query = "Solve x^2 - 4 = 0"
result = client.verify_math(query)

print(result.verified)  # True
print(result.value)     # [-2, 2]
```

The claim is in a supported symbolic domain, and the engine can prove it.

### Example 2: Simplified, Not Verified

```python
query = "x + x"
result = batch_verifier.verify_item(query)

print(result["is_valid"])   # False
print(result["status"])     # "SIMPLIFIED"
print(result["simplified"]) # "2*x"
```

The system transformed the expression, but no equality or proof claim was provided.

### Example 3: Unsupported

```python
query = "Which startup strategy is safest in 2027?"
result = verify_policy_decision(query)

print(result["status"])  # "UNVERIFIABLE"
```

The output may still be useful, but it is not deterministically provable.

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

-> [Continue to formal methods for developers](01-formal-methods-intro.md)
