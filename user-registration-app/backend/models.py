"""Database models for user registration and fingerprint storage."""
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr


class User(Document):
    """User model for registered users."""
    
    username: str = Field(..., unique=True)
    email: EmailStr = Field(..., unique=True)
    password_hash: str  # Hashed password using bcrypt
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "users"
        indexes = ["username", "email"]


class UserFingerprint(Document):
    """User fingerprint model for device identification."""
    
    user_id: str = Field(..., index=True)  # Reference to User.id
    fingerprint_hash: str = Field(..., index=True)  # Hashed fingerprint
    device_info: Optional[dict] = None  # Device information (browser, OS, etc.)
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "user_fingerprints"
        indexes = ["user_id", "fingerprint_hash"]


class UserPushSubscription(Document):
    """Link between User and Push Subscription in Push service."""
    
    user_id: str = Field(..., index=True)  # Reference to User.id
    push_subscription_id: str  # Reference to PushSubscription.id in Push service
    application_id: str  # Application ID in Push service
    endpoint: str  # Push subscription endpoint
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "user_push_subscriptions"
        indexes = ["user_id", "push_subscription_id", "application_id"]

