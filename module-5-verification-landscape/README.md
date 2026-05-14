# Module 5: The Verification Landscape

> **"Know your enemy, know yourself—a hundred battles, a hundred victories."** — Sun Tzu

⏱️ **Duration:** 45 minutes  
📊 **Level:** Intermediate  
🎯 **Goal:** Understand different verification approaches and where QWED fits.

---

## 🧠 What You'll Learn

After this module, you'll understand:

- ✅ The verification "zoo" - Guardrails, LLM-as-Judge, Beaver, QWED
- ✅ Why LLM-as-Judge is fundamentally broken
- ✅ Probabilistic vs Deterministic verification
- ✅ When to use what approach
- ✅ QWED's "Solver-as-a-Judge" philosophy

---

## 📚 Table of Contents

| Section | Title | Time |
|---------|-------|------|
| 5.1 | [The Verification Zoo](#51-the-verification-zoo) | 10 min |
| 5.2 | [Why LLM-as-Judge Fails](#52-why-llm-as-judge-fails) | 10 min |
| 5.3 | [Beaver: Probabilistic Bounds](#53-beaver-probabilistic-bounds) | 10 min |
| 5.4 | [QWED: Solver-as-a-Judge](#54-qwed-solver-as-a-judge) | 10 min |
| 5.5 | [Choosing the Right Tool](#55-choosing-the-right-tool) | 5 min |

---

## 5.1: The Verification Zoo

### The Problem Space

When you deploy LLMs in production, you need to ensure outputs are:

1. **Safe** - Won't cause harm
2. **Accurate** - Factually correct
3. **Compliant** - Meets regulations
4. **Consistent** - Reproducible results

Different tools address different parts of this problem.

### The Tool Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI OUTPUT VERIFICATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  GUARDRAILS │  │ LLM-AS-JUDGE│  │   BEAVER    │  │  QWED   │ │
│  │             │  │             │  │             │  │         │ │
│  │  Safety     │  │ Quality     │  │ Probability │  │ Proof   │ │
│  │  Filters    │  │ Scoring     │  │ Bounds      │  │ Engine  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                  │
│   "Block bad"     "Rate good"       "Estimate"      "Verify"    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Comparison

| Approach | Method | Output | Best For |
|----------|--------|--------|----------|
| **Guardrails** | Rule-based filters | Pass/Fail | Blocking harmful content |
| **LLM-as-Judge** | GPT rates GPT | Score (1-10) | Subjective quality |
| **Beaver** | Token exploration | Probability bound | Risk assessment |
| **QWED** | Symbolic solvers | Mathematical proof | Correctness verification |

---

## 5.2: Why LLM-as-Judge Fails

### The Concept

"LLM-as-Judge" uses one LLM to evaluate another:

```python
# Typical LLM-as-Judge pattern
def evaluate(response, criteria):
    prompt = f"""
    Rate this response on a scale of 1-10:
    Response: {response}
    Criteria: {criteria}
    """
    return gpt4(prompt)  # Returns "8/10"
```

### The Fatal Flaws

#### 1. Recursive Hallucination

If GPT-4 evaluates GPT-3.5, and both have the same biases...

```
User: "What's 17 × 24?"
GPT-3.5: "408" ❌ (Actual: 408... wait, that's right)
GPT-4 Judge: "Correct! 10/10" ✅

User: "What's 17 × 24 × 3?"  
GPT-3.5: "1,224" ✅
GPT-4 Judge: "Hmm, let me check... 17×24=408, 408×3=1,224. Correct! 10/10" ✅

User: "What's 1847 × 293?"
GPT-3.5: "541,571" ❌ (Actual: 541,171)
GPT-4 Judge: "That looks reasonable! 9/10" ❌ BUG!
```

**The judge can't catch errors it would make itself.**

#### 2. Position Bias

Research shows LLM judges favor responses based on **position**, not quality:

| Response Order | Preference |
|----------------|------------|
| A first, B second | Prefers A (60% of time) |
| B first, A second | Prefers B (60% of time) |

**The order matters more than the content.**

#### 3. Verbosity Bias

LLM judges prefer **longer** responses, regardless of accuracy:

```
Short Response: "The answer is 42."
Long Response: "After careful consideration of the underlying 
               mathematical principles and exploring various 
               approaches, I've determined that the answer is 43."

LLM Judge: "Long response is better—more thorough!" ❌
```

#### 4. Self-Enhancement Bias

GPT-4 prefers GPT-4 outputs. Claude prefers Claude outputs.

| Judge Model | Prefers Own Family |
|-------------|-------------------|
| GPT-4 | 67% preference for GPT models |
| Claude | 71% preference for Anthropic models |

#### 5. Non-Determinism

Same input, different outputs:

```python
for _ in range(5):
    score = gpt4_judge(response)
    print(score)

# Output:
# 8/10
# 7/10
# 9/10
# 8/10
# 7/10 (!)
```

**Which score is "correct"? None of them!**

### 🎯 Key Takeaway

> **"Using one probabilistic system to judge another is like having a drunk person check if another drunk person is sober."**

---

## 5.3: Beaver: Probabilistic Bounds

### The Concept

**Beaver** (Berkeley, 2024) computes **probability bounds** on whether an output satisfies a defined constraint.

Instead of asking "Was this claim proved?" it asks "What fraction of candidate outputs satisfy this structural constraint?"

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        BEAVER APPROACH                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Define constraint: "Output must be valid JSON"              │
│                                                                  │
│  2. Systematically explore token space:                         │
│     - Build token trie of possible outputs                      │
│     - Prune branches that violate constraints                   │
│     - Compute probability mass of valid branches                │
│                                                                  │
│  3. Output: "P(valid JSON) ≥ 87.3%"                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### When Beaver Works Well

| Use Case | Beaver Fit |
|----------|------------|
| Format constraints (JSON, XML) | ✅ Excellent |
| Length constraints | ✅ Good |
| Keyword inclusion/exclusion | ✅ Good |
| **Mathematical correctness** | ❌ Can't verify |
| **Logical consistency** | ❌ Can't verify |
| **Factual accuracy** | ❌ Can't verify |

### The Limitation

Beaver can tell you: **"87% chance this is valid JSON"**

Beaver **cannot** tell you: **"This calculation is correct"**

```
Query: "What is 2+2?"
LLM Response: "5"

Beaver: "This response has 100% probability of being a number!" ✅
QWED: "This response is mathematically WRONG." ❌
```

### Beaver vs QWED

| Aspect | Beaver | QWED |
|--------|--------|------|
| **Output** | "Constraint satisfaction is at least 87%" | "This supported claim was deterministically verified" |
| **Method** | Probability bounds | Mathematical proof |
| **Verifies** | Format/structure | Content/correctness |
| **Use case** | Risk assessment | Production deployment |

### 🎯 Key Takeaway

> **"Beaver tells you structural risk. QWED tells you whether a supported claim was deterministically verified."**

---

## 5.4: QWED: Solver-as-a-Judge

### The Philosophy

QWED replaces neural network opinions with **mathematical proof**.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│   LLM-as-Judge:    GPT-4  →  "This looks right"  (opinion)     │
│                                                                  │
│   Solver-as-Judge: SymPy  →  "2+2=4 ✓"           (proof)       │
│                    Z3     →  "Valid ∀x"          (theorem)     │
│                    AST    →  "No injection"      (analysis)    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### The 8 Specialized Engines

QWED doesn't use one tool for everything. It uses **specialized solvers**:

| Engine | Solver | Domain |
|--------|--------|--------|
| 🧮 **Math** | SymPy | Arithmetic, calculus, algebra |
| 🧠 **Logic** | Z3 | Propositional logic, quantifiers |
| 🛡️ **SQL** | SQLGlot | Query safety, injection detection |
| 📊 **Stats** | Sandbox | Statistical computations |
| ✅ **Facts** | TF-IDF + Entity Match | Claim verification |
| 🔐 **Code** | AST Analysis | Security vulnerabilities |
| 🖼️ **Image** | Metadata + VLM | Visual claims |
| 🤖 **Reasoning** | Multi-provider | Chain-of-thought |

### The Untrusted Translator Pattern

```python
from qwed_sdk import QWEDLocal

# LLM translates natural language → symbolic
# QWED verifies symbolically → proof

client = QWEDLocal(provider="openai")

# User asks in natural language
result = client.verify_math("Is 17*24 equal to 408?")

# QWED internally:
# 1. LLM translates: "17*24 == 408"
# 2. SymPy evaluates: 17*24 = 408 ✓
# 3. Returns: verified=True, proof="17*24 = 408"

print(result.verified)  # True (PROVEN, not guessed)
```

### Why It Works

| LLM Weakness | QWED Solution |
|--------------|---------------|
| Can't compute | SymPy computes exactly |
| Can't prove | Z3 proves formally |
| Makes parsing errors | AST parses correctly |
| Has biases | Solvers have no opinions |
| Non-deterministic | 100% reproducible |

### 🎯 Key Takeaway

> **"QWED uses the LLM for what it's good at (translation) and solvers for what they're good at (computation)."**

---

## 5.5: Choosing the Right Tool

### Decision Flowchart

```
                    What do you need to verify?
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Safety?         Quality?        Correctness?
              │               │               │
              ▼               ▼               ▼
        ┌─────────┐    ┌───────────┐    ┌─────────┐
        │Guardrails│    │LLM-as-Judge│    │  QWED   │
        │(if blocking│    │(if subjective│    │(if math,│
        │ harmful   │    │ rating OK)   │    │ logic,  │
        │ content)  │    │              │    │ code)   │
        └─────────┘    └───────────┘    └─────────┘
```

### Recommendation Matrix

| Scenario | Recommended Tool |
|----------|------------------|
| Block toxic content | Guardrails |
| Rate essay quality | LLM-as-Judge (with caveats) |
| Assess format compliance probability | Beaver |
| **Verify calculations** | **QWED** |
| **Verify logic** | **QWED** |
| **Verify code safety** | **QWED** |
| **Verify SQL queries** | **QWED** |
| **Enterprise compliance** | **QWED** |

### Hybrid Approach

In production, you often need multiple tools:

```python
def production_pipeline(llm_response):
    # Layer 1: Safety (Guardrails)
    if not guardrails.is_safe(llm_response):
        return "Blocked: Safety violation"
    
    # Layer 2: Format (Beaver, optional)
    if beaver.json_probability(llm_response) < 0.95:
        return "Warning: Format uncertain"
    
    # Layer 3: Correctness (QWED)
    result = qwed.verify(llm_response)
    if not result.verified:
        return f"Error: {result.error}"
    
    return result.value  # Deterministically verified output
```

### 🎯 Key Takeaway

> **"Guardrails for safety, Beaver for structural probability, QWED for deterministic verification."**

---

## 🧪 Exercise: Compare the Approaches

Try this verification task with different tools:

**Claim:** "The compound interest on $1000 at 5% for 3 years is $157.63"

### LLM-as-Judge Approach
```python
# Ask GPT-4 to verify
prompt = "Is this correct: compound interest on $1000 at 5% for 3 years = $157.63?"
result = gpt4(prompt)
# Result: "Yes, that appears correct!" (BUT IS IT?)
```

### QWED Approach
```python
from qwed_sdk import QWEDLocal

client = QWEDLocal()
result = client.verify_math(
    "1000 * (1 + 0.05)^3 - 1000 == 157.63"
)
print(result.verified)       # True
print(result.computed_value) # 157.625 (close enough with rounding)
```

**Which one would you trust with real money?**

---

## 📋 Self-Assessment Quiz

<details>
<summary><strong>Q1: What are the 4 categories in the verification "zoo"?</strong></summary>

**Answer:** Guardrails (safety filters), LLM-as-Judge (quality scoring), Beaver (probability bounds), and QWED (mathematical proof).

</details>

<details>
<summary><strong>Q2: Name 3 biases that make LLM-as-Judge unreliable.</strong></summary>

**Answer:** Any 3 of: Position bias, verbosity bias, self-enhancement bias, recursive hallucination, non-determinism.

</details>

<details>
<summary><strong>Q3: What's the difference between Beaver and QWED?</strong></summary>

**Answer:** Beaver reports a probability bound on a structural constraint, while QWED verifies whether a supported claim passed a deterministic check. Beaver is useful for format/risk assessment; QWED is for proof-oriented correctness checks.

</details>

<details>
<summary><strong>Q4: What is "Solver-as-a-Judge"?</strong></summary>

**Answer:** QWED's philosophy of using mathematical solvers (SymPy, Z3, AST) instead of LLMs to verify correctness. Math proves answers, AI doesn't judge.

</details>

<details>
<summary><strong>Q5: When should you use LLM-as-Judge vs QWED?</strong></summary>

**Answer:** Use LLM-as-Judge for subjective quality ratings (essay quality, creativity). Use QWED for objective correctness (math, logic, code, facts, SQL).

</details>

---

## 📝 Summary

| Tool | Method | Output | Trustworthiness |
|------|--------|--------|-----------------|
| **Guardrails** | Rules | Pass/Fail | High (for safety) |
| **LLM-as-Judge** | Neural | Score | Low (biased) |
| **Beaver** | Probabilistic | % Bound | Medium (for format) |
| **QWED** | Symbolic | Proof | **Highest** (math) |

---

## ➡️ Next Steps

Now that you understand the landscape, learn how to apply verification to specific industries:

**[→ Module 6: Domain-Specific Verification](../module-6-domains/README.md)**

---

*"If it can't be verified, it doesn't ship."*
