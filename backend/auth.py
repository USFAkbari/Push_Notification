"""Authentication utilities for admin access."""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
<<<<<<< HEAD
from fastapi import Depends, HTTPException, status
=======
from fastapi import Depends, HTTPException, status, Header
>>>>>>> 02675bc (After Deploy Shamim)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current authenticated admin from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username}


async def get_current_admin_with_permissions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated admin with full permissions from database."""
    from db_models import Admin
    
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get admin from database
    admin = await Admin.find_one({"username": username})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return admin


async def check_application_access(application_id: str, admin):
    """Check if admin has access to a specific application."""
    from fastapi import HTTPException, status
    
    # Super admin has access to all applications
    if admin.is_super_admin:
        return admin
    
    # Check if application_id is in admin's allowed applications
    if application_id not in admin.application_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this application"
        )
    
    return admin

<<<<<<< HEAD
=======

async def verify_application_secret(x_application_secret: Optional[str] = Header(None)):
    """
    Dependency to verify application secret and return the application.
    Uses X-Application-Secret header for authentication.
    """
    from db_models import Application
    from app_secret import verify_application_secret as verify_secret
    
    if not x_application_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Application-Secret header is required",
            headers={"WWW-Authenticate": "X-Application-Secret"},
        )
    
    # Find all applications and verify secret
    applications = await Application.find_all().to_list()
    
    for app in applications:
        if verify_secret(x_application_secret, app.secret_hash):
            return app
    
    # If no match found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid application secret",
        headers={"WWW-Authenticate": "X-Application-Secret"},
    )

>>>>>>> 02675bc (After Deploy Shamim)
