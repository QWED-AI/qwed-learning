# Module 14: Infrastructure Verification

> **"Don't let an LLM write your IAM policies. Let QWED verify them."**

⏱️ **Duration:** 75 minutes
📊 **Level:** Expert
🎯 **Goal:** Apply deterministic verification to Infrastructure as Code (IaC) — verify Terraform, IAM policies, network topologies, cost estimates, and release artifacts using `qwed-infra`.

---

## 🧠 What You'll Learn

After this module, you'll understand:

- ✅ **The Infrastructure Trust Problem** — Why AI-generated IaC needs deterministic gates
- ✅ **The Four Guards** — IamGuard, NetworkGuard, CostGuard, ArtifactBoundaryGuard
- ✅ **IamGuard** — Z3-based IAM policy verification with symbolic Allow/Deny precedence
- ✅ **NetworkGuard** — NetworkX-based VPC reachability analysis, fail-closed on unsupported topologies
- ✅ **CostGuard** — Decimal-arithmetic cost estimation, fail-closed on unknown types
- ✅ **ArtifactBoundaryGuard** — Package scanning, secret detection, build config validation
- ✅ **InfraDiagnosticResult** — The 3-layer diagnostic model with mandatory `proof_ref` on `VERIFIED`
- ✅ **CI/CD Integration** — Gating AI-generated IaC PRs before merge

---

## 📚 Table of Contents

| Lesson | Topic | Time |
|--------|-------|------|
| 14.1 | [The Infrastructure Trust Problem](#141-the-infrastructure-trust-problem) | 10 min |
| 14.2 | [The Four Guards](#142-the-four-guards) | 10 min |
| 14.3 | [IamGuard in Depth](#143-iamguard-in-depth) | 10 min |
| 14.4 | [NetworkGuard in Depth](#144-networkguard-in-depth) | 10 min |
| 14.5 | [CostGuard in Depth](#145-costguard-in-depth) | 10 min |
| 14.6 | [ArtifactBoundaryGuard in Depth](#146-artifactboundaryguard-in-depth) | 10 min |
| 14.7 | [InfraDiagnosticResult](#147-infradiagnosticresult) | 5 min |
| 14.8 | [CI/CD Integration](#148-cicd-integration) | 5 min |
| 14.9 | [Lab: Verify a Terraform PR](#149-lab-verify-a-terraform-pr) | 15 min |

---

## 14.1: The Infrastructure Trust Problem

### What Goes Wrong

AI agents (Devin, Copilot Workspace, Cursor) write Terraform and Kubernetes configs. But AI doesn't understand consequences:

| Case | What AI Wrote | Real World Impact |
|------|---------------|-------------------|
| **IAM Permission** | `Action: "s3:*", Resource: "*"` | Data breach — entire bucket exposed |
| **Network Rule** | `Ingress: 0.0.0.0/0, Port: 22` | Ransomware — SSH open to the internet |
| **Instance Type** | `instance_type = "p4d.24xlarge"` | Bankrupt — $23,000/month for a dev env |

These aren't syntax errors. A linter won't catch them. They are **logic errors** — and they require deterministic verification.

### Why Existing Tools Fall Short

| Tool | Approach | Blind Spot |
|------|----------|------------|
| **TFLint** | Regex pattern matching | Can't prove IAM Allow/Deny precedence |
| **Checkov** | Static policy checks | Can't trace network paths |
| **tfsec** | YAML-based rules | Can't estimate costs before deploy |
| **QWED-Infra** | Z3 + NetworkX + Decimal | **Proof**, not patterns |

### The QWED Philosophy Applied to Infrastructure

> **"A linter checks syntax. QWED checks logic."**

QWED-Infra mirrors the same deterministic fail-closed philosophy from the core curriculum:
- **P1 (Deterministic over Probabilistic)** — Z3 proves IAM access; no LLM involved
- **P3 (Proof before Trust)** — Every `VERIFIED` result carries a `proof_ref`
- **P4 (Fail Closed)** — Unknown instance types block deployment
- **P5 (Explicit Boundaries)** — ArtifactBoundaryGuard defines exactly what can ship
- **P8 (Verification before Execution)** — All guards run before `terraform apply`

---

## 14.2: The Four Guards

```python
pip install qwed-infra
```

QWED-Infra provides four deterministic guards, each covering a different IaC trust boundary:

| Guard | What It Verifies | Technology | Fail-Closed Trigger |
|-------|-----------------|------------|---------------------|
| **IamGuard** | IAM policy access (Allow vs Deny) | Z3 SMT solver | Parse error, unknown condition operator |
| **NetworkGuard** | VPC subnet reachability | NetworkX graph analysis | NAT, NACL, peering, transit gateway |
| **CostGuard** | Monthly cost estimate vs budget | Decimal arithmetic | Unknown instance/volume type |
| **ArtifactBoundaryGuard** | Release package integrity | File scanning + build config | Secret leak, debug file, missing control |

### Common Pattern

Every guard follows the same flow:

```python
from qwed_infra import IamGuard, NetworkGuard, CostGuard, ArtifactBoundaryGuard

guard = IamGuard()
result = guard.verify_access(policy, action="s3:GetObject", resource="arn:aws:s3:::my-bucket/*")
diagnostic = IamGuard.to_diagnostic(result)

print(diagnostic.status)       # InfraDiagnosticStatus.VERIFIED
print(diagnostic.is_verified)  # True
print(diagnostic.is_authoritative)  # True (proof_ref is present)
```

The `to_diagnostic()` converter produces an `InfraDiagnosticResult` — the same 3-layer model you learned in Module 0, now applied to infrastructure.

### Version Compatibility

These examples use `qwed-infra>=0.2.0`:

```
pip install "qwed-infra>=0.2.0"
```

---

## 14.3: IamGuard in Depth

### How It Works

IamGuard uses **Z3 SMT solving** to prove whether an IAM policy allows or denies a specific action on a specific resource. It handles condition operators (`StringEquals`, `StringLike`, `IpAddress`, `DateLessThan`) and enforces explicit Deny precedence.

```python
from qwed_infra import IamGuard

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "IpAddress": {"aws:SourceIp": "10.0.0.0/8"}
            }
        }
    ]
}

guard = IamGuard()

# Verify access from within the trusted IP range
result = guard.verify_access(
    policy,
    action="s3:GetObject",
    resource="arn:aws:s3:::my-bucket/secrets.json",
    context={"aws:SourceIp": "10.0.0.5"}
)
print(result.allowed)   # True
print(result.verified)  # True
print(result.proof)     # Z3 proof string

# Verify access from outside the trusted range
result_outside = guard.verify_access(
    policy,
    action="s3:GetObject",
    resource="arn:aws:s3:::my-bucket/secrets.json",
    context={"aws:SourceIp": "203.0.113.5"}
)
print(result_outside.allowed)  # False — IP condition blocks it
```

### Least Privilege Check

The `verify_least_privilege` method treats `Action: "*"` and `Resource: "*"` as a violation:

```python
result = guard.verify_least_privilege(policy)
if result.allowed:
    print("Policy is over-privileged — grants wildcard access")
```

### Converting to Diagnostic

```python
diagnostic = IamGuard.to_diagnostic(result, audit_trace={"rule": "iam_s3_access"})
print(diagnostic.status)          # InfraDiagnosticStatus.VERIFIED
print(diagnostic.proof_ref)       # "sha256:..."
print(diagnostic.agent_message)   # "IAM policy access: allowed"
```

### Fail-Closed Behavior

If the policy contains an unknown condition operator, IamGuard denies access (fail-closed):

```python
# Unknown operator → denied
result = guard.verify_access(bad_policy, ...)
print(result.allowed)  # False — fail-closed
```

---

## 14.4: NetworkGuard in Depth

### How It Works

NetworkGuard builds a **NetworkX directed graph** from your VPC resources and traces reachability from the internet to a destination subnet. It checks both routing table entries and security group ingress rules.

```python
from qwed_infra import NetworkGuard

resources = {
    "subnets": [
        {"id": "subnet-public", "security_groups": ["sg-web"]},
        {"id": "subnet-private", "security_groups": ["sg-app"]},
    ],
    "route_tables": [
        {
            "id": "rtb-public",
            "routes": [
                {"destination": "0.0.0.0/0", "target": "igw-12345"}
            ],
            "subnet_associations": ["subnet-public"]
        }
    ],
    "security_groups": {
        "sg-web": {
            "ingress": [
                {"port": 443, "cidr": "0.0.0.0/0"},
                {"port": 22, "cidr": "10.0.0.0/8"}
            ]
        }
    }
}

guard = NetworkGuard()
guard.build_graph(resources)

# Verify HTTPS reachability to the public subnet
result = guard.verify_reachability(
    resources,
    source="internet",
    destination="subnet-public",
    port=443
)
print(result.reachable)  # True — HTTPS is open to the internet
print(result.path)       # ["internet", "subnet-public"]
print(result.reason)     # "Reachable: route found + security group allows ingress"
```

### What Gets Blocked

NetworkGuard fails closed on topologies it cannot model:

| Topology | Behavior |
|----------|----------|
| VPC Peering | `unsupported_topology = True` |
| NAT Gateway | `unsupported_topology = True` |
| NACL rules | `unsupported_topology = True` |
| Transit Gateway | `unsupported_topology = True` |
| Internal source routing | `unsupported_topology = True` |

```python
# Unsupported topology → BLOCKED
result = guard.verify_reachability(
    resources_with_nat,
    source="internet",
    destination="subnet-private",
    port=3306
)
print(result.unsupported_topology)  # True
diagnostic = NetworkGuard.to_diagnostic(result)
print(diagnostic.status)            # InfraDiagnosticStatus.UNVERIFIABLE
```

### Security Group Enforcement

Even if routing exists, a security group blocking the port causes denial:

```python
result = guard.verify_reachability(
    resources,
    source="internet",
    destination="subnet-public",
    port=22  # Only 443 and 10.0.0.0/8:22 are allowed
)
print(result.reachable)      # False
print(result.failure_code)   # "sg_ingress_blocked"
```

---

## 14.5: CostGuard in Depth

### How It Works

CostGuard uses **Decimal arithmetic** (not float) to estimate monthly costs from a pricing catalog. It fails closed on unknown instance or volume types.

```python
from qwed_infra import CostGuard

resources = {
    "instances": [
        {"id": "web-server", "instance_type": "t3.micro", "count": 3},
        {"id": "db-server", "instance_type": "db.m5.large", "count": 1},
    ],
    "volumes": [
        {"id": "web-data", "volume_type": "gp3", "size_gb": 100},
    ]
}

guard = CostGuard()
result = guard.verify_budget(resources, budget_monthly="500")

print(result.total_monthly_cost)  # e.g. "47.52"
print(result.within_budget)       # True
print(result.breakdown)           # {"web-server": "21.90", "db-server": "21.90", "web-data": "3.72"}
print(result.reason)              # "Total $47.52 within budget of $500.00"
```

### Unknown Types → Blocked

If a resource uses an instance type not in the pricing catalog, CostGuard sets `has_unknown_types = True` and `to_diagnostic` returns `BLOCKED`:

```python
resources_with_unknown = {
    "instances": [
        {"id": "gpu-node", "instance_type": "p4d.24xlarge"},  # Known
        {"id": "mystery-box", "instance_type": "x99.mega"},    # Unknown
    ]
}

result = guard.verify_budget(resources_with_unknown, budget_monthly="10000")
print(result.has_unknown_types)   # True
print(result.within_budget)       # False — fail-closed

diagnostic = CostGuard.to_diagnostic(result)
print(diagnostic.status)          # InfraDiagnosticStatus.BLOCKED
print(diagnostic.agent_message)   # "Cost estimate incomplete -- unknown resource types"
```

### Budget Exceeded

```python
result = guard.verify_budget(expensive_resources, budget_monthly="100")
print(result.within_budget)  # False
diagnostic = CostGuard.to_diagnostic(result)
print(diagnostic.status)     # InfraDiagnosticStatus.BLOCKED
```

---

## 14.6: ArtifactBoundaryGuard in Depth

### How It Works

ArtifactBoundaryGuard scans a release package directory for secrets, debug files, build misconfigurations, and forbidden paths. It is the **final release gate** — "safe to ship."

```python
from qwed_infra import ArtifactBoundaryGuard

guard = ArtifactBoundaryGuard()

# Scan the package directory before publishing
result = guard.verify_package_boundary(
    package_dir="./dist/my-package",
    pyproject_path="./pyproject.toml",
    package_name="my-package"
)

if result.is_safe:
    print("Package boundary verified — safe to publish")
else:
    for finding in result.findings:
        print(f"[{finding.severity}] {finding.finding_type}: {finding.file_path} — {finding.reason}")
```

### What It Catches

| Finding Type | Severity | Example |
|-------------|----------|---------|
| `secret_leak` | BLOCK | `.env` file, `*.pem` key, `*credential*` file |
| `disclosure_risk` | BLOCK | `.gitignore`, `.dockerignore` in package |
| `debug_inclusion` | BLOCK | `__pycache__/`, `tests/`, `*.ipynb` in package |
| `missing_control` | BLOCK | No `pyproject.toml`, wheel config doesn't include package |
| `unknown_boundary` | BLOCK | Unparseable `pyproject.toml` |

### Converting to Diagnostic

```python
diagnostic = ArtifactBoundaryGuard.to_diagnostic(result)
if diagnostic.is_verified:
    print("✅", diagnostic.agent_message)  # "Package boundary verified -- safe to publish"
else:
    print("🚫", diagnostic.agent_message)  # "Package boundary violation -- do not publish"
    print(diagnostic.developer_fields.get("findings", []))
```

---

## 14.7: InfraDiagnosticResult

### The 3-Layer Model

`InfraDiagnosticResult` follows the same 3-layer pattern as `DiagnosticResult` from the core curriculum, with infrastructure-specific `developer_fields`:

```
┌──────────────────────────────────────────────┐
│  Layer 1: agent_message (str)                │
│  "IAM policy access: allowed"                │
├──────────────────────────────────────────────┤
│  Layer 2: developer_fields (Dict[str, Any])  │
│  constraint_id, audit_trace, findings,       │
│  advisory_checks                             │
├──────────────────────────────────────────────┤
│  Layer 3: proof_ref (Optional[str])          │
│  "sha256:..." — PRESENT ↔ VERIFIED           │
└──────────────────────────────────────────────┘
```

### Key Difference from Core DiagnosticResult

| Feature | Core `DiagnosticResult` | `InfraDiagnosticResult` |
|---------|------------------------|------------------------|
| Package | `qwed_new.core` | `qwed_infra` |
| Status enum | `DiagnosticStatus` | `InfraDiagnosticStatus` |
| Proof enforcement | `proof_ref` on `VERIFIED` | Same + `audit_trace` required in `developer_fields` |
| Factory methods | — | `.verified()`, `.unverifiable()`, `.blocked()` |

### Factory Methods

```python
from qwed_infra.diagnostics import InfraDiagnosticResult, InfraDiagnosticStatus

# VERIFIED — requires evidence for proof_ref computation
verified = InfraDiagnosticResult.verified(
    agent_message="Network reachability verified",
    developer_fields={"constraint_id": "network_guard.verify_reachability", "audit_trace": {...}},
    evidence={"reachable": True, "path": ["internet", "subnet-public"]}
)
print(verified.proof_ref)  # "sha256:<64-char-hex>"
print(verified.is_authoritative)  # True

# BLOCKED — no proof_ref
blocked = InfraDiagnosticResult.blocked(
    agent_message="Cost estimate exceeds budget",
    developer_fields={"constraint_id": "cost_guard.verify_budget"}
)
print(blocked.proof_ref)  # None
print(blocked.is_authoritative)  # False

# UNVERIFIABLE — topology can't be modeled
unverifiable = InfraDiagnosticResult.unverifiable(
    agent_message="Network reachability cannot be verified — unsupported topology",
    developer_fields={"constraint_id": "network_guard.verify_reachability"}
)
```

### Authority Contract

The same rule applies everywhere:

```python
if diagnostic.proof_ref is not None:
    proceed()      # Authoritative — may admit for control flow
else:
    block()        # Non-authoritative — must not drive control flow
```

---

## 14.8: CI/CD Integration

### The IaC Verification Pipeline

QWED-Infra integrates into CI/CD as a deterministic gate between `terraform plan` and `terraform apply`:

```yaml
# .github/workflows/iac-verification.yml
name: IaC Verification Gate

on: [pull_request]

jobs:
  verify-iac:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install qwed-infra
        run: pip install qwed-infra>=0.2.0

      - name: Verify IAM policies
        run: python ci/verify_iam.py

      - name: Verify network topology
        run: python ci/verify_network.py

      - name: Verify cost estimates
        run: python ci/verify_costs.py

      - name: Verify artifact boundary
        run: python ci/verify_artifact_boundary.py
```

### Example: IAM Verification Script

```python
# ci/verify_iam.py
import json, sys
from qwed_infra import IamGuard
from qwed_infra.diagnostics import InfraDiagnosticResult

with open("terraform/iam_policies.json") as f:
    policies = json.load(f)

guard = IamGuard()
all_verified = True

for name, policy in policies.items():
    result = guard.verify_access(policy, action="s3:GetObject", resource="arn:aws:s3:::my-bucket/*")
    diagnostic = IamGuard.to_diagnostic(result)
    print(f"[{diagnostic.status.value}] {name}: {diagnostic.agent_message}")
    if not diagnostic.is_verified:
        all_verified = False

if not all_verified:
    sys.exit(1)
```

### Connection to Module 9

This pattern extends Module 9's DevSecOps CI/CD verification. Module 9 teaches the **pattern** (deterministic verification as a CI gate). Module 14 teaches the **application** (infrastructure-specific guards).

---

## 14.9: Lab: Verify a Terraform PR

### Scenario

An intern runs an AI code generator to create a Terraform config. The result includes:
1. An IAM policy that grants `s3:*` to everyone
2. A security group with SSH open to `0.0.0.0/0`
3. A `p4d.24xlarge` GPU instance (budget: $500/month)

Your job: write a guard pipeline that **detects all three issues** and blocks the PR.

### Starter Code

```python
import sys
from qwed_infra import IamGuard, NetworkGuard, CostGuard
from qwed_infra.diagnostics import InfraDiagnosticResult

# The AI-generated Terraform (simplified)
terraform = {
    "iam_policy": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "s3:*",
                "Resource": "*"
            }
        ]
    },
    "network": {
        "subnets": [
            {"id": "subnet-db", "security_groups": ["sg-db"]}
        ],
        "route_tables": [
            {
                "id": "rtb-main",
                "routes": [{"destination": "0.0.0.0/0", "target": "igw-0001"}],
                "subnet_associations": ["subnet-db"]
            }
        ],
        "security_groups": {
            "sg-db": {
                "ingress": [{"port": 22, "cidr": "0.0.0.0/0"}]
            }
        }
    },
    "resources": {
        "instances": [
            {"id": "gpu-node", "instance_type": "p4d.24xlarge", "count": 1}
        ]
    }
}

budget_monthly = "500"

# Your code here:
# 1. Verify IAM — s3:* on * should over-privilege the policy
# 2. Verify network — port 22 from 0.0.0.0/0 to a DB subnet is dangerous
# 3. Verify cost — p4d.24xlarge costs ~$23K/month, budget is $500
```

### Solution

<details>
<summary><strong>Solution</strong></summary>

```python
from qwed_infra import IamGuard, NetworkGuard, CostGuard

all_blocked = []

# 1. IAM check
iam_guard = IamGuard()
iam_result = iam_guard.verify_access(
    terraform["iam_policy"],
    action="s3:*",
    resource="*"
)
iam_diag = IamGuard.to_diagnostic(iam_result)
print(f"[{iam_diag.status.value}] IAM: {iam_diag.agent_message}")
if not iam_diag.is_verified:
    all_blocked.append("IAM")

# 2. Network check
net_guard = NetworkGuard()
net_guard.build_graph(terraform["network"])
net_result = net_guard.verify_reachability(
    terraform["network"],
    source="internet",
    destination="subnet-db",
    port=22
)
net_diag = NetworkGuard.to_diagnostic(net_result)
print(f"[{net_diag.status.value}] Network: {net_diag.agent_message}")
if not net_diag.is_verified:
    all_blocked.append("Network")

# 3. Cost check
cost_guard = CostGuard()
cost_result = cost_guard.verify_budget(
    terraform["resources"],
    budget_monthly=budget_monthly
)
cost_diag = CostGuard.to_diagnostic(cost_result)
print(f"[{cost_diag.status.value}] Cost: {cost_diag.agent_message}")
if not cost_diag.is_verified:
    all_blocked.append("Cost")

if all_blocked:
    print(f"\n🚫 PR BLOCKED by: {', '.join(all_blocked)}")
    sys.exit(1)
else:
    print("\n✅ All checks passed")
```

**Expected output:**
```
[VERIFIED] IAM: IAM policy access: allowed
[BLOCKED] Network: Network reachability blocked
[BLOCKED] Cost: Cost estimate exceeds budget

🚫 PR BLOCKED by: Network, Cost
```

Note: IamGuard allows access because the policy explicitly grants `s3:*` on `*`. The `verify_least_privilege` check would flag this as over-privileged. In a real pipeline, both checks should run.
</details>

---

## 📝 Summary

| Concept | What You Learned |
|---------|-----------------|
| **The Infrastructure Trust Problem** | AI-generated IaC needs deterministic verification, not linting |
| **IamGuard** | Z3-proven IAM access with symbolic Allow/Deny precedence |
| **NetworkGuard** | NetworkX-based VPC reachability, fail-closed on unsupported topologies |
| **CostGuard** | Decimal-arithmetic cost estimation, fail-closed on unknown types |
| **ArtifactBoundaryGuard** | Package integrity scanning — the final release gate |
| **InfraDiagnosticResult** | 3-layer diagnostic model with mandatory `proof_ref` on `VERIFIED` |
| **CI/CD Integration** | IaC verification gates between `plan` and `apply` |

### How It Connects

| Module | Connection |
|--------|-----------|
| **Module 0** — Proof vs Confidence | `InfraDiagnosticResult.proof_ref` is the literal proof |
| **Module 6** — Domains | Infrastructure is the next verification domain |
| **Module 9** — DevSecOps | Module 14 is the IaC-specific implementation of the CI/CD gate pattern |

---

## ➡️ Next Steps

- ⭐ [Star qwed-infra](https://github.com/QWED-AI/qwed-infra)
- 📖 [Read the docs](https://docs.qwedai.com)
- 🚀 [Capstone Project](../capstone-project/README.md)

---

*"Infrastructure is where 'fail closed' stops being a philosophy and starts being your AWS bill."*
