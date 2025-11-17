"""Generate VAPID keys for Web Push notifications."""
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def generate_vapid_keys():
    """Generate VAPID public and private keys using cryptography."""
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
        
        print("=" * 60)
        print("VAPID Keys Generated Successfully")
        print("=" * 60)
        print("\nAdd these to your .env file:\n")
        print(f"VAPID_PUBLIC_KEY={public_key_b64}")
        print(f"VAPID_PRIVATE_KEY={private_key_b64}")
        print(f"VAPID_EMAIL=mailto:your-email@example.com")
        print("\n" + "=" * 60)
        
        return public_key_b64, private_key_b64
    except ImportError:
        print("Error: cryptography is not installed.")
        print("Install it with: pip install cryptography")
        return None, None
    except Exception as e:
        print(f"Error generating VAPID keys: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    generate_vapid_keys()

