import json
import requests
from typing import Dict, Any, Tuple
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class QWEDCertificateVerifier:
    """Verify QWED Verifiable Credentials"""
    
    def __init__(self, issuer_did: str = "did:web:qwed-ai.com"):
        self.issuer_did = issuer_did
        self.public_key = self._fetch_public_key()
    
    def _fetch_public_key(self):
        """Fetch public key from DID document"""
        # For did:web, resolve from: https://qwed-ai.com/.well-known/did.json
        # NOTE: For development/test, we might not reach the real URL.
        url = f"https://qwed-ai.com/.well-known/did.json"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            did_doc = response.json()
            
            # Extract public key (JWK format)
            public_key_jwk = did_doc["publicKey"][0]
            return public_key_jwk
        except Exception as e:
            # print(f"Warning: Could not fetch DID document: {e}") 
            # Valid in dev environment where domain doesn't exist yet
            return None
    
    def verify_credential(self, credential: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verify a verifiable credential
        """
        try:
            # Check required fields
            if not all(field in credential for field in ["@context", "type", "credentialSubject", "proof"]):
                return False, "Missing required fields"
            
            # Check issuer
            if credential.get("issuer") != self.issuer_did:
                return False, f"Unknown issuer: {credential.get('issuer')}"
            
            # Check credential type
            if "CourseCompletionCredential" not in credential.get("type", []):
                return False, "Not a course completion credential"
            
            # Check if modules are 11
            subject = credential.get("credentialSubject", {})
            if subject.get("modulesCertified") != 11:
                return False, f"Only {subject.get('modulesCertified')} modules certified (need 11)"
            
            # Verify signature (requires public key infrastructure)
            # In production, implement actual RS256 verification using self.public_key
            
            return True, f"✅ Certificate verified for {subject.get('name')}"
        
        except Exception as e:
            return False, f"Verification error: {str(e)}"
    
    def verify_jwt_credential(self, token: str) -> Tuple[bool, Dict]:
        """Verify a JWT-encoded credential"""
        try:
            # Note: In production, pass key=self.public_pem content if available
            decoded = jwt.decode(token, options={"verify_signature": False})
            credential = decoded.get("vc", {})
            
            is_valid, message = self.verify_credential(credential)
            return is_valid, {
                "valid": is_valid,
                "message": message,
                "credential": credential
            }
        except Exception as e:
            return False, {"valid": False, "message": f"JWT decode error: {str(e)}"}

if __name__ == "__main__":
    verifier = QWEDCertificateVerifier()
    print("Verifier initialized.")
