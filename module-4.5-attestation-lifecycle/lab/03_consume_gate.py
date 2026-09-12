"""Lab 03 — consume attestations through a fail-closed shipping gate.

Run:  python lab/03_consume_gate.py
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
ctx = AttestationContext(
    sender_agent_id="agent-A", receiver_agent_id="agent-B", payload=PAYLOAD
)
token = svc.sign_verdict(
    trace_id="lab-201",
    verdict_status="forwarded",
    engine="lab",
    sender_id="agent-A",
    receiver_id="agent-B",
    payload_hash=A2ACryptoService.payload_hash(PAYLOAD),
)


def ship(token, ctx):
    ok, _, err = svc.verify_attestation(token, ctx)
    return ("SHIP", None) if ok else ("HOLD", err)


assert ship(token, ctx)[0] == "SHIP"
print("fresh token ships")

# The gate consumed the slot: any later presentation is a replay.
decision, reason = ship(token, ctx)
assert decision == "HOLD" and "Replay" in reason, (decision, reason)
print("replayed token holds:", reason)
print("LAB 03 PASSED")
