#!/bin/bash
# Start development environment with Docker
# Usage: ./scripts/dev.sh [stop|logs]

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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_dependencies() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    print_success "Dependencies verified"
}

start_dev() {
    print_header "Starting development environment"
    print_info "This will start both backend and frontend with hot-reload"
    echo ""

    cd "$PROJECT_DIR"

    # Check if frontend node_modules exists
    if [ ! -d "frontend/node_modules" ]; then
        print_info "Installing frontend dependencies (first run)..."
        cd "$PROJECT_DIR/frontend"
        npm install
        cd "$PROJECT_DIR"
        echo ""
    fi

    # Start development services
    docker-compose -f docker-compose.dev.yml up --build

    # Note: Ctrl+C to stop
}

stop_dev() {
    print_header "Stopping development environment"
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.dev.yml down
    print_success "Development environment stopped"
}

show_logs() {
    print_header "Development environment logs"
    print_info "Press Ctrl+C to exit logs view"
    echo ""
    cd "$PROJECT_DIR"
    docker-compose -f docker-compose.dev.yml logs -f
}

show_usage() {
    cat << EOF
Usage: $0 [COMMAND]

Commands:
    [none/up]   Start development environment (default)
    stop        Stop development environment
    logs        View live development logs
    help        Show this help message

Environment:
    Backend:    http://localhost:8000
    Frontend:   http://localhost:5173
    API:        http://localhost:8000/api

Features:
    - Hot-reload for both backend and frontend
    - Automatic database initialization
    - WebSocket support
    - Live logs view
    - Development utilities

Examples:
    $0                  # Start dev environment
    $0 stop             # Stop dev environment
    $0 logs             # View live logs

Keyboard shortcuts:
    Ctrl+C              Stop services or exit logs

For production deployment, see:
    ./scripts/deploy.sh help

EOF
}

# Main script
main() {
    cd "$PROJECT_DIR"

    COMMAND=${1:-up}

    case "$COMMAND" in
        up|start|"")
            check_dependencies
            start_dev
            ;;
        stop|down)
            stop_dev
            ;;
        logs)
            show_logs
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
