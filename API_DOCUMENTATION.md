# API Documentation - Push Notification Service

Complete API documentation for managing push notifications via REST API with curl examples.

## Table of Contents

1. [Authentication](#authentication)
2. [Public Endpoints](#public-endpoints)
3. [Admin Endpoints](#admin-endpoints)
4. [Push Notification Endpoints](#push-notification-endpoints)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Authentication

All push notification endpoints require admin authentication using JWT Bearer tokens.

### Step 1: Login and Get Token

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Step 2: Use Token in Requests

Save the token to a variable for easier use:

```bash
# Save token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Use in requests
curl -X POST "http://localhost:8000/push/single/user123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Token Expiration:** Tokens expire after 24 hours. Re-login to get a new token.

---

## Public Endpoints

These endpoints don't require authentication and are used by clients to subscribe.

### GET /vapid-public-key

Get the VAPID public key for client subscription.

```bash
curl -X GET "http://localhost:8000/vapid-public-key"
```

**Response:**
```json
{
  "publicKey": "BEl62iUYgUivxIkv69yViEuiBIa40HI..."
}
```

### POST /subscribe

Store a new push subscription (used by clients).

```bash
curl -X POST "http://localhost:8000/subscribe" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "https://fcm.googleapis.com/fcm/send/...",
    "keys": {
      "p256dh": "base64_encoded_key",
      "auth": "base64_encoded_auth"
    },
    "user_id": "optional_user_id"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Subscription stored"
}
```

### GET /health

Health check endpoint.

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "vapid_keys_configured": true
}
```

---

## Admin Endpoints

All admin endpoints require authentication. Include the JWT token in the Authorization header.

### POST /admin/login

Login and receive JWT token.

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect username or password

---

## Push Notification Endpoints

All push notification endpoints require admin authentication.

### POST /push/single/{user_id}

Send push notification to a specific user by user_id.

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/push/single/user123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello User",
    "body": "This is a test notification",
    "icon": "https://example.com/icon.png",
    "badge": "https://example.com/badge.png",
    "data": {
      "url": "https://example.com/page",
      "custom_field": "custom_value"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Push notification sent"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Subscription not found for user_id
- `500 Internal Server Error`: Failed to send notification

### POST /push/broadcast

Send push notification to all subscribed users.

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/push/broadcast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Announcement",
    "body": "This is a broadcast message to all users",
    "icon": "https://example.com/icon.png",
    "badge": "https://example.com/badge.png",
    "data": {
      "type": "announcement",
      "url": "https://example.com/announcement"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Broadcast push notifications sent",
  "success_count": 150,
  "failed_count": 2,
  "total": 152
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: No subscriptions found
- `500 Internal Server Error`: Error sending broadcast

### POST /admin/push/single/{user_id}

Alternative endpoint for sending to a single user (same as `/push/single/{user_id}`).

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/admin/push/single/user123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello",
    "body": "Test message"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Push notification sent",
  "success_count": 1,
  "failed_count": 0,
  "total": 1
}
```

### POST /admin/push/broadcast

Alternative endpoint for broadcasting (same as `/push/broadcast`).

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/admin/push/broadcast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Broadcast",
    "body": "Message to all users"
  }'
```

### POST /admin/push/application/{app_id}

Send push notification to all users of a specific application.

```bash
TOKEN="your_jwt_token_here"
APP_ID="application_id_here"

curl -X POST "http://localhost:8000/admin/push/application/$APP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "App Update",
    "body": "New version available",
    "icon": "https://example.com/icon.png"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Push notifications sent to application: My App",
  "success_count": 45,
  "failed_count": 1,
  "total": 46
}
```

### POST /admin/push/users

Send push notification to a list of users by user_ids.

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/admin/push/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": ["user1", "user2", "user3"],
    "payload": {
      "title": "Personalized Message",
      "body": "This is for specific users",
      "icon": "https://example.com/icon.png",
      "data": {
        "custom": "data"
      }
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Push notifications sent to 3 users",
  "success_count": 3,
  "failed_count": 0,
  "total": 3
}
```

---

## Application Management Endpoints

### POST /admin/applications

Create a new application.

```bash
TOKEN="your_jwt_token_here"

curl -X POST "http://localhost:8000/admin/applications" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Application",
    "store_fingerprint": "optional_fingerprint"
  }'
```

**Response:**
```json
{
  "id": "app_id_here",
  "name": "My Application",
  "secret": "32_character_secret_here",
  "store_fingerprint": "optional_fingerprint",
  "created_at": "2024-01-01T00:00:00"
}
```

**Important:** Save the `secret` immediately - it's only shown once!

### GET /admin/applications

List all applications.

```bash
TOKEN="your_jwt_token_here"

curl -X GET "http://localhost:8000/admin/applications" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
[
  {
    "id": "app_id",
    "name": "My Application",
    "store_fingerprint": "optional_fingerprint",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### GET /admin/applications/{app_id}

Get a single application by ID.

```bash
TOKEN="your_jwt_token_here"
APP_ID="app_id_here"

curl -X GET "http://localhost:8000/admin/applications/$APP_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### PUT /admin/applications/{app_id}

Update an application.

```bash
TOKEN="your_jwt_token_here"
APP_ID="app_id_here"

curl -X PUT "http://localhost:8000/admin/applications/$APP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "store_fingerprint": "new_fingerprint"
  }'
```

### POST /admin/applications/{app_id}/reset-secret

Reset application secret and get new secret.

```bash
TOKEN="your_jwt_token_here"
APP_ID="app_id_here"

curl -X POST "http://localhost:8000/admin/applications/$APP_ID/reset-secret" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": "app_id",
  "name": "My Application",
  "secret": "new_32_character_secret",
  "store_fingerprint": "optional_fingerprint",
  "created_at": "2024-01-01T00:00:00"
}
```

### DELETE /admin/applications/{app_id}

Delete an application. Cannot delete if users are linked to it.

```bash
TOKEN="your_jwt_token_here"
APP_ID="app_id_here"

curl -X DELETE "http://localhost:8000/admin/applications/$APP_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "Application My Application deleted successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Cannot delete application - users are linked to it
- `404 Not Found`: Application not found
- `401 Unauthorized`: Missing or invalid token

**Note:** Before deleting an application, ensure no users are linked to it. If users are linked, you'll receive an error message indicating how many users need to be removed first.

---

## User Management Endpoints

### GET /admin/users

List users with pagination and filtering.

```bash
TOKEN="your_jwt_token_here"

# Basic list
curl -X GET "http://localhost:8000/admin/users?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# With filters
curl -X GET "http://localhost:8000/admin/users?limit=10&offset=0&application_name=My%20App&user_id=user123" \
  -H "Authorization: Bearer $TOKEN"
```

**Query Parameters:**
- `limit` (default: 10, max: 100) - Number of users per page
- `offset` (default: 0) - Pagination offset
- `application_name` (optional) - Filter by application name
- `application_id` (optional) - Filter by application ID
- `user_id` (optional) - Search user ID (partial match)
- `created_from` (optional) - Filter from date (ISO format)
- `created_to` (optional) - Filter to date (ISO format)

**Response:**
```json
{
  "users": [
    {
      "id": "subscription_id",
      "user_id": "user123",
      "endpoint": "https://fcm.googleapis.com/...",
      "application_id": "app_id",
      "application_name": "My App",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 150,
  "limit": 10,
  "offset": 0
}
```

### GET /admin/users/{user_id}

Get detailed information for a specific user.

```bash
TOKEN="your_jwt_token_here"
USER_ID="subscription_id_here"

curl -X GET "http://localhost:8000/admin/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "id": "subscription_id",
  "user_id": "user123",
  "endpoint": "https://fcm.googleapis.com/...",
  "application_id": "app_id",
  "application_name": "My App",
  "created_at": "2024-01-01T00:00:00"
}
```

### DELETE /admin/users/{user_id}

Delete a user subscription.

```bash
TOKEN="your_jwt_token_here"
USER_ID="subscription_id_here"

curl -X DELETE "http://localhost:8000/admin/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "User subscription_id deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: User not found
- `401 Unauthorized`: Missing or invalid token
- `500 Internal Server Error`: Error deleting user

**Note:** This permanently deletes the user subscription. The user will need to subscribe again to receive notifications.

---

## Error Handling

### Authentication Errors

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**Solution:** Login again to get a new token.

### Not Found Errors

**404 Not Found:**
```json
{
  "detail": "Subscription not found"
}
```

**Solution:** Verify the user_id exists and has an active subscription.

### Validation Errors

**400 Bad Request:**
```json
{
  "detail": "Application with this name already exists"
}
```

**Solution:** Use a different name or update the existing application.

### Server Errors

**500 Internal Server Error:**
```json
{
  "detail": "Error sending push: [error message]"
}
```

**Solution:** Check server logs and verify VAPID keys are configured correctly.

---

## Examples

### Complete Workflow Example

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Send notification to single user
curl -X POST "http://localhost:8000/push/single/user123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello",
    "body": "This is a test notification"
  }'

# 3. Send broadcast to all users
curl -X POST "http://localhost:8000/push/broadcast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Announcement",
    "body": "Important message for everyone"
  }'

# 4. Send to multiple users
curl -X POST "http://localhost:8000/admin/push/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": ["user1", "user2", "user3"],
    "payload": {
      "title": "Group Message",
      "body": "Message for selected users"
    }
  }'
```

### Using Environment Variables

Create a script for easier use:

```bash
#!/bin/bash

# Configuration
API_BASE="http://localhost:8000"
USERNAME="admin"
PASSWORD="your_password"

# Login
TOKEN=$(curl -s -X POST "$API_BASE/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "Login failed!"
  exit 1
fi

echo "Logged in successfully"

# Send notification
USER_ID=$1
TITLE=$2
BODY=$3

curl -X POST "$API_BASE/push/single/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"$TITLE\",
    \"body\": \"$BODY\"
  }"
```

**Usage:**
```bash
chmod +x send_notification.sh
./send_notification.sh user123 "Hello" "This is a test"
```

### Production Example

For production, use HTTPS and store credentials securely:

```bash
# Production API base
API_BASE="https://api.yourdomain.com"

# Use environment variables for credentials
TOKEN=$(curl -s -X POST "$API_BASE/admin/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_USERNAME\",\"password\":\"$ADMIN_PASSWORD\"}" \
  | jq -r '.access_token')

# Send notification
curl -X POST "$API_BASE/push/broadcast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Production Announcement",
    "body": "Important update",
    "icon": "https://yourdomain.com/icon.png",
    "data": {
      "url": "https://yourdomain.com/update"
    }
  }'
```

---

## Security Best Practices

1. **Never commit tokens to version control**
2. **Use environment variables for credentials**
3. **Rotate tokens regularly** (tokens expire after 24 hours)
4. **Use HTTPS in production**
5. **Store application secrets securely**
6. **Limit admin user access**
7. **Monitor API usage and set rate limits**

---

## Troubleshooting

### Token Expired

**Error:** `401 Unauthorized: Invalid authentication credentials`

**Solution:** Login again to get a new token.

### User Not Found

**Error:** `404 Not Found: Subscription not found`

**Solution:** 
- Verify the user_id is correct
- Check if the user has subscribed
- Use `/admin/users` to list all users

### Connection Refused

**Error:** `Connection refused`

**Solution:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check if port 8000 is accessible
- Verify firewall settings

### VAPID Keys Not Configured

**Error:** `500 Internal Server Error: VAPID keys not configured`

**Solution:**
- Generate VAPID keys: `python backend/generate_vapid_keys.py`
- Add keys to `.env` file
- Restart backend service

---

## Support

For issues or questions:
- Check server logs: `docker-compose logs backend`
- Verify health: `curl http://localhost:8000/health`
- Review API responses for detailed error messages

