#!/bin/bash

# =============================================================================
# Foodgram Development Environment Startup Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment is activated
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "Virtual environment is not activated"
        log_info "Activating virtual environment..."
        if [ -f "backend/venv/bin/activate" ]; then
            source backend/venv/bin/activate
            log_success "Virtual environment activated"
        else
            log_error "Virtual environment not found. Please create it first:"
            log_info "cd backend && python -m venv venv && source venv/bin/activate"
            exit 1
        fi
    else
        log_success "Virtual environment is activated: $VIRTUAL_ENV"
    fi
}

# Start infrastructure services
start_infrastructure() {
    log_info "Starting infrastructure services (PostgreSQL, Redis, MinIO)..."
    
    if ! docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.dev.yml up -d
        log_info "Waiting for services to be ready..."
        sleep 10
    else
        log_info "Infrastructure services are already running"
    fi
    
    # Check if services are healthy
    log_info "Checking service health..."
    
    # Check PostgreSQL
    if docker exec foodgram-dev-db pg_isready -U foodgram_user -d foodgram_dev > /dev/null 2>&1; then
        log_success "PostgreSQL is ready"
    else
        log_error "PostgreSQL is not ready"
        exit 1
    fi
    
    # Check Redis
    if docker exec foodgram-dev-redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis is ready"
    else
        log_error "Redis is not ready"
        exit 1
    fi
    
    # Check MinIO
    if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
        log_success "MinIO is ready"
    else
        log_warning "MinIO might not be fully ready yet"
    fi
}

# Setup Django backend
setup_backend() {
    log_info "Setting up Django backend..."
    
    cd backend
    
    # Install requirements if needed
    if [ ! -f ".requirements_installed" ] || [ requirements/development.txt -nt .requirements_installed ]; then
        log_info "Installing Python requirements..."
        pip install -r requirements/development.txt
        touch .requirements_installed
        log_success "Requirements installed"
    fi
    
    # Run migrations
    log_info "Running database migrations..."
    python manage.py migrate
    
    # Create superuser if not exists
    if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
        log_info "Creating superuser..."
        python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@foodgram.ru').exists():
    User.objects.create_superuser(
        email='admin@foodgram.ru',
        username='admin',
        first_name='Admin',
        last_name='User',
        password='admin123'
    )
    print('Superuser created: admin@foodgram.ru / admin123')
else:
    print('Superuser already exists')
"
    fi
    
    # Load initial data if needed
    if [ -f "../data/ingredients.json" ] && ! python manage.py shell -c "from apps.recipes.models import Ingredient; print(Ingredient.objects.exists())" | grep -q "True"; then
        log_info "Loading ingredients data..."
        python manage.py loaddata ../data/ingredients.json
        log_success "Ingredients loaded"
    fi
    
    # Create test data
    log_info "Creating test data..."
    python create_demo_data.py
    
    cd ..
    log_success "Backend setup completed"
}

# Start frontend development server
start_frontend() {
    log_info "Starting frontend development server..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ] || [ package.json -nt node_modules/.last_install ]; then
        log_info "Installing Node.js dependencies..."
        npm install
        touch node_modules/.last_install
        log_success "Dependencies installed"
    fi
    
    # Start development server in background
    log_info "Starting React development server..."
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    log_success "Frontend server started (PID: $FRONTEND_PID)"
}

# Start Django development server
start_backend_server() {
    log_info "Starting Django development server..."
    
    cd backend
    
    # Start Django development server
    python manage.py runserver 8000 &
    BACKEND_PID=$!
    
    cd ..
    log_success "Backend server started (PID: $BACKEND_PID)"
}

# Show status and URLs
show_status() {
    log_success "Development environment is ready!"
    echo ""
    echo "🌐 Services URLs:"
    echo "   Frontend:     http://localhost:3000"
    echo "   Backend API:  http://localhost:8000/api/"
    echo "   Admin panel:  http://localhost:8000/admin/"
    echo "   API docs:     http://localhost:8000/api/docs/"
    echo ""
    echo "🗄️  Infrastructure:"
    echo "   PostgreSQL:   localhost:5432 (foodgram_dev / foodgram_user)"
    echo "   Redis:        localhost:6379"
    echo "   MinIO API:    http://localhost:9000"
    echo "   MinIO Console: http://localhost:9001 (foodgram_minio / foodgram_minio_password)"
    echo ""
    echo "👤 Admin credentials:"
    echo "   Email:    admin@foodgram.ru"
    echo "   Password: admin123"
    echo ""
    echo "Press Ctrl+C to stop all services"
}

# Cleanup function
cleanup() {
    log_info "Stopping development servers..."
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    log_success "Development servers stopped"
}

# Set trap for cleanup
trap cleanup EXIT

# Main function
main() {
    log_info "Starting Foodgram development environment..."
    
    check_venv
    start_infrastructure
    setup_backend
    
    # Ask user if they want to start servers
    read -p "Start development servers? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_frontend
        start_backend_server
        show_status
        
        # Wait for user interrupt
        while true; do
            sleep 1
        done
    else
        log_info "Development environment is ready. You can manually start servers:"
        log_info "Backend: cd backend && python manage.py runserver"
        log_info "Frontend: cd frontend && npm start"
    fi
}

# Run main function
main "$@" 