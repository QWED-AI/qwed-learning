# QWED Quick Reference Cheat Sheet

**Master the trust-boundary basics in 5 minutes**

---

## Quick Start

### Installation

```bash
pip install qwed
```

### Initialize Client

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(
    provider="openai",
    model="gpt-4o-mini",
)
```

---

## The Most Important Rule

**Verified is not "high confidence."**

QWED result states should be treated as categories, not a confidence ladder:

- `VERIFIED`
- `INVALID`
- `UNVERIFIABLE`
- `HEURISTIC`
- `SIMPLIFIED`

If a claim cannot be proved deterministically, do not silently continue with a guessed answer.

---

## Basic Usage

```python
result = client.verify_math("What is 2+2?")

print(result.verified)  # True / False
print(result.value)     # Verified answer when available
print(result.error)     # Reason when verification fails
print(result.evidence)  # Verification details
```

---

## When to Use Each Engine

| Task | Engine | Method Call |
|------|--------|-------------|
| Calculus, algebra, finance | Math | `verify_math()` |
| If-then, logic proofs | Logic | `verify_logic()` |
| SQL syntax, injection | SQL | `verify_sql()` |
| eval(), exec(), security | Code | `verify_code()` |
| General verification | Auto | `verify()` |

---

## Safe Production Patterns

### Pattern 1: Verify Before Return

```python
def calculate(query: str):
    result = client.verify_math(query)
    if result.verified:
        return result.value
    raise ValueError(f"Verification failed: {result.error}")
```

### Pattern 2: Block and Escalate

```python
def calculate_or_escalate(query: str):
    result = client.verify_math(query)
    if result.verified:
        return result.value

    create_review_task(
        query=query,
        error=result.error,
        status="HUMAN_REVIEW_REQUIRED",
    )
    raise ValueError("Verification failed; routed for human review")
```

### Pattern 3: Quarantine Unsupported Results

```python
def calculate_or_quarantine(query: str):
    result = client.verify_math(query)
    if result.verified:
        return result.value

    logger.error("Blocking unverifiable result", extra={"query": query})
    return {
        "status": "UNVERIFIABLE",
        "message": "No deterministic proof was established",
    }
```

---

## Understanding Results

### VerificationResult Object

```python
result.verified   # bool: True only when the claim was proved
result.value      # any: Verified answer when available
result.error      # str | None: Failure reason
result.evidence   # dict: How the result was checked
```

### Evidence Fields

```python
result.evidence["method"]          # symbolic, solver, parser, etc.
result.evidence["symbolic_result"] # Raw symbolic output when available
result.evidence["pii_masked"]      # PII detection info
```

---

## PII Masking

```python
client = QWEDLocal(
    provider="openai",
    mask_pii=True,
    pii_entities=[
        "PERSON",
        "EMAIL_ADDRESS",
        "US_SSN",
        "CREDIT_CARD",
    ],
)
```

PII masking improves privacy, but it is not a proof of correctness.

---

## Key Principles

1. **Never trust LLMs to compute**. Use them to translate, not to decide trust.
2. **Keep proof separate from confidence**. A guess is not verification.
3. **Unknown must fail closed**. Unsupported, unverifiable, or heuristic states must not silently become trusted.
4. **Use caching carefully**. Cache deterministic results, not changing trust assumptions.
5. **Preserve auditability**. Critical systems should log why something was verified, blocked, or escalated.

---

## Common Errors and Safe Fixes

| Error | Cause | Safer fix |
|-------|-------|-----------|
| `API key not found` | Missing env var | Set the correct provider key |
| `Connection refused` | Local runtime not running | Start the local runtime explicitly |
| `Verification failed` | Claim too vague or unsupported | Rewrite the claim or escalate |
| `Import error` | Missing extras | Install the required extras |

---

## Full Documentation

- **Course:** [qwed-learning](https://github.com/QWED-AI/qwed-learning)
- **Main Repo:** [qwed-verification](https://github.com/QWED-AI/qwed-verification)

---

**Remember:** A useful output can still be unverifiable. QWED is about trust boundaries, not stronger vibes.
