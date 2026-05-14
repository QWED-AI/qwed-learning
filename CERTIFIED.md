# QWED Learning Credentials

**Total credential records:** 0 learners

## Important Scope Note

This file documents the **learning-repo credential demo**, not a production trust program.

The demo may be useful for understanding:

- W3C credential structure
- issuer / verifier roles
- signing-key lifecycle questions

But it should **not** be treated as a production-grade proof of identity, completion, or enterprise auditability without:

- a real DID document
- verified public-key distribution
- secure key storage
- operational rotation and revocation
- end-to-end signature verification

---

## What the Demo Illustrates

Each demo learner credential is shaped like a W3C Verifiable Credential and is intended to show:

- issuer metadata
- credential subject structure
- expiration handling
- detached verification concepts

---

## What This Demo Does Not Guarantee

This learning repository does **not** claim that the bundled demo artifacts are:

- tamper-proof in production
- enterprise-ready
- a substitute for managed key infrastructure
- safe to use with committed signing keys

If you want to build a real credentialing system, treat this folder as a starting point for threat modeling, not a ready-made trust anchor.

---

## Secure Usage Expectations

- Do not commit private signing keys.
- Generate local demo keys only in ignored directories.
- Verify signatures before accepting any credential as trusted.
- Document revocation, rotation, and issuer ownership before operational use.

---

## Credential Records

<!-- Automatically updated by GitHub Action when demo credentials are in use -->

---

*Want to experiment with the demo? Complete the course, then inspect the issuer and verifier code with the trust-boundary warnings above in mind.*
