"""Application secret generation and management utilities."""
import secrets
from passlib.context import CryptContext

# Context for hashing application secrets
secret_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_application_secret() -> str:
    """
    Generate a secure 32-character application secret.
    Uses cryptographic random generation for high entropy.
    """
    # Generate 32 random bytes and convert to URL-safe base64 (44 chars)
    # Then take first 32 characters to ensure exact length
    random_bytes = secrets.token_bytes(24)  # 24 bytes = 32 base64 chars
    secret = secrets.token_urlsafe(24)[:32]
    
    # Ensure exactly 32 characters
    if len(secret) < 32:
        # Pad if needed (shouldn't happen, but safety check)
        secret = secret.ljust(32, secrets.token_urlsafe(1)[0])
    elif len(secret) > 32:
        secret = secret[:32]
    
    return secret


def hash_application_secret(secret: str) -> str:
    """
    Hash an application secret using bcrypt for secure storage.
    The secret itself is already cryptographically random, but we hash it
    for additional security in case of database compromise.
    """
    return secret_context.hash(secret)


def verify_application_secret(secret: str, secret_hash: str) -> bool:
    """Verify an application secret against its hash."""
    return secret_context.verify(secret, secret_hash)

