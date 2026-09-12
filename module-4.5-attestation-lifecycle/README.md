# Module 4.5: Production Attestation Lifecycle

**Time:** 60 min · **Level:** Intermediate · **Prerequisites:** Modules 0–4

So far you have verified claims with engines. This module covers what happens *around* the proof in production: how an attestation is minted, what binds it to one exchange, how replays die, and how a shipping decision consumes it. Every snippet below runs for real against `qwed-a2a` — no mocks stand in for the crypto path.

```bash
pip install "git+https://github.com/QWED-AI/qwed-a2a.git@aa125ad6f982f9ad10565e6a8e234bb2b277c959"
```

> Pinned to the commit that carries the behavior taught here. `qwed-a2a` 0.2.0 on PyPI predates it — install from source until the next release. Each lab also needs `QWED_A2A_DEPLOYMENT_ID` set (any stable string per deployment) and generates its own throwaway P-256 signing key, so nothing here touches real credentials.

Run any section standalone (`lab/01_sign_bind_verify.py`, `lab/02_replay_lifecycle.py`, `lab/03_consume_gate.py`) — each asserts its outcomes and prints what happened.

---

## 1. Sign — mint a bound token, not a bare signature

```python
from qwed_a2a.security.crypto import A2ACryptoService

svc = A2ACryptoService(issuer_id="did:qwed:a2a:lab")
token = svc.sign_verdict(
    trace_id="lab-001",
    verdict_status="forwarded", engine="lab",
    sender_id="agent-A", receiver_id="agent-B",
    payload_hash=A2ACryptoService.payload_hash({"total": 150.0}),
)
```

The token binds five things: issuer, payload hash (`sub`), deployment, participants, and a unique `jti` (your `trace_id`). A signature over *less* than this is a souvenir, not an attestation.

> **Attack note.** Sign the same `trace_id` twice and the second call raises `ValueError`. Without that refusal, two contradictory tokens would share one `jti` — and whichever a consumer saw first would poison its replay registry against the other.

---

## 2. Bind — a valid signature alone verifies nothing

```python
from qwed_a2a.security.crypto import AttestationContext

ctx = AttestationContext(
    sender_agent_id="agent-A", receiver_agent_id="agent-B",
    payload={"total": 999.0},  # NOT what was signed
)
ok, _, err = svc.verify_attestation(token, ctx)
assert not ok  # Attestation payload hash mismatch — detached attestation rejected
```

A stolen token replayed against a different payload, sender, receiver, or session dies here — *after* the signature checks out. If your verifier skips context binding, possession of any valid token equals impersonation of every agent.

> **Attack note.** Detach the token from its exchange (different payload hash above) and watch it fail *despite* a valid signature. That gap is the whole threat model for unattended agents.

---

## 3. Verify — try every key, trust none before proof

```python
ctx = AttestationContext(
    sender_agent_id="agent-A", receiver_agent_id="agent-B",
    payload={"total": 150.0},
)
ok, claims, err = svc.verify_attestation(token, ctx)
assert ok  # claims["qwed_a2a"]["verdict"] == "forwarded"
```

Verification tries each configured key (own key, then trusted peer keys) and reads the header/payload *only after* a key verifies the signature. The verified `iss`/`kid` are then bound to the key that proved them; unknown issuers, kid mismatches, and deployment mismatches all deny. Nodes without a signing key verify peer tokens the same way.

> **Attack note.** Flip one character in the token and re-verify: `Invalid token`. Mint a token with an unregistered `iss`: no trusted key verifies it. Both die without ever trusting a single unverified byte.

---

## 4. Replay — one `jti`, one consumption

Signing and verifying track *separate* records, which is why the issuer above could verify its own token exactly once:

```python
# Second signing with the same trace_id:
svc.sign_verdict(trace_id="lab-001", ...)  # ValueError: duplicate trace_id
# Second verification of the same token:
ok, _, err = svc.verify_attestation(token, ctx)  # Replay detected: jti already seen
```

Peer issuers sharing a trace ID never shadow each other (consumption keys are namespaced per issuer), and two workers sharing one `JtiRegistry` close the cross-worker window — try it in `lab/02_replay_lifecycle.py`.

> **Attack note.** Replay the verified token and read the denial. Then consider: without the split registry, the issuer could never self-verify (signing would burn its own slot), and without namespacing, one deployment's trace IDs would deny another's.

---

## 5. Consume — gate on the tuple, fail closed

```python
def ship(token, ctx):
    ok, _, err = svc.verify_attestation(token, ctx)
    return ("SHIP", None) if ok else ("HOLD", err)
```

That is the entire shipping rule: `ok` ships, anything else holds with the reason attached. No fallthrough, no warning-to-ship promotion, no `verified`-ish states — the three-state contract from Module 0, enforced at the call site. Production gates formalize this as the Verification Context v1.0 object (`verdict`/`admission`/`proof_ref`); the discipline is identical.

> **Attack note.** Feed the replayed token to `ship()` and confirm `HOLD`. Every merge-bypass story in this specialization starts with someone treating a non-`ok` as shippable.

---

## ➡️ Next: Module 5

You now understand the trust machinery around a proof. Next, see how the wider verification landscape compares: [Module 5: Verification Landscape](../module-5-verification-landscape/README.md).
