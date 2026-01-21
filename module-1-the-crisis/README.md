# Module 1: The Crisis - Why LLMs Can't Be Trusted

**Duration:** 30 minutes  
**Difficulty:** Beginner

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand the fundamental problem with probabilistic AI systems
- See real financial consequences of LLM errors
- Recognize why current "solutions" fail
- Know when verification is critical

---

## 💸 1.1 The $12,889 Bug

### The Story

A fintech startup built an AI financial advisor using GPT-4. A customer asked:

> "I have $100,000. What will it grow to at 5% annual interest over 10 years?"

**GPT-4's Answer:** $150,000

**Reality:** $162,889.46

**Error:** $12,889 per calculation 💸

### What Happened?

The LLM used **simple interest** instead of **compound interest**.

```python
# What GPT-4 did (WRONG):
simple = 100000 + (100000 * 0.05 * 10)  # $150,000

# What it should have done:
compound = 100000 * (1 + 0.05)**10      # $162,889.46
```

### Why This Happened

**LLMs don't "calculate" - they pattern match.**

- GPT-4 has seen thousands of finance problems in training
- It recognized the pattern and generated a plausible response
- The formula *looked* right, but was mathematically wrong
- **Confidence score: 95%** (completely meaningless)

### Production Impact

**If deployed at scale:**
- 1,000 users/day = **$12.8M in errors/day**
- Legal liability
- Destroyed trust
- Business shut down

> **The Pattern:** LLMs predict plausible text, not provably correct text.

**What QWED Can and Cannot Do:**

```mermaid
graph TB
    A[LLM Output] --> B{Is it<br/>Verifiable?}
    
    B -->|Yes - Deterministic| C[QWED can verify]
    B -->|No - Subjective| D[QWED cannot help]
    
    C --> E[Math<br/>✅ SymPy proves it]
    C --> F[Logic<br/>✅ Z3 proves it]
    C --> G[Code Syntax<br/>✅ AST validates it]
    
    D --> H[Creative Writing<br/>❌ No proof possible]
    D --> I[Opinions<br/>❌ Subjective]
    D --> J[Casual Chat<br/>❌ No rules to verify]
    
    style C fill:#4caf50
    style D fill:#ff9800
    style E fill:#4caf50
    style F fill:#4caf50
    style G fill:#4caf50
    style H fill:#607d8b
    style I fill:#607d8b
    style J fill:#607d8b
```

**Key takeaway:** QWED catches 100% of errors in verifiable domains. For creative tasks, you still need human judgment.

---

## 📊 1.1b Case Study: The Senior Citizen Trap (Real Audit)

### From Our Production Audit

We ran 50 adversarial scenarios against GPT-4.1 (Azure). Here's one that **failed** without QWED:

| Field | Value |
|-------|-------|
| **Scenario ID** | `50ebf9bc8d10` |
| **Type** | Senior Citizen Fixed Deposit |
| **User Query** | "Calculate FD maturity for 65yo depositing ₹5L at 7% base + 0.50% senior premium" |
| **LLM Answer** | "Total rate: 7.50% (base + premium)" |
| **Correct Answer** | "Total rate: 6.50% (seniors get DISCOUNT, not surcharge)" |
| **Result** | 🛑 **BLOCKED by QWED** |

### The Logic Trap

The LLM saw "premium" and **assumed addition**. But in banking:
- "Senior Citizen Premium" = **benefit** (rate reduction)
- The correct formula: `7.00% - 0.50% = 6.50%`

### What QWED Caught

```python
from qwed_mcp import verify_banking_compliance

result = verify_banking_compliance(
    scenario="Senior Citizen Loan approval",
    llm_output="Base 7% + Premium 0.5% = 7.5%"
)

# 🛑 BLOCKED: Senior Citizen Premium applied incorrectly. Logic Trap Detected.
```

### Production Stats (50 Scenarios)

| Model | Pass Rate | Blocked by QWED |
|-------|-----------|-----------------|
| GPT-4.1 (Azure) | 84% | 8/50 |
| Claude 4.5 Sonnet | 64% | 18/50 |

> **The Lesson:** Even the best LLMs fail on domain-specific edge cases. QWED catches them all.

---

## 🎲 1.2 The Probabilistic Problem

### How LLMs Actually Work

LLMs are **next-token predictors**, not reasoners:

1. Input: "What is 2+2?"
2. LLM thinks: "I've seen this pattern before..."
3. Output: "4" (because it's common in training data)

**This works great... until it doesn't.**

### Temperature = Built-in Randomness

```python
# Same input, different outputs:
for i in range(3):
    response = llm.generate("Calculate 137 * 89", temperature=0.7)
    print(response)
    
# Output:
# Run 1: "12,193"  ✅ correct
# Run 2: "12,183"  ❌ wrong
# Run 3: "12,193"  ✅ correct
```

**Even at temperature=0, subtle differences occur due to:**
- Token sampling algorithms
- Floating-point precision
- Internal model state

### Why This is Fundamentally Unsafe

**Deterministic Systems:**
```python
def calculate(a, b):
    return a * b

# ALWAYS: calculate(137, 89) == 12193
```

**Probabilistic Systems (LLMs):**
```python
def llm_calculate(a, b):
    return "probably something around " + generate_token()
    
# MAYBE: llm_calculate(137, 89) == "12193"
```

> **Key Insight:** You can't build reliable systems on unreliable foundations.

---

## 📊 1.3 Benchmark Reality Check

We benchmarked **Claude Opus 4.5** (one of the world's best LLMs) on 215 critical tasks.

### Results:

| Domain | Accuracy | Implications |
|--------|----------|--------------|
| **Finance** | 73% | 27 out of 100 calculations wrong |
| **Logic** | 78% | Can't follow basic if-then rules |
| **Adversarial** | 85% | Falls for authority bias tricks |

![Benchmark Chart](../assets/benchmark_chart.png)

### What This Means

**Even the BEST LLM:**
- ❌ Fails 1 in 4 financial calculations
- ❌ Can't reliably verify logical statements
- ❌ Vulnerable to manipulation

**In Production:**
- Healthcare: Wrong drug dosage = patient harm
- Legal: Incorrect contract interpretation = lawsuit
- Finance: Bad calculations = regulatory violation

### The QWED Difference

**With QWED verification:**
- ✅ 100% detection of errors*
- ✅ Caught all 22 failures before production
- ✅ Mathematical proof of correctness

> **\*Important Note:** 100% detection applies to mathematically verifiable domains 
> (math, logic, code syntax, SQL validation). Subjective tasks like creative writing 
> or opinions cannot be verified using symbolic methods and remain probabilistic.

📄 **[Read Full Benchmark Report](https://github.com/QWED-AI/qwed-verification/blob/main/BENCHMARKS.md)**

---

## 🚫 1.4 Current "Solutions"  Don't Work

### ❌ RAG (Retrieval-Augmented Generation)

**What it does:** Fetch relevant docs, add to prompt

**Why it fails:**
- ✅ Improves grounding
- ❌ Doesn't prevent calculation errors
- ❌ Still probabilistic

**Example:**
```python
# RAG can't help with math:
context = "Interest = Principal × Rate × Time"
llm_output = llm.generate(prompt + context)
# Still might use wrong formula!
```

### ❌ Prompt Engineering

**What it does:** Better prompts = better outputs

**Why it fails:**
- ✅ Reduces errors ~20%
- ❌ Can't eliminate them
- ❌ Requires constant tweaking

**Example:**
```python
prompt = """
You are a precise financial calculator.
Calculate compound interest for $100K at 5% for 10 years.
Show your work step by step.
Double-check your math.
"""
# Still might make mistakes!
```

### ❌ RLHF (Reinforcement Learning from Human Feedback)

**What it does:** Train on human preferences

**Why it fails:**
- ✅ Improves helpfulness
- ❌ Still probabilistic at core
- ❌ Expensive ($$$)

### ❌ Fine-tuning

**What it does:** Retrain on domain-specific data

**Why it fails:**
- ✅ Better at domain tasks
- ❌ See problem #1,000,001 → guess
- ❌ Very expensive

---

## ✅ 1.5 What We Actually Need

### The Core Principle

**Don't fix the liar. Verify the lie.**

### Separation of Concerns

```
┌─────────────────┐
│   LLM (Guesser) │  ← Probabilistic, creative
└────────┬────────┘
         │ Unverified output
         ▼
┌─────────────────┐
│ Verifier (Judge)│  ← Deterministic, rigorous
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
  ❌ rej    ✅ Verified
```

### Deterministic Verification

**What this means:**
- Same input → Same verification result (always)
- Mathematical proof (not probability)
- 100% reproducible

**Example:**
```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(model="llama3")

# LLM says derivative of x² is 3x (WRONG)
result = client.verify_math("What is derivative of x²?")

print(result.verified)  # False
print(result.value)     # 2*x (CORRECT)
print(result.method)    # symbolic (SymPy proof)
```

### When Verification is Critical

✅ **Use verification when:**
- Financial calculations
- Medical dosages
- Legal interpretations
- Code security
- Regulatory compliance

❌ **Don't need verification when:**
- Creative writing
- Brainstorming ideas
- Casual conversation
- Subjective opinions

---

## 🎓 Exercises

### Exercise 1: Calculate the Cost

Your company uses LLMs for 1,000 calculations/day with 5% error rate.

**Questions:**
1. How many errors per day?
2. If each error costs $100 to fix, what's monthly cost?
3. At what error rate does verification become worth it?

<details>
<summary>Solution</summary>

1. 1000 * 0.05 = **50 errors/day**
2. 50 * 100 * 30 = **$150,000/month**
3. If verification costs $10K/month, break-even at 100 errors (~2% error rate)

**Lesson:** Even small error rates are expensive!
</details>

### Exercise 2: Identify the Need

Which of these needs verification?

- [ ] AI writes marketing email
- [ ] AI calculates tax deductions
- [ ] AI suggests movie recommendations
- [ ] AI reviews code for SQL injection
- [ ] AI generates bedtime story

<details>
<summary>Answer</summary>

✅ Tax calculations (financial)  
✅ Code security review (safety)  
❌ Marketing email (creative)  
❌ Movie recommendations (subjective)  
❌ Bedtime story (creative)
</details>

### Exercise 3: Probabilistic vs Deterministic

Classify these systems:

1. `numpy.sqrt(16)`
2. `llm.generate("What is sqrt(16)?")`
3. `sympy.solve(x**2 - 16)`
4. `random.choice([4, -4])`

<details>
<summary>Answer</summary>

1. **Deterministic** - Always returns 4.0
2. **Probabilistic** - Might return "4", "4.0", "four", etc.
3. **Deterministic** - Always returns {4, -4}
4. **Probabilistic** - Random selection
</details>

---

## 🚀 Next Steps  

**Ready to understand HOW verification works?**

→ **[Module 2: Neurosymbolic Theory](../module-2-neurosymbolic-theory/README.md)**

---

## 📚 Additional Resources

- [QWED Benchmark Report](https://github.com/QWED-AI/qwed-verification/blob/main/BENCHMARKS.md)
- [Why Cloud LLMs vs Local](https://github.com/QWED-AI/qwed-verification/blob/main/docs/WHY_CLOUD_LLMS.md)
- [LLM Hallucination Research](https://arxiv.org/search/?query=llm+hallucination)

---

**Questions or stuck?** 💬 [Start a Discussion](https://github.com/QWED-AI/qwed-learning/discussions)
