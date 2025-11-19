#!/usr/bin/env python3
"""Standalone script to initialize VAPID keys for Web Push notifications.

This script can be run independently to generate and configure VAPID keys.
It will check for existing keys and only generate new ones if needed.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import generate_vapid_keys
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_vapid_keys import ensure_vapid_keys
import argparse
import logging


def main():
    """Main function to initialize VAPID keys."""
    parser = argparse.ArgumentParser(
        description="Initialize VAPID keys for Web Push notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate keys and write to default .env file
  python scripts/init_vapid_keys.py

  # Generate keys without writing to file
  python scripts/init_vapid_keys.py --no-write

  # Generate keys with custom email
  python scripts/init_vapid_keys.py --email mailto:admin@example.com

  # Generate keys to custom .env file
  python scripts/init_vapid_keys.py --env-file /path/to/.env

  # Force regeneration of keys
  python scripts/init_vapid_keys.py --force
        """
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
        "--no-write",
        action="store_true",
        help="Don't write keys to .env file (only print them)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if keys already exist"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress output messages (useful for automation)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.silent:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    logger = logging.getLogger(__name__)
    
    # Determine .env file path
    if args.env_file:
        env_path = Path(args.env_file)
    else:
        # Default to backend/.env relative to script location
        env_path = Path(__file__).parent.parent / ".env"
    
    # Check if keys already exist (unless forcing)
    if not args.force:
        from generate_vapid_keys import get_vapid_keys_from_env, read_env_file, validate_vapid_keys
        
        # Check environment variables first
        public_key, private_key = get_vapid_keys_from_env()
        
        # Check .env file if not in environment
        if not public_key or not private_key:
            env_vars = read_env_file(env_path)
            public_key = env_vars.get("VAPID_PUBLIC_KEY")
            private_key = env_vars.get("VAPID_PRIVATE_KEY")
        
        # Validate existing keys
        if public_key and private_key:
            if validate_vapid_keys(public_key, private_key):
                if not args.silent:
                    print("VAPID keys already exist and are valid.")
                    print(f"Public Key: {public_key[:20]}...")
                    print("\nTo force regeneration, use --force flag.")
                return 0
            else:
                if not args.silent:
                    print("Warning: Existing VAPID keys are invalid. Regenerating...")
    
    # Generate keys
    if not args.silent:
        print("Initializing VAPID keys...")
    
    public_key, private_key, was_generated = ensure_vapid_keys(
        env_path=env_path,
        write_to_file=not args.no_write,
        silent=args.silent,
        vapid_email=args.email
    )
    
    if not public_key or not private_key:
        logger.error("Failed to generate VAPID keys")
        return 1
    
    if not args.silent:
        if was_generated:
            print("\n" + "=" * 60)
            print("VAPID Keys Initialized Successfully")
            print("=" * 60)
            
            if args.no_write:
                print("\nGenerated keys (not written to file):")
                print(f"\nVAPID_PUBLIC_KEY={public_key}")
                print(f"VAPID_PRIVATE_KEY={private_key}")
                if args.email:
                    print(f"VAPID_EMAIL={args.email}")
                print("\nAdd these to your .env file or environment variables.")
            else:
                print(f"\nKeys have been written to: {env_path}")
                print(f"Public Key: {public_key[:30]}...")
        else:
            print("VAPID keys are already configured and valid.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
