"""FastAPI application for Web Push Notification service."""
import logging
from fastapi import FastAPI, HTTPException, Depends, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from database import init_database
from db_models import PushSubscription, Admin, Application
from push_service import send_push_notification, get_vapid_public_key
from generate_vapid_keys import ensure_vapid_keys
from auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_admin, get_current_admin_with_permissions, check_application_access, verify_token,
    verify_application_secret
)
from app_secret import generate_application_secret, hash_application_secret

logger = logging.getLogger(__name__)

# Create main FastAPI app with Swagger enabled
# Note: docs_url and redoc_url must be accessible, so we use /api-v1 prefix
app = FastAPI(
    title="Web Push Notification Service",
    description="API for managing web push notifications, subscriptions, and admin operations",
    version="1.0.0",
    docs_url="/api-v1/docs",
    redoc_url="/api-v1/redoc",
    openapi_url="/api-v1/openapi.json"
)

# Create API router with /api-v1 prefix
api_router = APIRouter(prefix="/api-v1")

# Custom OpenAPI schema configuration will be set after router is mounted

# Root endpoint without prefix for easy access
@app.get("/")
async def root_redirect():
    """Root endpoint that provides API information."""
    return JSONResponse({
        "message": "Web Push Notification Service",
        "version": "1.0.0",
        "docs": "/api-v1/docs",
        "redoc": "/api-v1/redoc",
        "api_base": "/api-v1"
    })

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
    app_name: Optional[str] = None  # Application name for auto-linking


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


class PushToUsersRequest(BaseModel):
    """Push notification request for list of users."""
    user_ids: List[str]
    payload: PushPayload


class UserCreate(BaseModel):
    """User creation request model."""
    user_id: str
    endpoint: str
    keys: Dict  # Contains p256dh and auth keys
    application_id: Optional[str] = None


class UserAssignRequest(BaseModel):
    """User assignment request model."""
    application_id: Optional[str] = None  # None to unassign


class AdminCreate(BaseModel):
    """Admin creation request model."""
    username: str
    password: str
    is_super_admin: bool = False
    application_ids: List[str] = []


class AdminUpdate(BaseModel):
    """Admin update request model."""
    password: Optional[str] = None
    is_super_admin: Optional[bool] = None
    application_ids: Optional[List[str]] = None


class AdminResponse(BaseModel):
    """Admin response model."""
    id: str
    username: str
    is_super_admin: bool
    application_ids: List[str]
    created_at: datetime


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    current_password: str
    new_password: str


class PushResponse(BaseModel):
    """Push notification response model."""
    success: bool
    message: str
    success_count: int = 0
    failed_count: int = 0
    total: int = 0


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
    
    # Check if any admin exists, if not create default admin
    admin_count = await Admin.find({}).count()
    if admin_count == 0:
        logger.info("No admin users found. Creating default admin user...")
        default_username = "admin"
        default_password = "admin"
        
        # Check if default admin already exists (by username)
        existing_admin = await Admin.find_one({"username": default_username})
        if not existing_admin:
            password_hash = get_password_hash(default_password)
            default_admin = Admin(
                username=default_username,
                password_hash=password_hash,
                is_super_admin=True,  # First admin is super admin
                application_ids=[]
            )
            await default_admin.insert()
            logger.info(f"Default admin user '{default_username}' created successfully as super admin.")
        else:
            logger.info(f"Default admin user '{default_username}' already exists.")
    else:
        logger.info(f"Found {admin_count} admin user(s) in database.")


@api_router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Web Push Notification Service"}


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


@api_router.get("/vapid-public-key")
async def get_vapid_public_key_endpoint():
    """Get VAPID public key for client subscription."""
    public_key = get_vapid_public_key()
    if not public_key:
        raise HTTPException(status_code=500, detail="VAPID keys not configured")
    return {"publicKey": public_key}


@api_router.post("/subscribe")
async def subscribe(subscription: SubscriptionData):
    """Store a new push subscription."""
    try:
        logger.info(f"Received subscription request for endpoint: {subscription.endpoint[:50]}...")
        logger.info(f"User ID: {subscription.user_id}")
        logger.info(f"App Name: {subscription.app_name}")
        logger.info(f"Has keys: p256dh={bool(subscription.keys.get('p256dh'))}, auth={bool(subscription.keys.get('auth'))}")
        
        # Find or create application if app_name is provided
        application_id = None
        if subscription.app_name:
            application = await Application.find_one({"name": subscription.app_name})
            if application:
                logger.info(f"Found existing application: {application.name} (ID: {application.id})")
                application_id = str(application.id)
            else:
                # Auto-create application if it doesn't exist
                logger.info(f"Creating new application: {subscription.app_name}")
                secret = generate_application_secret()
                secret_hash = hash_application_secret(secret)
                new_app = Application(
                    name=subscription.app_name,
                    secret_hash=secret_hash,
                    created_at=datetime.utcnow()
                )
                await new_app.insert()
                application_id = str(new_app.id)
                logger.info(f"Application created with ID: {application_id}")
        
        # Check if subscription already exists
        existing = await PushSubscription.find_one({"endpoint": subscription.endpoint})
        
        if existing:
            # Update existing subscription
            logger.info(f"Updating existing subscription for endpoint: {subscription.endpoint[:50]}...")
            existing.keys = subscription.keys
            existing.user_id = subscription.user_id
            if application_id:
                existing.application_id = application_id
            await existing.save()
            logger.info(f"Subscription updated successfully for user_id: {subscription.user_id}, application_id: {application_id}")
            return {"success": True, "message": "Subscription updated"}
        
        # Create new subscription
        logger.info("Creating new subscription...")
        push_sub = PushSubscription(
            endpoint=subscription.endpoint,
            keys=subscription.keys,
            user_id=subscription.user_id,
            application_id=application_id,
            created_at=datetime.utcnow()
        )
        await push_sub.insert()
        logger.info(f"Subscription stored successfully for user_id: {subscription.user_id}, application_id: {application_id}")
        return {"success": True, "message": "Subscription stored"}
    except Exception as e:
        logger.error(f"Error storing subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error storing subscription: {str(e)}")


@api_router.post("/push/single/{user_id}", response_model=PushResponse)
async def push_single(
    user_id: str,
    payload: PushPayload,
    application = Depends(verify_application_secret)
):
    """Send push notification to a specific user using X-Application-Secret authentication."""
    try:
        # Find subscription by user_id for this application
        subscription = await PushSubscription.find_one({
            "user_id": user_id,
            "application_id": str(application.id)
        })
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found for this user in your application")
        
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
            return PushResponse(
                success=False,
                message="Failed to send push notification",
                success_count=0,
                failed_count=1,
                total=1
            )
        
        return PushResponse(
            success=True,
            message="Push notification sent",
            success_count=1,
            failed_count=0,
            total=1
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


@api_router.post("/push/broadcast", response_model=PushResponse)
async def push_broadcast(
    payload: PushPayload,
    application = Depends(verify_application_secret)
):
    """Send push notification to all users of this application using X-Application-Secret authentication."""
    try:
        # Get all subscriptions for this application
        subscriptions = await PushSubscription.find({"application_id": str(application.id)}).to_list()
        
        if not subscriptions:
            raise HTTPException(status_code=404, detail="No subscriptions found for this application")
        
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
        
        return PushResponse(
            success=True,
            message="Broadcast push notifications sent",
            success_count=success_count,
            failed_count=failed_count,
            total=len(subscriptions)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending broadcast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending broadcast: {str(e)}")


@api_router.post("/push/users", response_model=PushResponse)
async def push_to_users(
    request: PushToUsersRequest,
    application = Depends(verify_application_secret)
):
    """Send push notification to multiple users using X-Application-Secret authentication."""
    try:
        if not request.user_ids:
            raise HTTPException(status_code=400, detail="user_ids list cannot be empty")
        
        # Find subscriptions for all user_ids in this application
        filter_dict = {
            "user_id": {"$in": request.user_ids},
            "application_id": str(application.id)
        }
        
        subscriptions = await PushSubscription.find(filter_dict).to_list()
        
        if not subscriptions:
            raise HTTPException(
                status_code=404,
                detail=f"No subscriptions found for provided user_ids in this application"
            )
        
        success_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": subscription.keys
            }
            
            success = await send_push_notification(
                subscription_info=subscription_info,
                payload=request.payload.dict()
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        return PushResponse(
            success=True,
            message=f"Push notifications sent to {success_count} users",
            success_count=success_count,
            failed_count=failed_count,
            total=len(request.user_ids)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push to users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


# ==================== Admin Endpoints ====================

@api_router.post("/admin/login", response_model=AdminLoginResponse)
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


@api_router.post("/admin/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Change current admin's password."""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_admin.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if not password_data.new_password or len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="New password must be at least 6 characters long"
            )
        
        # Update password
        current_admin.password_hash = get_password_hash(password_data.new_password)
        await current_admin.save()
        
        logger.info(f"Password changed for admin '{current_admin.username}'")
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")


@api_router.post("/admin/applications", response_model=ApplicationCreateResponse)
async def create_application(
    app_data: ApplicationCreate,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Create a new application with generated secret. All admins can create applications."""
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
        
        # Automatically add application to admin's application_ids if not super admin
        if not current_admin.is_super_admin:
            if str(application.id) not in current_admin.application_ids:
                current_admin.application_ids.append(str(application.id))
                await current_admin.save()
        
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


@api_router.get("/admin/applications", response_model=List[ApplicationResponse])
async def list_applications(current_admin = Depends(get_current_admin_with_permissions)):
    """List applications. Super admins see all, regular admins see only their assigned applications."""
    try:
        if current_admin.is_super_admin:
            # Super admin sees all applications
            applications = await Application.find_all().to_list()
        else:
            # Regular admin sees only assigned applications
            if not current_admin.application_ids:
                applications = []
            else:
                # Convert string IDs to ObjectId for query
                from bson import ObjectId
                object_ids = [ObjectId(app_id) for app_id in current_admin.application_ids]
                applications = await Application.find({"_id": {"$in": object_ids}}).to_list()
        
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


@api_router.get("/admin/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: str,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Get a single application by ID. Regular admins can only see their assigned applications."""
    try:
        # Check access to application
        await check_application_access(app_id, current_admin)
        
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


@api_router.put("/admin/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str,
    app_data: ApplicationUpdate,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Update an application. All admins can update applications they have access to."""
    try:
        # Check access to application
        await check_application_access(app_id, current_admin)
        
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


@api_router.post("/admin/applications/{app_id}/reset-secret", response_model=ApplicationCreateResponse)
async def reset_application_secret(
    app_id: str,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Reset application secret and return new secret. All admins can reset secrets for applications they have access to."""
    try:
        # Check access to application
        await check_application_access(app_id, current_admin)
        
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


@api_router.delete("/admin/applications/{app_id}")
async def delete_application(
    app_id: str,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Delete an application. Cannot delete if users are linked to it. All admins can delete applications they have access to."""
    try:
        # Check access to application
        await check_application_access(app_id, current_admin)
        
        application = await Application.get(app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Check if any users are linked to this application
        linked_users_count = await PushSubscription.find({"application_id": app_id}).count()
        
        if linked_users_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete application: {linked_users_count} user(s) are linked to this application. Please remove or reassign users first."
            )
        
        # Delete the application
        await application.delete()
        
        logger.info(f"Application {app_id} ({application.name}) deleted by admin {current_admin.username}")
        
        return {
            "success": True,
            "message": f"Application {application.name} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting application: {str(e)}")


@api_router.get("/admin/users", response_model=UserListResponse)
async def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    application_name: Optional[str] = Query(None),
    application_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    created_from: Optional[str] = Query(None),
    created_to: Optional[str] = Query(None),
    current_admin = Depends(get_current_admin_with_permissions)
):
    """List users with pagination and optional filtering. Regular admins only see users from their assigned applications."""
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
        
        # Filter by application_id if provided
        if application_id:
            filter_dict["application_id"] = application_id
            # Check if admin has access to this application
            if not current_admin.is_super_admin:
                if application_id not in current_admin.application_ids:
                    # Return empty result if no access
                    return UserListResponse(
                        users=[],
                        total=0,
                        limit=limit,
                        offset=offset
                    )
        
        # Filter by admin permissions (if not super admin)
        if not current_admin.is_super_admin:
            if current_admin.application_ids:
                # Only show users from allowed applications
                if "application_id" in filter_dict:
                    # Check if filtered application is in allowed list
                    if filter_dict["application_id"] not in current_admin.application_ids:
                        return UserListResponse(
                            users=[],
                            total=0,
                            limit=limit,
                            offset=offset
                        )
                else:
                    # Filter by allowed application IDs
                    filter_dict["application_id"] = {"$in": current_admin.application_ids}
            else:
                # Admin has no assigned applications, return empty
                return UserListResponse(
                    users=[],
                    total=0,
                    limit=limit,
                    offset=offset
                )
        
        # Filter by user_id (partial match using regex)
        if user_id:
            filter_dict["user_id"] = {"$regex": user_id, "$options": "i"}
        
        # Filter by created_from date
        if created_from:
            try:
                from_date = datetime.fromisoformat(created_from.replace('Z', '+00:00'))
                if "created_at" not in filter_dict:
                    filter_dict["created_at"] = {}
                filter_dict["created_at"]["$gte"] = from_date
            except ValueError:
                logger.warning(f"Invalid created_from date format: {created_from}")
        
        # Filter by created_to date
        if created_to:
            try:
                to_date = datetime.fromisoformat(created_to.replace('Z', '+00:00'))
                if "created_at" not in filter_dict:
                    filter_dict["created_at"] = {}
                filter_dict["created_at"]["$lte"] = to_date
            except ValueError:
                logger.warning(f"Invalid created_to date format: {created_to}")
        
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


@api_router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Get detailed information for a specific user. Regular admins can only see users from their assigned applications."""
    try:
        subscription = await PushSubscription.get(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if admin has access to this user's application
        if not current_admin.is_super_admin:
            if subscription.application_id:
                if subscription.application_id not in current_admin.application_ids:
                    raise HTTPException(
                        status_code=403,
                        detail="You don't have permission to access this user"
                    )
        
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


@api_router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Delete a user subscription. Regular admins can only delete users from their assigned applications."""
    try:
        subscription = await PushSubscription.get(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if admin has access to this user's application
        if not current_admin.is_super_admin:
            if subscription.application_id:
                if subscription.application_id not in current_admin.application_ids:
                    raise HTTPException(
                        status_code=403,
                        detail="You don't have permission to delete this user"
                    )
        
        # Delete the subscription
        await subscription.delete()
        
        logger.info(f"User {user_id} deleted by admin {current_admin.username}")
        
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


@api_router.get("/app/users", response_model=UserListResponse)
async def list_app_users(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: Optional[str] = Query(None),
    application = Depends(verify_application_secret)
):
    """
    List users for an application using X-Application-Secret authentication.
    This endpoint is simpler and designed for app-to-service communication.
    """
    try:
        # Build filter - only show users from this application
        filter_dict = {"application_id": str(application.id)}
        
        # Filter by user_id (partial match using regex)
        if user_id:
            filter_dict["user_id"] = {"$regex": user_id, "$options": "i"}
        
        # Get total count
        total = await PushSubscription.find(filter_dict).count()
        
        # Get paginated subscriptions
        subscriptions = await PushSubscription.find(filter_dict).skip(offset).limit(limit).to_list()
        
        # Build user responses
        user_responses = [
            UserResponse(
                id=str(sub.id),
                user_id=sub.user_id,
                endpoint=sub.endpoint,
                application_id=sub.application_id,
                application_name=application.name,
                created_at=sub.created_at
            )
            for sub in subscriptions
        ]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing app users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")


@api_router.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Create a new user subscription manually. Regular admins can only create users for their assigned applications."""
    try:
        # Validate application_id if provided
        if user_data.application_id:
            # Check if admin has access to this application
            await check_application_access(user_data.application_id, current_admin)
            
            application = await Application.get(user_data.application_id)
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
        
        # Check if subscription with same endpoint already exists
        existing = await PushSubscription.find_one({"endpoint": user_data.endpoint})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Subscription with this endpoint already exists"
            )
        
        # Create new subscription
        subscription = PushSubscription(
            endpoint=user_data.endpoint,
            keys=user_data.keys,
            user_id=user_data.user_id,
            application_id=user_data.application_id,
            created_at=datetime.utcnow()
        )
        await subscription.insert()
        
        # Get application name if linked
        application_name = None
        if subscription.application_id:
            app = await Application.get(subscription.application_id)
            if app:
                application_name = app.name
        
        logger.info(f"User {user_data.user_id} created by admin {current_admin.username}")
        
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
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@api_router.put("/admin/users/{user_id}/assign", response_model=UserResponse)
async def assign_user_to_application(
    user_id: str,
    assign_data: UserAssignRequest,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Assign or unassign a user to/from an application. Regular admins can only assign to their assigned applications."""
    try:
        subscription = await PushSubscription.get(user_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate application_id if provided (to assign)
        if assign_data.application_id:
            # Check if admin has access to this application
            await check_application_access(assign_data.application_id, current_admin)
            
            application = await Application.get(assign_data.application_id)
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            subscription.application_id = assign_data.application_id
        else:
            # Unassign if application_id is None
            subscription.application_id = None
        
        await subscription.save()
        
        # Get application name if linked
        application_name = None
        if subscription.application_id:
            app = await Application.get(subscription.application_id)
            if app:
                application_name = app.name
        
        logger.info(f"User {user_id} assigned to application {assign_data.application_id or 'none'} by admin {current_admin.username}")
        
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
        logger.error(f"Error assigning user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error assigning user: {str(e)}")


# ==================== Admin Push Notification Endpoints ====================

@api_router.post("/admin/push/single/{user_id}", response_model=PushResponse)
async def admin_push_single(
    user_id: str,
    payload: PushPayload,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Send push notification to a specific user (admin endpoint). Regular admins can only push to users from their assigned applications."""
    try:
        # Find subscription by user_id
        subscription = await PushSubscription.find_one({"user_id": user_id})
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Check if admin has access to this user's application
        if not current_admin.is_super_admin:
            if subscription.application_id:
                if subscription.application_id not in current_admin.application_ids:
                    raise HTTPException(
                        status_code=403,
                        detail="You don't have permission to send push to this user"
                    )
        
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
            return PushResponse(
                success=False,
                message="Failed to send push notification",
                success_count=0,
                failed_count=1,
                total=1
            )
        
        return PushResponse(
            success=True,
            message="Push notification sent",
            success_count=1,
            failed_count=0,
            total=1
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push to user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


@api_router.post("/admin/push/broadcast", response_model=PushResponse)
async def admin_push_broadcast(
    payload: PushPayload,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Send push notification to all subscribed users (admin endpoint). Regular admins only push to users from their assigned applications."""
    try:
        # Get subscriptions based on admin permissions
        if current_admin.is_super_admin:
            subscriptions = await PushSubscription.find({}).to_list()
        else:
            if not current_admin.application_ids:
                raise HTTPException(status_code=403, detail="You don't have permission to send broadcast push")
            subscriptions = await PushSubscription.find({"application_id": {"$in": current_admin.application_ids}}).to_list()
        
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
        
        return PushResponse(
            success=True,
            message="Broadcast push notifications sent",
            success_count=success_count,
            failed_count=failed_count,
            total=len(subscriptions)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending broadcast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending broadcast: {str(e)}")


@api_router.post("/admin/push/application/{app_id}", response_model=PushResponse)
async def admin_push_to_application(
    app_id: str,
    payload: PushPayload,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Send push notification to all users of a specific application. Regular admins can only push to their assigned applications."""
    try:
        # Check access to application
        await check_application_access(app_id, current_admin)
        
        # Verify application exists
        application = await Application.get(app_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get all subscriptions for this application
        subscriptions = await PushSubscription.find({"application_id": app_id}).to_list()
        
        if not subscriptions:
            raise HTTPException(
                status_code=404,
                detail=f"No subscriptions found for application: {application.name}"
            )
        
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
        
        return PushResponse(
            success=True,
            message=f"Push notifications sent to application: {application.name}",
            success_count=success_count,
            failed_count=failed_count,
            total=len(subscriptions)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push to application {app_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


@api_router.post("/admin/push/users", response_model=PushResponse)
async def admin_push_to_users(
    request: PushToUsersRequest,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Send push notification to a list of users by user_id. Regular admins can only push to users from their assigned applications."""
    try:
        if not request.user_ids:
            raise HTTPException(status_code=400, detail="user_ids list cannot be empty")
        
        # Find subscriptions for all user_ids
        filter_dict = {"user_id": {"$in": request.user_ids}}
        
        # Filter by admin permissions (if not super admin)
        if not current_admin.is_super_admin:
            if current_admin.application_ids:
                filter_dict["application_id"] = {"$in": current_admin.application_ids}
            else:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to send push to these users"
                )
        
        subscriptions = await PushSubscription.find(filter_dict).to_list()
        
        if not subscriptions:
            raise HTTPException(
                status_code=404,
                detail=f"No subscriptions found for provided user_ids"
            )
        
        # Filter subscriptions to only include those admin has access to
        if not current_admin.is_super_admin:
            subscriptions = [s for s in subscriptions if s.application_id and s.application_id in current_admin.application_ids]
        
        # Create a map of user_id to subscription for quick lookup
        subscription_map = {sub.user_id: sub for sub in subscriptions if sub.user_id}
        
        success_count = 0
        failed_count = 0
        not_found_count = 0
        
        for user_id in request.user_ids:
            subscription = subscription_map.get(user_id)
            
            if not subscription:
                not_found_count += 1
                continue
            
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": subscription.keys
            }
            
            success = await send_push_notification(
                subscription_info=subscription_info,
                payload=request.payload.dict()
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
        
        return PushResponse(
            success=True,
            message=f"Push notifications sent to {success_count} users",
            success_count=success_count,
            failed_count=failed_count,
            total=len(request.user_ids)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push to users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error sending push: {str(e)}")


# ==================== Admin Management Endpoints ====================

@api_router.post("/admin/admins", response_model=AdminResponse)
async def create_admin(
    admin_data: AdminCreate,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Create a new admin user. Only super admins can create other admins."""
    try:
        # Check if current admin is super admin
        if not current_admin.is_super_admin:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can create other admins"
            )
        
        # Check if username already exists
        existing = await Admin.find_one({"username": admin_data.username})
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Admin with this username already exists"
            )
        
        # Validate application IDs if provided
        if admin_data.application_ids:
            for app_id in admin_data.application_ids:
                application = await Application.get(app_id)
                if not application:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Application with ID {app_id} not found"
                    )
        
        # Create admin
        password_hash = get_password_hash(admin_data.password)
        admin = Admin(
            username=admin_data.username,
            password_hash=password_hash,
            is_super_admin=admin_data.is_super_admin,
            application_ids=admin_data.application_ids,
            created_at=datetime.utcnow()
        )
        await admin.insert()
        
        logger.info(f"Admin '{admin_data.username}' created by super admin '{current_admin.username}'")
        
        return AdminResponse(
            id=str(admin.id),
            username=admin.username,
            is_super_admin=admin.is_super_admin,
            application_ids=admin.application_ids,
            created_at=admin.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating admin: {str(e)}")


@api_router.get("/admin/admins", response_model=List[AdminResponse])
async def list_admins(current_admin = Depends(get_current_admin_with_permissions)):
    """List all admins. Only super admins can see all admins."""
    try:
        # Only super admins can list all admins
        if not current_admin.is_super_admin:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can list all admins"
            )
        
        admins = await Admin.find_all().to_list()
        return [
            AdminResponse(
                id=str(admin.id),
                username=admin.username,
                is_super_admin=admin.is_super_admin,
                application_ids=admin.application_ids,
                created_at=admin.created_at
            )
            for admin in admins
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing admins: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing admins: {str(e)}")


@api_router.put("/admin/admins/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: str,
    admin_data: AdminUpdate,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Update an admin. Only super admins can update other admins."""
    try:
        # Check if current admin is super admin
        if not current_admin.is_super_admin:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can update other admins"
            )
        
        # Get admin to update
        admin = await Admin.get(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Prevent self-demotion from super admin
        if str(admin.id) == str(current_admin.id) and admin_data.is_super_admin is False:
            raise HTTPException(
                status_code=400,
                detail="You cannot remove super admin status from yourself"
            )
        
        # Update password if provided
        if admin_data.password:
            admin.password_hash = get_password_hash(admin_data.password)
        
        # Update super admin status if provided
        if admin_data.is_super_admin is not None:
            admin.is_super_admin = admin_data.is_super_admin
        
        # Update application IDs if provided
        if admin_data.application_ids is not None:
            # Validate application IDs
            for app_id in admin_data.application_ids:
                application = await Application.get(app_id)
                if not application:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Application with ID {app_id} not found"
                    )
            admin.application_ids = admin_data.application_ids
        
        await admin.save()
        
        logger.info(f"Admin '{admin.username}' updated by super admin '{current_admin.username}'")
        
        return AdminResponse(
            id=str(admin.id),
            username=admin.username,
            is_super_admin=admin.is_super_admin,
            application_ids=admin.application_ids,
            created_at=admin.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating admin: {str(e)}")


@api_router.delete("/admin/admins/{admin_id}")
async def delete_admin(
    admin_id: str,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Delete an admin. Only super admins can delete other admins."""
    try:
        # Check if current admin is super admin
        if not current_admin.is_super_admin:
            raise HTTPException(
                status_code=403,
                detail="Only super admins can delete other admins"
            )
        
        # Get admin to delete
        admin = await Admin.get(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Prevent self-deletion
        if str(admin.id) == str(current_admin.id):
            raise HTTPException(
                status_code=400,
                detail="You cannot delete yourself"
            )
        
        # Delete admin
        await admin.delete()
        
        logger.info(f"Admin '{admin.username}' deleted by super admin '{current_admin.username}'")
        
        return {
            "success": True,
            "message": f"Admin {admin.username} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting admin: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting admin: {str(e)}")


@api_router.get("/admin/admins/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin = Depends(get_current_admin_with_permissions)):
    """Get current admin's information."""
    return AdminResponse(
        id=str(current_admin.id),
        username=current_admin.username,
        is_super_admin=current_admin.is_super_admin,
        application_ids=current_admin.application_ids,
        created_at=current_admin.created_at
    )


@api_router.post("/admin/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_admin = Depends(get_current_admin_with_permissions)
):
    """Change current admin's password."""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_admin.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if not password_data.new_password or len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="New password must be at least 6 characters long"
            )
        
        # Update password
        current_admin.password_hash = get_password_hash(password_data.new_password)
        await current_admin.save()
        
        logger.info(f"Password changed for admin '{current_admin.username}'")
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")


# Mount API router to the main app
app.include_router(api_router)

# Custom OpenAPI schema configuration - must be after router is mounted
def custom_openapi():
    """Custom OpenAPI schema with correct paths for ReDoc and Swagger."""
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Remove servers configuration - ReDoc will use the current server automatically
    # This is important: when ReDoc is at /api-v1/redoc, it will load /api-v1/openapi.json
    # and the paths in schema already include /api-v1 prefix from the router
    if "servers" in openapi_schema:
        del openapi_schema["servers"]
    
    # Ensure info section is complete
    if "info" not in openapi_schema:
        openapi_schema["info"] = {}
    openapi_schema["info"]["title"] = app.title
    openapi_schema["info"]["version"] = app.version
    openapi_schema["info"]["description"] = app.description
    
    # Log schema generation for debugging
    paths_count = len(openapi_schema.get('paths', {}))
    logger.info(f"OpenAPI schema generated with {paths_count} paths")
    
    # Debug: Print first few paths to verify they include /api-v1 prefix
    if paths_count > 0:
        sample_paths = list(openapi_schema.get('paths', {}).keys())[:5]
        logger.debug(f"Sample paths in schema: {sample_paths}")
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Override default OpenAPI function to use custom schema
# This must be done after router is mounted so all routes are included
app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

