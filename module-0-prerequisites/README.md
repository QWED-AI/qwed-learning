# Module 0: Prerequisites - Trust-Boundary Basics

**Duration:** 20 minutes  
**For:** Developers new to LLMs, verification, or trust-critical AI systems  
**Goal:** Build the right mental model before touching any QWED API

---

## What You'll Learn

- Proof vs. confidence
- What an LLM actually does
- Why hallucinations are inevitable
- Probabilistic vs. deterministic systems
- Why fail-closed verification matters

---

## Start Here First

Before anything else, read:

- [Proof vs. Confidence](00-proof-vs-confidence.md)
- [What Are Formal Methods?](01-formal-methods-intro.md)

These two lessons establish the distinction that drives the entire QWED ecosystem:

- parsing is not proof
- simplification is not verification
- confidence is not evidence
- unsupported is not approved

---

## 1. What Is a Large Language Model?

An LLM is a **text prediction system** trained on massive corpora.

It does not "know" facts the way a deterministic engine proves facts. It predicts likely continuations.

### Example

```python
Prompt: "2 + 2 ="
LLM predicts: "4"

Prompt: "2843 + 7291 ="
LLM predicts a likely continuation, which may still be wrong
```

### What LLMs Are Good At

- drafting language
- summarization
- translation
- extracting structured information
- conversational interaction

### What LLMs Are Bad At

- exact arithmetic
- formal logic
- safety-critical execution decisions
- distinguishing a plausible answer from a proved answer

---

## 2. What Are Hallucinations?

A hallucination is a plausible-sounding output that is still wrong.

This happens because LLMs optimize for pattern completion, not truth.

### Examples of Hallucinations

- wrong calculations
- fake legal citations
- invalid medical dosages
- invented policies, studies, or references

---

## 3. Probabilistic vs. Deterministic Systems

### Probabilistic Systems

LLMs are probabilistic:

- they generate likely outputs
- they may vary across runs
- they can be helpful without being provable

### Deterministic Systems

Deterministic engines:

- follow exact rules
- produce the same result for the same input
- can prove or reject claims within supported domains

### Why QWED Uses Both

QWED uses the LLM as an **untrusted translator** and the deterministic engine as the **trust decision layer**.

```text
User query -> LLM translation -> deterministic verification -> verified / invalid / unverifiable
```

---

## 4. Why Verification Is Critical

Without verification:

- bugs ship to production
- users inherit silent trust failures
- "helpful" outputs can cause financial, legal, or safety harm

With verification:

- supported claims can be checked deterministically
- invalid claims can be blocked
- unsupported claims can be surfaced honestly as `UNVERIFIABLE`

---

## 5. What Fail-Closed Means

When QWED cannot establish proof, the answer should not silently degrade into:

- a fallback guess
- a lower confidence answer
- a default value that looks safe

The right outcomes are:

- `BLOCKED`
- `UNVERIFIABLE`
- `QUARANTINED`
- `HUMAN_REVIEW_REQUIRED`

This is what makes QWED a trust-boundary system rather than just another AI helper.

---

## Quick Check

1. What is the difference between a useful answer and a verified answer?
2. Why is confidence not the same thing as proof?
3. What should happen when a claim is unsupported?
4. Why is "safe default" often the wrong pattern for trust-critical AI?

If you can answer those clearly, you are ready for the rest of the course.

---

## Next

- [Proof vs. Confidence](00-proof-vs-confidence.md)
- [What Are Formal Methods?](01-formal-methods-intro.md)
