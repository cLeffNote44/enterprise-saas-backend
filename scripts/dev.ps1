# PowerShell script for Docker development on Windows
param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host ""
    Write-Host "Enterprise SaaS Foundation - Docker Helper (Windows)" -ForegroundColor Cyan
    Write-Host "====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\scripts\dev.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  build       - Build Docker images"
    Write-Host "  up          - Start all services"
    Write-Host "  down        - Stop all services"
    Write-Host "  restart     - Restart all services"
    Write-Host "  logs        - View all logs"
    Write-Host "  shell       - Django shell"
    Write-Host "  bash        - Bash shell in web container"
    Write-Host "  migrate     - Run migrations"
    Write-Host "  seed        - Seed development data"
    Write-Host "  test        - Run tests"
    Write-Host "  clean       - Remove containers and volumes"
    Write-Host ""
}

switch ($Command.ToLower()) {
    "build" {
        Write-Host "Building Docker images..." -ForegroundColor Yellow
        docker compose build
    }
    "up" {
        Write-Host "Starting all services..." -ForegroundColor Yellow
        docker compose up -d
        Write-Host ""
        Write-Host "Services are running at:" -ForegroundColor Green
        Write-Host "  Web:     http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  Admin:   http://localhost:8000/admin" -ForegroundColor Cyan
        Write-Host "  Flower:  http://localhost:5555" -ForegroundColor Cyan
        Write-Host "  MailHog: http://localhost:8025" -ForegroundColor Cyan
        Write-Host "  MinIO:   http://localhost:9001" -ForegroundColor Cyan
    }
    "down" {
        Write-Host "Stopping all services..." -ForegroundColor Yellow
        docker compose down
    }
    "restart" {
        Write-Host "Restarting all services..." -ForegroundColor Yellow
        docker compose down
        docker compose up -d
    }
    "logs" {
        docker compose logs -f
    }
    "shell" {
        docker compose exec web python foundation/manage.py shell
    }
    "bash" {
        docker compose exec web bash
    }
    "migrate" {
        Write-Host "Running migrations..." -ForegroundColor Yellow
        docker compose exec web python foundation/manage.py migrate
    }
    "seed" {
        Write-Host "Seeding development data..." -ForegroundColor Yellow
        docker compose exec web python foundation/manage.py seed_dev_data --clear
    }
    "test" {
        Write-Host "Running tests..." -ForegroundColor Yellow
        docker compose exec web python foundation/manage.py test
    }
    "clean" {
        Write-Host "Cleaning up Docker resources..." -ForegroundColor Yellow
        docker compose down -v
        docker system prune -f
    }
    default {
        Show-Help
    }
}