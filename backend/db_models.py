"""Database models for push subscription storage."""
from datetime import datetime
from typing import Optional
from beanie import Document


class PushSubscription(Document):
    """Push subscription model for storing PWA push subscriptions."""
    
    endpoint: str
    keys: dict  # Contains p256dh and auth keys
    user_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "push_subscriptions"
        indexes = ["endpoint", "user_id"]

