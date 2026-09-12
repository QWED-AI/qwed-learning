"""Lab 01 — sign a bound token, fail detached use, verify the true exchange.

Run:  python lab/01_sign_bind_verify.py
Needs: pip install "git+https://github.com/QWED-AI/qwed-a2a.git@aa125ad6f982f9ad10565e6a8e234bb2b277c959"
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

from qwed_a2a.security.crypto import A2ACryptoService, AttestationContext

PAYLOAD = {"total": 150.0}

svc = A2ACryptoService(issuer_id="did:qwed:a2a:lab")
token = svc.sign_verdict(
    trace_id="lab-001",
    verdict_status="forwarded",
    engine="lab",
    sender_id="agent-A",
    receiver_id="agent-B",
    payload_hash=A2ACryptoService.payload_hash(PAYLOAD),
)
print("minted:", token[:40], "...")

detached = AttestationContext(
    sender_agent_id="agent-A", receiver_agent_id="agent-B", payload={"total": 999.0}
)
ok, _, err = svc.verify_attestation(token, detached)
assert not ok, "detached token must not verify"
print("detached denied:", err[:70])

ctx = AttestationContext(
    sender_agent_id="agent-A", receiver_agent_id="agent-B", payload=PAYLOAD
)
ok, claims, err = svc.verify_attestation(token, ctx)
assert ok, err
assert claims["qwed_a2a"]["verdict"] == "forwarded"
print("verified ok")
print("LAB 01 PASSED")
