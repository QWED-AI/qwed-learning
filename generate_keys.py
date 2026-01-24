from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_keys():
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialize private key
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    pem_public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Save
    with open("private_key.pem", "wb") as f:
        f.write(pem_private)
        
    with open("public_key.pem", "wb") as f:
        f.write(pem_public)

    print("✅ Keys generated:")
    print("   - private_key.pem (Use in GitHub Secrets)")
    print("   - public_key.pem (Use in DID Document)")

if __name__ == "__main__":
    generate_keys()
