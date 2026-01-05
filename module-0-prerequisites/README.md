# Module 0: Prerequisites - AI Verification Basics

**Duration:** 20 minutes

**For:** Developers new to LLMs or AI verification

**Goal:** Understand core concepts before diving into verification techniques

---

## What You'll Learn

- 🤖 What is an LLM and how does it work?
- 💭 What are hallucinations and why do they happen?
- ⚖️ Probabilistic vs. Deterministic systems
- 🎯 Why verification is critical for production AI

---

## 1. What is a Large Language Model (LLM)?

### The Simple Explanation

An LLM is a **text prediction machine** trained on massive amounts of internet text.

**How it works:**
1. You give it a prompt: `"The capital of France is"`
2. It predicts the most likely next word: `"Paris"`
3. It keeps predicting: `"Paris, known for the Eiffel Tower..."`

**Key insight:** It doesn't "know" facts. It predicts patterns.

### Real Example

```python
Prompt: "2 + 2 ="
LLM predicts: "4" ✅ (saw this pattern a million times)

Prompt: "2843 + 7291 ="  
LLM predicts: "10134" ✅ or "9134" ❌ (less common, might guess wrong)
```

### What LLMs Are Good At

✅ **Pattern Recognition**
- Writing emails
- Translating languages
- Summarizing text
- Code generation (common patterns)

✅ **Creative Tasks**
- Brainstorming ideas
- Writing stories
- Conversational responses

### What LLMs Are Bad At

❌ **Precise Calculations**
- Math (they predict digits, not calculate)
- Logic (they pattern-match, not reason)
- Code execution (they generate code, can't run it)

❌ **Factual Accuracy**
- Might mix up dates, numbers, names
- Can't distinguish truth from plausible-sounding fiction

---

## 2. What Are Hallucinations?

### Definition

**Hallucination:** When an LLM generates plausible-sounding but incorrect information.

### Why They Happen

LLMs are trained to predict **plausible** text, not **true** text.

**Example:**
```
User: "Who was the first person on Mars?"
LLM: "Neil Armstrong in 1969."

✅ Plausible (Armstrong was first on Moon)
❌ Wrong (no one has been to Mars yet)
```

### Types of Hallucinations

1. **Factual Errors**
   - Wrong dates, numbers, names
   - "iPhone 15 was released in 2019" ❌

2. **Logic Errors**
   - "If A > B and B > C, then C > A" ❌

3. **Calculation Errors**
   - "15% of $200 is $35" ❌ (should be $30)

4. **Invented References**
   - "According to study XYZ-2023..." (study doesn't exist)

### Real-World Impact

**Healthcare:** Wrong dosage (could be fatal)  
**Finance:** Incorrect interest calculation ($12,889 error in production)  
**Legal:** Fake case citations (lawyer sanctioned)  
**E-commerce:** Hallucinated discounts (revenue loss)

---

## 3. Probabilistic vs. Deterministic Systems

### Probabilistic (LLMs)

**How it works:** Predicts based on patterns and probabilities

```python
# LLM generates different answers each time
llm("What is 2+2?")
→ "4" (90% probability)
→ "2+2 equals four" (8%)
→ "The answer is 4" (2%)
```

**Characteristics:**
- ✅ Flexible, creative
- ✅ Handles ambiguity well
- ❌ Not 100% reliable
- ❌ Different outputs for same input

**Use cases:** Creative writing, summarization, conversation

### Deterministic (Verification Engines)

**How it works:** Follows exact rules, always same output

```python
# Calculator always gives same answer
calculator(2 + 2)
→ 4 (100% certainty, always)
```

**Characteristics:**
- ✅ 100% reliable (for verifiable tasks)
- ✅ Same input = same output
- ❌ Can't handle ambiguity
- ❌ Needs precise specifications

**Examples:** SymPy (math), Z3 (logic), compilers (code)

### Why Both Matter

**Best practice:** Use LLM for **generation**, deterministic tools for **verification**

```
User Query (English)
    ↓
LLM translates to code
    ↓
Deterministic engine verifies
    ↓
Return verified result
```

This is the **neurosymbolic approach** QWED uses!

---

## 4. Why Verification is Critical

### The Trust Problem

**Without Verification:**
- Hope LLM is right (73-85% accuracy on finance tasks)
- Manually check outputs (slow, error-prone)
- Ship bugs to production (costly)

**With Verification:**
- Mathematically prove correctness
- Block errors before they reach users
- Ship with confidence

### Cost of Unverified AI

| Industry | Cost of Error | Example |
|----------|---------------|---------|
| Healthcare | Lives | Wrong dosage (1000x overdose) |
| Finance | Revenue | $12,889 calculation error |
| Legal | Sanctions | Fake case citations |
| E-commerce | Trust | Hallucinated discounts |

### When Verification is Required

✅ **Must verify:**
- Financial calculations
- Medical dosages
- Legal citations
- Security checks
- Regulatory compliance

⏸️ **Optional verification:**
- Creative writing
- Casual conversation
- Brainstorming
- Subjective opinions

---

## Quick Check: Did You Understand?

**Answer these to test yourself:**

1. **What is an LLM?**
   <details>
   <summary>Answer</summary>
   A text prediction machine that generates likely next words based on training patterns, not facts.
   </details>

2. **Why do hallucinations happen?**
   <details>
   <summary>Answer</summary>
   LLMs predict plausible text, not true text. They can't distinguish fact from fiction.
   </details>

3. **Difference between probabilistic and deterministic?**
   <details>
   <summary>Answer</summary>
   Probabilistic (LLM): Flexible but unreliable, different outputs each time.  
   Deterministic (Calculator): Exact same output for same input, 100% reliable.
   </details>

4. **When should you use verification?**
   <details>
   <summary>Answer</summary>
   When errors have real consequences: money, lives, legal issues, security.
   </details>

---

## Key Takeaways

✅ **LLMs predict patterns, not facts**  
✅ **Hallucinations are inevitable** (not bugs, it's how they work)  
✅ **Probabilistic ≠ Deterministic**  
✅ **Verification prevents costly errors**

**Next:** Now that you understand the problem, learn how QWED solves it!

→ [Module 1: The Crisis](../module-1-the-crisis/README.md)

---

## Additional Resources

- [OpenAI: GPT Concepts](https://platform.openai.com/docs/guides/text-generation)
- [Anthropic: Claude Model Card](https://www.anthropic.com/claude)
- [Paper: "On Hallucinations in LLMs"](https://arxiv.org/abs/2305.14552)
