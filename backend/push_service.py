"""VAPID push service for sending Web Push notifications."""
import os
import json
from typing import Dict, Optional
from pywebpush import webpush, WebPushException
from dotenv import load_dotenv

load_dotenv()

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL", "mailto:example@example.com")

VAPID_CLAIMS = {
    "sub": VAPID_EMAIL
}


def get_vapid_public_key() -> str:
    """Get VAPID public key for client subscription."""
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
    import asyncio
    try:
        # pywebpush is synchronous, so we run it in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key or VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        )
        return True
    except WebPushException as e:
        print(f"WebPush exception: {e}")
        return False
    except Exception as e:
        print(f"Error sending push notification: {e}")
        return False

