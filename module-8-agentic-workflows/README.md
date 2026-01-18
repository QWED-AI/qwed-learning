# Module 8: Agentic Integration

> **"The agent doesn't make the decision. It executes verified decisions."**

⏱️ **Duration:** 60 minutes  
📊 **Level:** Advanced  
🎯 **Goal:** Learn to verify AI agent tool calls in real-time streaming workflows.

---

## 🧠 What You'll Learn

After this module, you'll understand:

- ✅ The Interceptor Pattern for tool call verification
- ✅ Commerce safety with UCP (Universal Commerce Protocol)
- ✅ Using TypeScript SDK for Node.js agents
- ✅ Streaming verification in agentic loops

---

## 📚 Table of Contents

| Lesson | Topic | Time |
|--------|-------|------|
| 8.1 | [The Interceptor Pattern](#81-the-interceptor-pattern) | 20 min |
| 8.2 | [Commerce Safety (UCP)](#82-commerce-safety-ucp) | 20 min |
| 8.3 | [The Polyglot Agent](#83-the-polyglot-agent-typescript) | 20 min |

---

## 8.1: The Interceptor Pattern

### The Problem

Modern AI agents don't just chat—they **execute tools**:

```
User: "Transfer $5000 to account 123456"
Agent: Calls transfer_money(amount=5000, to="123456")
```

**What happens if the LLM hallucinates the amount?**

### The Solution: Verification Middleware

```mermaid
graph LR
    A[User Request] --> B[LLM Agent]
    B --> C[Tool Call Intent]
    C --> D[QWED Interceptor]
    D --> E{Verified?}
    E -->|✅ Yes| F[Execute Tool]
    E -->|❌ No| G[Block & Log]
    
    style D fill:#4caf50
    style G fill:#f44336
```

### Implementation with Open Responses

```python
from qwed_finance.integrations import OpenResponsesIntegration

# Create the interceptor
integration = OpenResponsesIntegration()

# Register tools with verification
integration.register_tool(
    name="transfer_money",
    function=actual_transfer_function,
    verifier=lambda params: guard.verify_transfer(
        amount=params["amount"],
        to_account=params["to_account"]
    )
)

# In your agentic loop
async for event in client.responses.create_stream(...):
    if event.type == "tool_call":
        # QWED intercepts and verifies before execution
        result = integration.verify_and_execute(event.tool_call)
        
        if result.blocked:
            print(f"🚫 Blocked: {result.reason}")
        else:
            print(f"✅ Executed: {result.output}")
```

### Key Concept: Never Trust, Always Verify

```python
# ❌ WRONG: Direct execution
def transfer_money(amount, to_account):
    bank.transfer(amount, to_account)  # What if amount is wrong?

# ✅ RIGHT: Verified execution  
def verified_transfer(amount, to_account, expected_amount):
    # Verify the LLM-generated amount matches user intent
    if integration.verify_amount(amount, expected_amount):
        bank.transfer(amount, to_account)
    else:
        raise VerificationError("Amount mismatch detected")
```

### 🎯 Key Takeaway

> **"Intercept before you execute. Log everything."**

---

## 8.2: Commerce Safety (UCP)

### The Stakes

E-commerce errors are expensive:

| Error | Consequence |
|-------|-------------|
| Wrong cart total | Customer overcharged → Chargebacks |
| Invalid discount | Revenue loss |
| Checkout amount mismatch | Legal liability |
| Failed verification | Cart abandonment |

### Scary Story: The $12,000 Checkout Bug

```
User: "Apply my 20% discount and checkout"

Agent calculated: $1,200 (after 20% off $1,500)
Actual system: $12,000 (bug: applied 20% MARKUP instead)

Result: Customer charged 10x more!
```

### QWED Solution: UCP Integration

```python
from qwed_finance.integrations import UCPIntegration

ucp = UCPIntegration()

# Before checkout, verify everything
payment_token = {
    "cart_total": 1200.00,
    "currency": "USD",
    "discount_applied": 0.20,
    "original_total": 1500.00,
    "customer_id": "CUST-12345"
}

result = ucp.verify_payment_token(payment_token)

if result.verified:
    # Safe to proceed
    process_payment(payment_token)
    print(f"✅ Payment verified: ${result.verified_amount}")
else:
    # Block the transaction
    print(f"🚫 Verification failed: {result.errors}")
    # Errors: ["Discount calculation mismatch: expected $1200, got $12000"]
```

### UCP Capability Discovery

UCP supports **dynamic capability discovery** for agents:

```python
# Agent discovers what verifications are available
capabilities = ucp.get_capability_definition()

print(capabilities)
# {
#   "name": "payment_verification",
#   "version": "1.0",
#   "operations": [
#     "verify_cart_total",
#     "verify_discount",
#     "verify_currency",
#     "verify_aml_flag"
#   ]
# }
```

### 🎯 Key Takeaway

> **"Every checkout is a potential lawsuit. Verify before you charge."**

---

## 8.3: The Polyglot Agent (TypeScript)

### Why TypeScript?

Many production agents run on Node.js:

- Next.js API routes
- Vercel AI SDK
- Express.js backends
- Deno deployments

QWED provides a **TypeScript SDK** that wraps the Python core.

### Installation

```bash
npm install @qwed-ai/finance
```

### Basic Usage

```typescript
import { FinanceVerifier, ComplianceGuard } from '@qwed-ai/finance';

// Verify NPV calculation
const verifier = new FinanceVerifier();

const result = await verifier.verifyNPV({
  cashflows: [-1000, 300, 400, 400, 300],
  rate: 0.10,
  llmOutput: "$180.42"
});

if (result.verified) {
  console.log(`✅ Correct: ${result.computedValue}`);
} else {
  console.log(`❌ Error: Expected ${result.computedValue}, got ${result.llmValue}`);
}
```

### Compliance Verification

```typescript
import { ComplianceGuard } from '@qwed-ai/finance';

const guard = new ComplianceGuard();

// Verify AML flagging
const result = await guard.verifyAMLFlag({
  amount: 15000,
  countryCode: "US",
  llmFlagged: true
});

console.log(`Compliant: ${result.compliant}`);
// Compliant: true (correctly flagged transaction over $10k)
```

### Integration with Vercel AI SDK

```typescript
import { generateText } from 'ai';
import { ComplianceGuard } from '@qwed-ai/finance';

const guard = new ComplianceGuard();

const { text, toolCalls } = await generateText({
  model: yourModel,
  prompt: "Process this wire transfer of $50,000 to Germany",
  tools: {
    wire_transfer: {
      execute: async (params) => {
        // Verify before executing
        const verification = await guard.verifyAMLFlag({
          amount: params.amount,
          countryCode: params.country,
          llmFlagged: params.flagged
        });
        
        if (!verification.compliant) {
          throw new Error(`Blocked: ${verification.reason}`);
        }
        
        return executeTransfer(params);
      }
    }
  }
});
```

### 🎯 Key Takeaway

> **"Your agent's language doesn't matter. Verification is universal."**

---

## 🧪 Exercise: Prevent the $12K Checkout Error

Build a checkout verification system:

```python
from qwed_finance.integrations import UCPIntegration

def verify_checkout(user_intent, agent_calculation):
    """
    Exercise: Implement checkout verification
    
    Args:
        user_intent: {"original_price": 1500, "discount": "20%"}
        agent_calculation: {"final_price": 12000}  # Bug!
    
    Returns:
        VerificationResult with pass/fail and reason
    """
    ucp = UCPIntegration()
    
    # Your code here:
    # 1. Parse discount from user intent
    # 2. Calculate expected price
    # 3. Compare with agent calculation
    # 4. Return verification result
    pass
```

<details>
<summary><strong>Solution</strong></summary>

```python
def verify_checkout(user_intent, agent_calculation):
    ucp = UCPIntegration()
    
    # Parse discount
    discount_str = user_intent["discount"]
    discount_rate = float(discount_str.replace("%", "")) / 100
    
    # Calculate expected
    original = user_intent["original_price"]
    expected = original * (1 - discount_rate)
    
    # Compare
    agent_price = agent_calculation["final_price"]
    
    if abs(expected - agent_price) < 0.01:
        return {"verified": True, "amount": expected}
    else:
        return {
            "verified": False, 
            "reason": f"Expected ${expected}, got ${agent_price}",
            "blocked": True
        }

# Test
result = verify_checkout(
    {"original_price": 1500, "discount": "20%"},
    {"final_price": 12000}
)
# Output: {"verified": False, "reason": "Expected $1200.0, got $12000", "blocked": True}
```

</details>

---

## 📝 Summary

| Pattern | Use Case | Integration |
|---------|----------|-------------|
| **Interceptor** | Tool call verification | OpenResponsesIntegration |
| **UCP** | E-commerce safety | UCPIntegration |
| **TypeScript** | Node.js agents | @qwed-ai/finance |

---

## ➡️ Next: Module 9

Now that you can verify agent actions, learn how to **automate verification in CI/CD**:

**[→ Continue to Module 9: DevSecOps](../module-9-devsecops/README.md)**

---

*"Agents execute. QWED verifies. Production stays safe."*
