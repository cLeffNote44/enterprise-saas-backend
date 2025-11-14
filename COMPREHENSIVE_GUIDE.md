# Enterprise SaaS Backend Foundation - Comprehensive Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Core Features](#core-features)
4. [API Reference](#api-reference)
5. [Deployment](#deployment)
6. [Development](#development)
7. [Testing](#testing)
8. [Contributing](#contributing)

## Quick Start

### Prerequisites
- Docker Desktop 4.0+
- Python 3.11+ (for local development)
- Git 2.0+
- 8GB RAM minimum (16GB recommended)

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/enterprise-saas-backend.git
cd enterprise-saas-backend

# 2. Copy environment file
cp .env.docker.example .env

# 3. Start all services
docker compose up -d

# 4. Run migrations
docker compose exec web sh -c "cd foundation && python manage.py migrate"

# 5. Create superuser
docker compose exec web sh -c "cd foundation && python manage.py createsuperuser"

# 6. Access the application
# Admin: http://localhost:8000/admin
# API Docs: http://localhost:8000/api/docs
# Health: http://localhost:8000/health/
```

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer/CDN                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Django Application Layer                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Accounts  │ │ Billing  │ │Compliance│ │Analytics │      │
│  │  RBAC    │ │ Stripe   │ │  GDPR    │ │ Insights │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Notificat │ │  Files   │ │  Search  │ │  Flags   │      │
│  │ions      │ │          │ │          │ │          │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────┬───────────┬───────────┬───────────────────────────┘
          │           │           │
    ┌─────▼─────┐ ┌──▼──┐ ┌─────▼─────┐
    │PostgreSQL │ │Redis│ │   MinIO    │
    │   15      │ │  7  │ │  (S3)      │
    └───────────┘ └─────┘ └───────────┘
          │           │           │
    ┌─────▼─────────────────────▼─────┐
    │      Celery Workers & Beat       │
    └──────────────────────────────────┘
```

### Multi-Tenant Architecture

```
Organization A                Organization B
     │                             │
     ├── Department 1              ├── Department X
     │   ├── User A1               │   ├── User B1
     │   └── User A2               │   └── User B2
     └── Department 2              └── Department Y
         ├── User A3                   ├── User B3
         └── User A4                   └── User B4

Data Isolation:
- Row-level: organization_id on every table
- Department-based: hierarchical access control
- Role-based: fine-grained permissions
```

## Core Features

### 1. Authentication & Authorization

#### Multi-Factor Authentication (MFA)
```python
from foundation.apps.accounts.security import MFAManager

# Enable MFA for user
manager = MFAManager(user)
qr_code, backup_codes = manager.setup_totp()

# Verify MFA token
is_valid = manager.verify_totp(token='123456')
```

#### API Key Management
```python
from foundation.apps.accounts.models import APIKey

# Generate API key
api_key = APIKey.generate_key(
    organization=org,
    name="Production API Key",
    expires_days=90
)
print(api_key.key)  # Display this once!
```

#### Role-Based Access Control
```python
# Check permissions
from foundation.apps.accounts.permissions import IsDataManager

class MyView(APIView):
    permission_classes = [IsAuthenticated, IsDataManager]
```

### 2. Billing & Subscriptions

#### Stripe Integration
```python
from foundation.apps.billing.models import Subscription

# Create subscription
subscription = Subscription.objects.create(
    organization=org,
    plan=plan,
    stripe_customer_id='cus_xxx'
)

# Check if active
if subscription.is_active():
    # Allow access
    pass
```

#### Usage-Based Billing
```python
from foundation.apps.billing.models import UsageRecord

# Track usage
UsageRecord.objects.create(
    organization=org,
    subscription=subscription,
    metric='api_calls',
    quantity=1000,
    period_start=period_start,
    period_end=period_end
)
```

### 3. Notifications

#### Send Multi-Channel Notification
```python
from foundation.apps.notifications.models import Notification

# Create notification
notification = Notification.objects.create(
    recipient=user,
    title="Payment Received",
    message="Your payment of $99 has been processed.",
    category='billing',
    priority='high',
    action_url='/billing/invoices/123'
)

# Will be sent via channels based on user preferences
```

#### Custom Notification Templates
```python
from foundation.apps.notifications.models import NotificationTemplate

template = NotificationTemplate.objects.create(
    name='welcome_email',
    channel='email',
    subject='Welcome to {{organization_name}}!',
    body_html='<h1>Welcome {{user_name}}!</h1>',
    available_variables=['user_name', 'organization_name']
)
```

### 4. Feature Flags & A/B Testing

#### Feature Flag Usage
```python
from foundation.apps.feature_flags.models import FeatureFlag

# Check if enabled
flag = FeatureFlag.objects.get(key='new_dashboard')
if flag.is_enabled_for_user(user):
    # Show new dashboard
    pass
```

#### A/B Testing
```python
from foundation.apps.feature_flags.models import Experiment

# Get variant
experiment = Experiment.objects.get(key='checkout_flow')
variant = experiment.get_variant_for_user(user)

if variant.key == 'variant_a':
    # Show variant A
    pass
elif variant.key == 'variant_b':
    # Show variant B
    pass
```

### 5. File Management

```python
from foundation.apps.files.models import File

# Upload file
file_obj = File.objects.create(
    organization=org,
    uploaded_by=user,
    name='document.pdf',
    file=uploaded_file,
    size_bytes=uploaded_file.size
)

# Share file
from foundation.apps.files.models import FileShare

FileShare.objects.create(
    file=file_obj,
    shared_with_user=recipient,
    permission='view',
    expires_at=timezone.now() + timedelta(days=7)
)
```

### 6. Compliance

#### GDPR Data Subject Requests
```python
from foundation.apps.compliance.models import DataSubjectRequest

# Create request
dsr = DataSubjectRequest.objects.create(
    organization=org,
    request_type='access',
    data_subject_email='user@example.com',
    description='Request for all my personal data'
)

# Process (generates JSON export)
result = dsr.process_request()
```

#### Audit Trails
```python
from foundation.apps.audit.models import ChangeHistory

# Automatically tracked via signals
# Query changes
changes = ChangeHistory.objects.filter(
    content_type=ContentType.objects.get_for_model(Invoice),
    object_id=invoice.id
).order_by('-timestamp')
```

## API Reference

### Authentication

All API requests require authentication. Supported methods:

1. **Session Authentication** (for web apps)
```javascript
// Login first, then use cookies
```

2. **JWT Authentication**
```bash
# Get tokens
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Use access token
curl http://localhost:8000/api/accounts/ \
  -H "Authorization: Bearer <access_token>"
```

3. **API Key Authentication**
```bash
curl http://localhost:8000/api/billing/invoices/ \
  -H "Authorization: Bearer <api_key>"
```

### Common Endpoints

#### Accounts
- `GET /api/accounts/api/organizations/` - List organizations
- `GET /api/accounts/api/permissions/` - List permissions
- `POST /api/accounts/auth/mfa/setup/` - Setup MFA

#### Billing
- `GET /api/billing/plans/` - List subscription plans
- `GET /api/billing/subscriptions/` - List subscriptions
- `POST /api/billing/subscriptions/{id}/cancel/` - Cancel subscription
- `GET /api/billing/invoices/` - List invoices

#### Notifications
- `GET /api/notifications/notifications/` - List notifications
- `POST /api/notifications/notifications/{id}/mark_read/` - Mark as read
- `GET /api/notifications/preferences/me/` - Get preferences

#### Feature Flags
- `GET /api/feature-flags/flags/my_flags/` - Get all flags for user
- `GET /api/feature-flags/flags/{id}/check/` - Check specific flag

#### Files
- `POST /api/files/files/` - Upload file
- `GET /api/files/files/` - List files
- `GET /api/files/shares/` - List shared files

#### Search
- `GET /api/search/search/query/?q=searchterm` - Search
- `POST /api/search/saved/` - Save search

### Pagination

All list endpoints support pagination:

```bash
GET /api/billing/invoices/?page=2&page_size=50
```

Response:
```json
{
  "count": 200,
  "next": "http://localhost:8000/api/billing/invoices/?page=3",
  "previous": "http://localhost:8000/api/billing/invoices/?page=1",
  "results": [...]
}
```

### Filtering

Most endpoints support filtering:

```bash
GET /api/billing/invoices/?status=paid&created_at__gte=2024-01-01
GET /api/notifications/notifications/?category=billing&priority=high
```

## Deployment

### Docker Production

```bash
# Build production image
docker build --target runtime -t myapp:latest .

# Run with production settings
docker run -d \
  --env-file .env.production \
  -p 8000:8000 \
  myapp:latest
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f kubernetes/

# Or use Helm
helm install myapp ./kubernetes/charts/enterprise-saas
```

### Environment Variables

Required for production:

```bash
# Security
DJANGO_SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=myapp.com,www.myapp.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Cache & Celery
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx

# Email
SENDGRID_API_KEY=SG.xxx

# SMS
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1xxx
```

## Development

### Creating Custom Apps

```python
# myproject/settings.py
from foundation.config.settings.base import *

PROJECT_EXTENSIONS = [
    'extensions.products',  # Your app
    'extensions.orders',    # Your app
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + FOUNDATION_APPS + PROJECT_EXTENSIONS
```

### Using Foundation Models

```python
# extensions/products/models.py
from django.db import models
from foundation.apps.accounts.models import Organization

class Product(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

## Testing

### Running Tests

```bash
# All tests
docker compose exec web sh -c "cd foundation && python manage.py test"

# With coverage
docker compose exec web sh -c "cd foundation && coverage run manage.py test && coverage report"

# Specific app
docker compose exec web sh -c "cd foundation && python manage.py test foundation.apps.billing"
```

### Writing Tests

```python
from django.test import TestCase
from foundation.apps.billing.models import SubscriptionPlan

class SubscriptionPlanTestCase(TestCase):
    def test_plan_creation(self):
        plan = SubscriptionPlan.objects.create(
            name="Pro Plan",
            tier="professional",
            price=99.00
        )
        self.assertEqual(str(plan), "Pro Plan (Monthly)")
```

## Performance Best Practices

### Database Optimization
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many
- Add indexes for frequently queried fields
- Use database-level constraints

### Caching
```python
from django.core.cache import cache

# Cache expensive queries
data = cache.get('expensive_query')
if data is None:
    data = expensive_query()
    cache.set('expensive_query', data, 300)  # 5 minutes
```

### Async Tasks
```python
from foundation.tasks import send_email_task

# Don't block the request
send_email_task.delay(user_id=user.id, template='welcome')
```

## Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up regular backups
- [ ] Enable MFA for admins
- [ ] Review and configure permissions
- [ ] Set up monitoring and alerts
- [ ] Configure log retention

## Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check database is running
docker compose ps db

# Check connection
docker compose exec db pg_isready

# View logs
docker compose logs db
```

**Migrations out of sync**
```bash
# Reset migrations (development only!)
docker compose exec web sh -c "cd foundation && python manage.py migrate --fake-initial"
```

**Permission denied errors**
- Check user has correct organization membership
- Verify role has required permissions
- Check data access policies

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- Documentation: https://docs.example.com
- Issues: https://github.com/yourorg/enterprise-saas-backend/issues
- Email: support@yourcompany.com
