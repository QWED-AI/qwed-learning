import json
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import jwt

class QWEDCertificateIssuer:
    """
    Issues W3C Verifiable Credentials for QWED AI Verification course completion.
    Uses did:web for decentralized identity (no blockchain needed initially).
    """
    
    def __init__(self, issuer_domain: str = "qwed-ai.com", private_key_path: str = None):
        """
        Args:
            issuer_domain: Domain for DID (did:web:qwed-ai.com)
            private_key_path: Path to private key for signing (if None, generates one)
        """
        self.issuer_domain = issuer_domain
        self.did = f"did:web:{issuer_domain}"
        self.private_key = self._load_or_generate_key(private_key_path)
    
    def _load_or_generate_key(self, key_path: Optional[str]):
        """Load existing key or generate new one"""
        if key_path:
            with open(key_path, 'rb') as f:
                return serialization.load_pem_private_key(
                    f.read(),
                    password=None, # In production, use password protection
                    backend=default_backend()
                )
        else:
            # Generate new RSA key (Ephemeral mode - verify in prod needs persistent key)
            return rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
    
    def get_public_key_jwk(self) -> Dict[str, Any]:
        """Export public key in JWK format"""
        public_key = self.private_key.public_key()
        numbers = public_key.public_numbers()
        
        return {
            "kty": "RSA",
            "kid": f"{self.did}#key-1",
            "use": "sig",
            "alg": "RS256",
            "n": self._int_to_base64url(numbers.n),
            "e": self._int_to_base64url(numbers.e)
        }
    
    @staticmethod
    def _int_to_base64url(num: int) -> str:
        """Convert integer to base64url"""
        import base64
        byte_length = (num.bit_length() + 7) // 8
        byte_array = num.to_bytes(byte_length, byteorder='big')
        return base64.urlsafe_b64encode(byte_array).decode('ascii').rstrip('=')
    
    def create_did_document(self) -> Dict[str, Any]:
        """Create DID document for did:web resolution"""
        return {
            "@context": "https://w3id.org/did/v1",
            "id": self.did,
            "publicKey": [self.get_public_key_jwk()],
            "authentication": [f"{self.did}#key-1"],
            "assertionMethod": [f"{self.did}#key-1"]
        }
    
    def issue_certificate(
        self,
        github_username: str,
        completion_date: str,
        modules_completed: int = 11
    ) -> Dict[str, Any]:
        """
        Issue a W3C Verifiable Credential for course completion
        """
        
        # Generate unique credential ID
        credential_id = self._generate_credential_id(github_username)
        
        # Create the unsigned credential
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://www.w3.org/2018/credentials/examples/v1"
            ],
            "type": ["VerifiableCredential", "CourseCompletionCredential"],
            "id": credential_id,
            "issuer": self.did,
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
            "expirationDate": self._add_years(datetime.utcnow(), 5).isoformat() + "Z",
            "credentialSubject": {
                "id": f"did:github:{github_username}",
                "name": github_username,
                "courseTitle": "Master AI Verification: Stop LLM Hallucinations in Production",
                "courseCode": "QWED-AI-2026",
                "completionDate": completion_date,
                "modulesCertified": modules_completed,
                "coursePath": "Full Course (11 Modules)",
                "issuerName": "QWED-AI"
            },
            "proof": {
                "type": "RsaSignature2018",
                "created": datetime.utcnow().isoformat() + "Z",
                "verificationMethod": f"{self.did}#key-1",
                "signatureValue": ""  # Will be filled by sign()
            }
        }
        
        # Sign the credential
        return self._sign_credential(credential)
    
    def _sign_credential(self, credential: Dict[str, Any]) -> Dict[str, Any]:
        """Sign the credential using RS256"""
        # Remove proof temporarily for signing
        proof = credential.pop("proof")
        
        # Convert to JSON string for signing (Canonicalization)
        credential_json = json.dumps(credential, separators=(',', ':'), sort_keys=True)
        
        # Sign
        signature_bytes = self.private_key.sign(
            credential_json.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Encode signature as base64url
        import base64
        signature_b64 = base64.urlsafe_b64encode(signature_bytes).decode('ascii').rstrip('=')
        
        # Add signature to proof
        proof["signatureValue"] = signature_b64
        credential["proof"] = proof
        
        return credential
    
    @staticmethod
    def _generate_credential_id(github_username: str) -> str:
        """Generate unique credential ID"""
        timestamp = datetime.utcnow().timestamp()
        hash_input = f"{github_username}:{timestamp}".encode()
        credential_hash = hashlib.sha256(hash_input).hexdigest()[:16]
        return f"urn:qwed:credential:{github_username}:{credential_hash}"
    
    @staticmethod
    def _add_years(date: datetime, years: int) -> datetime:
        """Add years to a datetime"""
        try:
            return date.replace(year=date.year + years)
        except ValueError:
            return date.replace(year=date.year + years, day=28)
    
    def create_jwt_credential(self, credential: Dict[str, Any]) -> str:
        """
        Create a JWT representation of the credential
        """
        payload = {
            "vc": credential,
            "iss": self.did,
            "aud": "https://github.com",
            "exp": int(datetime.utcnow().timestamp()) + (365 * 24 * 60 * 60)  # 1 year
        }
        
        # Encode using the private key
        token = jwt.encode(
            payload,
            self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ),
            algorithm="RS256"
        )
        
        return token

if __name__ == "__main__":
    # Test
    issuer = QWEDCertificateIssuer()
    doc = issuer.create_did_document()
    print(json.dumps(doc, indent=2))
