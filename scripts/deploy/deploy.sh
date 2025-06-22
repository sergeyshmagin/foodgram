#!/bin/bash

# =============================================================================
# Foodgram Production Deployment Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="192.168.0.4"
PROD_SERVER="192.168.0.10"
PROJECT_NAME="foodgram"

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

# Check if .env file exists
check_env_file() {
    if [ ! -f "infra/.env" ]; then
        log_error ".env file not found in infra/ directory"
        log_info "Please copy infra/production.env.example to infra/.env and configure it"
        exit 1
    fi
    log_success ".env file found"
}

# Build and push images to registry
build_and_push() {
    log_info "Building and pushing images to registry..."
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:latest backend/
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:latest
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest frontend/
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest
    
    log_success "Images built and pushed successfully"
}

# Deploy to production server
deploy_to_production() {
    log_info "Deploying to production server ${PROD_SERVER}..."
    
    # Copy docker-compose and configs to production server
    scp -r infra/ root@${PROD_SERVER}:/opt/${PROJECT_NAME}/
    
    # Update docker-compose.yml to use registry images
    ssh root@${PROD_SERVER} "cd /opt/${PROJECT_NAME}/infra && \
        sed -i 's|build:|image:|g' docker-compose.yml && \
        sed -i 's|context: ../backend|${DOCKER_REGISTRY}/${PROJECT_NAME}-backend:latest|g' docker-compose.yml && \
        sed -i 's|dockerfile: Dockerfile||g' docker-compose.yml && \
        sed -i 's|context: ../frontend|${DOCKER_REGISTRY}/${PROJECT_NAME}-frontend:latest|g' docker-compose.yml"
    
    # Pull images and restart services
    ssh root@${PROD_SERVER} "cd /opt/${PROJECT_NAME}/infra && \
        docker-compose pull && \
        docker-compose down && \
        docker-compose up -d"
    
    log_success "Deployment completed"
}

# Check service health
check_health() {
    log_info "Checking service health..."
    sleep 30
    
    # Check if services are running
    if ssh root@${PROD_SERVER} "docker-compose -f /opt/${PROJECT_NAME}/infra/docker-compose.yml ps | grep -q 'Up'"; then
        log_success "Services are running"
    else
        log_error "Some services are not running"
        exit 1
    fi
    
    # Check API health endpoint
    if curl -f http://${PROD_SERVER}/api/health/ > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_warning "API health check failed"
    fi
}

# Main deployment flow
main() {
    log_info "Starting Foodgram deployment..."
    
    check_env_file
    build_and_push
    deploy_to_production
    check_health
    
    log_success "Deployment completed successfully!"
    log_info "Application is available at: http://${PROD_SERVER}"
    log_info "Admin panel: http://${PROD_SERVER}/admin/"
    log_info "API docs: http://${PROD_SERVER}/api/docs/"
    log_info "MinIO console: http://${PROD_SERVER}:9001"
}

# Run main function
main "$@" 