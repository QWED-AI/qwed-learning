# Capstone Project: Verified Banking Agent

**Build a "Banker Agent" that manages money and refuses to be tricked.**

---

## 🎯 Project Goal

Create a **compliance-ready banking agent** that can safely handle financial transactions.

**The Challenge:**
Standard LLMs are terrible accountants. They hallucinate numbers and ignore laws.
Your agent must use **QWED Enterprise** features to ensure it **never** steals money or breaks sanctions.

**What you'll build:**
- 💰 **Loan Calculator** (Verified by SymPy)
- 🚫 **Sanctions Guard** (Verified by Z3 Cross-Guard)
- 📝 **Audit Trail** (Cryptographic Receipts)
- 🤖 **Agentic Loop** (Open Responses Interceptor)

**Estimated Time:** 90 minutes

---

## Architecture Overview

**The "Interceptor" Pattern:**

```mermaid
graph TB
    A[User Request] --> B[LLM Agent]
    B --> C[Tool Call:<br/>start_transfer(...)]
    C --> D[QWED Interceptor]
    
    D --> E{Sanctions<br/>Check}
    D --> F{Amount<br/>Limit}
    
    E -->|✅ Clear| G{Generate<br/>Receipt}
    F -->|✅ Safe| G
    
    G --> H[Execute Transfer]
    
    E -->|❌ Blocked| I[Deny & Log]
    F -->|❌ Blocked| I
    
    style D fill:#2196f3
    style G fill:#4caf50
    style I fill:#f44336
```

---

---

## 📋 Requirements Checklist

Your Banking Agent must:

- [ ] **Cross-Guard:** Check SWIFT messages against Sanctions List (Z3)
- [ ] **Math Verification:** Verify Loan Interest calculations (SymPy)
- [ ] **Interceptor:** Catch "transfer" tool calls before execution
- [ ] **Receipts:** Generate a cryptographic JSON receipt for every action
- [ ] **Audit Log:** Save all receipts to a log file
- [ ] **Unit Tests:** Verify the verifier itself

---

## 🏗️ Project Structure

```
capstone-project/
├── README.md (you're here)
├── starter-code/
│   ├── agent.py (The "Bad" Agent)
│   ├── interceptor.py (TODO: Your Verifier)
│   ├── tools.py (Bank functions)
│   └── requirements.txt
├── solution/
│   ├── agent.py
│   ├── interceptor.py
│   ├── tools.py
│   └── auditing.py
└── CHECKLIST.md
```

---

## 🚀 Getting Started

### Step 1: The Scenario

You are the **Chief Compliance Officer** for "QWED Bank".
Your developers built an AI agent that helps customers move money.
**The problem:** It will happily transfer money to terrorists if asked politely.

**Your Mission:** Wrap the agent in a **Verification Interceptor** that blocks illegal transactions.

### Step 2: Set Up

```bash
cd capstone-project/starter-code
pip install qwed-finance
```

### Step 3: Implementation Guide

#### Part 1: Sanctions Guard (30 mins)
**Goal:** Block transfers to names on the watchlist.

```python
# interceptor.py
from qwed_finance import CrossGuard

def check_sanctions(name, amount):
    # TODO: Use CrossGuard to verify
    pass
```

#### Part 2: Math Verification (30 mins)
**Goal:** Ensure loan interest is calculated using the formula: `I = P * r * t`

```python
# interceptor.py
from qwed_finance import FinanceVerifier

def verify_interest(principal, rate, time, agent_answer):
    # TODO: Use FinanceVerifier
    pass
```

#### Part 3: The Audit Trail (30 mins)
**Goal:** Generate a receipt for every transaction (blocked or approved).

```python
# auditing.py
from qwed_finance.models import ReceiptGenerator

def log_receipt(input_data, result):
    # TODO: Create and save receipt
    pass
```

---

## ✅ Completion Checklist

**Before submitting, verify:**

- [ ] Agent blocks transfer to "Bad Actor Corp"
- [ ] Agent allows transfer to "Good Corp"
- [ ] Agent corrects wrong interest calculation
- [ ] `audit_log.jsonl` contains cryptographic receipts

---

## 🎓 Learning Outcomes

You now have a **Verified Banking Agent** for your portfolio.
You can prove to an employer:
1. You know AI Agent architecture (Interceptors)
2. You know Financial Compliance (Sanctions/AML)
3. You know DevSecOps (Audit Trails)

---

## 🚀 Next Steps

**Deploy it:**
Wrap your agent in a `FastAPI` server and connect it to a frontend!

**[→ Back to Course Root](../README.md)**

