# Module 6: Domain-Specific Verification

> **"In God we trust. All others must bring data—verified data."** — W. Edwards Deming (adapted)

⏱️ **Duration:** 60 minutes  
📊 **Level:** Advanced  
🎯 **Goal:** Apply QWED verification to real industry use cases.

---

## 🧠 What You'll Learn

After this module, you'll understand:

- ✅ How to verify financial calculations (NPV, IRR, compound interest)
- ✅ HIPAA/GDPR compliant verification with PII masking
- ✅ Legal contract and clause verification
- ✅ Secure code review automation
- ✅ Statistical claim verification

---

## 📚 Table of Contents

| Section | Industry | Time |
|---------|----------|------|
| 6.1 | [Financial Services](#61-financial-services) | 15 min |
| 6.2 | [Healthcare (HIPAA)](#62-healthcare-hipaa) | 12 min |
| 6.3 | [Legal & Contracts](#63-legal--contracts) | 10 min |
| 6.4 | [Code & Security](#64-code--security) | 13 min |
| 6.5 | [Data & Analytics](#65-data--analytics) | 10 min |

---

## 6.1: Financial Services

### The Stakes

Financial errors aren't just embarrassing—they're **expensive** and **illegal**.

| Type | Consequence |
|------|-------------|
| Wrong interest calculation | Customer lawsuits |
| Incorrect tax computation | IRS penalties |
| Bad investment projections | SEC violations |
| Currency conversion errors | Trading losses |

### Scary Story: The $12,889 Bug

```
User: "Calculate compound interest on $100K at 5% for 10 years"

GPT-4 Response: "The compound interest would be $50,000, 
                giving you a total of $150,000."

Actual: $162,889.46 (compound) vs $150,000 (simple)
Error: $12,889.46 (8.6% off)
```

The LLM used **simple interest** instead of **compound interest**!

### QWED Solution

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="openai")

# Verify compound interest calculation
result = client.verify_math("""
Principal: $100,000
Rate: 5% annual
Time: 10 years
Compounding: Annual
Final Amount = Principal * (1 + rate)^time
""")

print(f"Verified: {result.verified}")
print(f"Computed: ${result.computed_value:,.2f}")
# Output: Verified: True, Computed: $162,889.46
```

### Financial Verification Patterns

#### Pattern 1: NPV/IRR Verification

```python
# Verify Net Present Value calculation
cash_flows = [-100000, 30000, 35000, 40000, 45000]
discount_rate = 0.10

result = client.verify_math(f"""
NPV of cash flows {cash_flows} at {discount_rate*100}% discount rate
""")

# QWED uses SymPy to compute exact NPV
# NPV = Σ(CF_t / (1+r)^t)
```

#### Pattern 2: Loan Amortization

```python
# Verify monthly payment calculation
result = client.verify_math("""
Loan: $500,000
Interest: 6.5% annual
Term: 30 years
Monthly Payment = ?
""")

# QWED computes: M = P * [r(1+r)^n] / [(1+r)^n - 1]
# Verified: $3,160.34/month
```

#### Pattern 3: Currency Conversion Chain

```python
# Verify multi-hop conversion
result = client.verify_math("""
Convert $1000 USD → EUR → GBP → USD
Rates: USD/EUR = 0.92, EUR/GBP = 0.86, GBP/USD = 1.27
Expected final USD amount
""")

# Catches arbitrage calculation errors
```

### 🎯 Key Takeaway

> **"Never trust an LLM with money. Verify every calculation."**

---

## 6.2: Healthcare (HIPAA)

### The Stakes

Healthcare AI errors can:
- Kill patients (wrong dosages)
- Violate HIPAA ($1.5M+ fines)
- Expose PHI (lawsuits, reputation)

### The Challenge: PII in Medical Queries

```
Patient Query: "John Smith (DOB: 03/15/1985, SSN: 123-45-6789) 
               weighs 180 lbs. Calculate his BMI."

Problem: We need to verify the calculation WITHOUT exposing PHI!
```

### QWED Solution: PII Masking

```python
from qwed_sdk import QWEDLocal

# Enable automatic PII masking
client = QWEDLocal(
    provider="ollama",  # Keep data local!
    mask_pii=True       # Auto-mask before LLM sees query
)

query = """
Patient: John Smith (DOB: 03/15/1985)
Height: 5'10" (70 inches)
Weight: 180 lbs
Calculate BMI
"""

result = client.verify_math(query)

# What the LLM sees (masked):
# "Patient: [PERSON_1] (DOB: [DATE_1])
#  Height: 5'10" (70 inches)
#  Weight: 180 lbs
#  Calculate BMI"

# What QWED verifies (math only):
# BMI = (weight_lbs * 703) / height_inches²
# BMI = (180 * 703) / 70² = 25.8

print(f"BMI: {result.computed_value}")  # 25.8
print(f"Verified: {result.verified}")   # True
# Patient name NEVER reached the LLM!
```

### Healthcare Verification Patterns

#### Pattern 1: Dosage Calculation

```python
# Pediatric dosage based on weight
result = client.verify_math("""
Medication: Amoxicillin
Child weight: 25 kg
Recommended dose: 25-50 mg/kg/day in divided doses
Prescribed: 500mg twice daily

Is this dosage correct?
""")

# QWED verifies:
# Min: 25 * 25 = 625 mg/day
# Max: 25 * 50 = 1250 mg/day
# Prescribed: 1000 mg/day ✅ (within range)
```

#### Pattern 2: Drug Interaction Check

```python
# Verify drug interaction claims
result = client.verify_fact(
    claim="Warfarin and Aspirin have no significant interaction",
    sources=["drug_interactions.json"]  # Your verified database
)

# QWED fact-checks against your sources
# Returns: verified=False, reason="Major interaction documented"
```

#### Pattern 3: Lab Value Interpretation

```python
# Verify lab result interpretation
result = client.verify_math("""
Patient glucose: 126 mg/dL (fasting)
Normal range: 70-100 mg/dL
Prediabetes: 100-125 mg/dL
Diabetes: ≥126 mg/dL

Classification: ?
""")

# QWED verifies: 126 >= 126 → Diabetes range ✅
```

### HIPAA Compliance Checklist

| Requirement | QWED Feature |
|-------------|--------------|
| Minimize data exposure | PII masking |
| Local processing option | QWEDLocal + Ollama |
| Audit trail | Verification logs |
| Data encryption | HTTPS + local storage |

### 🎯 Key Takeaway

> **"Healthcare AI needs two things: accuracy AND privacy. QWED provides both."**

---

## 6.3: Legal & Contracts

### The Stakes

Legal AI errors can:
- Invalid contracts
- Missed deadlines → defaults
- Wrong liability exposure
- Compliance violations

### Scary Story: AI Lawyer Disaster

In 2023, lawyers used ChatGPT for legal research. It cited **fake cases** that didn't exist. The lawyers were sanctioned by the court.

### QWED Solution: Contract Verification

#### Pattern 1: Date/Deadline Verification

```python
from qwed_sdk import QWEDLocal
from datetime import datetime

client = QWEDLocal(provider="openai")

contract_text = """
Agreement signed: January 15, 2024
Payment due: 30 days from signing
Late penalty applies after: February 14, 2024
"""

result = client.verify_logic(f"""
Given:
- Signed: 2024-01-15
- Due: 30 days later
- Penalty date: 2024-02-14

Verify: Is the penalty date correct?
(Account for 2024 being a leap year)
""")

# QWED calculates:
# Jan 15 + 30 days = Feb 14 ✅
# (Leap year: Jan has 31 days, so Jan 15 + 16 = Jan 31, then +14 = Feb 14)
```

#### Pattern 2: Logical Consistency

```python
# Check for contradictory clauses
result = client.verify_logic("""
Clause 5.1: "Seller may terminate with 30 days notice"
Clause 5.2: "Neither party may terminate before 90 days"
Clause 7.3: "Seller may terminate immediately upon breach"

Are these clauses logically consistent?
""")

# QWED uses Z3 to find contradictions
# Returns: "Clauses 5.1 and 5.2 may conflict if termination 
#          is attempted between days 30-90"
```

#### Pattern 3: Liability Cap Verification

```python
# Verify liability calculations
result = client.verify_math("""
Total contract value: $5,000,000
Liability cap: 200% of contract value
Maximum liability exposure: $10,000,000

Is this correct?
""")

# QWED: 5,000,000 * 2 = 10,000,000 ✅
```

### 🎯 Key Takeaway

> **"Contracts require precision. LLMs provide probability. QWED bridges the gap."**

---

## 6.4: Code & Security

### The Stakes

Code from LLMs can:
- Contain vulnerabilities
- Import malicious packages
- Expose secrets
- Enable injection attacks

### Scary Story: Package Hallucination

Researchers found that **22% of LLM-suggested packages don't exist**.

Attackers can:
1. Note non-existent package names
2. Register them on PyPI/npm
3. Add malware
4. Wait for developers to `pip install`

### QWED Solution: Code Security Engine

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="openai")

suspicious_code = """
import pickle
import os

def load_config(data):
    return pickle.loads(data)  # Unsafe deserialization!

def run_command(user_input):
    os.system(f"echo {user_input}")  # Command injection!
"""

result = client.verify_code(suspicious_code, language="python")

print(result.issues)
# [
#   {"severity": "HIGH", "type": "unsafe_deserialization", 
#    "line": 5, "message": "pickle.loads on untrusted data"},
#   {"severity": "CRITICAL", "type": "command_injection",
#    "line": 8, "message": "os.system with user input"}
# ]
```

### Code Verification Patterns

#### Pattern 1: SQL Injection Detection

```python
# Check SQL query safety
sql_query = """
SELECT * FROM users 
WHERE username = '{user_input}' 
AND password = '{password}'
"""

result = client.verify_sql(sql_query)

# QWED detects:
# - String interpolation (injection risk)
# - No parameterized queries
# - Plain text password comparison
```

#### Pattern 2: Secret Detection

```python
# Scan for exposed secrets
code = """
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgres://user:password123@host/db"
"""

result = client.verify_code(code, check_secrets=True)

# Detected:
# - AWS Access Key (line 1)
# - OpenAI API Key pattern (line 2)
# - Database credentials (line 3)
```

#### Pattern 3: Dependency Verification

```python
# Verify imported packages exist
imports = ["requests", "aiohttp_security", "flask_login"]

for pkg in imports:
    result = client.verify_fact(
        f"Python package '{pkg}' exists on PyPI",
        sources=["pypi_packages.json"]
    )
    if not result.verified:
        print(f"⚠️ WARNING: {pkg} may not exist!")

# Output: ⚠️ WARNING: aiohttp_security may not exist!
```

### 🎯 Key Takeaway

> **"Never deploy LLM-generated code without security verification."**

---

## 6.5: Data & Analytics

### The Stakes

Analytics errors can:
- Wrong business decisions
- Misleading reports
- False insights
- Compliance issues (SOX, etc.)

### QWED Solution: Statistical Verification

#### Pattern 1: Statistical Claim Verification

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="openai")

# Verify statistical claims
data = [23, 45, 67, 89, 12, 34, 56, 78, 90, 21]

result = client.verify_stats(f"""
Dataset: {data}
Claim: "The mean is 51.5 and standard deviation is 27.3"
""")

# QWED computes:
# Mean = sum(data)/len(data) = 515/10 = 51.5 ✅
# Std = sqrt(sum((x-mean)²)/n) = 27.28... ≈ 27.3 ✅
```

#### Pattern 2: SQL Query Verification

```python
# Verify SQL before execution
query = """
SELECT department, AVG(salary) as avg_salary
FROM employees
WHERE hire_date > '2020-01-01'
GROUP BY department
HAVING COUNT(*) > 5
ORDER BY avg_salary DESC
LIMIT 10
"""

result = client.verify_sql(query)

# QWED checks:
# ✅ Valid SQL syntax
# ✅ Aggregation with GROUP BY (correct)
# ✅ HAVING uses aggregate function (correct)
# ✅ No injection vulnerabilities
# ✅ Reasonable complexity (not a table scan bomb)
```

#### Pattern 3: Report Claim Verification

```python
# Verify claims in generated reports
report_claim = """
Q4 2024 Performance:
- Revenue: $12.5M (up 23% YoY)
- Q4 2023 Revenue was $10.2M
"""

result = client.verify_math("""
If Q4 2024 = $12.5M and YoY growth = 23%,
what was Q4 2023?

Calculation: Q4_2023 = Q4_2024 / 1.23
""")

# QWED: 12.5 / 1.23 = 10.16... ≈ $10.2M ✅
```

### 🎯 Key Takeaway

> **"Data drives decisions. Verified data drives good decisions."**

---

## 🧪 Exercise: Build a Domain Verifier

Choose an industry and build a verification workflow:

### Option A: Finance
```python
# Build a loan calculator verifier
def verify_loan_calculation(principal, rate, term, monthly_payment):
    # Your code here
    pass
```

### Option B: Healthcare
```python
# Build a dosage verifier with PII masking
def verify_dosage(patient_info, medication, dose):
    # Your code here
    pass
```

### Option C: Legal
```python
# Build a contract deadline verifier
def verify_deadlines(contract_text):
    # Your code here
    pass
```

---

## 📝 Summary

| Domain | Key Verification | QWED Engine |
|--------|------------------|-------------|
| **Finance** | Calculations, interest | Math Engine |
| **Healthcare** | Dosages, PII masking | Math + Masking |
| **Legal** | Logic, dates | Logic + Math |
| **Code** | Security, secrets | Code Engine |
| **Data** | Statistics, SQL | Stats + SQL |

---

## ➡️ Next Steps

Congratulations! You've completed the core QWED Learning Curriculum.

**What's Next?**
- ⭐ [Star the QWED repo](https://github.com/QWED-AI/qwed-verification)
- 📖 [Read the docs](https://docs.qwedai.com)
- 💬 [Join discussions](https://github.com/QWED-AI/qwed-verification/discussions)
- 🐦 [Follow updates](https://twitter.com/rahuldass29)

---

*"If it can't be verified, it doesn't ship."*
