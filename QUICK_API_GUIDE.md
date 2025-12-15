# Quick API Guide - Push Notification Service

Quick reference guide for sending push notifications via curl.

## Quick Start

### 1. Login and Get Token

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}' \
  | jq -r '.access_token')
```

### 2. Send to Single User

```bash
curl -X POST "http://localhost:8000/push/single/user123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hello",
    "body": "This is a test notification"
  }'
```

### 3. Send to All Users (Broadcast)

```bash
curl -X POST "http://localhost:8000/push/broadcast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Announcement",
    "body": "Message for everyone"
  }'
```

### 4. Send to Multiple Users

```bash
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

## One-Liner Scripts

### Send Notification Script

```bash
#!/bin/bash
# save as send_push.sh

API="http://localhost:8000"
USER="admin"
PASS="your_password"
TOKEN=$(curl -s -X POST "$API/admin/login" -H "Content-Type: application/json" -d "{\"username\":\"$USER\",\"password\":\"$PASS\"}" | jq -r '.access_token')

curl -X POST "$API/push/single/$1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$2\",\"body\":\"$3\"}"
```

**Usage:**
```bash
chmod +x send_push.sh
./send_push.sh user123 "Title" "Message body"
```

### Broadcast Script

```bash
#!/bin/bash
# save as broadcast.sh

API="http://localhost:8000"
USER="admin"
PASS="your_password"
TOKEN=$(curl -s -X POST "$API/admin/login" -H "Content-Type: application/json" -d "{\"username\":\"$USER\",\"password\":\"$PASS\"}" | jq -r '.access_token')

curl -X POST "$API/push/broadcast" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$1\",\"body\":\"$2\"}"
```

**Usage:**
```bash
chmod +x broadcast.sh
./broadcast.sh "Title" "Message body"
```

## Common Payload Options

### Basic Notification
```json
{
  "title": "Hello",
  "body": "This is a test"
}
```

### With Icon and Badge
```json
{
  "title": "Update Available",
  "body": "New version is ready",
  "icon": "https://example.com/icon.png",
  "badge": "https://example.com/badge.png"
}
```

### With Custom Data
```json
{
  "title": "New Message",
  "body": "You have a new message",
  "data": {
    "url": "https://example.com/message/123",
    "type": "message",
    "id": "123"
  }
}
```

## Endpoints Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/admin/login` | POST | No | Get JWT token |
| `/push/single/{user_id}` | POST | Yes | Send to one user |
| `/push/broadcast` | POST | Yes | Send to all users |
| `/admin/push/users` | POST | Yes | Send to multiple users |
| `/admin/push/application/{app_id}` | POST | Yes | Send to app users |
| `/admin/users` | GET | Yes | List users |
| `/admin/users/{user_id}` | DELETE | Yes | Delete user |
| `/admin/applications` | GET | Yes | List applications |
| `/admin/applications/{app_id}` | DELETE | Yes | Delete application |

## Error Codes

- `401` - Authentication required or token expired
- `404` - User/subscription not found
- `500` - Server error

## Delete Operations

### Delete User

```bash
TOKEN="your_jwt_token_here"
USER_ID="subscription_id_here"

curl -X DELETE "http://localhost:8000/admin/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Delete Application

```bash
TOKEN="your_jwt_token_here"
APP_ID="app_id_here"

curl -X DELETE "http://localhost:8000/admin/applications/$APP_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Note:** Cannot delete application if users are linked to it. Remove users first.

## Token Expiration

Tokens expire after 24 hours. Re-login to get a new token.

For complete documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

