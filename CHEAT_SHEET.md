# QWED Quick Reference Cheat Sheet

**Master AI Verification in 5 Minutes** 📚

---

## 🚀 Quick Start

### Installation

```bash
# Basic
pip install qwed

# With PII masking
pip install 'qwed[pii]'

# With LangChain
pip install 'qwed[langchain]'

# Everything
pip install 'qwed[all]'
```

### Free Setup (Ollama)

```bash
# Install Ollama from: https://ollama.ai
ollama pull llama3
ollama serve
```

---

## 💻 Basic Usage

### Initialize Client

```python
from qwed_sdk import QWEDLocal

# Ollama (free)
client = QWEDLocal(
    base_url="http://localhost:11434/v1",
    model="llama3"
)

# OpenAI
client = QWEDLocal(
    provider="openai",
    model="gpt-4o-mini"
)
```

### Verify Math

```python
result = client.verify_math("What is 2+2?")

print(result.verified)    # True/False
print(result.value)       # The answer
print(result.confidence)  # 0-100%
```

---

## 🎯 When to Use Each Engine

| Task | Engine | Method Call |
|------|--------|-------------|
| Calculus, algebra, finance | Math | `verify_math()` |
| If-then, logic proofs | Logic | `verify_logic()` |
| SQL syntax, injection | SQL | `verify_sql()` |
| eval(), exec(), security | Code | `verify_code()` |
| General verification | Auto | `verify()` |

---

## 🛡️ Production Patterns

### Pattern 1: Verify Before Return

```python
def calculate(query: str):
    result = client.verify_math(query)
    if result.verified:
        return result.value
    else:
        raise ValueError(f"Failed: {result.error}")
```

### Pattern 2: Fallback

```python
def safe_calculate(query: str):
    try:
        result = client.verify_math(query)
        return result.value if result.verified else safe_default
    except:
        return safe_default
```

### Pattern 3: Retry

```python
providers = ["openai", "anthropic", "gemini"]
for provider in providers:
    try:
        client = QWEDLocal(provider=provider)
        result = client.verify_math(query)
        if result.verified:
            return result
    except:
        continue
```

---

## 🔒 PII Masking (HIPAA/GDPR)

```python
client = QWEDLocal(
    provider="openai",
    mask_pii=True,
    pii_entities=[
        "PERSON",
        "EMAIL_ADDRESS",
        "US_SSN",
        "CREDIT_CARD"
    ]
)

# PII is automatically masked before LLM sees it!
```

---

## 🦜 LangChain Integration

```python
from qwed_sdk.integrations.langchain import QWEDTool
from langchain.agents import initialize_agent
from langchain_openai import ChatOpenAI

qwed_tool = QWEDTool(provider="openai")
llm = ChatOpenAI(temperature=0)

agent = initialize_agent(
    tools=[qwed_tool],
    llm=llm
)

response = agent.run("Verify that 2+2=4")
```

---

## ⚙️ Configuration Options

### Enable Caching (50-80% cost savings)

```python
client = QWEDLocal(
    provider="openai",
    use_cache=True  # Default: True
)
```

### Custom LLM Providers

```python
# OpenAI
QWEDLocal(provider="openai", model="gpt-4o-mini")

# Anthropic
QWEDLocal(provider="anthropic", model="claude-3-haiku-20240307")

# Google
QWEDLocal(provider="gemini", model="gemini-pro")

# Local (Ollama)
QWEDLocal(base_url="http://localhost:11434/v1", model="llama3")
```

---

## 📊 Understanding Results

### VerificationResult Object

```python
result.verified      # bool: True if proven
result.value         # any: The verified answer
result.confidence    # float: 0-100% (100% for symbolic)
result.error         # str | None: Error message
result.evidence      # dict: How it was verified
```

### Evidence Fields

```python
result.evidence['method']          # 'symbolic', 'consensus', etc.
result.evidence['symbolic_result'] # Raw SymPy result
result.evidence['pii_masked']      # PII detection info
```

---

## 🐛 Debugging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

client = QWEDLocal(provider="openai")
# Now you'll see verbose logs
```

### Check Cache Stats

```python
# After multiple calls:
print(f"Cache hits: {client.cache_stats['hits']}")
print(f"Cache misses: {client.cache_stats['misses']}")
```

---

## 🔥 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `API key not found` | Missing env var | Set `OPENAI_API_KEY` |
| `Connection refused` | Ollama not running | Run `ollama serve` |
| `Verification failed` | Query too vague | Be more specific |
| `Import error` | Missing extras | `pip install 'qwed[all]'` |

---

## 📚 Full Documentation

- **Course:** https://github.com/QWED-AI/qwed-learning
- **Main Repo:** https://github.com/QWED-AI/qwed-verification
- **Docs:** https://github.com/QWED-AI/qwed-verification/tree/main/docs

---

## 💡 Key Principles

1. **Never trust LLMs to compute** - Only to translate
2. **Always verify critical tasks** - Finance, healthcare, legal
3. **Use caching** - Save 50-80% on API costs
4. **Mask PII** - Comply with regulations
5. **Handle failures** - Retry, fallback, or escalate

---

<div align="center">

**🌟 Star the Course:** https://github.com/QWED-AI/qwed-learning

*"Safe AI is the only AI that scales."*

</div>
