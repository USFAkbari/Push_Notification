"""FastAPI application for Web Push Notification service."""
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from database import init_database
from db_models import PushSubscription
from push_service import send_push_notification, get_vapid_public_key
from generate_vapid_keys import ensure_vapid_keys

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
    from db_models import PushSubscription
    await init_database([PushSubscription])


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

