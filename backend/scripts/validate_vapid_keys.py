#!/usr/bin/env python3
"""Standalone script to validate VAPID keys for Web Push notifications.

This script checks if VAPID keys are properly configured and valid.
It can check environment variables, .env files, or validate specific keys.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import generate_vapid_keys
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_vapid_keys import (
    get_vapid_keys_from_env,
    read_env_file,
    validate_vapid_keys
)
import argparse
import logging


def main():
    """Main function to validate VAPID keys."""
    parser = argparse.ArgumentParser(
        description="Validate VAPID keys for Web Push notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate keys from environment or .env file
  python scripts/validate_vapid_keys.py

  # Validate keys from specific .env file
  python scripts/validate_vapid_keys.py --env-file /path/to/.env

  # Validate specific keys provided as arguments
  python scripts/validate_vapid_keys.py --public-key KEY --private-key KEY

  # Exit with code 0 if valid, 1 if invalid (useful for scripts)
  python scripts/validate_vapid_keys.py && echo "Keys are valid"
        """
    )
    
    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to .env file to check (default: backend/.env)"
    )
    parser.add_argument(
        "--public-key",
        type=str,
        help="VAPID public key to validate"
    )
    parser.add_argument(
        "--private-key",
        type=str,
        help="VAPID private key to validate"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output validation result (no detailed messages)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation information"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    logger = logging.getLogger(__name__)
    
    # Get keys from arguments, environment, or .env file
    public_key = args.public_key
    private_key = args.private_key
    
    if not public_key or not private_key:
        # Try environment variables first
        public_key, private_key = get_vapid_keys_from_env()
        
        # Try .env file if not in environment
        if not public_key or not private_key:
            if args.env_file:
                env_path = Path(args.env_file)
            else:
                env_path = Path(__file__).parent.parent / ".env"
            
            env_vars = read_env_file(env_path)
            public_key = public_key or env_vars.get("VAPID_PUBLIC_KEY")
            private_key = private_key or env_vars.get("VAPID_PRIVATE_KEY")
    
    # Check if keys were found
    if not public_key or not private_key:
        if not args.quiet:
            print("ERROR: VAPID keys not found")
            print("\nKeys can be provided via:")
            print("  - Environment variables: VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY")
            print("  - .env file: VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY")
            print("  - Command line arguments: --public-key and --private-key")
        return 1
    
    # Validate keys
    if args.verbose:
        print(f"Validating VAPID keys...")
        print(f"Public Key: {public_key[:30]}...")
        print(f"Private Key: {'*' * 30}...")
    
    is_valid = validate_vapid_keys(public_key, private_key)
    
    if is_valid:
        if not args.quiet:
            print("SUCCESS: VAPID keys are valid")
            if args.verbose:
                # Decode and show key lengths
                import base64
                try:
                    pub_bytes = base64.urlsafe_b64decode(public_key + '==')
                    priv_bytes = base64.urlsafe_b64decode(private_key + '==')
                    print(f"Public key length: {len(pub_bytes)} bytes (expected: 64)")
                    print(f"Private key length: {len(priv_bytes)} bytes (expected: 32)")
                except Exception as e:
                    logger.debug(f"Could not decode keys for detailed info: {e}")
        return 0
    else:
        if not args.quiet:
            print("ERROR: VAPID keys are invalid")
            print("\nPossible issues:")
            print("  - Keys are not in correct base64 URL-safe format")
            print("  - Keys have incorrect length")
            print("  - Keys are corrupted or incomplete")
            print("\nTo regenerate keys, run:")
            print("  python scripts/init_vapid_keys.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
