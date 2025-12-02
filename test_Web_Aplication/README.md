# User Registration App with Push Integration

A complete web application for user registration with fingerprint tracking and Push notification integration.

## Features

- User registration and authentication
- Device fingerprint tracking
- Push notification subscription
- Integration with existing Push service
- Users automatically linked to application in Push service

## Project Structure

```
user-registration-app/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── models.py       # Database models
│   ├── database.py     # MongoDB connection
│   ├── auth.py         # JWT authentication
│   ├── fingerprint.py   # Fingerprint utilities
│   ├── push_integration.py  # Push service integration
│   └── Dockerfile
├── frontend/           # Svelte frontend
│   ├── src/
│   │   ├── App.svelte
│   │   ├── Register.svelte
│   │   ├── Login.svelte
│   │   ├── Dashboard.svelte
│   │   └── services/
│   │       ├── api.js
│   │       └── fingerprint.js
│   └── Dockerfile
└── docker-compose.yml
```

## Prerequisites

- Docker and Docker Compose
- Access to MongoDB (via mongo_network)
- Access to Push service (via shamim_network)

## Environment Variables

### Backend

- `MONGODB_URI`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `PUSH_SERVICE_URL`: URL of Push service backend
- `PUSH_ADMIN_USERNAME`: Admin username for Push service
- `PUSH_ADMIN_PASSWORD`: Admin password for Push service
- `PUSH_APPLICATION_NAME`: Application name in Push service
- `JWT_SECRET_KEY`: Secret key for JWT tokens

### Frontend

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_PUSH_SERVICE_URL`: Push service API URL

## Quick Start

1. **Clone and navigate to project:**
   ```bash
   cd user-registration-app
   ```

2. **Create .env file (optional):**
   ```bash
   # Backend .env
   JWT_SECRET_KEY=your_secret_key_here
   ```

3. **Start services:**
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/api/docs

## Usage

1. **Register a new user:**
   - Go to http://localhost:3001
   - Click "Register"
   - Fill in username, email, and password
   - Device fingerprint is automatically captured and stored

2. **Login:**
   - Use your credentials to login
   - You'll be redirected to Dashboard

3. **Subscribe to Push Notifications:**
   - In Dashboard, click "Subscribe to Push Notifications"
   - Grant notification permission
   - Subscription is automatically linked to the application in Push service

4. **Send Test Push:**
   - Use the "Send Test Push Notification" form in Dashboard
   - Enter title and body
   - Click "Send Push Notification"

## API Endpoints

### Public Endpoints

- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `GET /api/health` - Health check

### Protected Endpoints (require authentication)

- `GET /api/user/me` - Get current user info
- `POST /api/user/fingerprint` - Update fingerprint
- `POST /api/push/subscribe` - Subscribe to push notifications
- `POST /api/push/send` - Send push notification to current user
- `POST /api/push/broadcast` - Send broadcast push notification

## Integration with Push Service

The application automatically:
1. Creates or retrieves an Application in Push service
2. Links all user subscriptions to this Application
3. Ensures all push notifications are sent through the Application context

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build
```

## Troubleshooting

### Push Notifications Not Working

If push notifications are not working, check the following:

#### 1. **Use localhost instead of 0.0.0.0**
   - **Problem**: Accessing the site via `0.0.0.0:3001` may not be recognized as a secure context
   - **Solution**: Use `localhost:3001` or `127.0.0.1:3001` instead
   - **Why**: Push notifications require HTTPS or localhost/127.0.0.1 for security

#### 2. **Don't use Incognito/Private Mode**
   - **Problem**: Push notifications are blocked in Incognito/Private browsing mode
   - **Solution**: Exit Incognito mode and use a regular browser window
   - **Why**: Service workers and push notifications are disabled in private browsing for privacy

#### 3. **Use HTTPS in Production**
   - **Problem**: Push notifications require a secure context
   - **Solution**: Deploy with HTTPS enabled
   - **Why**: Browsers require secure connections for push notifications

#### 4. **Browser Compatibility**
   - **Problem**: Older browsers may not support push notifications
   - **Solution**: Use a modern browser (Chrome, Firefox, Edge, Safari - latest versions)
   - **Why**: Push notifications require Service Workers, Push API, and Notification API

#### 5. **Check Browser Permissions**
   - **Problem**: Notification permission might be denied
   - **Solution**: 
     - Check browser settings for notification permissions
     - Reset permissions if needed
     - Allow notifications when prompted

#### Common Error Messages

- **"Push notifications are not supported in this browser"**
  - Check browser compatibility and version
  - Ensure you're not in Incognito mode
  - Verify you're using HTTPS or localhost

- **"Connection is not secure"**
  - Use `localhost:3001` instead of `0.0.0.0:3001`
  - Or enable HTTPS in production

- **"Not allowed in Incognito"**
  - Exit Incognito/Private browsing mode
  - Use a regular browser window

## Notes

- Users are automatically linked to the "User Registration App" application in Push service
- Fingerprints are hashed before storage
- JWT tokens expire after 24 hours
- Service worker is automatically registered for push notifications
- The application allows `0.0.0.0` for development, but `localhost` is recommended

