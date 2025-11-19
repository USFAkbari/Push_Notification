#!/bin/bash

# Fast Docker Deployment Script for Push Notification Application
# Usage: ./deploy.sh [options]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="push"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_dependencies() {
    print_header "Checking Dependencies"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_success "Docker daemon is running"
}

check_vapid_keys() {
    print_header "Checking VAPID Keys"
    
    if [ -f .env ]; then
        if grep -q "VAPID_PUBLIC_KEY=" .env && grep -q "VAPID_PRIVATE_KEY=" .env; then
            print_success "VAPID keys found in .env file"
            return 0
        fi
    fi
    
    print_warning "VAPID keys not found in .env file"
    print_info "VAPID keys will be auto-generated on first startup"
    print_info "You can generate them manually by running:"
    print_info "  docker compose exec backend python scripts/init_vapid_keys.py"
    return 1
}

stop_containers() {
    print_header "Stopping Containers"
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    print_success "Containers stopped"
}

build_containers() {
    print_header "Building Containers"
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache
    print_success "Containers built"
}

start_containers() {
    print_header "Starting Containers"
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    print_success "Containers started"
}

wait_for_services() {
    print_header "Waiting for Services"
    
    print_info "Waiting for MongoDB..."
    timeout=60
    counter=0
    while ! docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T mongodb mongosh --quiet --eval "db.runCommand('ping')" &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "MongoDB failed to start within $timeout seconds"
            return 1
        fi
    done
    print_success "MongoDB is ready"
    
    print_info "Waiting for Backend..."
    timeout=60
    counter=0
    while ! curl -s http://localhost:8000/health &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Backend failed to start within $timeout seconds"
            return 1
        fi
    done
    print_success "Backend is ready"
    
    print_info "Waiting for Frontend..."
    timeout=30
    counter=0
    while ! curl -s http://localhost:3000/health &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_warning "Frontend health check timeout (may still be starting)"
            return 0
        fi
    done
    print_success "Frontend is ready"
}

show_status() {
    print_header "Service Status"
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    echo ""
    print_info "Service URLs:"
    echo "  - Frontend:  http://localhost:3000"
    echo "  - Backend:   http://localhost:8000"
    echo "  - MongoDB:   localhost:27017"
    echo ""
    print_info "Admin Portal: http://localhost:3000 (default login page)"
    print_info "Public App:   http://localhost:3000/app"
}

show_logs() {
    print_header "Service Logs"
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs --tail=50 -f
}

create_admin_user() {
    print_header "Creating Admin User"
    
    if [ -z "$ADMIN_USERNAME" ] || [ -z "$ADMIN_PASSWORD" ]; then
        print_warning "Admin credentials not provided via environment variables"
        print_info "To create an admin user, run:"
        print_info "  docker compose exec backend python scripts/create_admin.py <username> <password>"
        return 0
    fi
    
    print_info "Creating admin user: $ADMIN_USERNAME"
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T backend python scripts/create_admin.py "$ADMIN_USERNAME" "$ADMIN_PASSWORD" || {
        print_warning "Admin user may already exist or creation failed"
    }
    print_success "Admin user creation attempted"
}

quick_deploy() {
    print_header "Quick Deployment"
    
    check_dependencies
    check_vapid_keys || true  # Don't exit if keys are missing (they'll be auto-generated)
    
    # Stop existing containers
    stop_containers 2>/dev/null || true
    
    # Build and start
    print_info "Building containers (this may take a few minutes)..."
    docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build
    
    print_info "Starting containers..."
    start_containers
    
    # Wait for services
    wait_for_services
    
    # Create admin user if credentials provided
    create_admin_user
    
    # Show status
    show_status
    
    print_header "Deployment Complete!"
    print_success "All services are running"
    echo ""
    print_info "Useful commands:"
    echo "  View logs:        ./deploy.sh logs"
    echo "  Stop services:    ./deploy.sh stop"
    echo "  Restart services: ./deploy.sh restart"
    echo "  Show status:      ./deploy.sh status"
    echo "  Create admin:     docker compose exec backend python scripts/create_admin.py <username> <password>"
}

# Main script logic
case "${1:-deploy}" in
    deploy|quick)
        quick_deploy
        ;;
    build)
        check_dependencies
        build_containers
        ;;
    start)
        check_dependencies
        start_containers
        wait_for_services
        show_status
        ;;
    stop)
        stop_containers
        ;;
    restart)
        check_dependencies
        stop_containers
        start_containers
        wait_for_services
        show_status
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    clean)
        print_header "Cleaning Up"
        stop_containers
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v
        print_success "All containers and volumes removed"
        ;;
    rebuild)
        check_dependencies
        stop_containers
        build_containers
        start_containers
        wait_for_services
        show_status
        ;;
    admin)
        if [ -z "$2" ] || [ -z "$3" ]; then
            print_error "Usage: ./deploy.sh admin <username> <password>"
            exit 1
        fi
        ADMIN_USERNAME="$2"
        ADMIN_PASSWORD="$3"
        create_admin_user
        ;;
    help|--help|-h)
        echo "Fast Docker Deployment Script for Push Notification Application"
        echo ""
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  deploy, quick    - Quick deployment (default): build, start, and wait for services"
        echo "  build            - Build Docker containers"
        echo "  start            - Start containers"
        echo "  stop             - Stop containers"
        echo "  restart          - Restart containers"
        echo "  status           - Show service status"
        echo "  logs             - Show and follow service logs"
        echo "  rebuild          - Rebuild and restart containers"
        echo "  clean            - Stop and remove all containers and volumes"
        echo "  admin <user> <pass> - Create admin user"
        echo "  help             - Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  ADMIN_USERNAME   - Admin username (for auto-creation during deploy)"
        echo "  ADMIN_PASSWORD  - Admin password (for auto-creation during deploy)"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh                    # Quick deployment"
        echo "  ./deploy.sh quick               # Same as above"
        echo "  ./deploy.sh rebuild             # Rebuild everything"
        echo "  ./deploy.sh admin admin pass123 # Create admin user"
        echo "  ADMIN_USERNAME=admin ADMIN_PASSWORD=pass123 ./deploy.sh  # Deploy with admin"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Run './deploy.sh help' for usage information"
        exit 1
        ;;
esac

