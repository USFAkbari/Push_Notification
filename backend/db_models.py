"""Database models for push subscription storage."""
from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import Field


class Admin(Document):
    """Admin user model for administrative access."""
    
    username: str = Field(..., unique=True)
    password_hash: str  # Hashed password using bcrypt
    is_super_admin: bool = False  # Super admin has access to all applications
    application_ids: List[str] = []  # List of application IDs this admin can access
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "admins"
        indexes = ["username"]


class Application(Document):
    """Application model for registered push notification applications."""
    
    name: str = Field(..., unique=True)  # Human-readable application name
    secret_hash: str  # Hashed 32-character application secret
    store_fingerprint: Optional[str] = None  # Unique fingerprint hash (package name hash, certificate hash, etc.)
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "applications"
        indexes = ["name", "store_fingerprint"]


class PushSubscription(Document):
    """Push subscription model for storing PWA push subscriptions."""
    
    endpoint: str
    keys: dict  # Contains p256dh and auth keys
    user_id: Optional[str] = None
    application_id: Optional[str] = None  # Link to Application
    created_at: datetime = datetime.utcnow()
    
    class Settings:
        name = "push_subscriptions"
        indexes = ["endpoint", "user_id", "application_id"]

