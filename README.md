<<<<<<< HEAD
# Push Notification System

A comprehensive full-stack Web Push Notification system with two integrated applications:
1. **Push Notification Service** - Core push notification service with FastAPI backend and Svelte PWA frontend
2. **User Registration App** - User registration and authentication system with push notification integration

Both applications support single-client and broadcast (multi-client) push notifications using VAPID authentication.

## 📚 Quick Links

- 📖 **New to this project?** Start here: [QUICKSTART.md](QUICKSTART.md) - Step-by-step instructions to get up and running quickly.
- 🔧 **Want to use the API?** Check out:
  - [QUICK_API_GUIDE.md](QUICK_API_GUIDE.md) - Quick reference for curl commands
  - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API documentation with examples

**Important:** All push notification endpoints require admin authentication for security. See the API documentation for authentication details.

## 🎯 Quick Start Summary

### Docker Deployment (Recommended)

1. **Generate VAPID keys** (if not already generated)
2. **Create `.env` file** with VAPID keys and other configuration
3. **Start all services:**
   ```bash
   # Full version (with health checks, resource limits)
   docker compose up -d --build
   
   # Or simple version (minimal config, faster startup)
   docker compose -f docker-compose.simple.yml up -d --build
   ```
4. **Access the applications:**
   - Push Notification Frontend: http://localhost:3000
   - Push Notification Backend API: http://localhost:8000
   - User Registration Frontend: http://localhost:3001
   - User Registration Backend API: http://localhost:8001

### Local Development

#### Push Notification Service
1. Install prerequisites (Python 3.8+, Node.js 18+, MongoDB)
2. Set up backend: Install dependencies, generate VAPID keys, configure MongoDB
3. Set up frontend: Install dependencies, configure API URL
4. Start MongoDB, backend (`uvicorn main:app --reload`), and frontend (`npm run dev`)
5. Access frontend at `http://localhost:3000` and backend at `http://localhost:8000`

#### User Registration App
1. Install prerequisites (Python 3.8+, Node.js 18+, MongoDB)
2. Set up backend: Install dependencies, configure environment variables
3. Set up frontend: Install dependencies, configure API URL
4. Start MongoDB, backend, and frontend
5. Access frontend at `http://localhost:3001` and backend at `http://localhost:8001`

---

<details>
<summary><h2>📋 Prerequisites</h2></summary>

### For Local Development:
- **Python 3.8+** - For FastAPI backends
- **Node.js 18+** - For Svelte frontends
- **MongoDB 6.0+** - Database for storing data
- **Modern Browser** - Chrome, Firefox, or Edge with Web Push support

### For Docker Deployment:
- **Docker 24.0+** - For containerization (latest stable version)
- **Docker Compose v2.20+** - Built into Docker CLI (use `docker compose` command)

### System Requirements:
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Disk**: 10GB+ free space

</details>

---

<details>
<summary><h2>📁 Project Structure</h2></summary>

```
Push_Notification/
├── backend/                      # Push Notification Service - FastAPI backend
│   ├── main.py                   # FastAPI app with endpoints
│   ├── db_models.py              # Beanie Document models
│   ├── database.py               # MongoDB connection setup
│   ├── push_service.py           # VAPID push service
│   ├── generate_vapid_keys.py    # VAPID key generation script
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Backend Docker image
│   └── .dockerignore             # Docker ignore rules
├── frontend/                     # Push Notification Service - Svelte PWA
│   ├── src/
│   │   ├── App.svelte            # Main Svelte component
│   │   └── main.js               # App initialization
│   ├── public/
│   │   ├── service-worker.js     # Service worker for push handling
│   │   └── manifest.json         # PWA manifest
│   ├── index.html                # HTML entry point
│   ├── package.json              # Node dependencies
│   ├── vite.config.js            # Vite configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── nginx.conf                # Nginx configuration for production
│   ├── Dockerfile                # Frontend Docker image (multi-stage)
│   └── .dockerignore             # Docker ignore rules
├── test_Web_Aplication/          # User Registration App
│   ├── backend/                  # User Registration - FastAPI backend
│   │   ├── main.py               # FastAPI app with API endpoints
│   │   ├── models.py             # Beanie Document models
│   │   ├── database.py           # MongoDB connection setup
│   │   ├── auth.py               # JWT authentication utilities
│   │   ├── fingerprint.py        # Device fingerprint utilities
│   │   ├── push_integration.py   # Push service integration logic
│   │   ├── requirements.txt      # Python dependencies
│   │   └── Dockerfile            # Backend Docker image
│   ├── frontend/                 # User Registration - Svelte frontend
│   │   ├── src/
│   │   │   ├── App.svelte        # Main Svelte component (routing)
│   │   │   ├── Register.svelte   # User registration page
│   │   │   ├── Login.svelte      # User login page
│   │   │   ├── Dashboard.svelte  # User dashboard with push controls
│   │   │   └── services/
│   │   │       ├── api.js        # API client service
│   │   │       └── fingerprint.js # Fingerprint capture service
│   │   ├── public/
│   │   │   ├── service-worker.js # Service worker for push notifications
│   │   │   └── manifest.json     # PWA manifest
│   │   ├── package.json          # Node dependencies
│   │   ├── vite.config.js        # Vite configuration
│   │   ├── nginx.conf            # Nginx configuration for production
│   │   └── Dockerfile            # Frontend Docker image
│   └── README.md                 # User Registration App documentation
├── docker-compose.yml            # Docker Compose v2 orchestration (full version with health checks)
├── docker-compose.simple.yml     # Docker Compose v2 simple version (minimal config)
├── .dockerignore                 # Root Docker ignore rules
└── README.md                     # This file
```

</details>

---

<details>
<summary><h2>🐳 Docker Deployment (Docker Compose v2)</h2></summary>

This project uses **Docker Compose v2** syntax (no `version` field). The `docker compose` command is built into Docker CLI (Docker 20.10+).

### Available Docker Compose Files

The project provides two Docker Compose files:

1. **`docker-compose.yml`** (Full version) - Includes health checks, resource limits, and production-ready features
   - Health checks for all services
   - Resource limits (CPU and memory)
   - Service health conditions in dependencies
   - Recommended for production use

2. **`docker-compose.simple.yml`** (Simple version) - Minimal configuration without extra features
   - No health checks
   - No resource limits
   - Simple dependencies
   - Perfect for development and quick testing

**Use the simple version for:**
- Quick local development
- Testing and experimentation
- When you don't need health checks or resource limits

**Use the full version for:**
- Production deployments
- When you need health monitoring
- When you need resource constraints

### Prerequisites

Before deploying with Docker, ensure you have:
- **Docker 24.0+** installed and running
- **Docker Compose v2.20+** (included with Docker)
- **VAPID keys** generated (see Backend Setup section)


## 3. Start All Services

**Using Full Version (default):**

```bash
# Build and start all services in detached mode
docker compose up -d --build

# Or explicitly specify the file
docker compose -f docker-compose.yml up -d --build
```

**Using Simple Version:**

```bash
# Build and start all services using simple configuration
docker compose -f docker-compose.simple.yml up -d --build
```

**Common Commands:**

```bash
# View service status
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs for specific service
docker compose logs -f backend
docker compose logs -f user-registration-backend

# For simple version, use the same commands with -f flag
docker compose -f docker-compose.simple.yml ps
docker compose -f docker-compose.simple.yml logs -f
```

#### 4. Verify Services

All services should be running:

```bash
docker compose ps
```

You should see all five services in "Up" status:
- `push-notification-mongodb` - MongoDB database
- `push-notification-backend` - Push Notification backend
- `push-notification-frontend` - Push Notification frontend
- `user-registration-backend` - User Registration backend
- `user-registration-frontend` - User Registration frontend

#### 5. Access Applications

- **Push Notification Frontend**: http://localhost:3000
- **Push Notification Backend API**: http://localhost:8000
- **User Registration Frontend**: http://localhost:3001
- **User Registration Backend API**: http://localhost:8001
- **MongoDB**: localhost:27017

<details>
<summary><h3>Full vs Simple Docker Compose Files</h3></summary>

### Comparison

| Feature | Full Version | Simple Version |
|---------|-------------|----------------|
| **File Name** | `docker-compose.yml` | `docker-compose.simple.yml` |
| **Health Checks** | ✅ Included | ❌ Not included |
| **Resource Limits** | ✅ Included | ❌ Not included |
| **Service Health Conditions** | ✅ Included | ❌ Simple dependencies |
| **All Services** | ✅ All 5 services | ✅ All 5 services |
| **Networks & Volumes** | ✅ Configured | ✅ Configured |
| **Use Case** | Production | Development/Testing |

### When to Use Simple Version

The simple version is perfect when you:
- Need quick setup for local development
- Want faster startup (no health check delays)
- Don't need resource monitoring
- Are just testing or experimenting
- Have limited system resources

### When to Use Full Version

Use the full version when you:
- Deploy to production
- Need health monitoring
- Want resource constraints
- Need service health dependencies
- Want production-ready configuration

### Switching Between Versions

You can easily switch between versions:

```bash
# Stop current version
docker compose down

# Start with simple version
docker compose -f docker-compose.simple.yml up -d --build

# Or switch back to full version
docker compose -f docker-compose.yml up -d --build
```

Both versions use the same:
- Service names
- Ports
- Environment variables
- Networks and volumes

So you can switch between them without any issues.

</details>

<details>
<summary><h3>Docker Services Overview</h3></summary>

### MongoDB Service
- **Image**: `mongo:latest`
- **Container**: `push-notification-mongodb`
- **Port**: 27017 (exposed to host)
- **Volume**: Persistent data in `mongodb_data` volume
- **Network**: `push-notification-network`
- **Health Check**: MongoDB connectivity check
- **Resources**: 2GB memory limit, 1 CPU limit

### Push Notification Backend
- **Build**: Multi-stage Python 3.11-slim build
- **Container**: `push-notification-backend`
- **Port**: 8000 (exposed to host)
- **Depends On**: MongoDB (waits for health check)
- **Network**: `push-notification-network`
- **Health Check**: API endpoint availability
- **Resources**: 1GB memory limit, 1 CPU limit

### Push Notification Frontend
- **Build**: Multi-stage (Node 18 Alpine for build, Nginx Alpine for runtime)
- **Container**: `push-notification-frontend`
- **Port**: 3000 (maps to Nginx port 80)
- **Depends On**: Backend service
- **Network**: `push-notification-network`
- **Health Check**: Nginx health endpoint
- **Resources**: 512MB memory limit, 0.5 CPU limit

### User Registration Backend
- **Build**: Multi-stage Python build
- **Container**: `user-registration-backend`
- **Port**: 8001 (exposed to host)
- **Depends On**: MongoDB and Push Notification backend
- **Network**: `push-notification-network`
- **Health Check**: API endpoint availability
- **Resources**: 1GB memory limit, 1 CPU limit

### User Registration Frontend
- **Build**: Multi-stage (Node Alpine for build, Nginx Alpine for runtime)
- **Container**: `user-registration-frontend`
- **Port**: 3001 (maps to Nginx port 80)
- **Depends On**: User Registration backend
- **Network**: `push-notification-network`
- **Health Check**: Nginx health endpoint
- **Resources**: 512MB memory limit, 0.5 CPU limit

</details>

<details>
<summary><h3>Docker Compose v2 Commands Reference</h3></summary>

> **Note**: Docker Compose v2 uses `docker compose` (space, not hyphen) as the command. The old `docker-compose` command still works but is deprecated.

#### Start Services:
```bash
# Start all services in detached mode
docker compose up -d

# Start with build
docker compose up -d --build

# Start specific service
docker compose up -d backend
docker compose up -d user-registration-backend
```

#### Stop Services:
```bash
# Stop all services (keeps containers)
docker compose stop

# Stop and remove containers (keeps volumes)
docker compose down

# Stop and remove containers and volumes (⚠️ deletes MongoDB data)
docker compose down -v

# Remove all stopped containers
docker compose rm
```

#### View Logs:
```bash
# All services (follow mode)
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mongodb
docker compose logs -f user-registration-backend

# Last N lines
docker compose logs --tail=100 backend

# Since specific time
docker compose logs --since 10m backend
```

#### Rebuild Services:
```bash
# Rebuild all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build backend

# Rebuild without cache
docker compose build --no-cache backend
docker compose up -d --build backend
```

#### Service Management:
```bash
# View service status
docker compose ps

# View service configuration
docker compose config

# Validate compose file
docker compose config --quiet

# List services
docker compose ps --services

# Restart service
docker compose restart backend

# Scale service (if configured)
docker compose up -d --scale backend=2
```

#### Execute Commands:
```bash
# Execute command in container
docker compose exec backend python generate_vapid_keys.py

# Open shell in container
docker compose exec backend sh
docker compose exec mongodb mongosh

# Run one-off command
docker compose run --rm backend python -c "print('test')"
```

#### Volume Management:
```bash
# List volumes
docker compose volume ls

# Inspect volume
docker volume inspect push-notification-mongodb-data

# Backup MongoDB data
docker compose exec mongodb mongodump --out /data/backup
docker cp push-notification-mongodb:/data/backup ./backup

# Restore MongoDB data
docker cp ./backup push-notification-mongodb:/data/backup
docker compose exec mongodb mongorestore /data/backup
```

#### Network Management:
```bash
# List networks
docker compose network ls

# Inspect network
docker network inspect push-notification-network

# Connect to network from external container
docker network connect push-notification-network my-container
```

</details>

<details>
<summary><h3>Docker Compose v2 Features</h3></summary>

### Modern Syntax (No Version Field)

Docker Compose v2 doesn't require a `version` field. The file uses the latest compose specification:

```yaml
services:
  backend:
    image: python:3.11-slim
    # ... configuration
```

### Health Checks with Conditions

Services wait for dependencies to be healthy:

```yaml
depends_on:
  mongodb:
    condition: service_healthy
```

### Resource Limits

Resource constraints are configured per service:

```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.25'
      memory: 512M
```

### Named Networks and Volumes

Explicit network and volume naming:

```yaml
networks:
  app-network:
    driver: bridge
    name: push-notification-network

volumes:
  mongodb_data:
    driver: local
    name: push-notification-mongodb-data
```

</details>

<details>
<summary><h3>Environment Variables</h3></summary>

### Push Notification Service

Create `.env` file in project root:

```env
# VAPID Keys for Push Notification Service
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_EMAIL=mailto:your-email@example.com
```

### User Registration App

Add to the same `.env` file:

```env
# User Registration App Configuration
PUSH_ADMIN_USERNAME=admin
PUSH_ADMIN_PASSWORD=your_admin_password
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### Environment Variable Usage

Docker Compose automatically loads `.env` file from project root:

```yaml
environment:
  - VAPID_PUBLIC_KEY=${VAPID_PUBLIC_KEY:-}
  - VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY:-}
```

The `${VARIABLE:-default}` syntax provides default values if variable is not set.

</details>

<details>
<summary><h3>Troubleshooting Docker Deployment</h3></summary>

**Services won't start:**
- Check Docker daemon: `docker info`
- Verify ports not in use: `netstat -tuln | grep -E '27017|8000|3000|8001|3001'`
- Check logs: `docker compose logs`

**Backend can't connect to MongoDB:**
- Verify MongoDB is healthy: `docker compose ps`
- Check MongoDB logs: `docker compose logs mongodb`
- Test connectivity: `docker compose exec backend ping mongodb`

**Frontend can't reach backend:**
- Check backend is running: `curl http://localhost:8000`
- Verify network connectivity: `docker compose exec frontend ping backend`
- Check browser console for CORS errors

**Build failures:**
- Clear Docker cache: `docker builder prune -a`
- Rebuild without cache: `docker compose build --no-cache`
- Check Dockerfile syntax and paths

**VAPID key errors:**
- Verify `.env` file exists in project root
- Check keys are correctly formatted (no quotes)
- Regenerate keys if needed

**Port conflicts:**
- Check what's using the port: `lsof -i :8000`
- Stop conflicting services
- Change ports in `docker-compose.yml` or `docker-compose.simple.yml` if needed

**Choosing between full and simple version:**
- Use `docker-compose.simple.yml` for quick testing and development
- Use `docker-compose.yml` for production or when you need monitoring
- Both files are functionally equivalent, simple version just lacks extra features

**Volume permissions:**
- Check volume permissions: `docker volume inspect push-notification-mongodb-data`
- Fix permissions if needed: `sudo chown -R $(id -u):$(id -g) /var/lib/docker/volumes/`

</details>

</details>

---

<details>
<summary><h2>🔧 Application 1: Push Notification Service</h2></summary>

A minimal, full-stack Web Push Notification application with FastAPI backend and Svelte PWA frontend.

### Features

- Single-client push notifications
- Broadcast (multi-client) push notifications
- VAPID authentication
- Service worker integration
- PWA support
- Admin authentication for push endpoints

### Quick Start
=======
# Web Push Notification Application

A minimal, full-stack Web Push Notification application with FastAPI backend and Svelte PWA frontend. Supports single-client and broadcast (multi-client) push notifications using VAPID authentication.

## Quick Start

📖 **New to this project?** Start here: [QUICKSTART.md](QUICKSTART.md) - Step-by-step instructions to get up and running quickly.

## API Documentation

🔧 **Want to use the API?** Check out:
- [QUICK_API_GUIDE.md](QUICK_API_GUIDE.md) - Quick reference for curl commands
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API documentation with examples

**Important:** All push notification endpoints now require admin authentication for security. See the API documentation for authentication details.

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
>>>>>>> 02675bc (After Deploy Shamim)

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

<<<<<<< HEAD
2. **Set up backend:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python generate_vapid_keys.py
   ```

3. **Configure environment variables:**
   Create `backend/.env`:
   ```env
   VAPID_PUBLIC_KEY=your_generated_public_key
   VAPID_PRIVATE_KEY=your_generated_private_key
   VAPID_EMAIL=mailto:your-email@example.com
   MONGODB_URI=mongodb://localhost:27017/push_db
   DATABASE_NAME=push_db
   ```

4. **Start backend:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Set up and start frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

6. **Access application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### API Endpoints

- `GET /vapid-public-key` - Get VAPID public key
- `POST /subscribe` - Subscribe to push notifications
- `POST /push/single/{user_id}` - Send push to single user (requires auth)
- `POST /push/broadcast` - Send broadcast push (requires auth)

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API documentation.

</details>

---

<details>
<summary><h2>👥 Application 2: User Registration App</h2></summary>

A complete web application for user registration with fingerprint tracking and push notification integration.

### Features

- User registration and authentication
- Device fingerprint tracking
- Push notification subscription
- Automatic integration with Push Notification service
- JWT-based authentication
- Secure password hashing

### Quick Start

1. **Navigate to backend directory:**
   ```bash
   cd test_Web_Aplication/backend
   ```

2. **Set up backend:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create `test_Web_Aplication/backend/.env`:
   ```env
   MONGODB_URI=mongodb://localhost:27017/user_registration_db
   DATABASE_NAME=user_registration_db
   PUSH_SERVICE_URL=http://localhost:8000
   PUSH_ADMIN_USERNAME=admin
   PUSH_ADMIN_PASSWORD=your_admin_password
   PUSH_APPLICATION_NAME=User Registration App
   JWT_SECRET_KEY=your_secret_key_here
   ```

4. **Start backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

5. **Set up and start frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

6. **Access application:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/api/docs

### API Endpoints

#### Public Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `GET /api/health` - Health check

#### Protected Endpoints (require JWT token)
- `GET /api/user/me` - Get current user info
- `POST /api/user/fingerprint` - Update fingerprint
- `POST /api/push/subscribe` - Subscribe to push notifications
- `POST /api/push/send` - Send push to current user
- `POST /api/push/broadcast` - Send broadcast push

See [test_Web_Aplication/README.md](test_Web_Aplication/README.md) for detailed documentation.

</details>

---

<details>
<summary><h2>⚙️ Installation & Setup (Local Development)</h2></summary>

### Push Notification Service

<details>
<summary><h3>Backend Setup</h3></summary>

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
=======
2. **Create virtual environment (recommended):**
>>>>>>> 02675bc (After Deploy Shamim)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

<<<<<<< HEAD
4. **Generate VAPID keys:**
=======
4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Generate VAPID keys:**
>>>>>>> 02675bc (After Deploy Shamim)
   ```bash
   python generate_vapid_keys.py
   ```
   
<<<<<<< HEAD
   Copy the generated keys to `.env` file:
=======
   Copy the generated keys to your `.env` file:
>>>>>>> 02675bc (After Deploy Shamim)
   ```env
   VAPID_PUBLIC_KEY=your_generated_public_key
   VAPID_PRIVATE_KEY=your_generated_private_key
   VAPID_EMAIL=mailto:your-email@example.com
<<<<<<< HEAD
=======
   ```

6. **Configure MongoDB:**
   Ensure MongoDB is running and update `.env` if needed:
   ```env
>>>>>>> 02675bc (After Deploy Shamim)
   MONGODB_URI=mongodb://localhost:27017/push_db
   DATABASE_NAME=push_db
   ```

<<<<<<< HEAD
5. **Start backend:**
   ```bash
   uvicorn main:app --reload
   ```

</details>

<details>
<summary><h3>Frontend Setup</h3></summary>
=======
### Frontend Setup
>>>>>>> 02675bc (After Deploy Shamim)

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

<<<<<<< HEAD
3. **Configure environment (optional):**
   Create `.env` file:
=======
3. **Set up environment variables (optional):**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` if your backend is on a different URL:
>>>>>>> 02675bc (After Deploy Shamim)
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

<<<<<<< HEAD
4. **Start development server:**
   ```bash
   npm run dev
   ```

</details>

### User Registration App

<details>
<summary><h3>Backend Setup</h3></summary>

1. **Navigate to backend directory:**
   ```bash
   cd test_Web_Aplication/backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create `.env` file:
   ```env
   MONGODB_URI=mongodb://localhost:27017/user_registration_db
   DATABASE_NAME=user_registration_db
   PUSH_SERVICE_URL=http://localhost:8000
   PUSH_ADMIN_USERNAME=admin
   PUSH_ADMIN_PASSWORD=your_admin_password
   PUSH_APPLICATION_NAME=User Registration App
   JWT_SECRET_KEY=your_secret_key_here
   ```

5. **Start backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

</details>

<details>
<summary><h3>Frontend Setup</h3></summary>

1. **Navigate to frontend directory:**
   ```bash
   cd test_Web_Aplication/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (optional):**
   Create `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8001
   VITE_PUSH_SERVICE_URL=http://localhost:8000
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

</details>

### MongoDB Setup

1. **Start MongoDB:**
   ```bash
   # Using systemd (Linux)
   sudo systemctl start mongod

   # Or using MongoDB directly
   mongod

   # Or using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. **Verify MongoDB is running:**
   ```bash
   mongosh
   # or
   mongo
   ```

</details>

---

<details>
<summary><h2>🚀 Production Deployment</h2></summary>

### Docker Compose v2 Production Configuration

For production deployment, consider the following:

#### 1. Environment Variables Security

- Use Docker secrets or environment variable injection
- Never commit `.env` files to version control
- Store VAPID keys securely
- Use strong JWT secrets

#### 2. HTTPS Configuration

- Configure Nginx with SSL certificates
- Update CORS settings to production domains
- Web Push requires HTTPS (except localhost)

#### 3. Resource Limits

The `docker-compose.yml` already includes resource limits. Adjust based on your needs:

```yaml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
```

#### 4. Health Checks

All services include health checks. Monitor service health:

```bash
docker compose ps
```

#### 5. Logging and Monitoring

- Configure log rotation
- Set up log aggregation
- Monitor container health
- Set up alerts for critical issues

#### 6. Database Backups

Set up automated MongoDB backups:

```bash
# Create backup script
docker compose exec mongodb mongodump --out /data/backup/$(date +%Y%m%d)
```

#### 7. Update CORS Settings

In backend services, update CORS origins:

```python
allow_origins=["https://your-production-domain.com"]
```

#### 8. Production Build

For frontend services, ensure production builds:

```bash
# Build frontend
cd frontend
npm run build

# The Dockerfile handles this automatically
```

</details>

---

<details>
<summary><h2>🛠️ Technologies Used</h2></summary>

### Backend (Both Applications)
- **FastAPI** - Modern, fast web framework
- **Beanie** - ODM for MongoDB
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **Python 3.11** - Programming language

### Push Notification Service
- **pywebpush** - Web Push library
- **NumPy** - Numerical computations

### User Registration App
- **PyJWT** - JWT token generation
- **bcrypt** - Password hashing
- **httpx** - Async HTTP client

### Frontend (Both Applications)
- **Svelte** - Frontend framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - CSS framework
- **DaisyUI** - UI component library
- **Axios** - HTTP client

### User Registration App Additional
- **FingerprintJS** - Device fingerprinting

### Infrastructure
- **Docker** - Containerization
- **Docker Compose v2** - Orchestration
- **MongoDB** - Database
- **Nginx** - Web server (production)

</details>

---

<details>
<summary><h2>🔧 Troubleshooting</h2></summary>

### Common Issues

**Services won't start:**
- Check Docker daemon: `docker info`
- Verify ports not in use
- Check logs: `docker compose logs`

**MongoDB connection errors:**
- Verify MongoDB is running
- Check connection string in environment variables
- Ensure network connectivity
=======
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
Sends a push notification to a specific user. **Requires admin authentication.**

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

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

**Note:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete authentication and usage examples.

### `POST /push/broadcast`
Sends a push notification to all subscribed users. **Requires admin authentication.**

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

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

**Note:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete authentication and usage examples.

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
>>>>>>> 02675bc (After Deploy Shamim)

**Push notifications not working:**
- Verify notification permission is granted
- Check browser supports Web Push API
<<<<<<< HEAD
- Ensure HTTPS is used (or localhost)
- Verify VAPID keys are correct

**CORS errors:**
- Check backend CORS settings
- Ensure frontend and backend URLs are correct
- Verify environment variables

**Authentication errors:**
- Check JWT secret key is set
- Verify token expiration
- Ensure token format is correct

### Get Help

For detailed troubleshooting:
- Check service logs: `docker compose logs -f [service]`
- Review API documentation
- Check browser console for frontend errors
- Check backend server logs

</details>

---

## 📄 License

This project is provided as-is for educational and development purposes.

## 📞 Support

For issues or questions:
- Check browser console for frontend errors
- Check backend server logs for API errors
- Check MongoDB logs for database issues
- Review API documentation at `/docs` endpoints
- Check Docker logs: `docker compose logs`

## 🔗 Related Documentation

- [Push Notification Service API Documentation](API_DOCUMENTATION.md)
- [User Registration App Documentation](test_Web_Aplication/README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Quick API Guide](QUICK_API_GUIDE.md)
=======
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
>>>>>>> 02675bc (After Deploy Shamim)

