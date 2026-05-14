import base64
import json
from typing import Any, Dict, Optional, Tuple

import jwt
import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class QWEDCertificateVerifier:
    """Verify demo QWED Verifiable Credentials.

    This verifier is intentionally strict: if it cannot establish a trusted
    public key, it fails closed rather than inspecting unsigned claims.
    """

    def __init__(self, issuer_did: str = "did:web:qwed-ai.com"):
        self.issuer_did = issuer_did
        self.public_key = self._fetch_public_key()

    def _fetch_public_key(self) -> Optional[rsa.RSAPublicKey]:
        """Fetch the issuer public key from the DID document."""
        url = "https://qwed-ai.com/.well-known/did.json"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            did_doc = response.json()
            public_key_jwk = did_doc["publicKey"][0]
            return self._load_public_key_from_jwk(public_key_jwk)
        except Exception:
            return None

    @staticmethod
    def _base64url_to_int(value: str) -> int:
        padding_len = (-len(value)) % 4
        decoded = base64.urlsafe_b64decode(value + ("=" * padding_len))
        return int.from_bytes(decoded, byteorder="big")

    def _load_public_key_from_jwk(self, jwk_data: Dict[str, Any]) -> rsa.RSAPublicKey:
        numbers = rsa.RSAPublicNumbers(
            e=self._base64url_to_int(jwk_data["e"]),
            n=self._base64url_to_int(jwk_data["n"]),
        )
        return numbers.public_key()

    @staticmethod
    def _canonical_credential_payload(credential: Dict[str, Any]) -> bytes:
        unsigned_credential = dict(credential)
        unsigned_credential.pop("proof", None)
        return json.dumps(
            unsigned_credential,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    @staticmethod
    def _signature_bytes(signature_value: str) -> bytes:
        padding_len = (-len(signature_value)) % 4
        return base64.urlsafe_b64decode(signature_value + ("=" * padding_len))

    def _verify_signature(self, credential: Dict[str, Any]) -> Tuple[bool, str]:
        if self.public_key is None:
            return False, "Trusted public key could not be resolved; fail closed"

        proof = credential.get("proof", {})
        signature_value = proof.get("signatureValue")
        if not signature_value:
            return False, "Credential is missing proof.signatureValue"

        try:
            self.public_key.verify(
                self._signature_bytes(signature_value),
                self._canonical_credential_payload(credential),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True, "Signature verified"
        except (InvalidSignature, ValueError, TypeError) as exc:
            return False, f"Signature verification failed: {exc}"

    def verify_credential(self, credential: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            if not all(field in credential for field in ["@context", "type", "credentialSubject", "proof"]):
                return False, "Missing required fields"

            if credential.get("issuer") != self.issuer_did:
                return False, f"Unknown issuer: {credential.get('issuer')}"

            if "CourseCompletionCredential" not in credential.get("type", []):
                return False, "Not a course completion credential"

            subject = credential.get("credentialSubject", {})
            if subject.get("modulesCertified") != 11:
                return False, f"Only {subject.get('modulesCertified')} modules certified (need 11)"

            return self._verify_signature(credential)
        except Exception as exc:
            return False, f"Verification error: {exc}"

    def verify_jwt_credential(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        try:
            if self.public_key is None:
                return False, {
                    "valid": False,
                    "message": "Trusted public key could not be resolved; refusing unsigned inspection",
                }

            decoded = jwt.decode(
                token,
                key=self.public_key,
                algorithms=["RS256"],
                audience="https://github.com",
            )
            credential = decoded.get("vc", {})

            is_valid, message = self.verify_credential(credential)
            return is_valid, {
                "valid": is_valid,
                "message": message,
                "credential": credential,
            }
        except Exception as exc:
            return False, {"valid": False, "message": f"JWT verification error: {exc}"}


if __name__ == "__main__":
    verifier = QWEDCertificateVerifier()
    print("Verifier initialized.")
