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

QWED result states — exactly three, not a confidence ladder:

- `VERIFIED` — deterministically proven (proof_ref is set)
- `UNVERIFIABLE` — could not be proved (proof_ref is None)
- `BLOCKED` — verification could not be attempted (proof_ref is None)

If a claim cannot be proved deterministically, do not silently continue with a guessed answer. Non-VERIFIED results are non-authoritative for control flow.

---

## Basic Usage

```python
from qwed_new.core import DiagnosticStatus

result = client.verify_math("What is 2+2?")

print(result.status)              # DiagnosticStatus.VERIFIED / UNVERIFIABLE / BLOCKED
print(result.agent_message)       # Human-readable diagnostic
print(result.developer_fields)    # Structured evidence
print(result.proof_ref)           # "sha256:..." when VERIFIED, None otherwise
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
from qwed_new.core import DiagnosticStatus

def calculate(query: str):
    result = client.verify_math(query)
    if result.status == DiagnosticStatus.VERIFIED:
        return result.developer_fields.get("value")
    raise ValueError(f"Cannot verify: {result.agent_message}")
```

### Pattern 2: Block and Escalate

```python
from qwed_new.core import DiagnosticStatus

def calculate_or_escalate(query: str):
    result = client.verify_math(query)
    if result.status == DiagnosticStatus.VERIFIED:
        return result.developer_fields.get("value")

    create_review_task(
        query=query,
        status=result.status.value,
        message=result.agent_message,
    )
    raise ValueError(f"Verification failed: {result.agent_message}")
```

### Pattern 3: Quarantine Unsupported Results

```python
from qwed_new.core import DiagnosticStatus

def calculate_or_quarantine(query: str):
    result = client.verify_math(query)
    if result.status == DiagnosticStatus.VERIFIED:
        return result.developer_fields.get("value")

    logger.error(
        "Blocking unverifiable result",
        extra={"status": result.status.value, "message": result.agent_message},
    )
    return {
        "status": result.status.value,
        "message": result.agent_message,
    }
```

---

## Understanding Results

### DiagnosticResult Object

```python
result.status            # DiagnosticStatus: VERIFIED / UNVERIFIABLE / BLOCKED
result.agent_message     # str: Human-readable diagnostic (always present)
result.developer_fields  # dict: Structured developer evidence
result.proof_ref         # str | None: "sha256:..." when VERIFIED, None otherwise
result.is_verified       # True when status == VERIFIED (implies proof_ref is set)
result.is_authoritative  # True when proof_ref is present (admissible for control flow)
result.is_fail_closed    # True when UNVERIFIABLE or BLOCKED
```

### Developer Fields

```python
result.developer_fields.get("constraint_id")       # str | None
result.developer_fields.get("method")              # symbolic, solver, parser, etc.
result.developer_fields.get("advisory_checks", []) # list of AdvisoryCheck
result.developer_fields.get("pii_masked")          # PII detection info
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
3. **Unknown must fail closed**. Unsupported or unverifiable results must not silently become trusted.
4. **Use caching carefully**. Cache deterministic results, not changing trust assumptions.
5. **Preserve auditability**. Critical systems should log status, proof_ref, and developer_fields.
6. **proof_ref is the authority bit**. Present = VERIFIED and admissible for control flow. Absent = non-authoritative.
7. **Diagnostics ≠ Explainability**. A `DiagnosticResult` tells you what was checked and what was found — never override it with an LLM's chain-of-thought.

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
