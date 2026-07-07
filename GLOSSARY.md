# 📖 Glossary: AI Verification for Humans

**Before diving into the course, let's learn the language of verification - without the PhD jargon!**

This glossary translates scary technical terms into plain English with real-world analogies.

---

## Core Concepts

### Deterministic

**Scary Definition:** A system that always produces the same output for the same input.

**Simple Meaning:** Always gives the same answer (2+2=4, every single time).

**Real-World Analogy:** 
- **Calculator** 🧮 - Press "2+2" and you always get "4"
- **Traffic Light Rules** - Red always means stop, green always means go
- **Recipe with Measurements** - 1 cup flour is always 1 cup, not "about a cup"

**Why It Matters:** Bank transfers, medical dosages, and tax calculations need determinism!

---

### Probabilistic

**Scary Definition:** A system that uses statistical patterns to generate outputs.

**Simple Meaning:** Probably gives the right answer, but it can change.

**Real-World Analogy:**
- **Human Guess** 🤔 - "I think 2+2 is... 4? Yeah, probably."
- **Weather Forecast** - "70% chance of rain" (might or might not rain)
- **Autocorrect** - Sometimes fixes "teh" to "the", sometimes doesn't

**Why LLMs are Probabilistic:** They predict the next word based on patterns, not facts!

---

### Hallucination

**Scary Definition:** When an AI generates plausible but incorrect information.

**Simple Meaning:** When AI presents an unsupported claim as if it were established.

**Real-World Analogy:**
- **Student Making Up Answers** - Sounds smart, totally wrong
- **Confident Liar** - Says "Trust me" but has no idea
- **Dream Logic** - Feels real while happening, nonsense when you wake up

**Example:**
```
User: "Who was the first person on Mars?"
LLM: "Neil Armstrong, in 1969." ❌ (Sounds plausible, completely false)
```

---

## Technical Terms (Simplified)

### AST (Abstract Syntax Tree)

**Scary Definition:** A tree representation of code structure.

**Simple Meaning:** Looking at code structure without running it.

**Real-World Analogy:**
- **Grammar Check** - Spell-check finds "their/they're" errors without understanding the essay
- **Blueprint** - See building structure before construction
- **X-Ray** - See bones without surgery

**What QWED Does:** Checks if code has `eval()` or `exec()` by reading its structure.

---

### Solver (Z3 / SymPy)

**Scary Definition:** Automated theorem prover using satisfiability modulo theories.

**Simple Meaning:** A tool that proves logic/math is correct, mathematically.

**Real-World Analogy:**
- **Impartial Judge** 👨‍⚖️ - Checks if arguments follow the rules
- **Fact Checker** - Verifies claims against evidence
- **Referee** - Ensures players follow game rules

**What It Does:**
```python
# You say: "If all A are B, and x is A, is x B?"
# Z3 proves: YES (always, mathematically certain)
```

---

### LLM-as-a-Judge

**Scary Definition:** Using one language model to evaluate another's outputs.

**Simple Meaning:** Asking an AI to check another AI.

**Real-World Analogy:**
- **Grading Your Own Homework** - Obviously flawed
- **Fox Guarding Henhouse** - Conflict of interest
- **Two Drunk Friends** - "Are you sober?" "Yeah, you?"

**Why It Fails:** Both LLMs trained on same (wrong) internet data!

---

### Solver-as-a-Judge (QWED)

**Scary Definition:** Using mathematical solvers instead of LLMs to verify correctness.

**Simple Meaning:** Math proving answers, not AI guessing.

**Real-World Analogy:**
- **Calculator vs Human** - Calculator always right for math
- **Breathalyzer vs Asking** - Scientific test, not opinion
- **GPS vs Directions** - Satellite precision, not memory

**Why It Works:** SymPy and Z3 are deterministic - they compute, not guess.

---

### Lossy Compression (The JPEG Analogy)

**Scary Definition:** Data compression that discards some information.

**Simple Meaning:** Making things smaller by throwing away details.

**Real-World Analogy:**
- **JPEG vs RAW Photo** - JPEG loses pixels, RAW keeps them all
- **Summary vs Book** - Summary loses details
- **LLM vs Internet** - LLM "compresses" knowledge, loses precision

**Why It Matters:** LLMs are lossy compression of the web - they lose facts!

---

### Probabilistic Gap

**Scary Definition:** The asymptotic limit of accuracy in gradient-based learning.

**Simple Meaning:** AI can never reach 100% accuracy, no matter how much training.

**Real-World Analogy:**
- **Diminishing Returns** - More training = smaller gains
- **Asymptote** - Gets closer but never touches the line
- **"Good Enough"** - 99.9% sounds great until it's 1 error per 1000

**Key Insight:** You can't fine-tune your way to determinism!

---

### Beaver (Probabilistic Verifier)

**Scary Definition:** Framework for computing probability bounds on LLM constraint satisfaction.

**Simple Meaning:** Tool that tells you "how likely" output is correct.

**Comparison with QWED:**
- **Beaver:** "87% likely correct"
- **QWED:** "Deterministically verified for a supported claim"

**When to Use:** Risk assessment, not production verification.

---

### Guardrails

**Scary Definition:** Rule-based filters that block unsafe AI outputs.

**Simple Meaning:** Safety filters that say "STOP" or "GO".

**Comparison with QWED:**
- **Guardrails:** Safety (is it harmful?)
- **QWED:** Correctness (is it right?)

**Analogy:** Guardrails = Seatbelts, QWED = Crash Test.

---

## Verification Concepts

### Symbolic Reasoning

**Scary Definition:** Manipulation of mathematical symbols according to formal rules.

**Simple Meaning:** Using math rules (not guessing) to get answers.

**Real-World Analogy:**
- **Following a Recipe Exactly** - Not "eyeballing" ingredients
- **Solving Algebra** - Step-by-step, provable
- **Chess Computer** - Calculates all moves, doesn't "feel" the best one

**Example:**
```python
# Symbolic (SymPy):
derivative = sp.diff(x**2, x)  # Always: 2*x (proven)

# Probabilistic (LLM):
"The derivative is probably... 2x? Or maybe x^2..." ❌
```

---

### Neurosymbolic AI

**Scary Definition:** Integration of neural networks with symbolic AI.

**Simple Meaning:** Combining "creative AI" with "precise math."

**Real-World Analogy:**
- **Artist + Accountant** - Artist creates, accountant verifies the numbers
- **Chef + Nutritionist** - Chef makes food, nutritionist checks calories
- **Poet + Spell Checker** - Poet writes, spell checker fixes grammar

**How QWED Uses It:**
1. **Neural (LLM):** Translates "Calculate interest" → Math formula
2. **Symbolic (SymPy):** Proves formula is correct

---

## Common Misconceptions

### "LLMs can do math if I prompt well"

**Reality:** No. LLMs predict text patterns, not calculate.

**Analogy:** Teaching a parrot to say "2+2=4" doesn't mean it understands math.

---

### "100% accuracy is impossible"

**Reality:** It IS possible in mathematically verifiable domains!

**Analogy:** Calculators have 100% accuracy for arithmetic. We can too (for math/logic/code).

**Caveat:** QWED can't verify creative writing or subjective opinions - only things with "correct answers."

---

### "More AI = Better Verification"

**Reality:** More AI = More probabilistic uncertainty.

**Analogy:** Asking 10 people who are all wrong doesn't make them right.

**Better:** Use deterministic tools (calculators, solvers) - not more AI.

---

## Agentic Security (v4.0.0)

### RAGGuard

**Simple Meaning:** Verifies that retrieved chunks in a RAG pipeline came from the correct source document.

**Analogy:** Checking that every page in a contract actually belongs to that contract, not a different one.

---

### ExfiltrationGuard

**Simple Meaning:** Prevents agents from sending sensitive data (PII, credentials) to unauthorized endpoints.

**Analogy:** A bouncer at the exit who checks what you're carrying before you leave the building.

---

### MCPPoisonGuard

**Simple Meaning:** Scans MCP tool descriptions for hidden malicious instructions before the agent loads them.

**Analogy:** A food inspector checking for poison before you serve the meal.

---

### SelfInitiatedCoTGuard (S-CoT)

**Simple Meaning:** Lets the AI reason freely, but verifies it covered all required topics before executing.

**Analogy:** A professor checking that a student's essay covered all required sections, regardless of writing style.

---

### Process Determinism (ProcessVerifier)

**Simple Meaning:** Verifies that AI reasoning follows a proper legal/compliance structure (IRAC).

**Analogy:** Checking that a lawyer's argument has an Issue, Rule, Application, and Conclusion — not just a conclusion.

---

### IRAC

**Simple Meaning:** Issue, Rule, Application, Conclusion — a structured legal reasoning framework.

**Why It Matters:** Every QWED guard produces IRAC audit fields, making blocks legally defensible.

---

### DRM (Document-Level Retrieval Mismatch)

**Simple Meaning:** When a vector database returns chunks from the wrong document because documents look similar.

**Why It's Dangerous:** Legal NDAs, medical records, and financial contracts are structurally similar — embeddings can't tell them apart.

---

---

## Diagnostic Architecture (v5.2.0)

### DiagnosticResult

**Simple Meaning:** The single unified result type for all QWED verification operations. Replaces the old incompatible `VerificationResult` variants.

**Three Layers:**
1. **`agent_message`** — Human-readable status ("Verification succeeded", "Proof not established"). Safe for downstream agents. Always present.
2. **`developer_fields`** — Structured evidence dictionary. Contains `constraint_id`, `advisory_checks`, solver traces, and engine metadata. For engineers and audit.
3. **`proof_ref`** — Cryptographic hash (`sha256:...`) of the proof artifact. Present only on `VERIFIED`. Absence means non-authoritative.

**Usage:**
```python
if result.status == DiagnosticStatus.VERIFIED:
    # proof_ref is guaranteed to be set
    process(result.developer_fields["value"])
else:
    raise ValueError(result.agent_message)
```

---

### DiagnosticStatus

**Simple Meaning:** The three-state enum that replaces the old five-state model.

| Value | Meaning | Can drive control flow? |
|-------|---------|------------------------|
| `VERIFIED` | Deterministically proven | Yes (proof_ref present) |
| `UNVERIFIABLE` | Could not be proven | No (proof_ref is None) |
| `BLOCKED` | Could not even be attempted | No (proof_ref is None) |

**What was removed:** `INVALID`, `HEURISTIC`, `SIMPLIFIED`. These are not verification states. Heuristic signals live in `advisory_checks`. Simplified expressions are transformations, not verdicts.

---

### proof_ref

**Simple Meaning:** A cryptographic fingerprint (`sha256:...`) that proves a verification result is authentic and hasn't been tampered with.

**Real-World Analogy:**
- **Tamper-Evident Seal** — If the seal is broken, you know the bottle was opened
- **Digital Signature** — Proves who signed a document
- **Checksum** — Verifies a file downloaded correctly

**How It Works:**
1. When a claim is `VERIFIED`, QWED hashes the evidence (solver traces, frequency counts, constraints) with SHA-256
2. The hash becomes the `proof_ref`: `"sha256:abcdef123456..."`
3. Any downstream gate can re-hash the evidence and compare — if it matches, the verdict is authentic
4. If `proof_ref` is `None`, the result is non-authoritative and must not drive control flow

**Why It Matters:** `proof_ref` makes audit trails replayable and tamper-detectable. Without it, a logged `VERIFIED` result is just a claim — with it, the claim is cryptographically bound to the evidence that justified it.

---

### advisory_checks

**Simple Meaning:** Optional, non-authoritative signals carried inside `developer_fields`. These are useful hints, not verdicts.

**Examples:**
- A heuristic safety score
- A "SIMPLIFIED" transformation note
- A model confidence estimate
- A policy warning

**Why It's Not a Status:** Advisory checks are information, not proof. They live in `developer_fields` so they don't pollute the verification state machine. A blocked result can still carry advisory signals.

---

### constraint_id

**Simple Meaning:** A unique identifier for the specific constraint or rule that was checked.

**Real-World Analogy:**
- **Regulation Section Number** — "Section 5.2.1 of HIPAA Privacy Rule"
- **Test Case ID** — "TC-4711: Interest rate must be positive"
- **Policy Rule** — "POLICY-03: No eval() in production code"

**Where It Lives:** `result.developer_fields["constraint_id"]`

**Why It Matters:** Enables targeted audit queries ("show me every time constraint POL-047 triggered"), structured compliance reporting, and policy-as-code workflows.

---

## Quick Reference Table

| Term | Translation | Emoji |
|------|-------------|-------|
| Deterministic | Always same answer | 🧮 |
| Probabilistic | Maybe right | 🎲 |
| Hallucination | Unsupported claim presented as fact | 🤥 |
| Symbolic | Math proof | ✅ |
| LLM-as-Judge | AI checks AI | 🤔 |
| Verification | Proof of correctness | 🛡️ |
| DSL (Domain-Specific Language) | Special code for one task | 🔧 |
| DiagnosticResult | Unified result type (3 states + proof_ref) | 📋 |
| DiagnosticStatus | VERIFIED / UNVERIFIABLE / BLOCKED | 🚦 |
| proof_ref | Cryptographic proof fingerprint | 🔏 |
| advisory_checks | Non-authoritative signals (not verdicts) | 💡 |
| constraint_id | Unique constraint/rule identifier | 🏷️ |

---

## Still Confused?

**That's okay!** The course uses these terms in context with examples.

**Tip:** Bookmark this page and come back whenever you see a scary word!

---

**Ready to start?**

→ [Module 1: The Crisis](../module-1-the-crisis/README.md)
