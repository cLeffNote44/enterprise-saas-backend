# 🚀 Production Deployment Guide

This guide walks you through deploying the Enterprise SaaS Foundation to production with best practices for security, performance, and reliability.

## 📋 Pre-Deployment Checklist

Before deploying to production, ensure you have:

- [ ] Reviewed and tested all application code
- [ ] Configured environment variables for production
- [ ] Set up production database (PostgreSQL 15+)
- [ ] Set up Redis cluster for caching
- [ ] Configured email service (SendGrid, AWS SES, etc.)
- [ ] Set up payment gateway (Stripe)
- [ ] Configured file storage (S3, GCS, or Azure Blob)
- [ ] Set up SSL certificates
- [ ] Configured monitoring and alerting
- [ ] Set up backup and disaster recovery
- [ ] Reviewed security settings
- [ ] Prepared rollback plan

## 🏗️ Deployment Options

### Option 1: Kubernetes (Recommended)
Best for: High availability, auto-scaling, enterprise deployments

### Option 2: Docker Compose
Best for: Small to medium deployments, single-server setups

### Option 3: Traditional VPS
Best for: Simple deployments, budget-conscious projects

### Option 4: Platform as a Service (Heroku, Railway, Render)
Best for: Quick deployments, minimal DevOps overhead

## ☸️ Kubernetes Deployment (Recommended)

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3+ (optional but recommended)
- Container registry access (Docker Hub, AWS ECR, GCR, etc.)

### Step 1: Build and Push Container Image

```bash
# Build production image
docker build -f Dockerfile.prod -t your-registry/foundation:v1.0.0 .

# Push to registry
docker push your-registry/foundation:v1.0.0
```

### Step 2: Create Namespace

```bash
kubectl create namespace foundation-prod
```

### Step 3: Configure Secrets

```bash
# Create secrets from .env file
kubectl create secret generic foundation-secrets \
  --from-env-file=.env.production \
  --namespace=foundation-prod

# Or create secrets individually
kubectl create secret generic foundation-secrets \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=REDIS_URL='redis://...' \
  --from-literal=STRIPE_SECRET_KEY='sk_live_...' \
  --namespace=foundation-prod
```

### Step 4: Deploy Database (RDS recommended for production)

For testing or small deployments, use PostgreSQL in Kubernetes:

```bash
kubectl apply -f kubernetes/database/postgresql.yaml -n foundation-prod
```

**Production Recommendation:** Use managed database services:
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Database

### Step 5: Deploy Redis

For testing or small deployments:

```bash
kubectl apply -f kubernetes/redis/redis.yaml -n foundation-prod
```

**Production Recommendation:** Use managed Redis:
- AWS ElastiCache
- Google Cloud Memorystore
- Azure Cache for Redis
- Redis Cloud

### Step 6: Deploy Application

```bash
# Update image in deployment.yaml
kubectl apply -f kubernetes/base/deployment.yaml -n foundation-prod

# Apply service
kubectl apply -f kubernetes/base/service.yaml -n foundation-prod

# Apply ingress
kubectl apply -f kubernetes/base/ingress.yaml -n foundation-prod
```

### Step 7: Run Migrations

```bash
# Create migration job
kubectl apply -f kubernetes/jobs/migrate.yaml -n foundation-prod

# Check migration status
kubectl logs -f jobs/migrate -n foundation-prod

# Or run migrations manually
kubectl exec -it deployment/foundation-web -n foundation-prod -- \
  python manage.py migrate
```

### Step 8: Create Superuser

```bash
kubectl exec -it deployment/foundation-web -n foundation-prod -- \
  python manage.py createsuperuser
```

### Step 9: Collect Static Files

```bash
kubectl exec -it deployment/foundation-web -n foundation-prod -- \
  python manage.py collectstatic --no-input
```

### Step 10: Verify Deployment

```bash
# Check pods are running
kubectl get pods -n foundation-prod

# Check services
kubectl get services -n foundation-prod

# Check ingress
kubectl get ingress -n foundation-prod

# View logs
kubectl logs -f deployment/foundation-web -n foundation-prod
```

### Kubernetes Configuration Example

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: foundation-web
  namespace: foundation-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: foundation
      component: web
  template:
    metadata:
      labels:
        app: foundation
        component: web
    spec:
      containers:
      - name: web
        image: your-registry/foundation:v1.0.0
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: foundation-secrets
        env:
        - name: DEBUG
          value: "False"
        - name: ALLOWED_HOSTS
          value: "api.yourcompany.com"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/live/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: foundation-celery-worker
  namespace: foundation-prod
spec:
  replicas: 5
  selector:
    matchLabels:
      app: foundation
      component: celery-worker
  template:
    metadata:
      labels:
        app: foundation
        component: celery-worker
    spec:
      containers:
      - name: celery-worker
        image: your-registry/foundation:v1.0.0
        command: ["celery", "-A", "foundation", "worker", "-l", "info"]
        envFrom:
        - secretRef:
            name: foundation-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: foundation-celery-beat
  namespace: foundation-prod
spec:
  replicas: 1  # Must be exactly 1
  selector:
    matchLabels:
      app: foundation
      component: celery-beat
  template:
    metadata:
      labels:
        app: foundation
        component: celery-beat
    spec:
      containers:
      - name: celery-beat
        image: your-registry/foundation:v1.0.0
        command: ["celery", "-A", "foundation", "beat", "-l", "info"]
        envFrom:
        - secretRef:
            name: foundation-secrets
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: foundation-web
  namespace: foundation-prod
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: foundation
    component: web
```

**ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: foundation-ingress
  namespace: foundation-prod
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourcompany.com
    secretName: foundation-tls
  rules:
  - host: api.yourcompany.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: foundation-web
            port:
              number: 80
```

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: foundation-web-hpa
  namespace: foundation-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: foundation-web
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🐳 Docker Compose Deployment

### Production Docker Compose Setup

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  web:
    image: your-registry/foundation:v1.0.0
    command: gunicorn foundation.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    restart: always
    networks:
      - foundation-network

  celery_worker:
    image: your-registry/foundation:v1.0.0
    command: celery -A foundation worker -l info --concurrency=4
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    restart: always
    networks:
      - foundation-network

  celery_beat:
    image: your-registry/foundation:v1.0.0
    command: celery -A foundation beat -l info
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    restart: always
    networks:
      - foundation-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - web
    restart: always
    networks:
      - foundation-network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: foundation
      POSTGRES_USER: foundation
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    restart: always
    networks:
      - foundation-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always
    networks:
      - foundation-network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  foundation-network:
    driver: bridge
```

### Nginx Configuration

**nginx/nginx.conf:**
```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name api.yourcompany.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourcompany.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### Deploy with Docker Compose

```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 🌩️ AWS Deployment with Terraform

### Infrastructure as Code

The repository includes Terraform configurations for AWS deployment.

### Prerequisites

- AWS account with appropriate permissions
- Terraform 1.0+ installed
- AWS CLI configured

### Step 1: Configure Terraform Variables

**terraform/terraform.tfvars:**
```hcl
project_name = "foundation"
environment  = "production"
region       = "us-east-1"

# VPC
vpc_cidr = "10.0.0.0/16"

# RDS
db_instance_class    = "db.t3.large"
db_allocated_storage = 100
db_name              = "foundation"
db_username          = "foundation_admin"

# ElastiCache
redis_node_type       = "cache.t3.medium"
redis_num_cache_nodes = 2

# EKS (optional)
eks_cluster_version = "1.28"
eks_node_instance_types = ["t3.large"]
eks_desired_capacity = 3
eks_min_capacity     = 2
eks_max_capacity     = 10
```

### Step 2: Initialize and Apply Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Get outputs
terraform output
```

### Step 3: Configure Application

```bash
# Get database endpoint
export DB_HOST=$(terraform output -raw db_endpoint)

# Get Redis endpoint
export REDIS_HOST=$(terraform output -raw redis_endpoint)

# Get S3 bucket name
export AWS_STORAGE_BUCKET_NAME=$(terraform output -raw s3_bucket_name)

# Update your .env.production with these values
```

## 🔒 Security Configuration

### Environment Variables

**Critical settings for production:**

```bash
# Django settings
SECRET_KEY='your-very-long-random-secret-key'  # Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
DEBUG=False
ALLOWED_HOSTS='api.yourcompany.com,yourcompany.com'

# Database
DATABASE_URL='postgresql://user:password@host:5432/dbname'

# Redis
REDIS_URL='redis://host:6379/0'

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS (adjust for your frontend domain)
CORS_ALLOWED_ORIGINS='https://app.yourcompany.com,https://yourcompany.com'

# Email
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.sendgrid.net'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='apikey'
EMAIL_HOST_PASSWORD='your-sendgrid-api-key'
DEFAULT_FROM_EMAIL='noreply@yourcompany.com'

# Storage (S3)
USE_S3=True
AWS_ACCESS_KEY_ID='your-access-key'
AWS_SECRET_ACCESS_KEY='your-secret-key'
AWS_STORAGE_BUCKET_NAME='your-bucket-name'
AWS_S3_REGION_NAME='us-east-1'

# Stripe
STRIPE_SECRET_KEY='sk_live_...'
STRIPE_PUBLISHABLE_KEY='pk_live_...'
STRIPE_WEBHOOK_SECRET='whsec_...'

# Monitoring
SENTRY_DSN='https://...@sentry.io/...'

# Rate limiting
RATELIMIT_ENABLE=True
```

### Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (never commit to git)
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] Secure cookies enabled
- [ ] HSTS enabled with long max-age
- [ ] CORS configured for specific domains only
- [ ] Database credentials secured
- [ ] API keys stored in secrets manager
- [ ] Rate limiting enabled
- [ ] File uploads restricted by size and type
- [ ] Regular security audits scheduled

## 📊 Monitoring & Logging

### Prometheus & Grafana

The foundation exposes Prometheus metrics at `/metrics/`.

**Deploy monitoring stack:**

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# Access Grafana (default: admin/prom-operator)
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

**Import Dashboard:**

Use the pre-built Grafana dashboard at `docs/deployment/grafana-dashboard.json`.

### Application Logging

Configure structured logging:

```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### Error Tracking with Sentry

```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment='production',
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**.github/workflows/deploy.yml:**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements/dev.txt
      - name: Run tests
        run: pytest --cov
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/postgres
          REDIS_URL: redis://localhost:6379/0

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -f Dockerfile.prod -t ${{ secrets.REGISTRY }}/foundation:${{ github.sha }} .
      - name: Push to registry
        run: |
          echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
          docker push ${{ secrets.REGISTRY }}/foundation:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          echo "${{ secrets.KUBECONFIG }}" > kubeconfig
          kubectl --kubeconfig=kubeconfig set image deployment/foundation-web \
            web=${{ secrets.REGISTRY }}/foundation:${{ github.sha }} \
            --namespace=foundation-prod
          kubectl --kubeconfig=kubeconfig rollout status deployment/foundation-web \
            --namespace=foundation-prod
```

## 💾 Backup & Disaster Recovery

### Database Backups

**Automated PostgreSQL Backups:**

```bash
# CronJob for daily backups
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: foundation-prod
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              pg_dump $DATABASE_URL | gzip > /backup/foundation-$(date +%Y%m%d).sql.gz
              aws s3 cp /backup/foundation-$(date +%Y%m%d).sql.gz s3://your-backup-bucket/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: foundation-secrets
                  key: DATABASE_URL
          restartPolicy: OnFailure
```

**Backup Retention:**
- Daily backups: Keep for 7 days
- Weekly backups: Keep for 4 weeks
- Monthly backups: Keep for 12 months

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 4 hours
2. **RPO (Recovery Point Objective)**: 24 hours

**Recovery Steps:**

```bash
# 1. Restore database from backup
pg_restore --dbname=foundation --clean backup.sql

# 2. Redeploy application
kubectl rollout restart deployment/foundation-web -n foundation-prod

# 3. Verify health
kubectl get pods -n foundation-prod
curl https://api.yourcompany.com/health/

# 4. Check logs
kubectl logs -f deployment/foundation-web -n foundation-prod
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_accounts_organization_slug ON accounts_organization(slug);
CREATE INDEX idx_billing_subscription_status ON billing_subscription(status);
CREATE INDEX idx_notifications_recipient ON notifications_notification(recipient_id, is_read);

-- Enable connection pooling with PgBouncer
-- Recommended settings:
-- pool_mode = transaction
-- max_client_conn = 1000
-- default_pool_size = 25
```

### Redis Configuration

```conf
# redis.conf for production
maxmemory 2gb
maxmemory-policy allkeys-lru
appendonly yes
appendfsync everysec
```

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 4
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

## 🔍 Health Checks

The foundation provides multiple health check endpoints:

```bash
# Liveness probe (is the app running?)
curl https://api.yourcompany.com/health/live/

# Readiness probe (is the app ready to serve traffic?)
curl https://api.yourcompany.com/health/ready/

# Detailed health check
curl https://api.yourcompany.com/health/
```

## 🚨 Troubleshooting

### Common Issues

**Issue: Pods are CrashLooping**
```bash
# Check logs
kubectl logs deployment/foundation-web -n foundation-prod

# Common causes:
# - Database connection failure
# - Missing environment variables
# - Migrations not run
```

**Issue: High response times**
```bash
# Check database connection pool
kubectl exec -it deployment/foundation-web -n foundation-prod -- \
  python manage.py shell -c "from django.db import connection; print(connection.queries)"

# Check Redis connection
kubectl exec -it deployment/redis -n foundation-prod -- redis-cli INFO stats
```

**Issue: Out of memory errors**
```bash
# Check memory usage
kubectl top pods -n foundation-prod

# Increase resource limits in deployment.yaml
```

## 📞 Support

### Enterprise Support

For Enterprise and White Label license holders:

- **Email**: support@yourcompany.com
- **Phone**: +1 (555) 123-4567
- **Slack**: Access to dedicated support channel
- **SLA**: 4-hour response time (1-hour for White Label)

### Community Support

For Open Source users:

- **GitHub Issues**: https://github.com/yourusername/enterprise-saas-backend/issues
- **Discussions**: https://github.com/yourusername/enterprise-saas-backend/discussions
- **Discord**: https://discord.gg/yourserver

## 📚 Additional Resources

- [Architecture Guide](ARCHITECTURE.md) - System design and architecture
- [Getting Started](GETTING_STARTED.md) - Development setup
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Features](FEATURES.md) - Detailed feature documentation

---

**Ready to deploy?** Follow this guide step-by-step, and you'll have a production-ready SaaS backend in no time! 🚀

For assistance with deployment, [contact our team](mailto:support@yourcompany.com).
