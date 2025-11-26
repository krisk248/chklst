.PHONY: help build start stop restart logs clean dev dev-stop dev-logs status

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)chklst Docker Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@echo "  make build          - Build Docker images"
	@echo "  make start          - Start production environment"
	@echo "  make stop           - Stop production environment"
	@echo "  make restart        - Restart production environment"
	@echo "  make logs           - View production logs"
	@echo "  make status         - Show service status"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev            - Start development environment"
	@echo "  make dev-stop       - Stop development environment"
	@echo "  make dev-logs       - View development logs"
	@echo ""
	@echo "$(GREEN)Maintenance:$(NC)"
	@echo "  make clean          - Clean up Docker artifacts"
	@echo "  make ps             - List running containers"
	@echo "  make shell          - Access backend shell"
	@echo "  make help           - Show this help message"
	@echo ""

# Production targets
build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build --no-cache

start: build
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "Access application at: http://localhost:8000"

stop:
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: stop start
	@echo "$(GREEN)Services restarted!$(NC)"

logs:
	@docker-compose logs -f

status:
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)Application Health:$(NC)"
	@docker-compose exec -T chklst curl -s http://localhost:8000/health 2>/dev/null && echo "Backend: $(GREEN)Healthy$(NC)" || echo "Backend: $(RED)Unhealthy$(NC)"

ps:
	@docker-compose ps

# Development targets
dev:
	@echo "$(BLUE)Starting development environment...$(NC)"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	docker-compose -f docker-compose.dev.yml up --build

dev-stop:
	@echo "$(BLUE)Stopping development environment...$(NC)"
	docker-compose -f docker-compose.dev.yml down
	@echo "$(GREEN)Development environment stopped!$(NC)"

dev-logs:
	@docker-compose -f docker-compose.dev.yml logs -f

# Shell access
shell:
	@echo "$(BLUE)Opening backend shell...$(NC)"
	@echo "Type 'exit' to close"
	docker-compose exec chklst /bin/bash

shell-frontend:
	@echo "$(BLUE)Opening frontend shell...$(NC)"
	@echo "Type 'exit' to close"
	docker-compose -f docker-compose.dev.yml exec frontend sh

# Database
db-reset:
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose exec chklst rm -f /app/data/chklst.db; \
		docker-compose restart chklst; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

# Maintenance
clean:
	@echo "$(BLUE)Cleaning up Docker artifacts...$(NC)"
	docker-compose down
	docker system prune -f
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-volumes:
	@echo "$(RED)WARNING: This will delete all data volumes!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		echo "$(GREEN)Volumes deleted!$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

# Testing
test:
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec -T chklst pytest /app/tests -v

test-coverage:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker-compose exec -T chklst pytest /app/tests --cov=/app/backend --cov-report=html

# Documentation
docs:
	@echo "$(BLUE)Building documentation...$(NC)"
	@echo "See: DOCKER_DEPLOYMENT.md"
	@echo "See: DOCKER_QUICKSTART.md"

# Installation
install-frontend-deps:
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	docker-compose -f docker-compose.dev.yml exec frontend npm install

# Utility
version:
	@echo "$(BLUE)Version Information:$(NC)"
	@docker --version
	@docker-compose --version

info:
	@echo "$(BLUE)Docker Configuration:$(NC)"
	@docker info | grep -E "Containers|Running|Paused|Stopped"
	@echo ""
	@echo "$(BLUE)Available Images:$(NC)"
	@docker images | grep chklst || echo "No chklst images found"

# Default target
.DEFAULT_GOAL := help
