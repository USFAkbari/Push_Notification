"""FastAPI application for Web Push Notification service."""
import logging
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from database import init_database
from db_models import PushSubscription, Admin, Application
from push_service import send_push_notification, get_vapid_public_key
from generate_vapid_keys import ensure_vapid_keys
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_admin, verify_token
)
from app_secret import generate_application_secret, hash_application_secret

logger = logging.getLogger(__name__)

app = FastAPI(title="Web Push Notification Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class SubscriptionData(BaseModel):
    """Subscription data from client."""
    endpoint: str
    keys: Dict
    user_id: Optional[str] = None


class PushPayload(BaseModel):
    """Push notification payload."""
    title: str = "Test Notification"
    body: str = "This is a test push notification"
    icon: Optional[str] = None
    badge: Optional[str] = None
    data: Optional[Dict] = None


# Admin Pydantic models
class AdminLogin(BaseModel):
    """Admin login request model."""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response model."""
    access_token: str
    token_type: str = "bearer"


class ApplicationCreate(BaseModel):
    """Application creation request model."""
    name: str
    store_fingerprint: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Application response model."""
    id: str
    name: str
    store_fingerprint: Optional[str] = None
    created_at: datetime


class ApplicationCreateResponse(BaseModel):
    """Application creation response model."""
    id: str
    name: str
    secret: str  # Only returned on creation/reset
    store_fingerprint: Optional[str] = None
    created_at: datetime


class ApplicationUpdate(BaseModel):
    """Application update request model."""
    name: Optional[str] = None
    store_fingerprint: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""
    id: str
    user_id: Optional[str]
    endpoint: str
    application_id: Optional[str] = None
    application_name: Optional[str] = None
    created_at: datetime


class UserListResponse(BaseModel):
    """User list response model."""
    users: List[UserResponse]
    total: int
    limit: int
    offset: int


@app.on_event("startup")
async def startup_event():
    """Initialize database and ensure VAPID keys exist on startup."""
    # Ensure VAPID keys exist before initializing database
    logger.info("Checking VAPID keys...")
    public_key, private_key, was_generated = ensure_vapid_keys(
        write_to_file=True,
        silent=False
    )
    
    if not public_key or not private_key:
        logger.error("Failed to ensure VAPID keys are available. Push notifications may not work.")
    elif was_generated:
        logger.warning("VAPID keys were auto-generated. Please verify they are correct for production use.")
    else:
        logger.info("VAPID keys are configured and valid.")
    
    # Initialize database
    from db_models import PushSubscription, Admin, Application
    await init_database([PushSubscription, Admin, Application])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Web Push Notification Service"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        from motor.motor_asyncio import AsyncIOMotorClient
        from database import MONGODB_URI
        client = AsyncIOMotorClient(MONGODB_URI)
        await client.admin.command('ping')
        client.close()
        
        # Check VAPID keys
        public_key = get_vapid_public_key()
        has_vapid_keys = bool(public_key)
        
        return {
            "status": "healthy",
            "database": "connected",
            "vapid_keys_configured": has_vapid_keys
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/vapid-public-key")
async def get_vapid_public_key_endpoint():
    """Get VAPID public key for client subscription."""
    public_key = get_vapid_public_key()
    if not public_key:
        raise HTTPException(status_code=500, detail="VAPID keys not configured")
    return {"publicKey": public_key}


@app.post("/subscribe")
async def subscribe(subscription: SubscriptionData):
    """Store a new push subscription."""
    try:
        logger.info(f"Received subscription request for endpoint: {subscription.endpoint[:50]}...")
        logger.info(f"User ID: {subscription.user_id}")
        logger.info(f"Has keys: p256dh={bool(subscription.keys.get('p256dh'))}, auth={bool(subscription.keys.get('auth'))}")
        
        # Check if subscription already exists
        existing = await PushSubscription.find_one({"endpoint": subscription.endpoint})
        
        if existing:
            # Update existing subscription
            logger.info(f"Updating existing subscription for endpoint: {subscription.endpoint[:50]}...")
            existing.keys = subscription.keys
            existing.user_id = subscription.user_id
            await existing.save()
            logger.info(f"Subscription updated successfully for user_id: {subscription.user_id}")
            return {"success": True, "message": "Subscription updated"}
        
        # Create new subscription
        logger.info("Creating new subscription...")
        push_sub = PushSubscription(
            endpoint=subscription.endpoint,
            keys=subscription.keys,
            user_id=subscription.user_id,
            created_at=datetime.utcnow()
        )
        await push_sub.insert()
        logger.info(f"Subscription stored successfully for user_id: {subscription.user_id}")
        return {"success": True, "message": "Subscription stored"}
    except Exception as e:
        logger.error(f"Error storing subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error storing subscription: {str(e)}")


@app.post("/push/single/{user_id}")
async def push_single(user_id: str, payload: PushPayload):
    """Send push notification to a specific user."""
    try:
        # Find subscription by user_id
        subscription = await PushSubscription.find_one({"user_id": user_id})
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Prepare subscription info for pywebpush
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": subscription.keys
        }
        
        # Send push notification
        success = await send_push_notification(
            subscription_info=subscription_info,
            payload=payload.dict()
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send push notification")
        
        return {"success": True, "message": "Push notification sent"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


@app.post("/push/broadcast")
async def push_broadcast(payload: PushPayload):
    """Send push notification to all subscribed users."""
    try:
        # Get all subscriptions
        subscriptions = await PushSubscription.find_all().to_list()
        
        if not subscriptions:
            raise HTTPException(status_code=404, detail="No subscriptions found")
        
        success_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": subscription.keys
            }
            
            success = await send_push_notification(
                subscription_info=subscription_info,
                payload=payload.dict()
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        return {
            "success": True,
            "message": "Broadcast push notifications sent",
            "success_count": success_count,
            "failed_count": failed_count,
            "total": len(subscriptions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending broadcast: {str(e)}")


# ==================== Admin Endpoints ====================

@app.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint with JWT token generation."""
    try:
        # Find admin by username
        admin = await Admin.find_one({"username": login_data.username})
        
        if not admin:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, admin.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": admin.username})
        
        return AdminLoginResponse(access_token=access_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during admin login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@app.post("/admin/applications", response_model=ApplicationCreateResponse)
async def create_application(
    app_data: ApplicationCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """Create a new application with generated secret."""
    try:
        # Check if application name already exists
        existing = await Application.find_one({"name": app_data.name})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Application with this name already exists"
            )
        
        # Generate and hash application secret
        secret = generate_application_secret()
        secret_hash = hash_application_secret(secret)
        
        # Create application
        application = Application(
            name=app_data.name,
            secret_hash=secret_hash,
            store_fingerprint=app_data.store_fingerprint,
            created_at=datetime.utcnow()
        )
        await application.insert()
        
        return ApplicationCreateResponse(
            id=str(application.id),
            name=application.name,
            secret=secret,  # Return plain secret only on creation
            store_fingerprint=application.store_fingerprint,
            created_at=application.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")


@app.get("/admin/applications", response_model=List[ApplicationResponse])
async def list_applications(current_admin: dict = Depends(get_current_admin)):
    """List all applications."""
    try:
        applications = await Application.find_all().to_list()
        return [
            ApplicationResponse(
                id=str(app.id),
                name=app.name,
                store_fingerprint=app.store_fingerprint,
                created_at=app.created_at
            )
            for app in applications
        ]
    except Exception as e:
        logger.error(f"Error listing applications: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing applications: {str(e)}")


@app.get("/admin/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get a single application by ID."""
    try:
        application = await Application.get(app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return ApplicationResponse(
            id=str(application.id),
            name=application.name,
            store_fingerprint=application.store_fingerprint,
            created_at=application.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting application: {str(e)}")


@app.put("/admin/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    app_data: ApplicationUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update an application."""
    try:
        application = await Application.get(app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update fields if provided
        if app_data.name is not None:
            # Check if new name conflicts with existing application
            existing = await Application.find_one({"name": app_data.name})
            if existing and str(existing.id) != app_id:
                raise HTTPException(
                    status_code=400,
                    detail="Application with this name already exists"
                )
            application.name = app_data.name
        
        if app_data.store_fingerprint is not None:
            application.store_fingerprint = app_data.store_fingerprint
        
        await application.save()
        
        return ApplicationResponse(
            id=str(application.id),
            name=application.name,
            store_fingerprint=application.store_fingerprint,
            created_at=application.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")


@app.post("/admin/applications/{app_id}/reset-secret", response_model=ApplicationCreateResponse)
async def reset_application_secret(
    app_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Reset application secret and return new secret."""
    try:
        application = await Application.get(app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Generate new secret and hash
        secret = generate_application_secret()
        secret_hash = hash_application_secret(secret)
        
        # Update application
        application.secret_hash = secret_hash
        await application.save()
        
        return ApplicationCreateResponse(
            id=str(application.id),
            name=application.name,
            secret=secret,  # Return plain secret only on reset
            store_fingerprint=application.store_fingerprint,
            created_at=application.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting application secret: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error resetting secret: {str(e)}")


@app.get("/admin/users", response_model=UserListResponse)
async def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    application_name: Optional[str] = Query(None),
    current_admin: dict = Depends(get_current_admin)
):
    """List all users with pagination and optional filtering by application name."""
    try:
        # Build filter
        filter_dict = {}
        
        # Filter by application name if provided
        if application_name:
            application = await Application.find_one({"name": application_name})
            if not application:
                # Return empty result if application not found
                return UserListResponse(
                    users=[],
                    total=0,
                    limit=limit,
                    offset=offset
                )
            filter_dict["application_id"] = str(application.id)
        
        # Get total count
        total = await PushSubscription.find(filter_dict).count()
        
        # Get paginated subscriptions
        subscriptions = await PushSubscription.find(filter_dict).skip(offset).limit(limit).to_list()
        
        # Get application names for each subscription
        user_responses = []
        for sub in subscriptions:
            application_name_value = None
            if sub.application_id:
                app = await Application.get(sub.application_id)
                if app:
                    application_name_value = app.name
            
            user_responses.append(UserResponse(
                id=str(sub.id),
                user_id=sub.user_id,
                endpoint=sub.endpoint,
                application_id=sub.application_id,
                application_name=application_name_value,
                created_at=sub.created_at
            ))
        
        return UserListResponse(
            users=user_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")


@app.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get detailed information for a specific user."""
    try:
        subscription = await PushSubscription.get(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get application name if linked
        application_name = None
        if subscription.application_id:
            app = await Application.get(subscription.application_id)
            if app:
                application_name = app.name
        
        return UserResponse(
            id=str(subscription.id),
            user_id=subscription.user_id,
            endpoint=subscription.endpoint,
            application_id=subscription.application_id,
            application_name=application_name,
            created_at=subscription.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

