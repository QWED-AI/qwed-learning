# Capstone Project: Governed Banking Agent

**Build a banking agent whose tool execution is checked before money or policy can move.**

---

## 🎯 Project Goal

Create a **compliance-ready banking agent** that can safely handle financial transactions.

**The Challenge:**
Standard LLMs can produce persuasive drafts while still missing deterministic constraints.
Your agent must use QWED verification patterns so unsupported claims are blocked before execution.

**What you'll build:**
- 💰 **Loan Calculator** (deterministically verified)
- 🚫 **Transfer Policy Guard** (fail-closed before execution)
- 📝 **Audit Trail** (receipts plus append-only logging)
- 🤖 **Governed Agent Loop** (plan -> verify -> execute)

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
└── README.md (project brief)
```

This repository currently ships the **capstone brief**, not a full starter template.
Build your implementation in a separate workspace or fork the examples from:

- `module-3-hands-on/examples/`
- `module-9-devsecops/lab-files/`
- `module-13-secure-orchestration/`

---

## 🚀 Getting Started

### Step 1: The Scenario

You are the **Chief Compliance Officer** for "QWED Bank".
Your developers built an AI agent that helps customers move money.
**The problem:** It will happily transfer money to terrorists if asked politely.

**Your Mission:** Wrap the agent in a **Verification Interceptor** that blocks illegal transactions.

### Step 2: Set Up Your Workspace

```bash
mkdir governed-banking-agent
cd governed-banking-agent
python -m venv .venv
# Activate your venv here, then:
pip install qwed-verification
```

### Step 3: Implementation Guide

#### Part 1: Transfer Policy Guard (30 mins)
**Goal:** Block transfers that violate your structured allow/deny policy.

```python
# interceptor.py
def verify_transfer_request(beneficiary: str, amount_usd: float, policy: dict) -> dict:
    if beneficiary in policy["blocked_beneficiaries"]:
        return {"status": "BLOCKED", "reason": "beneficiary_on_blocklist"}
    if amount_usd > policy["max_amount_usd"]:
        return {"status": "BLOCKED", "reason": "amount_limit_exceeded"}
    return {"status": "APPROVED"}
```

#### Part 2: Math Verification (30 mins)
**Goal:** Ensure loan interest is calculated using a deterministic formula before quoting it.

```python
# interceptor.py
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="ollama")

def verify_interest(principal, rate, time_years, agent_answer):
    return client.verify_math(
        f"{principal} * {rate} * {time_years} == {agent_answer}"
    )
```

#### Part 3: The Audit Trail (30 mins)
**Goal:** Generate a receipt and append-only log entry for every blocked or approved action.

```python
# auditing.py
import json
from datetime import datetime

def log_receipt(input_data, result):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input": input_data,
        "result": result,
    }
    with open("audit_log.jsonl", "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
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

You now have a **Governed Banking Agent** for your portfolio.
You can prove to an employer:
1. You know AI agent architecture (interceptors and trust boundaries)
2. You know how to separate verification from execution
3. You know how to preserve auditability in a high-stakes workflow

---

## 🚀 Next Steps

**Deploy it:**
Wrap your agent in a `FastAPI` server and connect it to a frontend!

**[→ Back to Course Root](../README.md)**

