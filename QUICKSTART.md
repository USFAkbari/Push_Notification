# Quick Start Guide

Step-by-step instructions to get the Web Push Notification application running.

## Option 1: Local Development (Recommended for Testing)

### Step 1: Prerequisites

Ensure you have installed:
- Python 3.8+
- Node.js 18+
- MongoDB

### Step 2: Start MongoDB

```bash
# Linux (systemd)
sudo systemctl start mongod

# Or manually
mongod

# macOS (Homebrew)
brew services start mongodb-community

# Verify MongoDB is running
mongosh --eval "db.version()"
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate VAPID keys
python generate_vapid_keys.py

# Copy the generated keys (you'll see output like):
# VAPID_PUBLIC_KEY=...
# VAPID_PRIVATE_KEY=...
# VAPID_EMAIL=mailto:your-email@example.com
```

### Step 4: Configure Backend Environment

```bash
# Create .env file in backend directory
cat > .env << EOF
MONGODB_URI=mongodb://localhost:27017/push_db
DATABASE_NAME=push_db
VAPID_PUBLIC_KEY=your_generated_public_key_here
VAPID_PRIVATE_KEY=your_generated_private_key_here
VAPID_EMAIL=mailto:your-email@example.com
EOF

# Replace the VAPID keys with the ones generated in Step 3
```

### Step 5: Start Backend Server

```bash
# Make sure you're in backend directory with venv activated
uvicorn main:app --reload

# Backend should start on http://localhost:8000
# Verify by opening http://localhost:8000 in browser
```

**Keep this terminal open!**

### Step 6: Frontend Setup

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional - defaults to http://localhost:8000)
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF
```

### Step 7: Start Frontend Server

```bash
# Make sure you're in frontend directory
npm run dev

# Frontend should start on http://localhost:3000
# It will automatically open in your browser
```

### Step 8: Test the Application

1. **Open the application** in your browser (http://localhost:3000)
2. **Click "Request Permission"** - Allow notifications when prompted
3. **Enter a User ID** (optional, e.g., "user123")
4. **Click "Subscribe"** - Status should change to "Subscribed"
5. **Enter notification title and body**
6. **Click "Send to User"** or "Broadcast to All"
7. **Check for push notification** on your device

## Option 2: Docker Deployment (Recommended for Production)

### Step 1: Prerequisites

Ensure you have installed:
- Docker 20.10+
- Docker Compose 2.0+

### Step 2: Generate VAPID Keys

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (one-time setup)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Generate VAPID keys
python3 generate_vapid_keys.py

# Copy the generated keys (you'll see output like):
# VAPID_PUBLIC_KEY=...
# VAPID_PRIVATE_KEY=...
# VAPID_EMAIL=mailto:your-email@example.com
```

### Step 3: Create Environment File

```bash
# From project root directory
cat > .env << EOF
VAPID_PUBLIC_KEY=your_generated_public_key_here
VAPID_PRIVATE_KEY=your_generated_private_key_here
VAPID_EMAIL=mailto:your-email@example.com
EOF

# Replace the VAPID keys with the ones generated in Step 2
```

### Step 4: Build and Start All Services

```bash
# From project root directory
docker compose up -d --build

# This will:
# - Build backend Docker image
# - Build frontend Docker image
# - Start MongoDB container
# - Start backend container
# - Start frontend container
```

### Step 5: Verify Services Are Running

```bash
# Check service status
docker compose ps

# You should see all three services in "Up" status:
# - push-mongodb (healthy)
# - push-backend (healthy)
# - push-frontend (healthy)
```

### Step 6: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **MongoDB:** localhost:27017

### Step 7: Test the Application

1. **Open the application** in your browser (http://localhost:3000)
2. **Click "Request Permission"** - Allow notifications when prompted
3. **Enter a User ID** (optional, e.g., "user123")
4. **Click "Subscribe"** - Status should change to "Subscribed"
5. **Enter notification title and body**
6. **Click "Send to User"** or "Broadcast to All"
7. **Check for push notification** on your device

### Useful Docker Commands

```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes MongoDB data)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

**MongoDB connection error:**
```bash
# Verify MongoDB is running
mongosh --eval "db.version()"

# Check MongoDB logs (if using Docker)
docker-compose logs mongodb
```

**VAPID keys not working:**
```bash
# Regenerate keys
cd backend
python generate_vapid_keys.py

# Verify .env file has correct keys (no quotes, no extra spaces)
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Vite will automatically use next available port
# Check terminal output for actual port
```

**Can't connect to backend:**
```bash
# Verify backend is running
curl http://localhost:8000

# Check CORS settings in backend/main.py
# Check VITE_API_BASE_URL in frontend/.env
```

**Service worker not registering:**
```bash
# Open browser DevTools > Application > Service Workers
# Check for errors in Console tab
# Try hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (macOS)
```

### Docker Issues

**Services won't start:**
```bash
# Check Docker daemon is running
docker ps

# Check logs for errors
docker-compose logs

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

**Backend can't connect to MongoDB:**
```bash
# Verify MongoDB is healthy
docker-compose ps

# Test network connectivity
docker-compose exec backend ping mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

## Next Steps

After getting the application running:

1. **Test push notifications** in different browsers
2. **Subscribe multiple users** to test broadcast functionality
3. **Review API endpoints** in README.md
4. **Customize notification styles** in service-worker.js
5. **Configure production settings** (HTTPS, CORS, etc.)

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review error messages in terminal/logs
- Ensure all prerequisites are installed correctly
- Verify environment variables are set correctly

