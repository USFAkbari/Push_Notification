"""Database models for push subscription storage."""
from datetime import datetime
from typing import Optional, List
from beanie import Document
<<<<<<< HEAD
from pydantic import Field, EmailStr
=======
from pydantic import Field
>>>>>>> 02675bc (After Deploy Shamim)


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

<<<<<<< HEAD

class User(Document):
    """User model from User Registration App - for unified access."""
    
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

=======
>>>>>>> 02675bc (After Deploy Shamim)
