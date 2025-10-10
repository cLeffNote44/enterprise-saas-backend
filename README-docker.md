# Docker Development Environment

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (with Docker Compose v2)
  - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Ensure WSL2 backend is enabled for better performance
- **Python 3.11+** (for local development)
- **Git** (for version control)

### Port Requirements

The following ports must be available on your system:

| Service | Port | Description |
|---------|------|-------------|
| Web | 8000 | Django development server |
| Flower | 5555 | Celery monitoring UI |
| MailHog | 8025 | Email testing UI |
| MinIO | 9000 | S3-compatible object storage API |
| MinIO Console | 9001 | MinIO management UI |
| PostgreSQL | 5432 | Database (optional external access) |
| Redis | 6379 | Cache/Queue (optional external access) |

### Quick Start Checklist

1. ✅ Docker Desktop installed and running
2. ✅ Docker Compose version 2+ verified:
   ```bash
   docker compose version
   ```
3. ✅ Ports available (check with `netstat -an | findstr :8000` on Windows)
4. ✅ At least 4GB RAM allocated to Docker
5. ✅ Clone the repository and navigate to project root

## Getting Started

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Build the containers**:
   ```bash
   docker compose build
   ```

3. **Start all services**:
   ```bash
   docker compose up -d
   ```

4. **Run migrations**:
   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. **Access the services**:
   - Django App: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - Flower (Celery): http://localhost:5555
   - MailHog: http://localhost:8025
   - MinIO Console: http://localhost:9001

## Common Commands

### Container Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Restart a service
docker compose restart web
```

### Django Commands
```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create migrations
docker compose exec web python manage.py makemigrations

# Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web python manage.py test
```

### Database Access
```bash
# PostgreSQL shell
docker compose exec db psql -U foundation

# Django DB shell
docker compose exec web python manage.py dbshell
```

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error, either:
1. Stop the conflicting service
2. Or change the port in `docker-compose.yml`

### Permission Issues on Windows
If you encounter permission errors:
1. Ensure Docker Desktop is running with WSL2 backend
2. Run PowerShell as Administrator when needed

### Container Won't Start
1. Check logs: `docker compose logs [service_name]`
2. Verify `.env` file exists and has correct values
3. Ensure Docker has enough resources allocated

### Database Connection Issues
1. Wait for PostgreSQL to be fully ready (check health status)
2. Verify DATABASE_URL in `.env` matches PostgreSQL settings
3. Check if migrations have been run

## Development Workflow

1. **Code changes** are automatically reflected (volume mounted)
2. **Email testing** via MailHog at http://localhost:8025
3. **File uploads** stored in MinIO (S3-compatible)
4. **Background tasks** monitored via Flower
5. **Database changes** require migrations

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Docker Network                         │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│   Web    │  Worker  │   Beat   │  Flower  │   Redis    │
│  (8000)  │          │          │  (5555)  │   (6379)   │
├──────────┼──────────┴──────────┴──────────┼────────────┤
│PostgreSQL│            MailHog              │   MinIO    │
│  (5432)  │            (8025)               │(9000/9001) │
└──────────┴─────────────────────────────────┴────────────┘
```