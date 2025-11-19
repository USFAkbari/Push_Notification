"""Generate VAPID keys for Web Push notifications."""
import os
import base64
import logging
import argparse
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Configure logging
logger = logging.getLogger(__name__)


def generate_vapid_keys() -> Tuple[Optional[str], Optional[str]]:
    """Generate VAPID public and private keys using cryptography.
    
    Returns:
        Tuple of (public_key, private_key) as base64 URL-safe strings, or (None, None) on error
    """
    try:
        # Generate EC private key
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        
        # Get public key bytes in uncompressed format
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        
        # Remove the first byte (0x04) which indicates uncompressed point
        # VAPID public key is 65 bytes (0x04 + 32-byte x + 32-byte y)
        # We need only the 64 bytes (x + y)
        public_key_bytes = public_key_bytes[1:]
        
        # Encode to base64 URL-safe
        public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
        
        # Get private key raw value (32 bytes)
        private_key_raw = private_key.private_numbers().private_value
        private_key_bytes = private_key_raw.to_bytes(32, 'big')
        
        # Encode to base64 URL-safe
        private_key_b64 = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8').rstrip('=')
        
        return public_key_b64, private_key_b64
    except ImportError:
        logger.error("Error: cryptography is not installed. Install it with: pip install cryptography")
        return None, None
    except Exception as e:
        logger.error(f"Error generating VAPID keys: {e}", exc_info=True)
        return None, None


def validate_vapid_keys(public_key: Optional[str], private_key: Optional[str]) -> bool:
    """Validate VAPID keys format.
    
    Args:
        public_key: VAPID public key as base64 URL-safe string
        private_key: VAPID private key as base64 URL-safe string
        
    Returns:
        True if keys are valid, False otherwise
    """
    if not public_key or not private_key:
        return False
    
    try:
        # Decode and check key lengths
        public_key_bytes = base64.urlsafe_b64decode(public_key + '==')
        private_key_bytes = base64.urlsafe_b64decode(private_key + '==')
        
        # Public key should be 64 bytes (x + y coordinates)
        # Private key should be 32 bytes
        if len(public_key_bytes) != 64 or len(private_key_bytes) != 32:
            return False
        
        # Try to reconstruct the key pair to verify they match
        # This is a basic validation - full validation would require using the keys
        return True
    except Exception as e:
        logger.debug(f"Key validation error: {e}")
        return False


def get_vapid_keys_from_env() -> Tuple[Optional[str], Optional[str]]:
    """Get VAPID keys from environment variables.
    
    Returns:
        Tuple of (public_key, private_key) from environment, or (None, None) if not found
    """
    public_key = os.getenv("VAPID_PUBLIC_KEY")
    private_key = os.getenv("VAPID_PRIVATE_KEY")
    return public_key, private_key


def read_env_file(env_path: Path) -> dict:
    """Read environment variables from .env file.
    
    Args:
        env_path: Path to .env file
        
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    if not env_path.exists():
        return env_vars
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        logger.warning(f"Error reading .env file: {e}")
    
    return env_vars


def write_keys_to_env(
    public_key: str,
    private_key: str,
    env_path: Optional[Path] = None,
    vapid_email: Optional[str] = None
) -> bool:
    """Write VAPID keys to .env file.
    
    Args:
        public_key: VAPID public key
        private_key: VAPID private key
        env_path: Path to .env file (defaults to backend/.env)
        vapid_email: VAPID email (optional)
        
    Returns:
        True if successful, False otherwise
    """
    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    
    try:
        # Read existing .env file if it exists
        env_vars = read_env_file(env_path)
        
        # Update VAPID keys
        env_vars["VAPID_PUBLIC_KEY"] = public_key
        env_vars["VAPID_PRIVATE_KEY"] = private_key
        if vapid_email:
            env_vars["VAPID_EMAIL"] = vapid_email
        elif "VAPID_EMAIL" not in env_vars:
            env_vars["VAPID_EMAIL"] = os.getenv("VAPID_EMAIL", "mailto:example@example.com")
        
        # Write to file
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"VAPID keys written to {env_path}")
        return True
    except PermissionError:
        logger.warning(f"Permission denied: Cannot write to {env_path}")
        return False
    except Exception as e:
        logger.error(f"Error writing to .env file: {e}")
        return False


def is_docker_environment() -> bool:
    """Check if running in Docker container.
    
    Returns:
        True if running in Docker, False otherwise
    """
    # Check for Docker-specific files
    return Path("/.dockerenv").exists() or os.path.exists("/proc/self/cgroup") and "docker" in open("/proc/self/cgroup").read()


def ensure_vapid_keys(
    env_path: Optional[Path] = None,
    write_to_file: bool = True,
    silent: bool = False,
    vapid_email: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], bool]:
    """Ensure VAPID keys exist, generating them if necessary.
    
    This is the main automation function that:
    1. Checks environment variables first
    2. Checks .env file if no env vars found
    3. Generates new keys if none exist
    4. Optionally writes keys to .env file
    
    Args:
        env_path: Path to .env file (defaults to backend/.env)
        write_to_file: Whether to write keys to .env file if generated
        silent: If True, suppress output messages
        vapid_email: VAPID email to use (optional)
        
    Returns:
        Tuple of (public_key, private_key, was_generated) where was_generated indicates if keys were just created
    """
    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    
    was_generated = False
    
    # First, check environment variables
    public_key, private_key = get_vapid_keys_from_env()
    
    if public_key and private_key:
        if validate_vapid_keys(public_key, private_key):
            if not silent:
                logger.info("VAPID keys found in environment variables")
            return public_key, private_key, False
        else:
            if not silent:
                logger.warning("VAPID keys found in environment but are invalid")
    
    # Second, check .env file
    if not public_key or not private_key:
        env_vars = read_env_file(env_path)
        public_key = env_vars.get("VAPID_PUBLIC_KEY")
        private_key = env_vars.get("VAPID_PRIVATE_KEY")
        
        if public_key and private_key:
            if validate_vapid_keys(public_key, private_key):
                if not silent:
                    logger.info(f"VAPID keys found in {env_path}")
                return public_key, private_key, False
            else:
                if not silent:
                    logger.warning(f"VAPID keys found in {env_path} but are invalid")
    
    # Generate new keys if none exist or existing ones are invalid
    if not silent:
        logger.info("Generating new VAPID keys...")
    
    public_key, private_key = generate_vapid_keys()
    
    if not public_key or not private_key:
        logger.error("Failed to generate VAPID keys")
        return None, None, False
    
    was_generated = True
    
    # Write to .env file if requested and file is writable
    if write_to_file:
        if env_path.parent.exists() and os.access(env_path.parent, os.W_OK):
            write_keys_to_env(public_key, private_key, env_path, vapid_email)
        else:
            if not silent:
                logger.warning(f"Cannot write to {env_path} - directory not writable or doesn't exist")
    
    if not silent:
        logger.info("VAPID keys generated successfully")
        if not write_to_file or not os.access(env_path.parent, os.W_OK):
            print("\n" + "=" * 60)
            print("VAPID Keys Generated Successfully")
            print("=" * 60)
            print("\nAdd these to your .env file or environment variables:\n")
            print(f"VAPID_PUBLIC_KEY={public_key}")
            print(f"VAPID_PRIVATE_KEY={private_key}")
            if vapid_email:
                print(f"VAPID_EMAIL={vapid_email}")
            else:
                print(f"VAPID_EMAIL=mailto:your-email@example.com")
            print("\n" + "=" * 60)
    
    return public_key, private_key, was_generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate VAPID keys for Web Push notifications")
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress output messages (useful for automation)"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        default=True,
        help="Write keys to .env file (default: True)"
    )
    parser.add_argument(
        "--no-write",
        dest="write",
        action="store_false",
        help="Don't write keys to .env file"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to .env file (default: backend/.env)"
    )
    parser.add_argument(
        "--email",
        type=str,
        help="VAPID email (e.g., mailto:example@example.com)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing keys instead of generating new ones"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.silent:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    env_path = Path(args.env_file) if args.env_file else None
    
    if args.validate:
        # Validate mode
        public_key, private_key = get_vapid_keys_from_env()
        if not public_key or not private_key:
            env_vars = read_env_file(env_path or Path(__file__).parent / ".env")
            public_key = env_vars.get("VAPID_PUBLIC_KEY")
            private_key = env_vars.get("VAPID_PRIVATE_KEY")
        
        if public_key and private_key:
            if validate_vapid_keys(public_key, private_key):
                print("VAPID keys are valid")
                exit(0)
            else:
                print("VAPID keys are invalid")
                exit(1)
        else:
            print("VAPID keys not found")
            exit(1)
    else:
        # Generate mode
        ensure_vapid_keys(
            env_path=env_path,
            write_to_file=args.write,
            silent=args.silent,
            vapid_email=args.email
        )

