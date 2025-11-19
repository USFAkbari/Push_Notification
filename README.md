# Web Push Notification Application

A minimal, full-stack Web Push Notification application with FastAPI backend and Svelte PWA frontend. Supports single-client and broadcast (multi-client) push notifications using VAPID authentication.

## Quick Start

📖 **New to this project?** Start here: [QUICKSTART.md](QUICKSTART.md) - Step-by-step instructions to get up and running quickly.

## Prerequisites

### For Local Development:
- **Python 3.8+** - For FastAPI backend
- **Node.js 18+** - For Svelte frontend
- **MongoDB** - Database for storing push subscriptions
- **Modern Browser** - Chrome, Firefox, or Edge with Web Push support

### For Docker Deployment:
- **Docker 20.10+** - For containerization
- **Docker Compose 2.0+** - For orchestration

## Project Structure

```
Push/
├── backend/               # FastAPI application
│   ├── main.py           # FastAPI app with endpoints
│   ├── db_models.py      # Beanie Document models
│   ├── database.py       # MongoDB connection setup
│   ├── push_service.py   # VAPID push service
│   ├── generate_vapid_keys.py  # VAPID key generation script
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile        # Backend Docker image
│   └── .dockerignore     # Docker ignore rules
├── frontend/             # Svelte PWA application
│   ├── src/
│   │   ├── App.svelte    # Main Svelte component
│   │   └── main.js       # App initialization
│   ├── public/
│   │   ├── service-worker.js  # Service worker for push handling
│   │   └── manifest.json      # PWA manifest
│   ├── index.html        # HTML entry point
│   ├── package.json      # Node dependencies
│   ├── vite.config.js    # Vite configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   ├── postcss.config.js    # PostCSS configuration
│   ├── nginx.conf        # Nginx configuration for production
│   ├── Dockerfile        # Frontend Docker image (multi-stage)
│   └── .dockerignore     # Docker ignore rules
├── docker-compose.yml    # Docker Compose orchestration
├── .dockerignore         # Root Docker ignore rules
└── README.md             # This file
```

## Installation

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

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Generate VAPID keys:**
   ```bash
   python generate_vapid_keys.py
   ```
   
   Copy the generated keys to your `.env` file:
   ```env
   VAPID_PUBLIC_KEY=your_generated_public_key
   VAPID_PRIVATE_KEY=your_generated_private_key
   VAPID_EMAIL=mailto:your-email@example.com
   ```

6. **Configure MongoDB:**
   Ensure MongoDB is running and update `.env` if needed:
   ```env
   MONGODB_URI=mongodb://localhost:27017/push_db
   DATABASE_NAME=push_db
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables (optional):**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` if your backend is on a different URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

## Running the Application

### Start MongoDB

Ensure MongoDB is running on your system:
```bash
# Using systemd (Linux)
sudo systemctl start mongod

# Or using MongoDB directly
mongod
```

### Start Backend Server

1. **From backend directory:**
   ```bash
   cd backend
   source venv/bin/activate  # If using virtual environment
   uvicorn main:app --reload
   ```

   Backend will run on `http://localhost:8000`

2. **Verify backend is running:**
   Visit `http://localhost:8000` - You should see:
   ```json
   {"message": "Web Push Notification Service"}
   ```

### Start Frontend Development Server

1. **From frontend directory:**
   ```bash
   cd frontend
   npm run dev
   ```

   Frontend will run on `http://localhost:3000` (or next available port)

2. **Open in browser:**
   The app should automatically open in your default browser.

## Docker Deployment

### Prerequisites

Before deploying with Docker, ensure you have:
- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- VAPID keys generated (see Backend Setup section)

### Quick Start with Docker

#### Fast Deployment Script (Recommended)

The fastest way to deploy is using the provided deployment script:

```bash
# Quick deployment (build, start, and wait for services)
./deploy.sh

# Or with admin user creation
ADMIN_USERNAME=admin ADMIN_PASSWORD=yourpassword ./deploy.sh
```

**Available commands:**
- `./deploy.sh` or `./deploy.sh quick` - Quick deployment
- `./deploy.sh rebuild` - Rebuild and restart everything
- `./deploy.sh restart` - Restart services
- `./deploy.sh stop` - Stop services
- `./deploy.sh status` - Show service status
- `./deploy.sh logs` - View and follow logs
- `./deploy.sh admin <username> <password>` - Create admin user
- `./deploy.sh clean` - Remove all containers and volumes
- `./deploy.sh help` - Show all commands

The script automatically:
- Checks Docker and Docker Compose installation
- Verifies VAPID keys (auto-generates if missing)
- Builds and starts all containers
- Waits for services to be healthy
- Shows service status and URLs

#### Manual Docker Deployment

1. **Generate VAPID keys:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python generate_vapid_keys.py
   ```
   Copy the generated keys for the next step.

2. **Create environment file:**
   ```bash
   # From project root
   cat > .env << EOF
   VAPID_PUBLIC_KEY=your_vapid_public_key_here
   VAPID_PRIVATE_KEY=your_vapid_private_key_here
   VAPID_EMAIL=mailto:your-email@example.com
   EOF
   ```

3. **Build and start all services:**
   ```bash
   docker-compose up -d --build
   ```

   This will:
   - Build the FastAPI backend image
   - Build the Svelte frontend image (with Nginx)
   - Start MongoDB container
   - Start all services in the correct order

4. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

   You should see all three services (mongodb, backend, frontend) in "Up" status.

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MongoDB: localhost:27017

### Docker Services

#### MongoDB Service
- **Image:** `mongo:latest`
- **Port:** 27017 (exposed to host)
- **Volume:** Persistent data stored in `mongodb_data` volume
- **Health Check:** Monitors MongoDB connectivity

#### Backend Service
- **Image:** Multi-stage Python 3.11-slim build
- **Port:** 8000 (exposed to host)
- **Environment Variables:**
  - `MONGODB_URI`: Points to MongoDB service
  - `VAPID_PUBLIC_KEY`: From `.env` file
  - `VAPID_PRIVATE_KEY`: From `.env` file
  - `VAPID_EMAIL`: From `.env` file
- **Health Check:** Monitors API endpoint availability
- **Depends On:** MongoDB (waits for health check)

#### Frontend Service
- **Image:** Multi-stage build (Node 18 Alpine for build, Nginx Alpine for runtime)
- **Port:** 3000 (maps to Nginx port 80)
- **Features:**
  - Svelte assets built in builder stage
  - Served via Nginx with optimized configuration
  - Gzip compression enabled
  - Static asset caching
  - Service worker properly configured
- **Health Check:** Monitors Nginx health endpoint
- **Depends On:** Backend service

### Docker Commands

#### Start services:
```bash
docker-compose up -d
```

#### Stop services:
```bash
docker-compose down
```

#### Stop and remove volumes (⚠️ deletes MongoDB data):
```bash
docker-compose down -v
```

#### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

#### Rebuild services:
```bash
# Rebuild all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

#### Execute commands in containers:
```bash
# Backend container
docker-compose exec backend python generate_vapid_keys.py

# MongoDB shell
docker-compose exec mongodb mongosh

# Frontend container (if needed)
docker-compose exec frontend sh
```

### Docker Network

All services communicate over a Docker bridge network named `push-network`:
- Services can reach each other by service name (e.g., `mongodb`, `backend`)
- Backend connects to MongoDB using `mongodb://mongodb:27017/push_db`
- Frontend can communicate with backend via `http://backend:8000` (internal)
- External access uses exposed ports on `localhost`

### Environment Variables

Create a `.env` file in the project root with:

```env
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_EMAIL=mailto:your-email@example.com
```

These variables are used by `docker-compose.yml` to configure the backend service.

### Volume Management

MongoDB data is persisted in a Docker volume:
- **Volume name:** `mongodb_data`
- **Location:** Managed by Docker
- **Persistence:** Data survives container restarts
- **Backup:** Use `docker volume inspect mongodb_data` to find volume location

To backup MongoDB data:
```bash
docker-compose exec mongodb mongodump --out /data/backup
docker cp push-mongodb:/data/backup ./backup
```

### Production Considerations

For production deployment:

1. **Update CORS settings:**
   In `backend/main.py`, update:
   ```python
   allow_origins=["https://your-domain.com"]
   ```

2. **Use secrets management:**
   - Don't commit `.env` files
   - Use Docker secrets or environment variable injection
   - Store VAPID keys securely

3. **Configure Nginx for HTTPS:**
   - Add SSL certificates
   - Update `nginx.conf` with SSL configuration
   - Web Push requires HTTPS (except localhost)

4. **Set resource limits:**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 512M
   ```

5. **Enable logging:**
   - Configure log rotation
   - Set up log aggregation
   - Monitor container health

6. **Database backups:**
   - Set up automated MongoDB backups
   - Store backups in secure location
   - Test restore procedures

### Troubleshooting Docker Deployment

**Services won't start:**
- Check Docker daemon is running: `docker ps`
- Verify ports are not in use: `netstat -tuln | grep -E '27017|8000|3000'`
- Check logs: `docker-compose logs`

**Backend can't connect to MongoDB:**
- Verify MongoDB container is healthy: `docker-compose ps`
- Check MongoDB logs: `docker-compose logs mongodb`
- Ensure network connectivity: `docker-compose exec backend ping mongodb`

**Frontend can't reach backend:**
- Check backend is running: `curl http://localhost:8000`
- Verify CORS settings in `backend/main.py`
- Check browser console for errors

**Build failures:**
- Clear Docker cache: `docker system prune -a`
- Rebuild without cache: `docker-compose build --no-cache`
- Check Dockerfile syntax

**VAPID key errors:**
- Verify `.env` file exists in project root
- Check keys are correctly formatted (no quotes needed)
- Regenerate keys if needed

## Usage

### 1. Request Push Permission

1. Open the application in your browser
2. Click "Request Permission" button
3. Allow notifications when prompted by the browser

### 2. Subscribe to Push Notifications

1. Enter an optional User ID (for targeted pushes)
2. Click "Subscribe" button
3. Status should change to "Subscribed"

### 3. Send Test Push Notifications

#### Send to Single User:
1. Enter a User ID (must match the user_id used during subscription)
2. Enter notification title and body
3. Click "Send to User"

#### Send Broadcast to All Users:
1. Enter notification title and body
2. Click "Broadcast to All"

## API Endpoints

### `GET /vapid-public-key`
Returns the VAPID public key for client subscription.

**Response:**
```json
{
  "publicKey": "your_vapid_public_key"
}
```

### `POST /subscribe`
Stores a new push subscription.

**Request Body:**
```json
{
  "endpoint": "https://fcm.googleapis.com/...",
  "keys": {
    "p256dh": "key_value",
    "auth": "auth_value"
  },
  "user_id": "optional_user_id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Subscription stored"
}
```

### `POST /push/single/{user_id}`
Sends a push notification to a specific user.

**Request Body:**
```json
{
  "title": "Test Notification",
  "body": "This is a test push notification",
  "icon": "optional_icon_url",
  "badge": "optional_badge_url",
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

### `POST /push/broadcast`
Sends a push notification to all subscribed users.

**Request Body:**
```json
{
  "title": "Test Notification",
  "body": "This is a test push notification",
  "icon": "optional_icon_url",
  "badge": "optional_badge_url",
  "data": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Broadcast push notifications sent",
  "success_count": 5,
  "failed_count": 0,
  "total": 5
}
```

## Testing

### Test Push Notification Flow

1. **Open the application** in your browser
2. **Grant notification permission** and subscribe
3. **Note your User ID** (if provided during subscription)
4. **Send a test push** using the UI or API
5. **Verify notification** appears on your device

### Test with Multiple Browsers/Tabs

1. Open the application in multiple browser tabs or different browsers
2. Subscribe with different User IDs in each tab
3. Send single pushes to specific User IDs
4. Send broadcast pushes to test multi-client delivery

## Troubleshooting

### Backend Issues

**VAPID keys not configured:**
- Ensure VAPID keys are generated and added to `.env` file
- Verify `.env` file is in the backend directory
- Check that `python-dotenv` is installed

**MongoDB connection error:**
- Verify MongoDB is running: `mongosh` or `mongo`
- Check `MONGODB_URI` in `.env` file
- Ensure database name is correct

**Import errors:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version`

### Frontend Issues

**Service Worker not registering:**
- Check browser console for errors
- Ensure service worker file is in `public/` directory
- Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser supports service workers (Chrome, Firefox, Edge)

**Push notifications not working:**
- Verify notification permission is granted
- Check browser supports Web Push API
- Ensure HTTPS is used (or localhost for development)
- Check browser console for errors
- Verify VAPID public key is loaded correctly

**CORS errors:**
- Check backend CORS settings in `main.py`
- Ensure frontend and backend URLs are correct
- Verify `.env` files have correct API base URL

### Common Issues

**"Push notifications are not supported":**
- Use a modern browser (Chrome, Firefox, Edge)
- Ensure HTTPS is enabled (or localhost)
- Check browser settings allow notifications

**"Subscription not found":**
- Verify User ID matches during subscription and push
- Check MongoDB for stored subscriptions
- Ensure subscription endpoint is correct

**"Failed to send push notification":**
- Check VAPID keys are correct in `.env`
- Verify subscription keys are valid
- Check backend logs for detailed error messages

## Production Deployment

### Backend

1. Set proper CORS origins in `main.py`:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```

2. Use environment variables for all secrets
3. Enable HTTPS (required for Web Push)
4. Use production MongoDB instance
5. Set up proper logging and monitoring

### Frontend

1. Build for production:
   ```bash
   npm run build
   ```

2. Serve `dist/` directory with HTTPS
3. Update `VITE_API_BASE_URL` to production backend URL
4. Ensure service worker is properly cached
5. Set up proper PWA icons

### Security Considerations

- Never expose VAPID private key to client
- Use HTTPS in production (required for Web Push)
- Validate all subscription data
- Implement rate limiting for push endpoints
- Use secure MongoDB connections in production

## Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework
- **Beanie** - ODM for MongoDB
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **pywebpush** - Web Push library
- **NumPy** - Numerical computations

### Frontend
- **Svelte** - Frontend framework
- **DaisyUI** - UI component library
- **Tailwind CSS** - CSS framework
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, check:
- Browser console for frontend errors
- Backend server logs for API errors
- MongoDB logs for database issues
- Web Push API documentation

