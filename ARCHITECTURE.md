# Architecture Diagrams

Visual guides to understanding QWED's neurosymbolic verification system.

---

## 1. The Neurosymbolic Flow

**How QWED verifies LLM outputs:**

```mermaid
graph TB
    A[User Query<br/>Natural Language] --> B[LLM<br/>Translator]
    B --> C{Can Translate<br/>to DSL?}
    C -->|Yes| D[Domain-Specific Language<br/>SymPy/Z3/AST]
    C -->|No| E[Consensus Engine<br/>Multi-Provider]
    D --> F[Symbolic Engine<br/>Executes DSL]
    E --> G[Cross-Check Results]
    F --> H{Proven<br/>Correct?}
    G --> H
    H -->|✅ Yes| I[Return Verified Result<br/>Confidence: 100%]
    H -->|❌ No| J[Return Error<br/>+ Explanation]
    
    style B fill:#ffc107
    style F fill:#4caf50
    style I fill:#4caf50
    style J fill:#f44336
```

**Key Insight:** LLM translates, symbolic engine proves. Never trust LLM to compute!

---

## 2. The 8 Verification Engines

**Domain-specific routing:**

```mermaid
graph LR
    A[User Query] --> B{Domain<br/>Detector}
    
    B -->|Math| C[Math Verifier<br/>SymPy + NumPy]
    B -->|Logic| D[Logic Verifier<br/>Z3 Solver]
    B -->|Code| E[Code Security<br/>AST + Semgrep]
    B -->|SQL| F[SQL Validator<br/>SQLGlot]
    B -->|Stats| G[Stats Engine<br/>Pandas]
    B -->|Facts| H[Fact Checker<br/>NLI Model]
    B -->|Images| I[Image Verifier<br/>OpenCV]
    B -->|Unknown| J[Consensus<br/>Multi-LLM]
    
    C --> K[✅ Verified Result]
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    
    style C fill:#2196f3
    style D fill:#9c27b0
    style E fill:#f44336
    style F fill:#ff9800
    style G fill:#4caf50
    style H fill:#00bcd4
    style I fill:#e91e63
    style J fill:#607d8b
```

---

## 3. PII Masking Flow

**HIPAA/GDPR compliance:**

```mermaid
sequenceDiagram
    participant User
    participant QWED
    participant PIIDetector
    participant LLM
    participant SymEngine
    
    User->>QWED: Query with PII<br/>Calculate for SSN: 123-45-6789
    QWED->>PIIDetector: Detect PII
    PIIDetector-->>QWED: Found: [US_SSN]
    QWED->>QWED: Mask PII<br/>Calculate for SSN: US_SSN
    QWED->>LLM: Send masked query
    LLM-->>QWED: Translation (DSL)
    QWED->>SymEngine: Execute DSL
    SymEngine-->>QWED: Verified result
    QWED-->>User: Result + PII audit info
    
    Note over PIIDetector,LLM: LLM NEVER sees real PII!
    
    rect rgb(76, 175, 80, 0.1)
        Note right of PIIDetector: ✅ Compliant with:<br/>HIPAA, GDPR, PCI-DSS
    end
```

---

## 4. LangChain Integration

**Agent + QWED flow:**

```mermaid
graph TB
    A[User: Calculate 2+2 and verify] --> B[LangChain Agent]
    B --> C{Choose Tool}
    C -->|Math Query| D[QWEDTool]
    C -->|Search| E[DuckDuckGo]
    C -->|Wikipedia| F[WikipediaTool]
    
    D --> G[QWED Verification]
    G --> H[Symbolic Proof]
    H --> I[Verified: 4]
    I --> B
    
    E --> B
    F --> B
    
    B --> J[Final Answer<br/>with Proof]
    J --> A
    
    style D fill:#ffc107
    style H fill:#4caf50
    style J fill:#2196f3
```

---

## 5. Production Deployment Architecture

**Scalable verification system:**

```mermaid
graph TB
    subgraph Client Layer
        A1[Web App]
        A2[Mobile App]
        A3[API Client]
    end
    
    subgraph Load Balancer
        B[NGINX/<br/>API Gateway]
    end
    
    subgraph Application Layer
        C1[FastAPI<br/>Instance 1]
        C2[FastAPI<br/>Instance 2]
        C3[FastAPI<br/>Instance N]
    end
    
    subgraph QWED Layer
        D1[QWED Client<br/>+ Cache]
        D2[QWED Client<br/>+ Cache]
        D3[QWED Client<br/>+ Cache]
    end
    
    subgraph External Services
        E1[OpenAI API]
        E2[Anthropic API]
        E3[Ollama Local]
    end
    
    subgraph Data Layer
        F1[Redis Cache]
        F2[PostgreSQL<br/>Audit Logs]
        F3[Prometheus<br/>Metrics]
    end
    
    A1 --> B
    A2 --> B
    A3 --> B
    
    B --> C1
    B --> C2
    B --> C3
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    
    D1 --> E1
    D1 --> E2
    D1 --> E3
    D2 --> E1
    D2 --> E2
    D2 --> E3
    D3 --> E1
    D3 --> E2
    D3 --> E3
    
    D1 --> F1
    D2 --> F1
    D3 --> F1
    
    C1 --> F2
    C2 --> F2
    C3 --> F2
    
    C1 --> F3
    C2 --> F3
    C3 --> F3
    
    style D1 fill:#4caf50
    style D2 fill:#4caf50
    style D3 fill:#4caf50
    style F1 fill:#2196f3
```

---

## 6. Error Handling Flow

**Graceful degradation:**

```mermaid
graph TD
    A[Calculate Query] --> B[Try Primary Provider<br/>OpenAI]
    B --> C{Success?}
    C -->|✅| D[Return Verified Result]
    C -->|❌| E[Try Fallback<br/>Anthropic]
    E --> F{Success?}
    F -->|✅| D
    F -->|❌| G[Try Local<br/>Ollama]
    G --> H{Success?}
    H -->|✅| D
    H -->|❌| I[Use Conservative<br/>Fallback Value]
    I --> J[Log Warning<br/>+ Alert Ops]
    J --> K[Return Unverified<br/>Confidence: 0%]
    
    style D fill:#4caf50
    style I fill:#ff9800
    style K fill:#f44336
```

---

## Legend

- **Yellow/Orange** 🟨 = LLM components (probabilistic)
- **Green** 🟩 = Symbolic engines (deterministic)
- **Blue** 🟦 = Infrastructure/Data
- **Red** 🟥 = Errors/Failures
- **Purple** 🟪 = Logic/Constraints

---

## Usage in Course

These diagrams appear in:
- Module 2: Neurosymbolic Theory
- Module 3: Production Patterns
- Module 4: Advanced Architectures

**Mermaid rendering:** GitHub automatically renders these diagrams!
