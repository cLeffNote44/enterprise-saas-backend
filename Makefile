.PHONY: help build up down restart logs shell test migrate clean

# Default target
help:
	@echo "Enterprise SaaS Foundation - Docker Commands"
	@echo "============================================"
	@echo ""
	@echo "Setup & Build:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Development:"
	@echo "  make shell          - Django shell"
	@echo "  make bash           - Bash shell in web container"
	@echo "  make logs           - View all logs"
	@echo "  make logs-web       - View web logs"
	@echo "  make logs-worker    - View worker logs"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run migrations"
	@echo "  make makemigrations - Create migrations"
	@echo "  make superuser      - Create superuser"
	@echo "  make db-shell       - PostgreSQL shell"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run tests"
	@echo "  make test-coverage  - Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make reset          - Full reset (clean + rebuild)"
	@echo ""

# Build Docker images
build:
	docker compose build

# Start all services
up:
	docker compose up -d
	@echo ""
	@echo "Services are starting up..."
	@echo "Web: http://localhost:8000"
	@echo "Admin: http://localhost:8000/admin"
	@echo "Flower: http://localhost:5555"
	@echo "MailHog: http://localhost:8025"
	@echo "MinIO: http://localhost:9001"

# Stop all services
down:
	docker compose down

# Restart all services
restart: down up

# View logs
logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-worker:
	docker compose logs -f worker

logs-db:
	docker compose logs -f db

# Shell access
shell:
	docker compose exec web python foundation/manage.py shell

bash:
	docker compose exec web bash

# Database operations
migrate:
	docker compose exec web python foundation/manage.py migrate

makemigrations:
	docker compose exec web python foundation/manage.py makemigrations

superuser:
	docker compose exec web python foundation/manage.py createsuperuser

db-shell:
	docker compose exec db psql -U foundation

# Testing
test:
	docker compose exec web python foundation/manage.py test

test-coverage:
	docker compose exec web coverage run --source='.' foundation/manage.py test
	docker compose exec web coverage report

# Maintenance
clean:
	docker compose down -v
	docker system prune -f

reset: clean build up migrate
	@echo "Reset complete!"