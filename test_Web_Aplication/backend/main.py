"""FastAPI application for User Registration with Push Integration."""
import logging
import sys
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

from database import init_database
from models import User, UserFingerprint, UserPushSubscription
from auth import verify_password, get_password_hash, create_access_token, get_current_user
from fingerprint import hash_fingerprint, validate_fingerprint, normalize_device_info
from push_integration import (
    get_or_create_application,
    subscribe_user_to_push,
    send_push_to_user,
    send_push_broadcast
)

# Configure logging to output to stdout/stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create main FastAPI app
app = FastAPI(
    title="User Registration Service",
    description="API for user registration with fingerprint tracking and Push notification integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class UserRegister(BaseModel):
    """User registration request model."""
    username: str
    email: EmailStr
    password: str
    fingerprint: str
    device_info: Optional[Dict] = None


class UserLogin(BaseModel):
    """User login request model."""
    username: str  # Can be username or email
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    email: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    username: str
    email: str
    created_at: datetime


class FingerprintUpdate(BaseModel):
    """Fingerprint update request model."""
    fingerprint: str
    device_info: Optional[Dict] = None


class PushSubscribeRequest(BaseModel):
    """Push subscription request model."""
    endpoint: str
    keys: Dict
    user_id: Optional[str] = None


class PushSendRequest(BaseModel):
    """Push notification send request model."""
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    data: Optional[Dict] = None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Initializing database...")
    await init_database([User, UserFingerprint, UserPushSubscription])
    
    # Ensure application exists in Push service
    try:
        application_id = await get_or_create_application()
        logger.info(f"Push service application ready: {application_id}")
    except Exception as e:
        logger.warning(f"Could not connect to Push service on startup: {e}")
        logger.warning("Push service integration will be available after service is ready")


@api_router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "User Registration Service API"}


@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        from motor.motor_asyncio import AsyncIOMotorClient
        from database import MONGODB_URI
        client = AsyncIOMotorClient(MONGODB_URI)
        await client.admin.command('ping')
        client.close()
        
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@api_router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """Register a new user with fingerprint."""
    try:
        # Validate fingerprint
        if not validate_fingerprint(user_data.fingerprint):
            raise HTTPException(status_code=400, detail="Invalid fingerprint format")
        
        # Check if username already exists
        existing_user = await User.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = await User.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        password_hash = get_password_hash(user_data.password)
        
        # Hash fingerprint
        fingerprint_hash = hash_fingerprint(user_data.fingerprint)
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        await user.insert()
        
        # Save fingerprint
        device_info = normalize_device_info(user_data.device_info)
        user_fingerprint = UserFingerprint(
            user_id=str(user.id),
            fingerprint_hash=fingerprint_hash,
            device_info=device_info,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await user_fingerprint.insert()
        
        logger.info(f"User registered: {user.username} ({user.email})")
        
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during registration: {str(e)}")


@api_router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    """User login endpoint."""
    try:
        # Find user by username or email
        user = await User.find_one({"username": login_data.username})
        if not user:
            user = await User.find_one({"email": login_data.username})
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username/email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username/email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=str(user.id),
            username=user.username,
            email=user.email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@api_router.get("/user/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at
    )


@api_router.post("/user/fingerprint")
async def update_fingerprint(
    fingerprint_data: FingerprintUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update or create user fingerprint."""
    try:
        # Validate fingerprint
        if not validate_fingerprint(fingerprint_data.fingerprint):
            raise HTTPException(status_code=400, detail="Invalid fingerprint format")
        
        # Hash fingerprint
        fingerprint_hash = hash_fingerprint(fingerprint_data.fingerprint)
        
        # Find existing fingerprint
        user_fingerprint = await UserFingerprint.find_one({"user_id": str(current_user.id)})
        
        if user_fingerprint:
            # Update existing
            user_fingerprint.fingerprint_hash = fingerprint_hash
            user_fingerprint.device_info = normalize_device_info(fingerprint_data.device_info)
            user_fingerprint.updated_at = datetime.utcnow()
            await user_fingerprint.save()
        else:
            # Create new
            device_info = normalize_device_info(fingerprint_data.device_info)
            user_fingerprint = UserFingerprint(
                user_id=str(current_user.id),
                fingerprint_hash=fingerprint_hash,
                device_info=device_info,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await user_fingerprint.insert()
        
        return {"success": True, "message": "Fingerprint updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating fingerprint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating fingerprint: {str(e)}")


@api_router.post("/push/subscribe")
async def subscribe_to_push(
    subscription_data: PushSubscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """Subscribe user to push notifications in Push service."""
    try:
        # Get or create application in Push service
        application_id = await get_or_create_application()
        
        # Subscribe to Push service
        result = await subscribe_user_to_push(
            user_id=str(current_user.id),
            subscription_data=subscription_data.dict(),
            application_id=application_id
        )
        
        if result.get("success"):
            # Save subscription link
            subscription_id = result.get("subscription_id")
            if subscription_id:
                # Check if link already exists
                existing_link = await UserPushSubscription.find_one({
                    "user_id": str(current_user.id)
                })
                
                if existing_link:
                    # Update existing
                    existing_link.push_subscription_id = subscription_id
                    existing_link.application_id = application_id
                    existing_link.endpoint = subscription_data.endpoint
                    await existing_link.save()
                else:
                    # Create new link
                    user_push_link = UserPushSubscription(
                        user_id=str(current_user.id),
                        push_subscription_id=subscription_id,
                        application_id=application_id,
                        endpoint=subscription_data.endpoint,
                        created_at=datetime.utcnow()
                    )
                    await user_push_link.insert()
        
        return result
        
    except Exception as e:
        logger.error(f"Error subscribing to push: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error subscribing to push: {str(e)}")


@api_router.post("/push/send")
async def send_push_notification(
    push_data: PushSendRequest,
    current_user: User = Depends(get_current_user)
):
    """Send push notification to current user (for testing)."""
    try:
        # Get application_id
        application_id = await get_or_create_application()
        
        # Send push notification
        result = await send_push_to_user(
            user_id=str(current_user.id),
            payload=push_data.dict(),
            application_id=application_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending push: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


@api_router.post("/push/broadcast")
async def send_broadcast_push(
    push_data: PushSendRequest,
    current_user: User = Depends(get_current_user)
):
    """Send broadcast push notification to all users of this application."""
    try:
        # Get application_id
        application_id = await get_or_create_application()
        
        # Send broadcast push
        result = await send_push_broadcast(
            payload=push_data.dict(),
            application_id=application_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending broadcast push: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending broadcast push: {str(e)}")


# Mount API router to the main app
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

