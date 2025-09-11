#!/bin/bash

# Production Deployment Script for Mistral AI Chat
# Usage: ./deploy.sh [frontend|backend|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend"
BACKEND_DIR="backend"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if running from project root
    if [[ ! -d "$FRONTEND_DIR" || ! -d "$BACKEND_DIR" ]]; then
        log_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check for required environment variables
    if [[ -z "$MISTRAL_API_KEY" ]]; then
        log_warning "MISTRAL_API_KEY environment variable not set"
        log_info "Please set it before deployment: export MISTRAL_API_KEY=your_key_here"
    fi
    
    log_success "Requirements check passed"
}

deploy_frontend() {
    log_info "Deploying frontend..."
    
    cd $FRONTEND_DIR
    
    # Install dependencies
    log_info "Installing frontend dependencies..."
    npm ci
    
    # Build the application
    log_info "Building frontend application..."
    npm run build
    
    # Check if build was successful
    if [[ -d ".next" ]]; then
        log_success "Frontend built successfully"
    else
        log_error "Frontend build failed"
        exit 1
    fi
    
    cd ..
    log_success "Frontend deployment completed"
}

deploy_backend() {
    log_info "Deploying backend..."
    
    cd $BACKEND_DIR
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    log_info "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        log_warning ".env file not found in backend directory"
        log_info "Creating .env file template..."
        echo "MISTRAL_API_KEY=${MISTRAL_API_KEY:-your_mistral_api_key_here}" > .env
        echo "ENVIRONMENT=production" >> .env
        log_info "Please edit backend/.env with your actual API key"
    fi
    
    cd ..
    log_success "Backend deployment completed"
}

test_deployment() {
    log_info "Testing deployment..."
    
    # Check if integration test script exists
    if [[ -f "test_integration.sh" ]]; then
        log_info "Running integration tests..."
        chmod +x test_integration.sh
        ./test_integration.sh
    else
        log_warning "Integration test script not found"
    fi
}

start_services() {
    log_info "Starting services..."
    
    # Start backend
    log_info "Starting backend server..."
    cd $BACKEND_DIR
    source venv/bin/activate
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend
    log_info "Starting frontend server..."
    cd $FRONTEND_DIR
    nohup npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    log_success "Services started"
    log_info "Backend PID: $BACKEND_PID (logged to backend.log)"
    log_info "Frontend PID: $FRONTEND_PID (logged to frontend.log)"
    log_info "Frontend: http://localhost:3000"
    log_info "Backend API: http://localhost:8000"
    log_info "API Docs: http://localhost:8000/docs"
}

stop_services() {
    log_info "Stopping services..."
    
    # Stop backend
    if [[ -f "backend.pid" ]]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_success "Backend stopped (PID: $BACKEND_PID)"
        fi
        rm backend.pid
    fi
    
    # Stop frontend
    if [[ -f "frontend.pid" ]]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_success "Frontend stopped (PID: $FRONTEND_PID)"
        fi
        rm frontend.pid
    fi
}

show_help() {
    echo "Mistral AI Chat Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  frontend    Deploy frontend only"
    echo "  backend     Deploy backend only"
    echo "  all         Deploy both frontend and backend (default)"
    echo "  start       Start services in background"
    echo "  stop        Stop running services"
    echo "  test        Run integration tests"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  MISTRAL_API_KEY    Your Mistral AI API key (required)"
    echo ""
    echo "Examples:"
    echo "  export MISTRAL_API_KEY=your_key_here"
    echo "  $0 all"
    echo "  $0 start"
    echo "  $0 test"
    echo "  $0 stop"
}

# Main script
main() {
    local command=${1:-all}
    
    case $command in
        "frontend")
            check_requirements
            deploy_frontend
            ;;
        "backend")
            check_requirements
            deploy_backend
            ;;
        "all")
            check_requirements
            deploy_backend
            deploy_frontend
            log_success "🎉 Deployment completed successfully!"
            log_info "Next steps:"
            log_info "1. Run './deploy.sh start' to start services"
            log_info "2. Run './deploy.sh test' to run integration tests"
            log_info "3. Open http://localhost:3000 in your browser"
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "test")
            test_deployment
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Trap to handle script interruption
trap 'log_warning "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"
