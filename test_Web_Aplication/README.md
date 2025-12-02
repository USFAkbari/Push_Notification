# User Registration App with Push Integration

A complete web application for user registration with fingerprint tracking and push notification integration. Built with FastAPI backend and Svelte frontend, seamlessly integrated with the Push Notification service.

## 🎯 Overview

This application provides a complete user registration and authentication system with:
- User registration and login functionality
- Device fingerprint tracking for security
- Push notification subscription and management
- Automatic integration with Push Notification service
- Secure JWT-based authentication

## 📚 Quick Links

- **Backend API Docs**: Access interactive API documentation at `http://localhost:8001/api/docs`
- **Push Notification Service**: This app integrates with the main Push Notification service

## 🚀 Quick Start Summary

### Local Development
1. Install prerequisites (Python 3.8+, Node.js 18+, MongoDB)
2. Set up backend: Install dependencies, configure environment variables
3. Set up frontend: Install dependencies, configure API URL
4. Start MongoDB service
5. Start backend (`uvicorn main:app --reload`)
6. Start frontend (`npm run dev`)
7. Access frontend at `http://localhost:3001`

### Docker Deployment
1. Configure environment variables
2. Build and start containers with Docker
3. Access frontend at `http://localhost:3001` and backend at `http://localhost:8001`

---

<details>
<summary><h2>📋 Prerequisites</h2></summary>

### For Local Development:
- **Python 3.8+** - For FastAPI backend
- **Node.js 18+** - For Svelte frontend
- **MongoDB** - Database for storing users, fingerprints, and subscriptions
- **Modern Browser** - Chrome, Firefox, or Edge with Web Push support

### For Docker Deployment:
- **Docker 20.10+** - For containerization
- **Docker Compose 2.0+** - For orchestration (if using docker-compose)

### External Services:
- **MongoDB** - Accessible via network (mongo_network) or localhost
- **Push Notification Service** - Accessible via network (shamim_network) or configured URL

</details>

---

<details>
<summary><h2>📁 Project Structure</h2></summary>

```
test_Web_Aplication/
├── backend/                      # FastAPI backend application
│   ├── main.py                   # FastAPI app with API endpoints
│   ├── models.py                 # Beanie Document models (User, UserFingerprint, UserPushSubscription)
│   ├── database.py               # MongoDB connection setup
│   ├── auth.py                   # JWT authentication utilities
│   ├── fingerprint.py            # Device fingerprint utilities
│   ├── push_integration.py       # Push service integration logic
│   ├── requirements.txt          # Python dependencies
│   └── Dockerfile                # Backend Docker image
├── frontend/                     # Svelte frontend application
│   ├── src/
│   │   ├── App.svelte            # Main Svelte component (routing)
│   │   ├── Register.svelte       # User registration page
│   │   ├── Login.svelte          # User login page
│   │   ├── Dashboard.svelte      # User dashboard with push controls
│   │   ├── main.js               # App initialization
│   │   ├── app.css               # Global styles
│   │   └── services/
│   │       ├── api.js            # API client service
│   │       └── fingerprint.js    # Fingerprint capture service
│   ├── public/
│   │   ├── service-worker.js     # Service worker for push notifications
│   │   └── manifest.json         # PWA manifest
│   ├── index.html                # HTML entry point
│   ├── package.json              # Node dependencies
│   ├── vite.config.js            # Vite configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── postcss.config.js         # PostCSS configuration
│   ├── nginx.conf                # Nginx configuration for production
│   └── Dockerfile                # Frontend Docker image
└── README.md                     # This file
```

</details>

---

<details>
<summary><h2>⚙️ Environment Variables</h2></summary>

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/user_registration_db
DATABASE_NAME=user_registration_db

# Push Service Integration
PUSH_SERVICE_URL=http://localhost:8000
PUSH_ADMIN_USERNAME=admin
PUSH_ADMIN_PASSWORD=your_admin_password
PUSH_APPLICATION_NAME=User Registration App

# JWT Authentication
JWT_SECRET_KEY=your_secret_key_here_change_in_production
```

### Frontend Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8001

# Push Service URL (for VAPID key retrieval)
VITE_PUSH_SERVICE_URL=http://localhost:8000
```

### Environment Variables Explanation

#### Backend Variables:
- `MONGODB_URI`: MongoDB connection string
- `DATABASE_NAME`: Database name for storing user data
- `PUSH_SERVICE_URL`: URL of the Push Notification service backend
- `PUSH_ADMIN_USERNAME`: Admin username for Push service authentication
- `PUSH_ADMIN_PASSWORD`: Admin password for Push service authentication
- `PUSH_APPLICATION_NAME`: Application name in Push service (automatically created if doesn't exist)
- `JWT_SECRET_KEY`: Secret key for JWT token signing (use strong random string in production)

#### Frontend Variables:
- `VITE_API_BASE_URL`: Backend API base URL for API requests
- `VITE_PUSH_SERVICE_URL`: Push service URL for retrieving VAPID public key

</details>

---

<details>
<summary><h2>🔧 Installation & Setup</h2></summary>

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env  # If .env.example exists
   # Or create .env manually with required variables
   ```

5. **Configure environment variables:**
   Edit `.env` file and set all required variables (see Environment Variables section).

6. **Verify MongoDB connection:**
   Ensure MongoDB is running and accessible at the configured URI.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file (optional):**
   ```bash
   # Create .env file with frontend environment variables
   ```

4. **Configure environment variables:**
   Edit `.env` file if you need to customize API URLs (defaults work for local development).

</details>

---

<details>
<summary><h2>🚀 Running the Application</h2></summary>

### Start MongoDB

Ensure MongoDB is running on your system:

```bash
# Using systemd (Linux)
sudo systemctl start mongod

# Or using MongoDB directly
mongod

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Start Backend Server

1. **From backend directory:**
   ```bash
   cd backend
   source venv/bin/activate  # If using virtual environment
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

   Backend will run on `http://localhost:8001`

2. **Verify backend is running:**
   - Visit `http://localhost:8001/api/docs` - You should see interactive API documentation
   - Visit `http://localhost:8001/api/health` - Should return `{"status": "healthy"}`

### Start Frontend Development Server

1. **From frontend directory:**
   ```bash
   cd frontend
   npm run dev
   ```

   Frontend will run on `http://localhost:3001` (or next available port)

2. **Open in browser:**
   Navigate to `http://localhost:3001` in your browser.

### Access Points

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/api/docs
- **API ReDoc**: http://localhost:8001/api/redoc

</details>

---

<details>
<summary><h2>🐳 Docker Deployment</h2></summary>

### Build Backend Image

```bash
cd backend
docker build -t user-registration-backend .
```

### Build Frontend Image

```bash
cd frontend
docker build -t user-registration-frontend .
```

### Run Backend Container

```bash
docker run -d \
  --name user-registration-backend \
  -p 8001:8001 \
  --env-file backend/.env \
  --network mongo_network \
  --network shamim_network \
  user-registration-backend
```

### Run Frontend Container

```bash
docker run -d \
  --name user-registration-frontend \
  -p 3001:80 \
  --env-file frontend/.env \
  user-registration-frontend
```

### Docker Network Configuration

If using external networks for MongoDB and Push service:

```bash
# Connect backend to MongoDB network
docker network connect mongo_network user-registration-backend

# Connect backend to Push service network
docker network connect shamim_network user-registration-backend
```

### Docker Commands

#### View logs:
```bash
# Backend logs
docker logs -f user-registration-backend

# Frontend logs
docker logs -f user-registration-frontend
```

#### Stop containers:
```bash
docker stop user-registration-backend user-registration-frontend
```

#### Remove containers:
```bash
docker rm user-registration-backend user-registration-frontend
```

</details>

---

<details>
<summary><h2>💻 Usage</h2></summary>

### 1. Register a New User

1. Navigate to the application at `http://localhost:3001`
2. Click on "Register" button or link
3. Fill in the registration form:
   - Username (unique)
   - Email (unique)
   - Password
4. Device fingerprint is automatically captured and stored during registration
5. Click "Register" to complete registration

### 2. Login

1. Navigate to the login page
2. Enter your registered username/email and password
3. Click "Login"
4. Upon successful login, you'll be redirected to the Dashboard
5. A JWT token is stored for authentication

### 3. Subscribe to Push Notifications

1. In the Dashboard, find the "Push Notifications" section
2. Click "Subscribe to Push Notifications" button
3. Grant notification permission when prompted by the browser
4. Subscription is automatically:
   - Created in the Push service
   - Linked to your user account
   - Linked to the application in Push service
5. Status should change to "Subscribed"

### 4. Send Test Push Notification

1. In the Dashboard, find the "Send Test Push Notification" form
2. Enter notification details:
   - Title
   - Body message
3. Click "Send Push Notification"
4. The notification will be sent to your subscribed device

### 5. Broadcast Push Notification (if available)

1. Use the broadcast feature in Dashboard (if implemented)
2. Enter notification title and body
3. Notification will be sent to all subscribed users in the application

</details>

---

<details>
<summary><h2>🔌 API Endpoints</h2></summary>

### Public Endpoints

#### `POST /api/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "fingerprint": "device_fingerprint_hash"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "user_id_here"
}
```

#### `POST /api/login`
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user_id": "user_id_here"
}
```

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### Protected Endpoints (Require Authentication)

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

#### `GET /api/user/me`
Get current user information.

**Response:**
```json
{
  "user_id": "user_id_here",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

#### `POST /api/user/fingerprint`
Update user's device fingerprint.

**Request Body:**
```json
{
  "fingerprint": "new_fingerprint_hash",
  "device_info": {
    "browser": "Chrome",
    "os": "Linux"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Fingerprint updated"
}
```

#### `POST /api/push/subscribe`
Subscribe current user to push notifications.

**Request Body:**
```json
{
  "subscription": {
    "endpoint": "https://fcm.googleapis.com/...",
    "keys": {
      "p256dh": "key_value",
      "auth": "auth_value"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Subscribed to push notifications"
}
```

#### `POST /api/push/send`
Send push notification to current user.

**Request Body:**
```json
{
  "title": "Test Notification",
  "body": "This is a test message",
  "icon": "optional_icon_url",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Push notification sent"
}
```

#### `POST /api/push/broadcast`
Send broadcast push notification to all users in the application.

**Request Body:**
```json
{
  "title": "Broadcast Notification",
  "body": "This is a broadcast message",
  "icon": "optional_icon_url",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Broadcast push notification sent",
  "success_count": 10,
  "failed_count": 0,
  "total": 10
}
```

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8001/api/docs`
- **ReDoc**: `http://localhost:8001/api/redoc`

</details>

---

<details>
<summary><h2>🔗 Integration with Push Service</h2></summary>

### Automatic Application Management

The application automatically manages its integration with the Push Notification service:

1. **Application Creation/Retrieval:**
   - On first use, automatically creates an Application in the Push service
   - Application name is configured via `PUSH_APPLICATION_NAME` environment variable
   - Subsequent requests retrieve the existing Application

2. **User Subscription Linking:**
   - All user push subscriptions are automatically linked to the Application
   - Each user's subscription is associated with their user_id
   - Subscriptions are stored both locally and in Push service

3. **Push Notification Delivery:**
   - Single-user pushes are sent through the Application context
   - Broadcast pushes target all subscribers within the Application
   - All push operations use the Application's credentials

### Integration Flow

```
User Registration → User Login → Push Subscription
                                         ↓
                              Application Created/Retrieved
                                         ↓
                              Subscription Linked to Application
                                         ↓
                              Push Notifications via Application
```

### Configuration Requirements

Ensure the following are configured in backend environment variables:
- `PUSH_SERVICE_URL`: Must point to the Push service backend
- `PUSH_ADMIN_USERNAME`: Admin username with push permissions
- `PUSH_ADMIN_PASSWORD`: Admin password
- `PUSH_APPLICATION_NAME`: Unique name for this application in Push service

</details>

---

<details>
<summary><h2>🔒 Security Features</h2></summary>

### Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing (not stored in plain text)
- **Token Expiration**: JWT tokens expire after 24 hours
- **Protected Endpoints**: All user-specific endpoints require authentication

### Device Fingerprinting

- **Fingerprint Hashing**: Device fingerprints are hashed before storage
- **Privacy**: Raw device information is not stored
- **Security**: Prevents unauthorized access even if database is compromised
- **Validation**: Fingerprint validation ensures data integrity

### Data Protection

- **Email Uniqueness**: Email addresses are unique and validated
- **Username Uniqueness**: Usernames are unique identifiers
- **Secure Storage**: All sensitive data is properly hashed
- **HTTPS Recommended**: Use HTTPS in production for secure connections

</details>

---

<details>
<summary><h2>🧪 Testing</h2></summary>

### Test User Registration Flow

1. Open the application in your browser
2. Navigate to registration page
3. Fill in user details and submit
4. Verify user is created successfully
5. Check MongoDB for user record

### Test Authentication Flow

1. Register a new user
2. Logout (if logged in automatically)
3. Login with credentials
4. Verify JWT token is received
5. Access protected endpoints with token

### Test Push Notification Flow

1. Register and login to the application
2. Grant notification permission
3. Subscribe to push notifications
4. Verify subscription status in Dashboard
5. Send a test push notification
6. Verify notification appears on device

### Test Multiple Users

1. Register multiple users with different accounts
2. Each user subscribes to push notifications
3. Send individual pushes to specific users
4. Send broadcast pushes to all users
5. Verify correct delivery to each user

### Test Fingerprint Tracking

1. Register a user from one device/browser
2. Login from different device/browser
3. Verify fingerprint is updated
4. Check fingerprint records in database

</details>

---

<details>
<summary><h2>🔧 Troubleshooting</h2></summary>

### Backend Issues

**MongoDB connection error:**
- Verify MongoDB is running: `mongosh` or `mongo`
- Check `MONGODB_URI` in `.env` file
- Ensure database name is correct
- Check network connectivity if using remote MongoDB

**Push service integration error:**
- Verify Push service is running and accessible
- Check `PUSH_SERVICE_URL` in backend `.env`
- Verify admin credentials (`PUSH_ADMIN_USERNAME`, `PUSH_ADMIN_PASSWORD`)
- Check network connectivity if Push service is on different network
- View backend logs for detailed error messages

**JWT authentication errors:**
- Verify `JWT_SECRET_KEY` is set in backend `.env`
- Check token expiration (tokens expire after 24 hours)
- Ensure Authorization header format: `Bearer <token>`
- Verify token is being sent with requests

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (requires 3.8+)

### Frontend Issues

**API connection errors:**
- Check `VITE_API_BASE_URL` in frontend `.env`
- Verify backend is running on configured port
- Check browser console for CORS errors
- Verify backend CORS settings allow frontend origin

**Service Worker not registering:**
- Check browser console for errors
- Ensure service worker file is in `public/` directory
- Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser supports service workers (Chrome, Firefox, Edge)
- Don't use Incognito/Private mode (service workers disabled)

**Push notifications not working:**
- Verify notification permission is granted
- Check browser supports Web Push API
- Ensure using `localhost` or HTTPS (not `0.0.0.0`)
- Check browser console for errors
- Verify VAPID public key is loaded correctly
- Check `VITE_PUSH_SERVICE_URL` in frontend `.env`

**Fingerprint not capturing:**
- Check browser console for errors
- Verify FingerprintJS library is loaded
- Ensure browser supports required APIs
- Check network connectivity for fingerprint collection

### Common Issues

**"Push notifications are not supported in this browser":**
- Use a modern browser (Chrome, Firefox, Edge, Safari - latest versions)
- Ensure HTTPS is enabled (or localhost for development)
- Check browser settings allow notifications
- Don't use Incognito/Private browsing mode

**"Connection is not secure":**
- Use `localhost:3001` instead of `0.0.0.0:3001`
- Or enable HTTPS in production
- Web Push requires secure context (HTTPS or localhost)

**"Subscription not found":**
- Verify user is logged in
- Check user has subscribed to push notifications
- Verify subscription exists in database
- Check Push service integration

**"Authentication failed":**
- Check JWT token is valid and not expired
- Verify token is sent in Authorization header
- Ensure token format: `Bearer <token>`
- Try logging in again to get fresh token

**"Application not found in Push service":**
- Check Push service is running
- Verify `PUSH_APPLICATION_NAME` is configured
- Check admin credentials are correct
- View backend logs for creation errors

### Error Messages Guide

**"User already exists":**
- Username or email is already registered
- Try different username/email
- Check MongoDB for existing user

**"Invalid credentials":**
- Username/email or password is incorrect
- Check password is correct
- Verify user exists in database

**"Token expired":**
- JWT token has expired (24 hours)
- Login again to get new token
- Implement token refresh if needed

**"Push service unavailable":**
- Push service backend is not accessible
- Check `PUSH_SERVICE_URL` configuration
- Verify network connectivity
- Check Push service logs

</details>

---

<details>
<summary><h2>🚀 Production Deployment</h2></summary>

### Backend Production Considerations

1. **Environment Variables:**
   - Use secure secret management (Docker secrets, Kubernetes secrets, etc.)
   - Never commit `.env` files
   - Use strong `JWT_SECRET_KEY` (random 32+ character string)
   - Configure secure MongoDB connection string

2. **CORS Settings:**
   - Update CORS origins to production frontend domain:
     ```python
     allow_origins=["https://your-frontend-domain.com"]
     ```
   - Remove wildcard (`*`) in production

3. **HTTPS:**
   - Enable HTTPS for all connections
   - Use reverse proxy (Nginx, Traefik) with SSL certificates
   - Web Push requires HTTPS (except localhost)

4. **MongoDB:**
   - Use production MongoDB instance
   - Configure replica sets for high availability
   - Enable authentication and authorization
   - Set up regular backups

5. **Logging & Monitoring:**
   - Configure structured logging
   - Set up log aggregation
   - Monitor API performance and errors
   - Set up alerts for critical issues

6. **Security:**
   - Implement rate limiting
   - Use secure password policies
   - Enable request validation
   - Monitor for suspicious activity

### Frontend Production Considerations

1. **Build for Production:**
   ```bash
   cd frontend
   npm run build
   ```
   This creates optimized production build in `dist/` directory.

2. **Environment Variables:**
   - Set production API URLs in build-time variables
   - Use environment-specific configurations
   - Never expose sensitive keys in frontend

3. **Serve with HTTPS:**
   - Serve `dist/` directory with HTTPS
   - Configure SSL certificates
   - Use reverse proxy (Nginx) for serving static files

4. **Service Worker:**
   - Ensure service worker is properly cached
   - Test push notifications in production environment
   - Verify VAPID public key is correct

5. **Nginx Configuration:**
   - Use provided `nginx.conf` as base
   - Configure SSL/TLS
   - Set up proper caching headers
   - Configure compression (gzip)

6. **PWA Features:**
   - Set up proper PWA icons
   - Configure manifest.json
   - Test offline functionality
   - Verify installation prompts

### Docker Production Deployment

1. **Multi-stage Builds:**
   - Use multi-stage Docker builds for smaller images
   - Optimize layer caching
   - Minimize image size

2. **Health Checks:**
   - Implement health check endpoints
   - Configure Docker health checks
   - Set up container monitoring

3. **Resource Limits:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 512M
   ```

4. **Secrets Management:**
   - Use Docker secrets for sensitive data
   - Never hardcode credentials
   - Rotate secrets regularly

5. **Networking:**
   - Configure proper Docker networks
   - Use service discovery
   - Secure inter-service communication

</details>

---

<details>
<summary><h2>🛠️ Technologies Used</h2></summary>

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Beanie** - ODM (Object Document Mapper) for MongoDB
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation using Python type annotations
- **PyJWT** - JWT token generation and verification
- **bcrypt** - Password hashing
- **python-dotenv** - Environment variable management
- **httpx** - Async HTTP client for Push service integration

### Frontend
- **Svelte** - Component-based frontend framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Tailwind CSS component library
- **Axios** - HTTP client for API requests
- **FingerprintJS** - Device fingerprinting library
- **Service Workers API** - For push notification handling

### Database
- **MongoDB** - NoSQL document database

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Web server and reverse proxy (production)

</details>

---

<details>
<summary><h2>📝 Development Notes</h2></summary>

### Key Features

- **Automatic Application Linking:** Users are automatically linked to the "User Registration App" application in Push service
- **Fingerprint Security:** Fingerprints are hashed before storage for privacy and security
- **JWT Token Management:** Tokens expire after 24 hours for security
- **Service Worker Integration:** Service worker is automatically registered for push notifications
- **Localhost Recommendation:** The application works with `0.0.0.0` for development, but `localhost` is recommended for push notifications

### Code Structure

- **Backend:** Follows FastAPI best practices with separate modules for different concerns
- **Frontend:** Component-based architecture with service layer for API calls
- **Integration:** Clean separation between application logic and Push service integration

### Future Enhancements

Potential improvements for future versions:
- Token refresh mechanism
- Password reset functionality
- Email verification
- Multi-factor authentication
- User profile management
- Push notification preferences
- Notification history
- Admin dashboard

</details>

---

## 📄 License

This project is provided as-is for educational and development purposes.

## 📞 Support

For issues or questions:
- Check browser console for frontend errors
- Check backend server logs for API errors
- Check MongoDB logs for database issues
- Review API documentation at `/api/docs`
- Check Push service integration logs
