#!/bin/bash
# Deploy chklst to production
# Usage: ./scripts/deploy.sh [start|stop|restart|logs|build]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}"
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

check_dependencies() {
    print_header "Checking dependencies"

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Install Docker from: https://docs.docker.com/engine/install/"
        exit 1
    fi
    print_success "Docker installed"

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        echo "Install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose installed"

    if ! command -v curl &> /dev/null; then
        print_warning "curl is not installed (optional, for health checks)"
    fi
}

build_images() {
    print_header "Building Docker images"
    cd "$PROJECT_DIR"
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

start_services() {
    print_header "Starting services"
    cd "$PROJECT_DIR"
    docker-compose up -d
    print_success "Services started"

    # Wait for services to be ready
    echo ""
    echo "Waiting for services to be healthy..."
    sleep 5

    if docker-compose exec -T chklst curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend is healthy"
    else
        print_warning "Backend health check returned non-200 status (may still be starting)"
    fi

    print_success "Application is ready!"
}

stop_services() {
    print_header "Stopping services"
    cd "$PROJECT_DIR"
    docker-compose down
    print_success "Services stopped"
}

restart_services() {
    stop_services
    echo ""
    start_services
}

show_logs() {
    cd "$PROJECT_DIR"
    docker-compose logs -f
}

show_status() {
    print_header "Service status"
    cd "$PROJECT_DIR"
    docker-compose ps

    echo ""
    echo "Application info:"
    if docker-compose exec -T chklst curl -s http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}Backend status: Running${NC}"
        echo "Local access: http://localhost:8000"
    else
        echo -e "${YELLOW}Backend status: Not responding${NC}"
    fi
}

show_usage() {
    cat << EOF
Usage: $0 [COMMAND]

Commands:
    build       Build Docker images
    start       Start services (builds if needed)
    stop        Stop all services
    restart     Restart all services
    logs        View live service logs
    status      Show service status and info
    help        Show this help message

Examples:
    $0 build                # Build images
    $0 start                # Start chklst
    $0 logs                 # View logs in real-time
    $0 restart              # Restart all services

Documentation:
    - Local development: Use 'docker-compose -f docker-compose.dev.yml up'
    - Production with Nginx: Use 'docker-compose --profile production up'
    - Access logs: docker-compose logs -f chklst
    - SSH into container: docker-compose exec chklst /bin/bash

EOF
}

# Main script
main() {
    cd "$PROJECT_DIR"

    COMMAND=${1:-start}

    case "$COMMAND" in
        build)
            check_dependencies
            build_images
            ;;
        start)
            check_dependencies
            build_images
            start_services
            echo ""
            echo -e "${GREEN}Deployment complete!${NC}"
            echo "Application available at: http://localhost:8000"
            echo "Run '${SCRIPT_DIR}/deploy.sh logs' to view logs"
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        status)
            check_dependencies
            show_status
            ;;
        help)
            show_usage
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
