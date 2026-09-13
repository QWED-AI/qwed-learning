"""Lab 02 — replay dies at issuance, at consumption, and across workers.

Run:  python lab/02_replay_lifecycle.py
Needs: pip install "qwed-a2a==0.3.0"
"""

import os

os.environ.setdefault("QWED_A2A_DEPLOYMENT_ID", "lab-deploy")

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

key = ec.generate_private_key(ec.SECP256R1())
os.environ["QWED_A2A_SIGNING_KEY_PEM"] = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode()

from qwed_a2a.security.crypto import (
    A2ACryptoService,
    AttestationContext,
    JtiRegistry,
)

PAYLOAD = {"total": 150.0}
ISSUER = "did:qwed:a2a:lab"
CTX_KW = {
    "sender_agent_id": "agent-A",
    "receiver_agent_id": "agent-B",
    "payload": PAYLOAD,
}

svc = A2ACryptoService(issuer_id=ISSUER)


def fresh_token(svc, trace_id):
    return svc.sign_verdict(
        trace_id=trace_id,
        verdict_status="forwarded",
        engine="lab",
        sender_id="agent-A",
        receiver_id="agent-B",
        payload_hash=A2ACryptoService.payload_hash(PAYLOAD),
    )


# Issuance: the second mint under one trace_id raises.
token = fresh_token(svc, "lab-101")
try:
    fresh_token(svc, "lab-101")
    raise SystemExit("duplicate trace_id should have raised")
except ValueError as exc:
    print("duplicate refused:", exc)

# Consumption: first verify ok, second is a replay.
ctx = AttestationContext(**CTX_KW)
assert svc.verify_attestation(token, ctx)[0]
ok, _, err = svc.verify_attestation(token, ctx)
assert not ok and "Replay" in err, err
print("replay denied:", err)

# Cross-instance (same process): a shared registry closes the second
# instance's window. Cross-PROCESS workers need an out-of-process store
# implementing the ReplayRegistry contract — an in-memory registry cannot
# cross a process boundary.
shared = JtiRegistry(ttl_seconds=300)
w1 = A2ACryptoService(issuer_id=ISSUER, jti_registry=shared)
w1._key_pair = svc._ensure_key_pair()
w2 = A2ACryptoService(issuer_id=ISSUER, jti_registry=shared)
w2._key_pair = svc._key_pair
token2 = fresh_token(svc, "lab-102")
assert w1.verify_attestation(token2, AttestationContext(**CTX_KW))[0]
assert not w2.verify_attestation(token2, AttestationContext(**CTX_KW))[0]
print("cross-worker replay denied")
print("LAB 02 PASSED")
