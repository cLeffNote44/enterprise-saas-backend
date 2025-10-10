# Quick Reference Cards

[← Back to Documentation](../README.md)

---

## 🚀 Quick Start Card

| Task | Command | Notes |
|------|---------|-------|
| **Install Dependencies** | `pip install -r requirements.txt` | Use virtual environment |
| **Run Migrations** | `python manage.py migrate` | Run after installation |
| **Create Admin User** | `python manage.py createsuperuser` | Required for admin access |
| **Start Dev Server** | `python manage.py runserver` | Development only |
| **Run Tests** | `pytest` | Requires test database |
| **Collect Static Files** | `python manage.py collectstatic` | For production |
| **Check System** | `python manage.py check` | Verify configuration |

---

## 🔒 Security Checklist Card

### Pre-Production Checklist
- [ ] Change `SECRET_KEY` in production
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up database credentials securely
- [ ] Enable MFA for admin users
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review and enable security headers
- [ ] Enable audit logging
- [ ] Configure backup strategy
- [ ] Test disaster recovery plan
- [ ] Review user permissions
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure CORS properly
- [ ] Disable DEBUG mode

---

## 📊 Environment Variables Card

### Essential Environment Variables

```bash
# Security
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True

# AWS (if using)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

---

## 🛠️ Django Management Commands

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username

# Create regular user (in shell)
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('username', 'email@example.com', 'password')
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_name

# Database shell
python manage.py dbshell

# Dump data
python manage.py dumpdata > backup.json

# Load data
python manage.py loaddata backup.json
```

### Static Files & Cache
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Compress static files (if using compression)
python manage.py compress
```

---

## 🐳 Docker Commands

### Container Management
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f service_name

# Execute command in container
docker-compose exec web python manage.py migrate

# Shell into container
docker-compose exec web bash

# List running containers
docker-compose ps

# Remove all containers and volumes
docker-compose down -v
```

### Docker Maintenance
```bash
# Clean up unused images
docker image prune -a

# Clean up all unused objects
docker system prune -a

# View disk usage
docker system df

# Export/Import images
docker save -o backup.tar image_name
docker load -i backup.tar
```

---

## 📡 API Testing Commands

### Using cURL
```bash
# GET request
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/users/

# POST request
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-token" \
  -d '{"name": "Test"}' \
  http://localhost:8000/api/items/

# PUT request
curl -X PUT \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-token" \
  -d '{"name": "Updated"}' \
  http://localhost:8000/api/items/1/

# DELETE request
curl -X DELETE \
  -H "Authorization: Token your-token" \
  http://localhost:8000/api/items/1/
```

### Using HTTPie (more user-friendly)
```bash
# Install HTTPie
pip install httpie

# GET request
http GET localhost:8000/api/users/ \
  "Authorization: Token your-token"

# POST request
http POST localhost:8000/api/items/ \
  name="Test" \
  "Authorization: Token your-token"
```

---

## 🔍 Debugging Commands

### Django Debug
```bash
# Django shell
python manage.py shell

# Django shell with IPython
python manage.py shell_plus

# SQL queries for a command
python manage.py command_name --verbosity=2

# Debug server with pdb
python -m pdb manage.py runserver

# Show URLs
python manage.py show_urls
```

### System Debug
```bash
# Check Python packages
pip freeze

# Check Python path
python -c "import sys; print(sys.path)"

# Check Django settings
python manage.py diffsettings

# Validate models
python manage.py validate

# Check deployment readiness
python manage.py check --deploy
```

---

## 🚨 Emergency Procedures

### Site is Down
```bash
# 1. Check server status
systemctl status nginx
systemctl status gunicorn

# 2. Check logs
tail -f /var/log/nginx/error.log
tail -f /path/to/django/logs/error.log

# 3. Restart services
sudo systemctl restart nginx
sudo systemctl restart gunicorn

# 4. Check database
psql -U postgres -c "SELECT 1;"
```

### Database Issues
```bash
# Check connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';"

# Emergency backup
pg_dump -U postgres dbname > emergency_backup.sql
```

### High Load
```bash
# Check system resources
htop
df -h
free -m

# Check slow queries
psql -U postgres -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Restart application
docker-compose restart web
```

---

## 📈 Performance Monitoring

### Quick Performance Checks
```bash
# Database query analysis
python manage.py debugsqlshell

# Profile view performance
python manage.py runprofileserver

# Memory usage
python -c "import psutil; print(psutil.virtual_memory())"

# Cache hit rate
redis-cli INFO stats | grep keyspace
```

---

## 📋 Git Commands

### Common Git Operations
```bash
# Check status
git status

# Add and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/new-feature

# Merge branch
git checkout main
git merge feature/new-feature

# Stash changes
git stash
git stash pop
```

---

## 🔗 Useful URLs

### Development
- **Admin Interface**: `http://localhost:8000/admin/`
- **API Documentation**: `http://localhost:8000/api/docs/`
- **Health Check**: `http://localhost:8000/api/health/`
- **Django Debug Toolbar**: `http://localhost:8000/__debug__/`

### Documentation
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Python Docs**: https://docs.python.org/3/

---

**Last Updated**: January 2024  
**Version**: 1.0.0
