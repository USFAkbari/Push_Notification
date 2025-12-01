"""Integration with Push service for managing subscriptions and sending notifications."""
import os
import asyncio
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Push service configuration
PUSH_SERVICE_URL = os.getenv("PUSH_SERVICE_URL", "http://shamim_push_back:8000")
PUSH_SERVICE_API_BASE = f"{PUSH_SERVICE_URL}/api-v1"
PUSH_ADMIN_USERNAME = os.getenv("PUSH_ADMIN_USERNAME", "admin")
PUSH_ADMIN_PASSWORD = os.getenv("PUSH_ADMIN_PASSWORD", "admin")
PUSH_APPLICATION_NAME = os.getenv("PUSH_APPLICATION_NAME", "User Registration App")

# Cache for application_id and admin token
_application_id_cache: Optional[str] = None
_admin_token_cache: Optional[str] = None


async def get_admin_token() -> str:
    """Get admin authentication token from Push service."""
    global _admin_token_cache
    
    if _admin_token_cache:
        return _admin_token_cache
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PUSH_SERVICE_API_BASE}/admin/login",
                json={
                    "username": PUSH_ADMIN_USERNAME,
                    "password": PUSH_ADMIN_PASSWORD
                }
            )
            response.raise_for_status()
            data = response.json()
            _admin_token_cache = data.get("access_token")
            if not _admin_token_cache:
                raise Exception("No access token in response")
            return _admin_token_cache
    except Exception as e:
        logger.error(f"Failed to get admin token: {e}")
        raise Exception(f"Failed to authenticate with Push service: {str(e)}")


async def get_or_create_application() -> str:
    """Get or create application in Push service and return application_id."""
    global _application_id_cache
    
    if _application_id_cache:
        return _application_id_cache
    
    try:
        token = await get_admin_token()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First, try to get existing application
            response = await client.get(
                f"{PUSH_SERVICE_API_BASE}/admin/applications",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            applications = response.json()
            
            # Check if application exists
            for app in applications:
                if app.get("name") == PUSH_APPLICATION_NAME:
                    _application_id_cache = app.get("id")
                    logger.info(f"Found existing application: {_application_id_cache}")
                    return _application_id_cache
            
            # Create new application if not found
            logger.info(f"Creating new application: {PUSH_APPLICATION_NAME}")
            response = await client.post(
                f"{PUSH_SERVICE_API_BASE}/admin/applications",
                headers={"Authorization": f"Bearer {token}"},
                json={"name": PUSH_APPLICATION_NAME}
            )
            response.raise_for_status()
            app_data = response.json()
            _application_id_cache = app_data.get("id")
            logger.info(f"Created application: {_application_id_cache}")
            return _application_id_cache
            
    except Exception as e:
        logger.error(f"Failed to get or create application: {e}")
        raise Exception(f"Failed to get or create application in Push service: {str(e)}")


async def subscribe_user_to_push(
    user_id: str,
    subscription_data: Dict[str, Any],
    application_id: Optional[str] = None
) -> Dict[str, Any]:
    """Subscribe user to push notifications in Push service."""
    try:
        if not application_id:
            application_id = await get_or_create_application()
        
        # Prepare subscription data with user_id
        push_subscription = {
            "endpoint": subscription_data["endpoint"],
            "keys": subscription_data["keys"],
            "user_id": user_id
        }
        
        # Subscribe to Push service
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PUSH_SERVICE_API_BASE}/subscribe",
                json=push_subscription
            )
            response.raise_for_status()
            result = response.json()
        
        # Assign subscription to application
        if result.get("success"):
            # Get the subscription from Push service to get its ID
            # We need to find it by user_id
            token = await get_admin_token()
            async with httpx.AsyncClient(timeout=10.0) as client:
            # Get user subscriptions - wait a bit for subscription to be saved
            await asyncio.sleep(0.5)
                
                # Get user subscriptions
                response = await client.get(
                    f"{PUSH_SERVICE_API_BASE}/admin/users",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"user_id": user_id, "limit": 10}
                )
                response.raise_for_status()
                users_data = response.json()
                
                # Find subscription by endpoint
                subscription_id = None
                if users_data.get("users"):
                    for user_sub in users_data["users"]:
                        if user_sub.get("endpoint") == subscription_data["endpoint"]:
                            subscription_id = user_sub["id"]
                            break
                
                if subscription_id:
                    # Assign to application
                    assign_response = await client.put(
                        f"{PUSH_SERVICE_API_BASE}/admin/users/{subscription_id}/assign",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"application_id": application_id}
                    )
                    assign_response.raise_for_status()
                    
                    return {
                        "success": True,
                        "subscription_id": subscription_id,
                        "application_id": application_id
                    }
                else:
                    # Subscription created but couldn't find it for assignment
                    # This is okay, it will be assigned later if needed
                    logger.warning(f"Subscription created but couldn't find it for assignment (user_id: {user_id})")
                    return {
                        "success": True,
                        "subscription_id": None,
                        "application_id": application_id,
                        "message": "Subscription created but assignment may need to be done manually"
                    }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to subscribe user to push: {e}")
        raise Exception(f"Failed to subscribe user to push service: {str(e)}")


async def send_push_to_user(
    user_id: str,
    payload: Dict[str, Any],
    application_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send push notification to a specific user via Push service."""
    try:
        if not application_id:
            application_id = await get_or_create_application()
        
        token = await get_admin_token()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PUSH_SERVICE_API_BASE}/push/single/{user_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        logger.error(f"Failed to send push to user: {e}")
        raise Exception(f"Failed to send push notification: {str(e)}")


async def send_push_broadcast(
    payload: Dict[str, Any],
    application_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send push notification to all users of this application."""
    try:
        if not application_id:
            application_id = await get_or_create_application()
        
        token = await get_admin_token()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{PUSH_SERVICE_API_BASE}/admin/push/application/{application_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        logger.error(f"Failed to send broadcast push: {e}")
        raise Exception(f"Failed to send broadcast push notification: {str(e)}")

