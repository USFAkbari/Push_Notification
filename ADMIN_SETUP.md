# Admin Portal Setup Guide

This document describes the admin portal implementation for the Push Notification System.

## Overview

The admin portal provides secure management of applications and users in the push notification system. It includes:

- Secure admin authentication with JWT tokens
- Application management (create, list, update, reset secrets)
- User management (list, filter, view details)
- 32-character secure application secret generation

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `python-jose[cryptography]` - JWT token handling
- `passlib[bcrypt]` - Password hashing
- `bcrypt` - Bcrypt implementation

### 2. Create Initial Admin User

Before accessing the admin portal, you need to create an admin user:

```bash
cd backend
python scripts/create_admin.py <username> <password>
```

Example:
```bash
python scripts/create_admin.py admin mySecurePassword123
```

**Note:** Password must be at least 8 characters long.

### 3. Start the Services

#### Using Docker Compose:
```bash
docker-compose up -d --build
```

#### Manual Start:
```bash
# Start MongoDB
mongod

# Start Backend
cd backend
uvicorn main:app --reload

# Start Frontend
cd frontend
npm run dev
```

### 4. Access Admin Portal

Navigate to: `http://localhost:3000/admin` (or your frontend URL)

Login with the credentials you created in step 2.

## Database Models

### Admin
- `username` (unique) - Admin username
- `password_hash` - Bcrypt hashed password
- `created_at` - Creation timestamp

### Application
- `name` (unique) - Human-readable application name
- `secret_hash` - Bcrypt hashed 32-character secret
- `store_fingerprint` (optional) - Application fingerprint hash
- `created_at` - Creation timestamp

### PushSubscription (Updated)
- `endpoint` - Push subscription endpoint
- `keys` - Encryption keys (p256dh, auth)
- `user_id` (optional) - User identifier
- `application_id` (optional) - Link to Application
- `created_at` - Creation timestamp

## API Endpoints

### Authentication

#### POST `/admin/login`
Login and receive JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Application Management

All application endpoints require authentication (Bearer token in Authorization header).

#### POST `/admin/applications`
Create a new application.

**Request:**
```json
{
  "name": "My App",
  "store_fingerprint": "optional_fingerprint_hash"
}
```

**Response:**
```json
{
  "id": "app_id",
  "name": "My App",
  "secret": "32_character_secret_here",
  "store_fingerprint": "optional_fingerprint_hash",
  "created_at": "2024-01-01T00:00:00"
}
```

**Note:** The `secret` is only returned on creation. Store it securely!

#### GET `/admin/applications`
List all applications.

**Response:**
```json
[
  {
    "id": "app_id",
    "name": "My App",
    "store_fingerprint": "optional_fingerprint_hash",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### GET `/admin/applications/{app_id}`
Get a single application by ID.

#### PUT `/admin/applications/{app_id}`
Update an application.

**Request:**
```json
{
  "name": "Updated Name",
  "store_fingerprint": "new_fingerprint"
}
```

#### POST `/admin/applications/{app_id}/reset-secret`
Reset application secret and get new secret.

**Response:**
```json
{
  "id": "app_id",
  "name": "My App",
  "secret": "new_32_character_secret",
  "store_fingerprint": "optional_fingerprint_hash",
  "created_at": "2024-01-01T00:00:00"
}
```

### User Management

All user endpoints require authentication.

#### GET `/admin/users`
List users with pagination and optional filtering.

**Query Parameters:**
- `limit` (default: 10, max: 100) - Number of users per page
- `offset` (default: 0) - Pagination offset
- `application_name` (optional) - Filter by application name

**Response:**
```json
{
  "users": [
    {
      "id": "user_id",
      "user_id": "optional_user_identifier",
      "endpoint": "push_endpoint_url",
      "application_id": "app_id",
      "application_name": "My App",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

#### GET `/admin/users/{user_id}`
Get detailed information for a specific user.

**Response:**
```json
{
  "id": "user_id",
  "user_id": "optional_user_identifier",
  "endpoint": "push_endpoint_url",
  "application_id": "app_id",
  "application_name": "My App",
  "created_at": "2024-01-01T00:00:00"
}
```

## Application Secret Generation

Application secrets are:
- Exactly 32 characters long
- Generated using cryptographic random functions (`secrets.token_urlsafe`)
- Hashed using bcrypt before storage
- Only returned in plain text on creation or reset

## Security Features

1. **Password Hashing**: Admin passwords are hashed using bcrypt
2. **JWT Tokens**: Secure token-based authentication with 24-hour expiration
3. **Secret Hashing**: Application secrets are hashed before storage
4. **Bearer Token Authentication**: All admin endpoints require valid JWT token

## Frontend Admin Interface

The admin interface is accessible at `/admin` route and includes:

1. **Login Page**: Secure login form
2. **Dashboard**: 
   - Application management section
   - User management section with filtering and pagination
   - User details modal

## Environment Variables

Optional environment variable for JWT secret:
- `JWT_SECRET_KEY` - Custom JWT secret key (defaults to auto-generated)

## Troubleshooting

### Cannot login
- Verify admin user was created: `python scripts/create_admin.py <username> <password>`
- Check backend logs for authentication errors
- Ensure password is correct

### Token expired
- Tokens expire after 24 hours
- Simply login again to get a new token

### Application secret not shown
- Secrets are only returned on creation or reset
- If you lose a secret, use the "Reset Secret" button to generate a new one

### Users not showing
- Check if users have subscribed via the main app
- Verify database connection
- Check application_id links are correct

## Next Steps

1. Create your first admin user
2. Create applications for your push notification clients
3. Store application secrets securely
4. Link user subscriptions to applications (update subscription endpoint to include application_id)

