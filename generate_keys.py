from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keys() -> None:
    """Generate local demo keys for the credential walkthrough.

    These keys are for local learning use only. They are written into an ignored
    directory so the course repo does not model committed signing material.
    """

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pem_public = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    output_dir = Path("local-dev-keys")
    output_dir.mkdir(exist_ok=True)

    private_key_path = output_dir / "private_key.pem"
    public_key_path = output_dir / "public_key.pem"

    private_key_path.write_bytes(pem_private)
    public_key_path.write_bytes(pem_public)

    print("Keys generated for local demo use:")
    print(f"  - {private_key_path}")
    print(f"  - {public_key_path}")
    print("Do not commit these files or use them as a production trust anchor.")


if __name__ == "__main__":
    generate_keys()
