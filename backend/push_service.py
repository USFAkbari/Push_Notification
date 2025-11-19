"""VAPID push service for sending Web Push notifications."""
import os
import json
import logging
from typing import Dict, Optional
from pywebpush import webpush, WebPushException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Function to reload VAPID keys from environment (useful after key generation)
def _reload_vapid_keys():
    """Reload VAPID keys from environment variables."""
    global VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL, VAPID_CLAIMS
    load_dotenv(override=True)  # Reload .env file
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
    VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:example@example.com")
    VAPID_CLAIMS = {
        "sub": VAPID_EMAIL
    }

# Initial load of VAPID keys
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:example@example.com")

VAPID_CLAIMS = {
    "sub": VAPID_EMAIL
}

# Validate VAPID keys on import
def _validate_keys_on_import():
    """Validate VAPID keys when module is imported.
    
    Returns:
        True if keys are valid, False if invalid, None if validation unavailable
    """
    try:
        from generate_vapid_keys import validate_vapid_keys
        
        if not VAPID_PUBLIC_KEY or not VAPID_PRIVATE_KEY:
            logger.warning(
                "VAPID keys are not configured. "
                "Keys will be auto-generated on application startup if possible. "
                "Set VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY environment variables "
                "or add them to a .env file for manual configuration."
            )
            return False
        
        if not validate_vapid_keys(VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY):
            logger.error(
                "VAPID keys are invalid. "
                "Please regenerate keys using: python scripts/init_vapid_keys.py "
                "or let the application auto-generate them on startup."
            )
            return False
        
        logger.debug("VAPID keys are valid and configured")
        return True
    except ImportError:
        # generate_vapid_keys might not be available in all contexts
        logger.debug("Could not import key validation module - validation skipped")
        return None
    except Exception as e:
        logger.warning(f"Error validating VAPID keys: {e}")
        return None

# Perform validation on import
_VAPID_KEYS_VALID = _validate_keys_on_import()


def get_vapid_public_key() -> Optional[str]:
    """Get VAPID public key for client subscription.
    
    This function will reload keys from environment if they're not available,
    which is useful if keys were generated after module import.
    
    Returns:
        VAPID public key string, or None if not configured
    """
    # Reload keys if not available (in case they were generated after import)
    if not VAPID_PUBLIC_KEY:
        _reload_vapid_keys()
    
    if not VAPID_PUBLIC_KEY:
        logger.warning("VAPID public key is not configured")
    return VAPID_PUBLIC_KEY


async def send_push_notification(
    subscription_info: Dict,
    payload: Dict,
    vapid_private_key: Optional[str] = None
) -> bool:
    """
    Send a push notification to a subscription.
    
    Args:
        subscription_info: Dictionary containing endpoint and keys
        payload: Notification payload (title, body, etc.)
        vapid_private_key: Optional override for VAPID private key
        
    Returns:
        True if successful, False otherwise
    """
    # Reload keys if not available (in case they were generated after import)
    if not VAPID_PRIVATE_KEY:
        _reload_vapid_keys()
    
    # Check if keys are configured
    key_to_use = vapid_private_key or VAPID_PRIVATE_KEY
    if not key_to_use:
        logger.error(
            "VAPID private key is not configured. Cannot send push notification. "
            "Ensure VAPID keys are set in environment variables or .env file."
        )
        return False
    
    import asyncio
    try:
        # pywebpush is synchronous, so we run it in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=key_to_use,
                vapid_claims=VAPID_CLAIMS
            )
        )
        return True
    except WebPushException as e:
        logger.error(f"WebPush exception: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return False

