# Enterprise SaaS Backend Foundation
## Comprehensive User Guide

---

### Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Prerequisites and Installation](#prerequisites-and-installation)
4. [Initial Setup and Configuration](#initial-setup-and-configuration)
5. [Basic Operations](#basic-operations)
6. [User Management](#user-management)
7. [Organization and Multi-Tenancy](#organization-and-multi-tenancy)
8. [Security Features](#security-features)
9. [API Usage](#api-usage)
10. [Analytics and Monitoring](#analytics-and-monitoring)
11. [Compliance Features](#compliance-features)
12. [Advanced Configuration](#advanced-configuration)
13. [Development and Extensions](#development-and-extensions)
14. [Production Deployment](#production-deployment)
15. [Troubleshooting Guide](#troubleshooting-guide)
16. [Common Issues and Solutions](#common-issues-and-solutions)

---

## 1. Introduction

### What is the Enterprise SaaS Backend Foundation?

The Enterprise SaaS Backend Foundation is a comprehensive, production-ready Django-based backend framework designed specifically for building enterprise-grade Software as a Service (SaaS) applications. It provides all the essential components needed to create secure, scalable, and compliant SaaS platforms.

### Key Benefits

- **🚀 Rapid Development**: Skip months of infrastructure development and focus on your unique business logic
- **🔒 Enterprise Security**: Built-in MFA, API key management, role-based access control, and security headers
- **🏢 Multi-Tenant Architecture**: Complete organization management with roles, permissions, and isolation
- **📊 Analytics Ready**: User tracking, engagement metrics, and usage analytics out of the box
- **⚖️ Compliance Framework**: GDPR, HIPAA, SOC2 compliance features including audit logging
- **🛡️ Content Moderation**: Automated content scanning and policy enforcement
- **📡 API First**: Complete REST API with auto-generated documentation
- **🧪 Production Ready**: Comprehensive testing, monitoring, and deployment configurations

### Who Should Use This Guide?

- **Developers** building SaaS applications
- **DevOps Engineers** deploying and maintaining the platform
- **Product Managers** understanding capabilities and features
- **System Administrators** configuring and managing the system

---

## 2. System Overview

### Architecture Overview

The foundation follows a modular, app-based architecture with clear separation of concerns:

```
Enterprise SaaS Foundation
│
├── 🏗️ Core Infrastructure
│   ├── Authentication & Authorization
│   ├── Multi-Tenant Organizations
│   ├── Security & Compliance
│   └── Performance & Caching
│
├── 📊 Analytics & Monitoring
│   ├── User Activity Tracking
│   ├── Usage Metrics
│   ├── Performance Monitoring
│   └── Audit Logging
│
├── 💬 Communication
│   ├── Real-time Messaging
│   ├── Email Integration
│   ├── Notifications
│   └── WebSocket Support
│
├── 🛡️ Content & Security
│   ├── Content Moderation
│   ├── Policy Enforcement
│   ├── Threat Detection
│   └── Data Classification
│
└── 🔌 Extensions & Integration
    ├── Custom App Support
    ├── Third-party Integrations
    ├── Workflow Automation
    └── Plugin Architecture
```

### Technology Stack

**Backend Framework:**
- Django 5.0+ (Python web framework)
- Django REST Framework (API development)
- Channels (WebSocket support)

**Database:**
- PostgreSQL (recommended for production)
- SQLite (development/testing)

**Caching & Performance:**
- Redis (caching, sessions, real-time features)
- Django-Redis (Redis integration)

**Security:**
- Django-OTP (Multi-factor authentication)
- Django-Allauth (Social authentication)
- Django-Axes (Brute force protection)
- Custom API key management

**Compliance & Auditing:**
- Django-Auditlog (Audit trails)
- Custom compliance modules
- Data retention policies

**API Documentation:**
- DRF Spectacular (OpenAPI/Swagger)
- Auto-generated documentation

### Core Apps Structure

**Accounts App** (`foundation.apps.accounts`)
- User management and authentication
- API key management
- Security profiles and MFA
- Enterprise features (organizations, roles)

**Analytics App** (`foundation.apps.analytics`)
- User activity tracking
- Usage metrics and reporting
- Performance monitoring
- Custom analytics events

**Compliance App** (`foundation.apps.compliance`)
- GDPR, HIPAA, SOC2 features
- Data subject rights
- Audit logging
- Policy management

**Messaging App** (`foundation.apps.messaging`)
- Real-time notifications
- Email integration
- In-app messaging
- Communication templates

**Moderation App** (`foundation.apps.moderation`)
- Content scanning
- Policy enforcement
- Automated moderation
- Manual review workflows

**Core App** (`foundation.apps.core`)
- Shared utilities and models
- Security middleware
- Base classes and mixins
- Common functionality

---

## 3. Prerequisites and Installation

### System Requirements

**Minimum Requirements:**
- Python 3.11 or higher
- 4GB RAM
- 10GB available disk space
- Internet connection for package installation

**Recommended for Production:**
- Python 3.11+
- 8GB+ RAM
- 50GB+ SSD storage
- Redis server
- PostgreSQL database

### Required Software

Before installing the foundation, ensure you have these components installed:

#### 1. Python Installation

**Windows:**
1. Download Python from [python.org](https://python.org)
2. Run installer with "Add Python to PATH" checked
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
pip3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
python3.11 --version
```

#### 2. Redis Installation (Recommended)

**Windows:**
1. Download Redis from [GitHub releases](https://github.com/microsoftarchive/redis/releases)
2. Install and start Redis service
3. Test: `redis-cli ping` (should return "PONG")

**macOS:**
```bash
brew install redis
brew services start redis
redis-cli ping
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
redis-cli ping
```

#### 3. PostgreSQL (Production)

**Windows:**
1. Download from [postgresql.org](https://postgresql.org)
2. Install with default settings
3. Remember the superuser password

**macOS:**
```bash
brew install postgresql
brew services start postgresql
createdb foundation_db
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Foundation Installation

#### Step 1: Clone or Download the Foundation

```bash
# If using Git
git clone <repository-url> enterprise-saas-foundation
cd enterprise-saas-foundation

# Or download and extract ZIP file
```

#### Step 2: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your command prompt, indicating the virtual environment is active.

#### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install foundation dependencies
pip install -r requirements.txt
```

**Common Installation Issues:**
- If you get permission errors, ensure you're in the virtual environment
- For compilation errors on Windows, install Microsoft Visual C++ Build Tools
- On macOS, you may need Xcode command line tools: `xcode-select --install`

#### Step 4: Verify Installation

Run the foundation test to verify everything is working:

```bash
python test_foundation.py
```

You should see output similar to:
```
✅ Database connection successful
✅ User creation successful  
✅ Organization creation successful
✅ API key generation successful
✅ All foundation tests passed!
```

---

## 4. Initial Setup and Configuration

### Environment Configuration

#### Step 1: Create Environment File

Create a `.env` file in your project root:

**For Development:**
```bash
# Copy the example environment file
cp .env.example .env
```

**Basic .env Configuration:**
```env
# Security
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
DEBUG=True

# Database (Development - uses SQLite by default)
# DATABASE_URL=sqlite:///db.sqlite3

# Redis (Optional for development)
REDIS_URL=redis://localhost:6379/0

# Email (Optional for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Allowed hosts
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generate a Secure Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Step 2: Database Setup

**Initialize the Database:**
```bash
# Run initial migrations
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser
```

Follow the prompts to create your admin account:
```
Username: admin
Email address: admin@yourcompany.com
Password: [secure password]
```

#### Step 3: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### Step 4: Verify Setup

**Start the Development Server:**
```bash
python manage.py runserver
```

**Test the Installation:**

1. **Admin Interface**: Visit `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials
   - You should see the Django admin interface

2. **API Documentation**: Visit `http://127.0.0.1:8000/api/docs/`
   - You should see the Swagger API documentation

3. **Health Check**: Visit `http://127.0.0.1:8000/api/health/`
   - Should return: `{"status": "healthy"}`

### System Configuration

#### Django Settings Structure

The foundation uses environment-based settings:

```
foundation/config/settings/
├── base.py          # Base configuration (shared settings)
├── development.py   # Development-specific settings
├── production.py    # Production-specific settings
└── testing.py       # Test-specific settings
```

**Setting the Environment:**
```bash
# Development (default)
export DJANGO_SETTINGS_MODULE=foundation.config.settings.development

# Production
export DJANGO_SETTINGS_MODULE=foundation.config.settings.production
```

#### Feature Configuration

The foundation includes configurable features that can be enabled/disabled:

**In your settings or .env:**
```python
# Feature flags
FEATURE_FLAGS = {
    'analytics_enabled': True,
    'content_moderation': True,
    'real_time_messaging': True,
    'advanced_compliance': False,
    'mfa_required': False,
    'api_rate_limiting': True,
}

# Usage limits per organization tier
USAGE_LIMITS = {
    'free': {
        'users': 5,
        'api_calls_per_month': 1000,
        'storage_mb': 100
    },
    'starter': {
        'users': 25,
        'api_calls_per_month': 10000,
        'storage_mb': 1000
    },
    'professional': {
        'users': 100,
        'api_calls_per_month': 100000,
        'storage_mb': 10000
    },
    'enterprise': {
        'users': -1,  # Unlimited
        'api_calls_per_month': -1,  # Unlimited
        'storage_mb': -1  # Unlimited
    }
}
```

---

## 5. Basic Operations

### Starting the System

#### Development Server

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Start the server
python manage.py runserver

# Start on different port
python manage.py runserver 8080

# Start on all interfaces (be careful in production)
python manage.py runserver 0.0.0.0:8000
```

#### Background Tasks (Optional)

If using Celery for background tasks:

```bash
# In a separate terminal, start Celery worker
celery -A foundation.config worker -l info

# Start Celery beat for scheduled tasks
celery -A foundation.config beat -l info
```

### Initial Data Setup

#### Creating Organizations

Organizations are the core of the multi-tenant architecture. Here's how to create them:

**Via Django Admin:**
1. Go to `http://127.0.0.1:8000/admin/`
2. Navigate to "Accounts" → "Organizations"
3. Click "Add Organization"
4. Fill in the required fields:
   - Name: "Acme Corporation"
   - Slug: "acme-corp" (auto-generated)
   - Subscription Tier: "professional"
   - Primary Contact Email: "admin@acme.com"

**Via Python Shell:**
```bash
python manage.py shell
```

```python
from foundation.apps.accounts.enterprise import Organization

# Create organization
org = Organization.objects.create(
    name="Acme Corporation",
    slug="acme-corp",
    subscription_tier="professional",
    primary_contact_email="admin@acme.com",
    settings={
        "features_enabled": ["analytics", "moderation"],
        "branding": {
            "primary_color": "#007bff",
            "logo_url": ""
        }
    }
)
print(f"Created organization: {org.name}")
```

#### Adding Users to Organizations

**Via Python Shell:**
```python
from django.contrib.auth.models import User
from foundation.apps.accounts.enterprise import Organization, OrganizationMembership

# Get user and organization
user = User.objects.get(username='admin')
org = Organization.objects.get(slug='acme-corp')

# Create membership
membership = OrganizationMembership.objects.create(
    user=user,
    organization=org,
    is_admin=True,
    role='admin'
)
print(f"Added {user.username} to {org.name} as admin")
```

### System Health Checks

#### Django System Checks

```bash
# Run all system checks
python manage.py check

# Run deployment checks (production settings)
python manage.py check --deploy

# Check specific apps
python manage.py check accounts
```

#### Database Health

```bash
# Check database connectivity
python manage.py dbshell
# Type \q to exit PostgreSQL or .exit for SQLite

# Show migration status
python manage.py showmigrations

# Check for pending migrations
python manage.py migrate --check
```

#### Foundation Health Test

```bash
# Run comprehensive foundation tests
python test_foundation.py

# Expected output shows all components working:
# ✅ Database connection successful
# ✅ User creation successful  
# ✅ Organization creation successful
# ✅ API key generation successful
# ✅ All foundation tests passed!
```

### Daily Operations

#### Viewing Logs

**Development Logs:**
```bash
# View Django server logs (in the terminal where runserver is running)
# Logs appear in real-time

# For file-based logging (if configured):
tail -f logs/django.log
tail -f logs/error.log
```

#### Database Operations

```bash
# Create database backup
python manage.py dumpdata > backup.json

# Restore from backup
python manage.py loaddata backup.json

# Clear all data (be careful!)
python manage.py flush
```

#### Cache Operations

```bash
# Clear Redis cache (if using Redis)
python manage.py shell -c "
from django.core.cache import cache
cache.clear()
print('Cache cleared!')
"
```

---

## 6. User Management

### User Registration and Authentication

#### Creating Users

**Via Django Admin:**
1. Navigate to `http://127.0.0.1:8000/admin/auth/user/`
2. Click "Add User"
3. Enter username and password
4. Click "Save and continue editing"
5. Fill in additional details (email, first name, last name)
6. Set permissions and group memberships

**Via API:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Via Python Code:**
```python
from django.contrib.auth.models import User
from foundation.apps.accounts.models import UserSecurityProfile

# Create user
user = User.objects.create_user(
    username='johndoe',
    email='john@example.com',
    password='SecurePassword123!',
    first_name='John',
    last_name='Doe'
)

# Security profile is created automatically via signals
profile = user.security_profile
print(f"User created with profile: {profile}")
```

#### User Authentication

**API Authentication Methods:**

1. **Session Authentication** (web interface):
   ```bash
   # Login via API
   curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "johndoe", "password": "SecurePassword123!"}'
   ```

2. **Token Authentication** (mobile/API):
   ```bash
   # Get token
   curl -X POST http://127.0.0.1:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "johndoe", "password": "SecurePassword123!"}'
   
   # Use token
   curl -H "Authorization: Token your-token-here" \
     http://127.0.0.1:8000/api/user/profile/
   ```

3. **API Key Authentication** (service-to-service):
   ```python
   from foundation.apps.accounts.models import APIKey
   
   # Generate API key for user
   api_key, raw_key = APIKey.generate_key(
       user=user,
       name="Mobile App",
       expires_in_days=90
   )
   print(f"API Key: {raw_key}")
   ```

   ```bash
   # Use API key
   curl -H "Authorization: Api-Key your-api-key-here" \
     http://127.0.0.1:8000/api/user/profile/
   ```

### Multi-Factor Authentication (MFA)

#### Enabling MFA for Users

**Via Python Shell:**
```python
from foundation.apps.accounts.models import UserSecurityProfile
from django.contrib.auth.models import User

user = User.objects.get(username='johndoe')
profile = user.security_profile

# Enable MFA
profile.mfa_enabled = True
profile.save()

# Generate TOTP device for authenticator apps
from django_otp.plugins.otp_totp.models import TOTPDevice

device = TOTPDevice.objects.create(
    user=user,
    name='Authenticator App',
    confirmed=True
)

# Get QR code URL for setup
print(f"Setup URL: {device.config_url}")
```

**Via API:**
```bash
# Enable MFA
curl -X POST http://127.0.0.1:8000/api/auth/mfa/enable/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"

# Verify MFA token
curl -X POST http://127.0.0.1:8000/api/auth/mfa/verify/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456"}'
```

#### MFA Login Process

With MFA enabled, the login process becomes:

1. **Standard Login** (username/password)
2. **MFA Challenge** (TOTP/SMS/Email verification)
3. **Access Granted**

```bash
# Step 1: Initial login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "password": "SecurePassword123!"}'

# Response: {"mfa_required": true, "token": "temp-token"}

# Step 2: MFA verification
curl -X POST http://127.0.0.1:8000/api/auth/mfa/verify/ \
  -H "Authorization: Token temp-token" \
  -H "Content-Type: application/json" \
  -d '{"token": "123456"}'

# Response: {"token": "full-access-token"}
```

### User Security Profiles

Each user automatically gets a security profile with additional security features:

**Security Profile Fields:**
- `mfa_enabled`: Multi-factor authentication status
- `failed_login_attempts`: Track login failures
- `last_login_ip`: Track login locations
- `password_expires_at`: Password expiration
- `security_questions`: Additional verification
- `trusted_devices`: Device management

**Managing Security Profiles:**
```python
from foundation.apps.accounts.models import UserSecurityProfile

# Get user's security profile
profile = user.security_profile

# Configure security settings
profile.mfa_enabled = True
profile.password_expires_at = timezone.now() + timedelta(days=90)
profile.save()

# Track login attempts
profile.failed_login_attempts += 1
profile.last_login_ip = '192.168.1.100'
profile.save()
```

### Password Management

#### Password Policies

The foundation includes comprehensive password validation:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

#### Password Reset

**Via API:**
```bash
# Request password reset
curl -X POST http://127.0.0.1:8000/api/auth/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com"}'

# Reset with token (from email)
curl -X POST http://127.0.0.1:8000/api/auth/password/reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "user-id-base64",
    "token": "password-reset-token",
    "new_password1": "NewSecurePassword123!",
    "new_password2": "NewSecurePassword123!"
  }'
```

#### Password Change

```bash
# Change password (authenticated user)
curl -X POST http://127.0.0.1:8000/api/auth/password/change/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "OldPassword123!",
    "new_password1": "NewPassword123!",
    "new_password2": "NewPassword123!"
  }'
```

---

## 7. Organization and Multi-Tenancy

### Understanding Multi-Tenancy

The foundation implements a **shared database, multi-tenant architecture** where:

- **Organizations** are the primary tenant unit
- **Users** can belong to multiple organizations
- **Data** is isolated by organization
- **Features** can be enabled per organization
- **Billing** is handled per organization

### Organization Management

#### Creating Organizations

**Organization Model Fields:**
- `name`: Display name ("Acme Corporation")
- `slug`: URL-friendly identifier ("acme-corp")
- `subscription_tier`: Billing tier ("free", "starter", "professional", "enterprise")
- `is_active`: Organization status
- `settings`: JSON field for custom configuration
- `created_at`, `updated_at`: Timestamps

**Via Admin Interface:**
1. Go to `/admin/accounts/organization/`
2. Click "Add Organization"
3. Fill required fields
4. Configure settings (JSON format):
   ```json
   {
     "features_enabled": ["analytics", "moderation", "messaging"],
     "branding": {
       "primary_color": "#007bff",
       "secondary_color": "#6c757d",
       "logo_url": "https://example.com/logo.png"
     },
     "limits": {
       "max_users": 100,
       "max_storage_mb": 10000
     }
   }
   ```

**Via Python Code:**
```python
from foundation.apps.accounts.enterprise import Organization

org = Organization.objects.create(
    name="Tech Startup Inc",
    slug="tech-startup",
    subscription_tier="professional",
    primary_contact_email="admin@techstartup.com",
    settings={
        "features_enabled": ["analytics", "messaging"],
        "api_rate_limits": {
            "requests_per_minute": 1000,
            "requests_per_day": 50000
        }
    }
)
```

#### Organization Settings and Features

**Feature Management:**
```python
# Check if feature is enabled for organization
def is_feature_enabled(org, feature_name):
    features = org.settings.get('features_enabled', [])
    return feature_name in features

# Enable feature for organization
org = Organization.objects.get(slug='tech-startup')
features = org.settings.get('features_enabled', [])
if 'advanced_analytics' not in features:
    features.append('advanced_analytics')
    org.settings['features_enabled'] = features
    org.save()
```

**Usage Limits:**
```python
# Set usage limits for organization
org.settings['limits'] = {
    'max_users': 250,
    'max_api_calls_per_month': 100000,
    'max_storage_mb': 50000,
    'max_concurrent_connections': 100
}
org.save()
```

### User-Organization Relationships

#### Organization Membership

Users can belong to multiple organizations with different roles:

**OrganizationMembership Model:**
- `user`: Foreign key to User
- `organization`: Foreign key to Organization  
- `role`: User's role in the organization
- `is_admin`: Admin privileges flag
- `is_active`: Membership status
- `joined_at`: Membership start date

**Adding Users to Organizations:**
```python
from foundation.apps.accounts.enterprise import OrganizationMembership

# Add user as admin
membership = OrganizationMembership.objects.create(
    user=user,
    organization=org,
    role='admin',
    is_admin=True
)

# Add user as regular member
membership = OrganizationMembership.objects.create(
    user=user,
    organization=org,
    role='member',
    is_admin=False
)
```

#### User Role Management

**Built-in Roles:**
- `owner`: Organization owner (highest privileges)
- `admin`: Administrative access
- `manager`: Team management access
- `member`: Regular user access
- `viewer`: Read-only access

**Custom Role Management:**
```python
from foundation.apps.accounts.models import Role

# Create custom role
role = Role.objects.create(
    name='data_analyst',
    description='Access to analytics and reporting',
    permissions=[
        'accounts.view_user',
        'analytics.view_usagemetric',
        'analytics.view_userengagement'
    ]
)

# Assign custom role to user
membership = OrganizationMembership.objects.get(
    user=user, organization=org
)
membership.role = 'data_analyst'
membership.save()
```

### Multi-Tenant Data Isolation

#### Automatic Tenant Filtering

The foundation includes middleware and model managers to automatically filter data by organization:

**Tenant-Aware Models:**
```python
from foundation.apps.core.models import TenantAwareModel

class ProjectModel(TenantAwareModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        tenant_field = 'organization'  # Field that determines tenant

# Usage automatically filters by current user's organization
projects = ProjectModel.objects.all()  # Only shows projects for current org
```

**Manual Tenant Filtering:**
```python
# Get current user's organization
def get_user_organization(user):
    try:
        membership = user.organization_memberships.filter(is_active=True).first()
        return membership.organization if membership else None
    except:
        return None

# Filter data by organization
org = get_user_organization(request.user)
if org:
    projects = ProjectModel.objects.filter(organization=org)
```

#### Tenant Context Middleware

The foundation includes middleware to set organization context:

```python
# In views, access current organization
class ProjectListView(APIView):
    def get(self, request):
        # request.organization is set by middleware
        projects = ProjectModel.objects.filter(
            organization=request.organization
        )
        return Response(ProjectSerializer(projects, many=True).data)
```

### Organization Administration

#### Admin Dashboard Features

**Organization Overview:**
- User count and activity
- Resource usage statistics
- Billing and subscription status
- Feature utilization

**User Management:**
- Add/remove users
- Modify roles and permissions
- View user activity logs
- Manage user security settings

**Settings Management:**
- Feature toggles
- Branding customization
- API rate limits
- Integration settings

#### Bulk Operations

**Bulk User Management:**
```python
# Add multiple users to organization
emails = ['user1@company.com', 'user2@company.com', 'user3@company.com']

for email in emails:
    try:
        user = User.objects.get(email=email)
        OrganizationMembership.objects.get_or_create(
            user=user,
            organization=org,
            defaults={'role': 'member', 'is_admin': False}
        )
        print(f"Added {email} to organization")
    except User.DoesNotExist:
        print(f"User {email} not found")
```

**Bulk Feature Management:**
```python
# Enable feature for multiple organizations
orgs = Organization.objects.filter(subscription_tier='enterprise')

for org in orgs:
    features = org.settings.get('features_enabled', [])
    if 'advanced_analytics' not in features:
        features.append('advanced_analytics')
        org.settings['features_enabled'] = features
        org.save()
        print(f"Enabled advanced_analytics for {org.name}")
```

### Organization API

#### REST API Endpoints

**Organization Management:**
```bash
# List user's organizations
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/organizations/

# Get organization details
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/organizations/tech-startup/

# Update organization
curl -X PATCH \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tech Startup Corporation"}' \
  http://127.0.0.1:8000/api/organizations/tech-startup/
```

**Membership Management:**
```bash
# List organization members
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/organizations/tech-startup/members/

# Add member to organization
curl -X POST \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@techstartup.com", "role": "member"}' \
  http://127.0.0.1:8000/api/organizations/tech-startup/members/

# Update member role
curl -X PATCH \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "is_admin": true}' \
  http://127.0.0.1:8000/api/organizations/tech-startup/members/user123/
```

---

## 8. Security Features

### Overview of Security Features

The Enterprise SaaS Foundation includes comprehensive security features designed for enterprise environments:

**Authentication & Authorization:**
- Multi-factor authentication (MFA)
- API key management with rotation
- Role-based access control (RBAC)
- Session security

**Data Protection:**
- Encryption at rest and in transit
- Secure headers and HTTPS enforcement
- Input validation and sanitization
- SQL injection prevention

**Threat Protection:**
- Brute force protection
- Rate limiting
- Content security policy (CSP)
- Cross-site scripting (XSS) prevention

**Compliance & Auditing:**
- Audit logging
- Data retention policies
- Privacy controls
- Compliance reporting

### Multi-Factor Authentication (MFA)

#### Supported MFA Methods

1. **TOTP (Time-based One-Time Passwords)**
   - Google Authenticator, Authy, 1Password
   - 6-digit codes that refresh every 30 seconds

2. **Static Recovery Codes**
   - Backup codes for account recovery
   - One-time use codes

3. **Email-based Codes**
   - Codes sent via email
   - Useful for emergency access

#### Setting Up MFA

**For Users (via API):**
```bash
# Step 1: Enable MFA for user
curl -X POST http://127.0.0.1:8000/api/auth/mfa/enable/ \
  -H "Authorization: Token user-token" \
  -H "Content-Type: application/json"

# Response includes QR code URL and setup key
{
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "setup_key": "ABCD1234EFGH5678",
  "backup_codes": ["12345678", "87654321", ...]
}
```

**For Administrators:**
```python
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice

# Enable TOTP for user
device = TOTPDevice.objects.create(
    user=user,
    name='Primary Authenticator',
    confirmed=False  # User must confirm setup
)

# Generate backup codes
static_device = StaticDevice.objects.create(
    user=user,
    name='Backup Codes'
)

# Create 10 backup codes
for _ in range(10):
    static_device.token_set.create()
```

#### MFA Configuration Options

**Organization-Level MFA Policies:**
```python
# Set MFA requirements per organization
org_settings = {
    "security": {
        "mfa_required": True,
        "mfa_grace_period_days": 7,
        "backup_codes_required": True,
        "allowed_mfa_methods": ["totp", "static"],
        "session_timeout_minutes": 480
    }
}

org.settings.update(org_settings)
org.save()
```

**User Security Profiles:**
```python
from foundation.apps.accounts.models import UserSecurityProfile

# Configure user security settings
profile = user.security_profile
profile.mfa_enabled = True
profile.mfa_backup_codes_used = 0
profile.last_mfa_setup = timezone.now()
profile.save()
```

### API Key Management

API keys provide secure programmatic access to your API without exposing user credentials.

#### Creating API Keys

**Via Python:**
```python
from foundation.apps.accounts.models import APIKey

# Generate API key for user
api_key, raw_key = APIKey.generate_key(
    user=user,
    name="Mobile Application",
    expires_in_days=90,
    permissions=['read', 'write'],
    rate_limit_per_hour=1000
)

print(f"API Key ID: {api_key.id}")
print(f"Raw Key (store securely): {raw_key}")
print(f"Expires: {api_key.expires_at}")
```

**Via API:**
```bash
# Create API key
curl -X POST http://127.0.0.1:8000/api/auth/api-keys/ \
  -H "Authorization: Token user-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App Key",
    "expires_in_days": 90,
    "permissions": ["read", "write"]
  }'

# Response
{
  "id": "key_123456",
  "name": "Mobile App Key",
  "key": "ak_live_abcd1234...",  # Store this securely!
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2024-04-15T10:00:00Z"
}
```

#### Using API Keys

**Authentication Header:**
```bash
# Use API key in requests
curl -H "Authorization: Api-Key ak_live_abcd1234..." \
  http://127.0.0.1:8000/api/user/profile/

# Or use X-API-Key header
curl -H "X-API-Key: ak_live_abcd1234..." \
  http://127.0.0.1:8000/api/data/
```

#### API Key Management

**List API Keys:**
```bash
curl -H "Authorization: Token user-token" \
  http://127.0.0.1:8000/api/auth/api-keys/
```

**Rotate API Key:**
```bash
curl -X POST \
  -H "Authorization: Token user-token" \
  http://127.0.0.1:8000/api/auth/api-keys/key_123456/rotate/

# Returns new key, old key becomes invalid
```

**Revoke API Key:**
```bash
curl -X DELETE \
  -H "Authorization: Token user-token" \
  http://127.0.0.1:8000/api/auth/api-keys/key_123456/
```

### Role-Based Access Control (RBAC)

#### Permission System

The foundation uses Django's built-in permissions extended with custom organization-level permissions:

**Built-in Permission Types:**
- `add_modelname`: Can create instances
- `change_modelname`: Can modify instances
- `delete_modelname`: Can delete instances
- `view_modelname`: Can view instances

**Custom Permissions:**
```python
# In your models
class ProjectModel(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        permissions = [
            ("can_manage_team", "Can manage project team"),
            ("can_view_analytics", "Can view project analytics"),
            ("can_export_data", "Can export project data"),
        ]
```

#### Organization-Level Roles

**Predefined Roles:**
```python
ORGANIZATION_ROLES = {
    'owner': {
        'description': 'Organization owner',
        'permissions': ['*'],  # All permissions
        'is_admin': True
    },
    'admin': {
        'description': 'Organization administrator',
        'permissions': [
            'accounts.add_user',
            'accounts.change_user',
            'accounts.view_user',
            'analytics.*',  # All analytics permissions
            'messaging.*'
        ],
        'is_admin': True
    },
    'manager': {
        'description': 'Team manager',
        'permissions': [
            'accounts.view_user',
            'analytics.view_*',
            'messaging.add_message'
        ],
        'is_admin': False
    },
    'member': {
        'description': 'Regular member',
        'permissions': [
            'accounts.view_user',
            'messaging.view_message'
        ],
        'is_admin': False
    }
}
```

#### Permission Checking

**In Views:**
```python
from foundation.apps.accounts.permissions import IsOrganizationAdmin, HasOrganizationPermission

class ProjectViewSet(ModelViewSet):
    permission_classes = [IsOrganizationAdmin]
    
    def get_permissions(self):
        if self.action == 'create':
            return [HasOrganizationPermission('add_project')]
        elif self.action in ['update', 'partial_update']:
            return [HasOrganizationPermission('change_project')]
        elif self.action == 'destroy':
            return [HasOrganizationPermission('delete_project')]
        return [HasOrganizationPermission('view_project')]
```

**In Templates:**
```django
{% if perms.accounts.can_manage_users %}
  <a href="{% url 'user_management' %}">Manage Users</a>
{% endif %}

{% if user.is_organization_admin %}
  <a href="{% url 'admin_dashboard' %}">Admin Dashboard</a>
{% endif %}
```

**In Python Code:**
```python
# Check permissions programmatically
def user_can_access_analytics(user, organization):
    membership = OrganizationMembership.objects.get(
        user=user, 
        organization=organization
    )
    
    # Check if user has specific permission
    if user.has_perm('analytics.view_usagemetric', organization):
        return True
    
    # Check role-based access
    if membership.role in ['admin', 'manager']:
        return True
    
    return False
```

### Security Headers and Middleware

#### Security Headers Middleware

The foundation includes middleware that adds security headers to all responses:

**Applied Headers:**
```python
class SecurityHeadersMiddleware:
    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HSTS (if HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
```

#### HTTPS and SSL Configuration

**Production Settings:**
```python
# Force HTTPS redirect
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True

# HTTPS cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content type sniffing protection
SECURE_CONTENT_TYPE_NOSNIFF = True

# Browser XSS protection
SECURE_BROWSER_XSS_FILTER = True
```

### Brute Force Protection

#### Django-Axes Configuration

The foundation uses Django-Axes for brute force protection:

**Settings Configuration:**
```python
# Axes settings
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = timedelta(minutes=30)  # 30-minute lockout
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_ONLY_USER_FAILURES = False

# Track failures in database
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'

# Reset attempts on successful login
AXES_RESET_ON_SUCCESS = True
```

**Monitoring Failed Attempts:**
```python
from axes.models import AccessAttempt

# View recent failed attempts
failed_attempts = AccessAttempt.objects.filter(
    attempt_time__gte=timezone.now() - timedelta(hours=24)
).order_by('-attempt_time')

for attempt in failed_attempts:
    print(f"Failed login: {attempt.username} from {attempt.ip_address}")
```

#### Rate Limiting

**API Rate Limiting:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='POST')
def api_endpoint(request):
    # Limited to 100 POST requests per hour per user
    pass

@ratelimit(key='ip', rate='1000/h', method=['GET', 'POST'])
def public_endpoint(request):
    # Limited to 1000 requests per hour per IP
    pass
```

### Data Encryption

#### Encryption at Rest

**Database Field Encryption:**
```python
from cryptography.fernet import Fernet
from django.conf import settings

class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.cipher = Fernet(settings.FIELD_ENCRYPTION_KEY)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.cipher.decrypt(value.encode()).decode()
    
    def to_python(self, value):
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(value.encode()).decode()

# Usage
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ssn = EncryptedCharField(max_length=255)  # Encrypted in database
    phone = EncryptedCharField(max_length=255)
```

#### File Encryption

**Encrypted File Storage:**
```python
import os
from cryptography.fernet import Fernet

class EncryptedFileStorage:
    def __init__(self, key=None):
        self.key = key or settings.FILE_ENCRYPTION_KEY
        self.cipher = Fernet(self.key)
    
    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as file:
            data = file.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(f"{file_path}.encrypted", 'wb') as file:
            file.write(encrypted_data)
        
        # Remove original file
        os.remove(file_path)
    
    def decrypt_file(self, encrypted_file_path):
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        original_path = encrypted_file_path.replace('.encrypted', '')
        with open(original_path, 'wb') as file:
            file.write(decrypted_data)
```

---

## 9. API Usage

### API Overview

The Enterprise SaaS Foundation provides a comprehensive REST API built with Django REST Framework. The API follows RESTful conventions and includes:

**Key Features:**
- **Auto-generated Documentation** (OpenAPI/Swagger)
- **Multiple Authentication Methods** (Session, Token, API Key, JWT)
- **Pagination and Filtering**
- **Rate Limiting**
- **Versioning Support**
- **Comprehensive Error Handling**

### API Documentation

#### Accessing API Documentation

**Interactive Documentation:**
- **Swagger UI**: `http://your-domain.com/api/docs/`
- **ReDoc**: `http://your-domain.com/api/redoc/`
- **OpenAPI Schema**: `http://your-domain.com/api/schema/`

**Generate Static Documentation:**
```bash
# Generate OpenAPI schema file
python manage.py spectacular --color --file schema.yml

# Generate markdown documentation  
python manage.py spectacular --format openapi-json --file api-schema.json
```

#### API Structure

**Base URL Structure:**
```
/api/v1/
├── auth/           # Authentication endpoints
├── users/          # User management
├── organizations/  # Organization management  
├── analytics/      # Usage analytics
├── messaging/      # Notifications and messages
├── compliance/     # Compliance and audit features
└── health/         # System health checks
```

### Authentication

#### Authentication Methods

**1. Session Authentication (Web Interface):**
```bash
# Login to get session
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}' \
  -c cookies.txt

# Use session for subsequent requests
curl -H "X-CSRFToken: csrf-token" \
  -b cookies.txt \
  http://127.0.0.1:8000/api/users/profile/
```

**2. Token Authentication (Mobile/SPA):**
```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Response: {"token": "abcd1234..."}

# Use token
curl -H "Authorization: Token abcd1234..." \
  http://127.0.0.1:8000/api/users/profile/
```

**3. API Key Authentication (Service-to-Service):**
```bash
# Create API key (authenticated request)
curl -X POST http://127.0.0.1:8000/api/auth/api-keys/ \
  -H "Authorization: Token user-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Service Key", "expires_in_days": 365}'

# Use API key
curl -H "Authorization: Api-Key ak_live_123..." \
  http://127.0.0.1:8000/api/data/
```

**4. JWT Authentication (Advanced):**
```bash
# Get JWT token
curl -X POST http://127.0.0.1:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Response: {"access": "eyJ0eXAi...", "refresh": "eyJ0eXAi..."}

# Use JWT token
curl -H "Authorization: JWT eyJ0eXAi..." \
  http://127.0.0.1:8000/api/users/profile/
```

### Core API Endpoints

#### Authentication Endpoints

**User Registration:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Login/Logout:**
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Logout
curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
  -H "Authorization: Token your-token"
```

**Password Management:**
```bash
# Password change
curl -X POST http://127.0.0.1:8000/api/auth/password/change/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "oldpass",
    "new_password1": "newpass",
    "new_password2": "newpass"
  }'

# Password reset request
curl -X POST http://127.0.0.1:8000/api/auth/password/reset/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

#### User Management Endpoints

**User Profile:**
```bash
# Get current user profile
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/users/profile/

# Update user profile
curl -X PATCH \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Updated", "bio": "New bio"}' \
  http://127.0.0.1:8000/api/users/profile/
```

**User List (Admin Only):**
```bash
# List all users (paginated)
curl -H "Authorization: Token admin-token" \
  http://127.0.0.1:8000/api/users/

# Search users
curl -H "Authorization: Token admin-token" \
  "http://127.0.0.1:8000/api/users/?search=john&ordering=-date_joined"
```

#### Organization Endpoints

**Organization Management:**
```bash
# List user's organizations
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/organizations/

# Get specific organization
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/organizations/acme-corp/

# Create organization (if permitted)
curl -X POST \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Company",
    "slug": "new-company",
    "subscription_tier": "professional"
  }' \
  http://127.0.0.1:8000/api/organizations/
```

**Organization Membership:**
```bash
# List organization members
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/organizations/acme-corp/members/

# Invite user to organization
curl -X POST \
  -H "Authorization: Token admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newmember@acme.com",
    "role": "member",
    "send_invitation": true
  }' \
  http://127.0.0.1:8000/api/organizations/acme-corp/members/

# Update member role
curl -X PATCH \
  -H "Authorization: Token admin-token" \
  -H "Content-Type: application/json" \
  -d '{"role": "manager", "is_admin": false}' \
  http://127.0.0.1:8000/api/organizations/acme-corp/members/123/
```

### Pagination and Filtering

#### Pagination

**Default Pagination (20 items per page):**
```bash
# First page
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/users/

# Response structure:
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/users/?page=2",
  "previous": null,
  "results": [...]
}

# Specific page
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?page=3"

# Custom page size
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?page_size=50"
```

#### Filtering and Search

**Basic Filtering:**
```bash
# Filter by field
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?is_active=true"

# Multiple filters
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?is_active=true&is_staff=false"

# Date range filtering
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?date_joined__gte=2024-01-01"
```

**Search:**
```bash
# Text search
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?search=john"

# Search with ordering
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/users/?search=john&ordering=-date_joined"
```

**Advanced Filtering Examples:**
```bash
# Analytics data with date range
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/analytics/usage/?date__gte=2024-01-01&date__lte=2024-01-31"

# Organizations by subscription tier
curl -H "Authorization: Token admin-token" \
  "http://127.0.0.1:8000/api/organizations/?subscription_tier=enterprise"

# Messages with status and type
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/messaging/notifications/?status=unread&type=system"
```

### Error Handling

#### HTTP Status Codes

**Success Codes:**
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted (async processing)
- `204 No Content`: Successful deletion

**Client Error Codes:**
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded

**Server Error Codes:**
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: Upstream server error
- `503 Service Unavailable`: Service temporarily down

#### Error Response Format

**Standard Error Response:**
```json
{
  "error": {
    "code": "validation_error",
    "message": "The submitted data is invalid",
    "details": {
      "email": ["This field is required"],
      "password": ["Password must be at least 12 characters long"]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**Validation Error Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "u", "email": "invalid-email"}'

# Response (400 Bad Request):
{
  "error": {
    "code": "validation_error",
    "message": "Invalid input data",
    "details": {
      "username": ["Username must be at least 3 characters long"],
      "email": ["Enter a valid email address"],
      "password": ["This field is required"]
    }
  }
}
```

### Rate Limiting

#### Rate Limit Headers

**Response Headers:**
```http
X-RateLimit-Limit: 1000      # Requests allowed per period
X-RateLimit-Remaining: 999   # Requests remaining
X-RateLimit-Reset: 1642262400 # Unix timestamp when limit resets
```

**Rate Limit Exceeded Response:**
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Too many requests. Try again in 60 seconds.",
    "details": {
      "limit": 1000,
      "window": "1 hour",
      "retry_after": 60
    }
  }
}
```

#### Rate Limit Configuration

Different limits apply based on authentication:

**Unauthenticated Requests:**
- 100 requests per hour per IP

**Authenticated Users:**
- 10,000 requests per hour per user

**API Key Authentication:**
- Configurable per key (default: 50,000 per hour)

**Enterprise Organizations:**
- Higher limits or unlimited (configurable)

### API Versioning

#### Version Selection

**URL-based Versioning (Recommended):**
```bash
# Version 1 (current)
curl http://127.0.0.1:8000/api/v1/users/

# Version 2 (when available)
curl http://127.0.0.1:8000/api/v2/users/
```

**Header-based Versioning:**
```bash
curl -H "Accept: application/json; version=1" \
  http://127.0.0.1:8000/api/users/
```

#### Version Compatibility

**Deprecation Warnings:**
```json
{
  "data": {...},
  "warnings": [
    {
      "code": "deprecation_warning",
      "message": "This endpoint will be deprecated in v2. Use /api/v2/users/ instead.",
      "sunset_date": "2024-12-01"
    }
  ]
}
```

### Batch Operations

#### Bulk Create

```bash
curl -X POST http://127.0.0.1:8000/api/users/bulk_create/ \
  -H "Authorization: Token admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "users": [
      {
        "username": "user1",
        "email": "user1@example.com",
        "password": "SecurePass123!"
      },
      {
        "username": "user2", 
        "email": "user2@example.com",
        "password": "SecurePass123!"
      }
    ]
  }'
```

#### Bulk Update

```bash
curl -X PATCH http://127.0.0.1:8000/api/users/bulk_update/ \
  -H "Authorization: Token admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "updates": [
      {"id": 1, "is_active": false},
      {"id": 2, "is_active": false}
    ]
  }'
```

### Webhooks

#### Webhook Configuration

**Available Events:**
- `user.created`
- `user.updated`
- `user.deleted`
- `organization.created`
- `organization.updated`
- `membership.created`
- `membership.updated`

**Configure Webhooks:**
```bash
curl -X POST http://127.0.0.1:8000/api/webhooks/ \
  -H "Authorization: Token admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/foundation/",
    "events": ["user.created", "user.updated"],
    "secret": "your-webhook-secret",
    "active": true
  }'
```

#### Webhook Payload Example

**User Created Event:**
```json
{
  "event": "user.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": 123,
    "username": "newuser",
    "email": "newuser@example.com",
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "organization": {
    "id": 1,
    "slug": "acme-corp"
  }
}
```

---

## 14. Production Deployment

### Deployment Overview

Deploying the Enterprise SaaS Foundation to production requires careful planning and configuration. This section covers various deployment strategies and best practices.

**Deployment Options:**
- **Docker Containers** (Recommended)
- **Cloud Platforms** (AWS, GCP, Azure)
- **Traditional Servers** (VPS, Dedicated)
- **Platform as a Service** (Heroku, DigitalOcean App Platform)

### Docker Deployment

#### Creating Docker Configuration

**Dockerfile:**
```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=foundation.config.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create logs directory
RUN mkdir -p /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/')"

# Start server
CMD ["gunicorn", "foundation.config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://foundation:password@db:5432/foundation_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/api/health/')"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=foundation_db
      - POSTGRES_USER=foundation
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U foundation"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - web
    restart: unless-stopped

  celery:
    build: .
    command: celery -A foundation.config worker -l info
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://foundation:password@db:5432/foundation_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A foundation.config beat -l info
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://foundation:password@db:5432/foundation_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

#### Nginx Configuration

**docker/nginx/nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    upstream app_server {
        server web:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 1d;
        ssl_session_tickets off;
        ssl_stapling on;
        ssl_stapling_verify on;

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # Main application
        location / {
            proxy_pass http://app_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://app_server;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### Cloud Platform Deployment

#### AWS Deployment with ECS

**task-definition.json:**
```json
{
  "family": "foundation-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "foundation-web",
      "image": "YOUR_ACCOUNT.dkr.ecr.region.amazonaws.com/foundation:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DJANGO_SETTINGS_MODULE", "value": "foundation.config.settings.production"},
        {"name": "DEBUG", "value": "False"}
      ],
      "secrets": [
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:region:account:parameter/foundation/database-url"},
        {"name": "REDIS_URL", "valueFrom": "arn:aws:ssm:region:account:parameter/foundation/redis-url"},
        {"name": "DJANGO_SECRET_KEY", "valueFrom": "arn:aws:ssm:region:account:parameter/foundation/secret-key"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/foundation",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/health/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

**Terraform Configuration (main.tf):**
```hcl
# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "foundation-vpc"
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "foundation-public-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "foundation-private-${count.index + 1}"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "foundation-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = false
  
  tags = {
    Environment = "production"
  }
}

resource "aws_lb_target_group" "app" {
  name        = "foundation-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/api/health/"
    matcher             = "200"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "foundation"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "foundation-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.private[*].id
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "foundation-web"
    container_port   = 8000
  }
  
  depends_on = [aws_lb_listener.app]
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "foundation-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  
  db_name  = "foundation"
  username = "foundation"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "foundation-final-snapshot"
  
  tags = {
    Name = "foundation-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "foundation-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "foundation-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}
```

### Environment-Specific Configurations

#### Production Settings

**foundation/config/settings/production.py:**
```python
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# Security
DEBUG = False
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Session and Cookie Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Database
DATABASES = {
    'default': env.db('DATABASE_URL')
}
DATABASES['default']['CONN_MAX_AGE'] = 600

# Static and Media Files (AWS S3)
if env.bool('USE_S3', default=False):
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Static files
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    
    # Media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/error.log',
            'maxBytes': 1024*1024*10,
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
        'foundation': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
    },
}

# Error Monitoring
if env('SENTRY_DSN', default=None):
    sentry_sdk.init(
        dsn=env('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(transaction_style='url'),
            CeleryIntegration(monitor_beat_tasks=True),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
        environment=env('SENTRY_ENVIRONMENT', default='production'),
    )

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# Performance Settings
USE_TZ = True
TIME_ZONE = env('TIME_ZONE', default='UTC')

# Feature Flags
FEATURE_FLAGS.update({
    'debug_toolbar': False,
    'silk_profiler': False,
})
```

### Monitoring and Logging

#### Application Monitoring

**Sentry Configuration:**
```python
# In production settings
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(
            transaction_style='url',
            middleware_spans=True,
            signals_spans=False,
        ),
        CeleryIntegration(
            monitor_beat_tasks=True,
        ),
        RedisIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    send_default_pii=True,
    environment=env('SENTRY_ENVIRONMENT', default='production'),
    release=env('SENTRY_RELEASE', default=None),
    # Performance monitoring
    profiles_sample_rate=0.1,
    # Error filtering
    before_send=filter_sentry_events,
)

def filter_sentry_events(event, hint):
    """Filter out certain events from Sentry"""
    # Don't send 404 errors
    if event.get('logger') == 'django.request' and event.get('level') == 'error':
        if '404' in str(event.get('message', '')):
            return None
    
    # Don't send health check failures
    url = event.get('request', {}).get('url', '')
    if '/health/' in url or '/api/health/' in url:
        return None
    
    return event
```

#### Log Management

**Structured Logging with ELK Stack:**
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - logging

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./docker/logstash/pipeline:/usr/share/logstash/pipeline
      - ./docker/logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml
    ports:
      - "5000:5000/tcp"
      - "5000:5000/udp"
      - "9600:9600"
    environment:
      LS_JAVA_OPTS: "-Xmx256m -Xms256m"
    depends_on:
      - elasticsearch
    networks:
      - logging

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - logging

volumes:
  elasticsearch_data:

networks:
  logging:
    driver: bridge
```

### SSL/TLS Configuration

#### Let's Encrypt with Certbot

**SSL Certificate Setup:**
```bash
#!/bin/bash
# setup-ssl.sh

# Install certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Setup auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Test renewal
sudo certbot renew --dry-run
```

**Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;

    # Rest of your nginx configuration...
}
```

### Database Management

#### Database Migrations in Production

**Migration Strategy:**
```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting production deployment...${NC}"

# 1. Pull latest code
echo -e "${YELLOW}Pulling latest code...${NC}"
git pull origin main

# 2. Build new Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t foundation:latest .

# 3. Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker run --rm --env-file .env.production \
  --network foundation_default \
  foundation:latest \
  python manage.py migrate --check

if [ $? -eq 0 ]; then
  echo -e "${GREEN}No pending migrations${NC}"
else
  echo -e "${YELLOW}Running migrations...${NC}"
  docker run --rm --env-file .env.production \
    --network foundation_default \
    foundation:latest \
    python manage.py migrate
fi

# 4. Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
docker run --rm --env-file .env.production \
  foundation:latest \
  python manage.py collectstatic --noinput

# 5. Update services
echo -e "${YELLOW}Updating services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 6. Health check
echo -e "${YELLOW}Performing health check...${NC}"
sleep 10
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health/)

if [ $response -eq 200 ]; then
  echo -e "${GREEN}Deployment successful! Health check passed.${NC}"
else
  echo -e "${RED}Deployment failed! Health check returned $response${NC}"
  exit 1
fi

# 7. Cleanup old images
echo -e "${YELLOW}Cleaning up old images...${NC}"
docker image prune -f

echo -e "${GREEN}Deployment completed successfully!${NC}"
```

#### Database Backup Strategy

**Automated Backup Script:**
```bash
#!/bin/bash
# backup-database.sh

set -e

# Configuration
BACKUP_DIR="/backups/postgres"
S3_BUCKET="your-backup-bucket"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="foundation_backup_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting database backup at $(date)"

# Create database dump
docker exec foundation_db_1 pg_dump -U foundation foundation_db > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$S3_BUCKET/database-backups/"

# Verify upload
if aws s3 ls "s3://$S3_BUCKET/database-backups/$BACKUP_FILE" > /dev/null; then
  echo "Backup uploaded successfully to S3"
  
  # Remove local backup
  rm "$BACKUP_DIR/$BACKUP_FILE"
  echo "Local backup removed"
else
  echo "Failed to upload backup to S3"
  exit 1
fi

# Clean up old backups from S3
echo "Cleaning up old backups..."
aws s3 ls "s3://$S3_BUCKET/database-backups/" | \
  awk '{print $4}' | \
  head -n -$RETENTION_DAYS | \
  xargs -I {} aws s3 rm "s3://$S3_BUCKET/database-backups/{}"

echo "Database backup completed at $(date)"
```

### Scaling Considerations

#### Horizontal Scaling

**Load Balancer Configuration:**
```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  web:
    build: .
    environment:
      - DEBUG=False
      - DATABASE_URL=postgres://foundation:password@db:5432/foundation_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    deploy:
      placement:
        constraints: [node.role == manager]
```

#### Database Scaling

**Read Replicas Configuration:**
```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default=5432),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_REPLICA_HOST'),
        'PORT': env('DB_PORT', default=5432),
        'CONN_MAX_AGE': 600,
    }
}

# Database routing
class DatabaseRouter:
    """A router to control database operations for read replicas"""
    
    def db_for_read(self, model, **hints):
        """Reading from the replica database."""
        if model._meta.app_label in ['analytics', 'compliance']:
            return 'replica'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Writing to the primary database."""
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """All migrations go to primary."""
        return db == 'default'

DATABASE_ROUTERS = ['path.to.routers.DatabaseRouter']
```

---

## 15. Troubleshooting Guide

### Common Deployment Issues

#### Database Connection Issues

**Problem**: `django.db.utils.OperationalError: could not connect to server`

**Solutions:**

1. **Check Database Service**:
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps db
   
   # Check database logs
   docker-compose logs db
   
   # Test database connection
   docker-compose exec db psql -U foundation -d foundation_db -c "SELECT 1;"
   ```

2. **Verify Connection String**:
   ```bash
   # Check environment variables
   echo $DATABASE_URL
   
   # Test connection with psql
   psql $DATABASE_URL -c "SELECT version();"
   ```

3. **Network Issues**:
   ```bash
   # Check Docker networks
   docker network ls
   docker network inspect foundation_default
   
   # Test connectivity from web container
   docker-compose exec web ping db
   ```

#### Redis Connection Issues

**Problem**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solutions:**

1. **Check Redis Service**:
   ```bash
   # Check Redis status
   docker-compose ps redis
   
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   
   # Check Redis logs
   docker-compose logs redis
   ```

2. **Test from Application**:
   ```bash
   # Test Redis from Django shell
   docker-compose exec web python manage.py shell
   ```
   
   ```python
   from django.core.cache import cache
   cache.set('test', 'value')
   print(cache.get('test'))
   ```

#### SSL Certificate Issues

**Problem**: SSL certificate validation errors

**Solutions:**

1. **Check Certificate Status**:
   ```bash
   # Test SSL certificate
   openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
   
   # Check certificate expiration
   echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
   ```

2. **Renew Let's Encrypt Certificate**:
   ```bash
   # Test renewal
   sudo certbot renew --dry-run
   
   # Force renewal
   sudo certbot renew --force-renewal
   
   # Reload nginx
   sudo nginx -s reload
   ```

### Application Performance Issues

#### Slow Database Queries

**Problem**: Application responds slowly due to database queries

**Diagnosis:**

1. **Enable Query Logging**:
   ```python
   # In development settings
   LOGGING['loggers']['django.db.backends'] = {
       'level': 'DEBUG',
       'handlers': ['console'],
   }
   ```

2. **Use Django Debug Toolbar**:
   ```python
   # Add to development settings
   if DEBUG:
       INSTALLED_APPS += ['debug_toolbar']
       MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
       INTERNAL_IPS = ['127.0.0.1']
   ```

3. **Profile Queries**:
   ```python
   from django.db import connection
   from django.conf import settings
   
   def show_queries():
       if settings.DEBUG:
           for query in connection.queries:
               print(f"Time: {query['time']}s")
               print(f"SQL: {query['sql']}\n")
   ```

**Solutions:**

1. **Add Database Indexes**:
   ```python
   class MyModel(models.Model):
       field = models.CharField(max_length=100, db_index=True)
       
       class Meta:
           indexes = [
               models.Index(fields=['field1', 'field2']),
               models.Index(fields=['-created_at']),
           ]
   ```

2. **Optimize Queries**:
   ```python
   # Use select_related for foreign keys
   users = User.objects.select_related('profile').all()
   
   # Use prefetch_related for reverse foreign keys and many-to-many
   orgs = Organization.objects.prefetch_related('members').all()
   
   # Use only() to limit fields
   users = User.objects.only('username', 'email').all()
   ```

#### Memory Issues

**Problem**: Application runs out of memory

**Diagnosis:**

1. **Monitor Memory Usage**:
   ```bash
   # Check container memory usage
   docker stats
   
   # Check system memory
   free -h
   
   # Check Django memory usage
   docker-compose exec web python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
   ```

2. **Profile Memory Usage**:
   ```python
   import psutil
   import os
   
   def get_memory_usage():
       process = psutil.Process(os.getpid())
       return process.memory_info().rss / 1024 / 1024  # MB
   ```

**Solutions:**

1. **Optimize Queries**:
   ```python
   # Use iterator() for large querysets
   for user in User.objects.iterator():
       process_user(user)
   
   # Process in batches
   from django.core.paginator import Paginator
   
   paginator = Paginator(User.objects.all(), 1000)
   for page_num in paginator.page_range:
       for user in paginator.page(page_num):
           process_user(user)
   ```

2. **Increase Container Memory**:
   ```yaml
   # docker-compose.yml
   services:
     web:
       build: .
       deploy:
         resources:
           limits:
             memory: 1G
           reservations:
             memory: 512M
   ```

### Security Issues

#### Authentication Problems

**Problem**: Users cannot authenticate

**Diagnosis:**

1. **Check Authentication Backend**:
   ```python
   # In Django shell
   from django.contrib.auth import authenticate
   user = authenticate(username='testuser', password='testpass')
   print(user)
   ```

2. **Check User Status**:
   ```python
   from django.contrib.auth.models import User
   user = User.objects.get(username='testuser')
   print(f"Active: {user.is_active}")
   print(f"Staff: {user.is_staff}")
   print(f"Last login: {user.last_login}")
   ```

**Solutions:**

1. **Reset User Password**:
   ```python
   # In Django shell
   from django.contrib.auth.models import User
   user = User.objects.get(username='testuser')
   user.set_password('newpassword')
   user.save()
   ```

2. **Check Rate Limiting**:
   ```python
   # Check if user is locked out by django-axes
   from axes.models import AccessAttempt
   attempts = AccessAttempt.objects.filter(username='testuser')
   print(f"Failed attempts: {attempts.count()}")
   
   # Reset attempts
   attempts.delete()
   ```

#### Permission Denied Errors

**Problem**: `403 Forbidden` errors for API access

**Diagnosis:**

1. **Check User Permissions**:
   ```python
   # Check user permissions
   user = User.objects.get(username='testuser')
   print(user.get_all_permissions())
   
   # Check organization membership
   memberships = user.organization_memberships.all()
   for membership in memberships:
       print(f"Org: {membership.organization.name}, Role: {membership.role}")
   ```

2. **Check API Key**:
   ```python
   # Verify API key
   from foundation.apps.accounts.models import APIKey
   try:
       key = APIKey.objects.get(key='your-key-here')
       print(f"Key valid: {key.is_active}")
       print(f"Expires: {key.expires_at}")
   except APIKey.DoesNotExist:
       print("API key not found")
   ```

**Solutions:**

1. **Grant Permissions**:
   ```python
   # Add user to organization
   from foundation.apps.accounts.enterprise import OrganizationMembership
   membership = OrganizationMembership.objects.create(
       user=user,
       organization=org,
       role='member'
   )
   ```

2. **Generate New API Key**:
   ```python
   # Generate new API key
   api_key, raw_key = APIKey.generate_key(
       user=user,
       name="New Key",
       expires_in_days=30
   )
   print(f"New key: {raw_key}")
   ```

### Data and Migration Issues

#### Migration Failures

**Problem**: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solutions:**

1. **Check Migration Status**:
   ```bash
   # Show migration status
   python manage.py showmigrations
   
   # Check for conflicts
   python manage.py showmigrations --plan
   ```

2. **Fix Migration Issues**:
   ```bash
   # Fake apply migration
   python manage.py migrate app_name migration_name --fake
   
   # Reset migrations (dangerous!)
   python manage.py migrate app_name zero
   python manage.py migrate app_name
   ```

3. **Merge Migrations**:
   ```bash
   # Create merge migration
   python manage.py makemigrations --merge
   ```

#### Data Corruption

**Problem**: Database data appears corrupted or inconsistent

**Solutions:**

1. **Restore from Backup**:
   ```bash
   # Stop the application
   docker-compose stop web
   
   # Restore database
   docker exec -i foundation_db_1 psql -U foundation -d foundation_db < backup.sql
   
   # Start application
   docker-compose start web
   ```

2. **Run Data Validation**:
   ```python
   # Create management command to validate data
   from django.core.management.base import BaseCommand
   from django.db import transaction
   
   class Command(BaseCommand):
       help = 'Validate database integrity'
       
       def handle(self, *args, **options):
           self.validate_user_profiles()
           self.validate_organizations()
           
       def validate_user_profiles(self):
           from django.contrib.auth.models import User
           users_without_profiles = User.objects.filter(
               security_profile__isnull=True
           )
           self.stdout.write(f"Users without profiles: {users_without_profiles.count()}")
   ```

---

## 16. Common Issues and Solutions

### Quick Reference Guide

#### Installation Issues

**Issue**: `pip install` fails with compilation errors

**Solution**:
```bash
# Install build dependencies
# Ubuntu/Debian
sudo apt-get install build-essential libpq-dev python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install postgresql-devel python3-devel

# macOS
brew install postgresql
xcode-select --install
```

**Issue**: Redis connection refused

**Solution**:
```bash
# Start Redis service
# Ubuntu/Debian
sudo systemctl start redis-server

# macOS
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

#### Configuration Issues

**Issue**: `SECRET_KEY` security warning

**Solution**:
```python
# Generate secure secret key
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())

# Add to .env file
DJANGO_SECRET_KEY=your-generated-key-here
```

**Issue**: Static files not loading

**Solution**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check settings
# In settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

#### API Issues

**Issue**: CORS errors in browser

**Solution**:
```python
# Add to settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True
```

**Issue**: API key authentication fails

**Solution**:
```python
# Check API key format
# Correct: Authorization: Api-Key ak_live_...
# Check for typos in header name

# Verify key exists and is active
from foundation.apps.accounts.models import APIKey
key = APIKey.objects.get(key='your-key')
print(f"Active: {key.is_active}, Expires: {key.expires_at}")
```

#### Database Issues

**Issue**: Migration conflicts

**Solution**:
```bash
# Create merge migration
python manage.py makemigrations --merge

# Or reset migrations (careful!)
python manage.py migrate app_name zero
rm app_name/migrations/0002_*.py
python manage.py makemigrations app_name
python manage.py migrate app_name
```

**Issue**: Foreign key constraint errors

**Solution**:
```python
# Check data integrity
from django.core.management import call_command
call_command('check')

# Fix orphaned records
from myapp.models import MyModel
MyModel.objects.filter(foreign_key__isnull=True).delete()
```

### Performance Optimization

#### Slow Queries

**Quick Fixes**:
```python
# Add select_related for ForeignKey
users = User.objects.select_related('profile')

# Add prefetch_related for reverse ForeignKey
orgs = Organization.objects.prefetch_related('members')

# Use database indexes
class MyModel(models.Model):
    field = models.CharField(max_length=100, db_index=True)
```

#### High Memory Usage

**Quick Fixes**:
```python
# Use iterator() for large datasets
for item in MyModel.objects.iterator():
    process_item(item)

# Process in batches
from django.core.paginator import Paginator
paginator = Paginator(MyModel.objects.all(), 1000)
for page_num in paginator.page_range:
    page = paginator.page(page_num)
    for item in page:
        process_item(item)
```

#### Cache Issues

**Quick Fixes**:
```python
# Clear cache
from django.core.cache import cache
cache.clear()

# Check cache key patterns
from django.core.cache.utils import make_template_fragment_key
key = make_template_fragment_key('fragment_name', [var1, var2])
print(f"Cache key: {key}")
```

### Security Checklist

#### Pre-Production Checklist

- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` configured
- [ ] `ALLOWED_HOSTS` properly set
- [ ] HTTPS/SSL certificates installed
- [ ] Security headers configured
- [ ] Database credentials secured
- [ ] API keys rotated
- [ ] User permissions reviewed
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Error tracking enabled

#### Security Commands

```bash
# Run security checks
python manage.py check --deploy

# Test SSL configuration
nmap --script ssl-enum-ciphers -p 443 yourdomain.com

# Check for security updates
pip list --outdated
pip-audit  # If installed
```

### Emergency Procedures

#### Site Down

1. **Check Health Status**:
   ```bash
   curl -I https://yourdomain.com/api/health/
   ```

2. **Check Services**:
   ```bash
   docker-compose ps
   docker-compose logs web
   ```

3. **Restart Services**:
   ```bash
   docker-compose restart web
   docker-compose restart
   ```

#### Database Connection Lost

1. **Check Database Status**:
   ```bash
   docker-compose exec db pg_isready -U foundation
   ```

2. **Restart Database**:
   ```bash
   docker-compose restart db
   ```

3. **Check Connections**:
   ```bash
   docker-compose exec db psql -U foundation -c "SELECT count(*) FROM pg_stat_activity;"
   ```

#### High Load

1. **Check Resource Usage**:
   ```bash
   docker stats
   htop
   ```

2. **Scale Services**:
   ```bash
   docker-compose up -d --scale web=3
   ```

3. **Enable Rate Limiting**:
   ```python
   # Temporarily reduce rate limits
   RATELIMIT_RATE = '100/h'  # Instead of 1000/h
   ```

### Support Resources

#### Getting Help

- **Documentation**: Review this guide and inline documentation
- **Logs**: Always check application and system logs first
- **Community**: Django and Python communities
- **Professional Support**: Consider hiring Django experts

#### Useful Commands

```bash
# Django debugging
python manage.py shell
python manage.py dbshell
python manage.py check
python manage.py showmigrations

# Docker debugging
docker-compose logs service_name
docker exec -it container_name bash
docker stats
docker system df

# System debugging
tail -f /var/log/nginx/error.log
journalctl -u service_name -f
ps aux | grep python
netstat -tulpn | grep :8000
```

#### Log Locations

- **Application Logs**: `/app/logs/` (in container)
- **Nginx Logs**: `/var/log/nginx/`
- **PostgreSQL Logs**: `/var/log/postgresql/`
- **System Logs**: `/var/log/syslog`
- **Docker Logs**: `docker-compose logs service_name`

---

**Congratulations!** You now have a comprehensive understanding of the Enterprise SaaS Backend Foundation. This guide covers everything from basic installation to production deployment and troubleshooting. Use this as your reference manual and adapt the configurations to your specific needs.

For updates and additional resources, refer to the project's documentation and community channels.

---

**Enterprise SaaS Backend Foundation** - Built for scale, security, and compliance. 🚀

## 13. Development and Extensions

### Extension Architecture

The Enterprise SaaS Foundation is designed with extensibility in mind. You can extend the foundation in several ways:

**Extension Methods:**
- **Custom Apps**: Create new Django apps that integrate with the foundation
- **Plugin System**: Use the built-in plugin architecture for modular features
- **API Extensions**: Extend existing APIs with custom endpoints
- **Middleware Extensions**: Add custom processing logic
- **Model Extensions**: Extend existing models with additional fields

#### Creating Custom Apps

**App Structure:**
```bash
your_project/
├── your_custom_app/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── admin.py
│   └── migrations/
└── settings.py
```

**Example Custom App (apps.py):**
```python
from django.apps import AppConfig

class CustomFeatureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_project.apps.custom_feature'
    verbose_name = 'Custom Feature'
    
    def ready(self):
        # Import signals when the app is ready
        from . import signals
```

**Custom Models with Foundation Integration:**
```python
from django.db import models
from foundation.apps.core.models import TenantAwareModel, TimestampedModel
from foundation.apps.accounts.models import User
from foundation.apps.accounts.enterprise import Organization

class CustomModel(TenantAwareModel, TimestampedModel):
    """Custom model that integrates with the foundation"""
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='custom_models'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_models'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Custom business logic fields
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High')
        ],
        default='medium'
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'custom_models'
        ordering = ['-created_at']
        permissions = [
            ("can_view_analytics", "Can view custom model analytics"),
            ("can_export_data", "Can export custom model data"),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.organization.name})"
```

#### API Extensions

**Custom ViewSets:**
```python
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from foundation.apps.accounts.permissions import IsOrganizationMember
from foundation.apps.analytics.models import UserActivity
from .models import CustomModel
from .serializers import CustomModelSerializer

class CustomModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomModelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        # Automatically filter by user's organization
        user_org = self.request.user.organization_memberships.first()
        if user_org:
            return CustomModel.objects.filter(
                organization=user_org.organization,
                is_active=True
            )
        return CustomModel.objects.none()
    
    def perform_create(self, serializer):
        # Automatically set organization and user
        user_org = self.request.user.organization_memberships.first()
        serializer.save(
            user=self.request.user,
            organization=user_org.organization
        )
        
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            action='custom_model_created',
            description=f'Created custom model: {serializer.instance.title}',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
    
    @action(detail=True, methods=['post'])
    def mark_priority(self, request, pk=None):
        """Custom action to update priority"""
        obj = self.get_object()
        new_priority = request.data.get('priority')
        
        if new_priority in ['low', 'medium', 'high']:
            obj.priority = new_priority
            obj.save()
            
            # Log the change
            UserActivity.objects.create(
                user=request.user,
                action='priority_changed',
                description=f'Changed priority to {new_priority}',
                metadata={'model_id': obj.id, 'old_priority': obj.priority}
            )
            
            return Response({'status': 'priority updated'})
        
        return Response(
            {'error': 'Invalid priority'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
```

### Plugin System

#### Creating Plugins

**Plugin Base Class:**
```python
from abc import ABC, abstractmethod
from django.apps import apps

class BasePlugin(ABC):
    """Base class for all foundation plugins"""
    
    name = None
    version = None
    description = None
    author = None
    
    @abstractmethod
    def install(self):
        """Install the plugin"""
        pass
    
    @abstractmethod
    def uninstall(self):
        """Uninstall the plugin"""
        pass
    
    @abstractmethod
    def get_urls(self):
        """Return URL patterns for the plugin"""
        return []
    
    def get_admin_urls(self):
        """Return admin URL patterns for the plugin"""
        return []
    
    def get_api_urls(self):
        """Return API URL patterns for the plugin"""
        return []
    
    def register_permissions(self):
        """Register custom permissions"""
        return []
    
    def register_signals(self):
        """Register signal handlers"""
        pass

class PluginManager:
    """Manages plugin registration and lifecycle"""
    
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin_class):
        """Register a plugin"""
        plugin = plugin_class()
        self.plugins[plugin.name] = plugin
        plugin.install()
        plugin.register_signals()
    
    def unregister_plugin(self, plugin_name):
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            plugin.uninstall()
            del self.plugins[plugin_name]
    
    def get_plugin_urls(self):
        """Get all plugin URLs"""
        urls = []
        for plugin in self.plugins.values():
            urls.extend(plugin.get_urls())
        return urls

# Global plugin manager instance
plugin_manager = PluginManager()
```

**Example Plugin:**
```python
from django.urls import path, include
from foundation.plugins.base import BasePlugin
from . import views, urls

class CustomReportsPlugin(BasePlugin):
    name = 'custom_reports'
    version = '1.0.0'
    description = 'Advanced reporting and analytics'
    author = 'Your Company'
    
    def install(self):
        """Install plugin dependencies and setup"""
        # Run any setup code
        from .models import ReportTemplate
        
        # Create default report templates
        ReportTemplate.objects.get_or_create(
            name='User Activity Report',
            defaults={
                'description': 'Shows user activity over time',
                'template_type': 'user_activity',
                'is_system': True
            }
        )
    
    def uninstall(self):
        """Clean up plugin data"""
        # Optionally clean up plugin-specific data
        pass
    
    def get_urls(self):
        """Return URL patterns"""
        return [
            path('reports/', include(urls)),
        ]
    
    def get_api_urls(self):
        """Return API URL patterns"""
        return [
            path('api/reports/', include('custom_reports.api.urls')),
        ]
    
    def register_permissions(self):
        """Register custom permissions"""
        return [
            ('custom_reports.view_report', 'Can view reports'),
            ('custom_reports.create_report', 'Can create reports'),
            ('custom_reports.export_report', 'Can export reports'),
        ]
```

### Model Extensions

#### Extending Existing Models

**Using Model Inheritance:**
```python
from foundation.apps.accounts.models import User
from django.db import models

# Extend User with additional fields
class ExtendedUserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='extended_profile'
    )
    
    # Additional fields
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    
    # Custom preferences
    notification_preferences = models.JSONField(default=dict)
    theme_preferences = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'extended_user_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.job_title}"

# Signal to create profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_extended_profile(sender, instance, created, **kwargs):
    if created:
        ExtendedUserProfile.objects.create(user=instance)
```

**Adding Custom Methods to Existing Models:**
```python
# In your app's models.py or a separate file
from foundation.apps.accounts.models import User
from foundation.apps.accounts.enterprise import Organization

def get_user_dashboard_data(self):
    """Custom method to get dashboard data for user"""
    from .models import CustomModel
    
    user_org = self.organization_memberships.first()
    if not user_org:
        return {}
    
    return {
        'custom_models_count': CustomModel.objects.filter(
            user=self,
            organization=user_org.organization
        ).count(),
        'recent_activities': self.user_activities.all()[:5],
        'organization_role': user_org.role,
    }

# Add method to User model
User.add_to_class('get_dashboard_data', get_user_dashboard_data)

def get_organization_custom_stats(self):
    """Custom method for organization statistics"""
    from .models import CustomModel
    
    return {
        'total_custom_models': CustomModel.objects.filter(
            organization=self
        ).count(),
        'active_models': CustomModel.objects.filter(
            organization=self,
            is_active=True
        ).count(),
    }

# Add method to Organization model
Organization.add_to_class('get_custom_stats', get_organization_custom_stats)
```

### Custom Middleware

#### Request Processing Middleware

```python
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import time
import logging

logger = logging.getLogger(__name__)

class CustomRequestMiddleware(MiddlewareMixin):
    """Custom middleware for request processing"""
    
    def process_request(self, request):
        # Add custom request processing
        request.start_time = time.time()
        
        # Add organization context
        if request.user.is_authenticated:
            try:
                membership = request.user.organization_memberships.first()
                request.organization = membership.organization if membership else None
            except:
                request.organization = None
        else:
            request.organization = None
        
        # Custom header processing
        client_version = request.META.get('HTTP_X_CLIENT_VERSION')
        if client_version:
            request.client_version = client_version
    
    def process_response(self, request, response):
        # Add custom headers
        response['X-Response-Time'] = f"{time.time() - getattr(request, 'start_time', time.time()):.3f}"
        response['X-Server-Version'] = '1.0.0'
        
        # Log request details
        if hasattr(request, 'start_time'):
            processing_time = time.time() - request.start_time
            if processing_time > 1.0:  # Log slow requests
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {processing_time:.3f}s"
                )
        
        return response
    
    def process_exception(self, request, exception):
        # Custom exception handling
        logger.error(
            f"Exception in {request.method} {request.path}: {str(exception)}",
            exc_info=True,
            extra={
                'user': getattr(request, 'user', None),
                'organization': getattr(request, 'organization', None),
                'ip_address': request.META.get('REMOTE_ADDR'),
            }
        )
        
        # Return custom error response for API endpoints
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': {
                    'code': 'internal_error',
                    'message': 'An internal error occurred',
                    'request_id': getattr(request, 'request_id', 'unknown')
                }
            }, status=500)
```

### Custom Management Commands

#### Creating Custom Commands

```python
# your_app/management/commands/sync_custom_data.py
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from your_app.models import CustomModel
from foundation.apps.accounts.enterprise import Organization

class Command(BaseCommand):
    help = 'Sync custom data from external source'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization',
            type=str,
            help='Organization slug to sync data for'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch'
        )
    
    def handle(self, *args, **options):
        organization_slug = options.get('organization')
        dry_run = options.get('dry_run', False)
        batch_size = options.get('batch_size', 100)
        
        if organization_slug:
            try:
                org = Organization.objects.get(slug=organization_slug)
                organizations = [org]
            except Organization.DoesNotExist:
                raise CommandError(f'Organization "{organization_slug}" does not exist')
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        total_synced = 0
        
        for org in organizations:
            self.stdout.write(f'Processing organization: {org.name}')
            
            # Your custom sync logic here
            synced_count = self.sync_organization_data(org, dry_run, batch_size)
            total_synced += synced_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Synced {synced_count} records for {org.name}'
                )
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would have synced {total_synced} total records'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully synced {total_synced} total records'
                )
            )
    
    @transaction.atomic
    def sync_organization_data(self, organization, dry_run, batch_size):
        # Your custom sync logic
        external_data = self.fetch_external_data(organization)
        synced_count = 0
        
        for i in range(0, len(external_data), batch_size):
            batch = external_data[i:i + batch_size]
            
            for item in batch:
                if not dry_run:
                    custom_model, created = CustomModel.objects.update_or_create(
                        organization=organization,
                        external_id=item['id'],
                        defaults={
                            'title': item['title'],
                            'description': item['description'],
                            'priority': item.get('priority', 'medium'),
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'  Created: {custom_model.title}')
                    else:
                        self.stdout.write(f'  Updated: {custom_model.title}')
                
                synced_count += 1
        
        return synced_count
    
    def fetch_external_data(self, organization):
        # Mock external data fetch
        # In real implementation, this would call external APIs
        return [
            {
                'id': 'ext_123',
                'title': 'External Item 1',
                'description': 'Description from external system',
                'priority': 'high'
            }
        ]
```

### Testing Extensions

#### Testing Custom Functionality

```python
# tests/test_custom_extensions.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from foundation.apps.accounts.enterprise import Organization, OrganizationMembership
from your_app.models import CustomModel

class CustomModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Organization',
            slug='test-org'
        )
        
        self.membership = OrganizationMembership.objects.create(
            user=self.user,
            organization=self.organization,
            role='admin'
        )
    
    def test_custom_model_creation(self):
        """Test creating a custom model"""
        custom_model = CustomModel.objects.create(
            organization=self.organization,
            user=self.user,
            title='Test Model',
            description='Test Description',
            priority='high'
        )
        
        self.assertEqual(custom_model.title, 'Test Model')
        self.assertEqual(custom_model.priority, 'high')
        self.assertTrue(custom_model.is_active)
    
    def test_organization_filtering(self):
        """Test that models are filtered by organization"""
        # Create model for test organization
        CustomModel.objects.create(
            organization=self.organization,
            user=self.user,
            title='Org 1 Model'
        )
        
        # Create another organization and model
        other_org = Organization.objects.create(
            name='Other Organization',
            slug='other-org'
        )
        
        CustomModel.objects.create(
            organization=other_org,
            user=self.user,
            title='Org 2 Model'
        )
        
        # Test filtering
        org_models = CustomModel.objects.filter(organization=self.organization)
        self.assertEqual(org_models.count(), 1)
        self.assertEqual(org_models.first().title, 'Org 1 Model')

class CustomAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        
        self.organization = Organization.objects.create(
            name='API Test Organization',
            slug='api-test-org'
        )
        
        self.membership = OrganizationMembership.objects.create(
            user=self.user,
            organization=self.organization,
            role='member'
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
    
    def test_create_custom_model_via_api(self):
        """Test creating custom model via API"""
        url = reverse('custommodel-list')
        data = {
            'title': 'API Created Model',
            'description': 'Created via API',
            'priority': 'medium'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomModel.objects.count(), 1)
        
        custom_model = CustomModel.objects.first()
        self.assertEqual(custom_model.title, 'API Created Model')
        self.assertEqual(custom_model.organization, self.organization)
        self.assertEqual(custom_model.user, self.user)
    
    def test_custom_action_mark_priority(self):
        """Test custom action for updating priority"""
        # Create a custom model
        custom_model = CustomModel.objects.create(
            organization=self.organization,
            user=self.user,
            title='Test Priority Model',
            priority='low'
        )
        
        # Test the custom action
        url = reverse('custommodel-mark-priority', args=[custom_model.pk])
        data = {'priority': 'high'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the priority was updated
        custom_model.refresh_from_db()
        self.assertEqual(custom_model.priority, 'high')
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the API"""
        self.client.force_authenticate(user=None)  # Unauthenticate
        
        url = reverse('custommodel-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

---

## 10. Analytics and Monitoring

### Analytics Overview

The Enterprise SaaS Foundation includes comprehensive analytics capabilities to track user behavior, system performance, and business metrics. The analytics system provides:

**User Analytics:**
- User activity tracking
- Engagement metrics
- Usage patterns
- Retention analysis

**System Analytics:**
- API usage statistics
- Performance metrics
- Error tracking
- Resource utilization

**Business Analytics:**
- Organization growth
- Feature adoption
- Revenue metrics
- Customer health scores

### User Activity Tracking

#### Automatic Activity Logging

The foundation automatically tracks user activities through middleware and signals:

**Tracked Activities:**
- Login/logout events
- Page views and API calls
- Data modifications (CRUD operations)
- Feature usage
- Error occurrences

**Activity Model:**
```python
from foundation.apps.accounts.models import UserActivity

# View recent user activities
activities = UserActivity.objects.filter(
    user=user,
    timestamp__gte=timezone.now() - timedelta(days=7)
).order_by('-timestamp')

for activity in activities:
    print(f"{activity.timestamp}: {activity.action} - {activity.description}")
```

#### Manual Activity Tracking

**Track Custom Events:**
```python
from foundation.apps.accounts.models import UserActivity

# Track custom user action
UserActivity.objects.create(
    user=request.user,
    action='data_export',
    description='Exported customer data to CSV',
    ip_address=get_client_ip(request),
    metadata={
        'export_type': 'csv',
        'record_count': 1500,
        'file_size_bytes': 250000
    }
)
```

**API Endpoint for Activity Tracking:**
```bash
curl -X POST http://127.0.0.1:8000/api/analytics/activities/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "feature_used",
    "description": "Used advanced analytics dashboard",
    "metadata": {
      "feature": "analytics_dashboard",
      "duration_seconds": 120
    }
  }'
```

### Usage Analytics

#### Usage Metrics Collection

**Usage Metric Model:**
```python
from foundation.apps.analytics.models import UsageMetric

# Record usage metrics
UsageMetric.objects.create(
    organization=org,
    metric_name='api_calls',
    metric_value=1,
    date=timezone.now().date(),
    metadata={
        'endpoint': '/api/users/',
        'method': 'GET',
        'response_time_ms': 150
    }
)
```

#### API Usage Analytics

**Track API Calls Automatically:**
```python
# In middleware or decorators
class APIUsageMiddleware:
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        if request.path.startswith('/api/'):
            # Record API usage
            UsageMetric.objects.create(
                organization=getattr(request, 'organization', None),
                user=getattr(request, 'user', None) if request.user.is_authenticated else None,
                metric_name='api_call',
                metric_value=1,
                date=timezone.now().date(),
                metadata={
                    'endpoint': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'response_time_ms': round((time.time() - start_time) * 1000, 2)
                }
            )
        
        return response
```

#### Getting Usage Analytics

**Via API:**
```bash
# Get organization usage summary
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/analytics/usage/?date__gte=2024-01-01&date__lte=2024-01-31"

# Response:
{
  "summary": {
    "total_api_calls": 15000,
    "total_users": 45,
    "total_sessions": 300,
    "avg_response_time": 180
  },
  "daily_metrics": [
    {
      "date": "2024-01-01",
      "api_calls": 500,
      "active_users": 12,
      "avg_response_time": 175
    }
  ]
}
```

**Via Python:**
```python
from foundation.apps.analytics.models import UsageMetric
from django.db.models import Sum, Avg, Count

# Get usage statistics for organization
stats = UsageMetric.objects.filter(
    organization=org,
    date__gte=start_date,
    date__lte=end_date
).aggregate(
    total_api_calls=Sum('metric_value', filter=Q(metric_name='api_call')),
    avg_response_time=Avg('metadata__response_time_ms'),
    unique_users=Count('user', distinct=True)
)
```

### User Engagement Analytics

#### Engagement Tracking

**User Engagement Model:**
```python
from foundation.apps.analytics.models import UserEngagement

# Track user engagement
engagement = UserEngagement.objects.create(
    user=user,
    organization=org,
    date=timezone.now().date(),
    sessions_count=3,
    total_time_seconds=7200,  # 2 hours
    page_views=45,
    api_calls=120,
    features_used=['dashboard', 'reports', 'settings']
)
```

#### Engagement Metrics

**Daily Engagement Calculation:**
```python
def calculate_daily_engagement(user, date):
    activities = UserActivity.objects.filter(
        user=user,
        timestamp__date=date
    )
    
    # Calculate metrics
    sessions = activities.values('session_id').distinct().count()
    total_time = activities.aggregate(
        total=Sum('metadata__duration_seconds')
    )['total'] or 0
    
    unique_features = set()
    for activity in activities:
        if 'feature' in activity.metadata:
            unique_features.add(activity.metadata['feature'])
    
    # Create or update engagement record
    engagement, created = UserEngagement.objects.update_or_create(
        user=user,
        organization=user.current_organization,
        date=date,
        defaults={
            'sessions_count': sessions,
            'total_time_seconds': total_time,
            'features_used': list(unique_features),
            'engagement_score': calculate_engagement_score(sessions, total_time, len(unique_features))
        }
    )
    
    return engagement
```

#### Engagement Analytics API

```bash
# Get user engagement data
curl -H "Authorization: Token your-token" \
  "http://127.0.0.1:8000/api/analytics/engagement/?user_id=123&date__gte=2024-01-01"

# Get organization engagement summary
curl -H "Authorization: Token admin-token" \
  "http://127.0.0.1:8000/api/analytics/engagement/summary/?date__gte=2024-01-01"
```

### Performance Monitoring

#### Response Time Tracking

**Automatic Performance Monitoring:**
```python
class PerformanceMonitoringMiddleware:
    def __call__(self, request):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        response = self.get_response(request)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        # Record performance metrics
        from foundation.apps.analytics.models import PerformanceMetric
        
        PerformanceMetric.objects.create(
            endpoint=request.path,
            method=request.method,
            response_time_ms=(end_time - start_time) * 1000,
            memory_usage_bytes=end_memory - start_memory,
            status_code=response.status_code,
            timestamp=timezone.now()
        )
        
        return response
```

#### Database Query Monitoring

**Track Database Performance:**
```python
from django.db import connection
from django.core.management.base import BaseCommand

class DatabaseMonitoringMixin:
    def monitor_queries(self, func):
        def wrapper(*args, **kwargs):
            queries_before = len(connection.queries)
            start_time = time.time()
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            queries_after = len(connection.queries)
            
            # Log slow queries
            query_count = queries_after - queries_before
            execution_time = end_time - start_time
            
            if execution_time > 1.0 or query_count > 10:
                logger.warning(f"Slow operation: {query_count} queries in {execution_time:.2f}s")
            
            return result
        return wrapper
```

#### System Health Monitoring

**Health Check Endpoints:**
```bash
# Basic health check
curl http://127.0.0.1:8000/api/health/

# Detailed health check
curl http://127.0.0.1:8000/api/health/detailed/

# Response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": {"status": "healthy", "response_time_ms": 5},
    "redis": {"status": "healthy", "response_time_ms": 2},
    "email": {"status": "healthy"},
    "storage": {"status": "healthy", "free_space_gb": 450}
  },
  "metrics": {
    "active_users": 1250,
    "total_requests_today": 45000,
    "avg_response_time_ms": 180,
    "error_rate_percent": 0.02
  }
}
```

### Analytics Dashboard

#### Dashboard Data API

**Analytics Dashboard Endpoint:**
```bash
curl -H "Authorization: Token admin-token" \
  http://127.0.0.1:8000/api/analytics/dashboard/

# Response:
{
  "user_metrics": {
    "total_users": 1250,
    "active_users_today": 450,
    "new_users_this_week": 75,
    "user_growth_rate": 15.5
  },
  "usage_metrics": {
    "total_api_calls_today": 45000,
    "avg_response_time": 180,
    "error_rate": 0.02,
    "most_used_endpoints": [
      {"endpoint": "/api/users/", "calls": 12000},
      {"endpoint": "/api/organizations/", "calls": 8500}
    ]
  },
  "engagement_metrics": {
    "avg_session_duration": 1800,
    "daily_active_users": 450,
    "feature_adoption": {
      "analytics": 85,
      "messaging": 72,
      "compliance": 45
    }
  }
}
```

#### Custom Analytics Queries

**Build Custom Reports:**
```python
from foundation.apps.analytics.models import UsageMetric, UserActivity
from django.db.models import Count, Avg, Sum

def generate_monthly_report(organization, year, month):
    start_date = date(year, month, 1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # API usage statistics
    api_stats = UsageMetric.objects.filter(
        organization=organization,
        date__range=[start_date, end_date],
        metric_name='api_call'
    ).aggregate(
        total_calls=Sum('metric_value'),
        avg_response_time=Avg('metadata__response_time_ms'),
        unique_endpoints=Count('metadata__endpoint', distinct=True)
    )
    
    # User activity statistics
    user_stats = UserActivity.objects.filter(
        user__organization_memberships__organization=organization,
        timestamp__date__range=[start_date, end_date]
    ).aggregate(
        total_activities=Count('id'),
        unique_users=Count('user', distinct=True),
        unique_actions=Count('action', distinct=True)
    )
    
    return {
        'period': f"{year}-{month:02d}",
        'api_statistics': api_stats,
        'user_statistics': user_stats
    }
```

### Real-time Analytics

#### WebSocket Analytics

**Real-time Analytics Updates:**
```javascript
// Connect to analytics WebSocket
const ws = new WebSocket('ws://127.0.0.1:8000/ws/analytics/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'usage_update') {
        updateDashboard(data.metrics);
    } else if (data.type === 'user_activity') {
        addActivityToFeed(data.activity);
    }
};

// Send analytics query
ws.send(JSON.stringify({
    type: 'subscribe',
    metrics: ['api_calls', 'active_users', 'error_rate']
}));
```

#### Live Metrics Updates

**Server-sent Events for Live Updates:**
```python
from django.http import StreamingHttpResponse
import json
import time

def live_metrics_stream(request):
    def event_stream():
        while True:
            # Get current metrics
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'active_users': get_active_user_count(),
                'api_calls_per_minute': get_api_calls_per_minute(),
                'error_rate': get_current_error_rate()
            }
            
            yield f"data: {json.dumps(metrics)}\n\n"
            time.sleep(5)  # Update every 5 seconds
    
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/plain'
    )
```

### Analytics Configuration

#### Analytics Settings

**Configure Analytics Collection:**
```python
# In settings
ANALYTICS_SETTINGS = {
    'collect_user_activities': True,
    'collect_api_metrics': True,
    'collect_performance_metrics': True,
    'retention_days': 365,
    'sampling_rate': 1.0,  # Collect 100% of events
    'batch_size': 1000,
    'flush_interval_seconds': 60
}

# Feature flags
FEATURE_FLAGS = {
    'real_time_analytics': True,
    'advanced_reporting': True,
    'data_export': True,
    'custom_dashboards': True
}
```

#### Data Retention

**Configure Data Retention Policies:**
```python
from foundation.apps.analytics.models import UsageMetric, UserActivity

# Cleanup old analytics data
def cleanup_old_analytics():
    retention_date = timezone.now() - timedelta(days=settings.ANALYTICS_RETENTION_DAYS)
    
    # Delete old usage metrics
    deleted_metrics = UsageMetric.objects.filter(
        date__lt=retention_date.date()
    ).delete()
    
    # Delete old user activities
    deleted_activities = UserActivity.objects.filter(
        timestamp__lt=retention_date
    ).delete()
    
    return {
        'deleted_metrics': deleted_metrics[0],
        'deleted_activities': deleted_activities[0]
    }
```

---

## 11. Compliance Features

### Compliance Overview

The Enterprise SaaS Foundation includes comprehensive compliance features to help organizations meet regulatory requirements including:

**Supported Compliance Frameworks:**
- **GDPR** (General Data Protection Regulation)
- **HIPAA** (Health Insurance Portability and Accountability Act)
- **SOC 2** (System and Organization Controls 2)
- **PCI-DSS** (Payment Card Industry Data Security Standard)

**Key Compliance Features:**
- Data subject rights management
- Audit logging and trails
- Data retention policies
- Privacy controls and consent management
- Breach detection and notification
- Compliance reporting and dashboards

### GDPR Compliance

#### Data Subject Rights

**GDPR Data Subject Rights Management:**
```python
from foundation.apps.compliance.models import DataSubjectRequest

# Create data subject request
request = DataSubjectRequest.objects.create(
    email="user@example.com",
    request_type="deletion",  # deletion, access, rectification, portability
    description="Please delete all my personal data",
    identity_verified=False,
    organization=org
)

# Process the request
request.status = "in_progress"
request.assigned_to = compliance_officer
request.save()
```

**Data Subject Request Types:**

1. **Right of Access (Article 15)**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/compliance/data-requests/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "request_type": "access",
       "description": "I want to see what personal data you have about me"
     }'
   ```

2. **Right to Rectification (Article 16)**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/compliance/data-requests/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com", 
       "request_type": "rectification",
       "description": "My email address is incorrect"
     }'
   ```

3. **Right to Erasure (Article 17)**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/compliance/data-requests/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "request_type": "deletion", 
       "description": "Delete all my personal data"
     }'
   ```

4. **Right to Data Portability (Article 20)**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/compliance/data-requests/ \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "request_type": "portability",
       "description": "Export my data in a machine-readable format"
     }'
   ```

#### Consent Management

**Consent Tracking:**
```python
from foundation.apps.compliance.models import ConsentRecord

# Record user consent
consent = ConsentRecord.objects.create(
    user=user,
    organization=org,
    purpose="marketing_emails",
    consent_given=True,
    consent_method="web_form",
    legal_basis="consent",
    consent_text="I agree to receive marketing emails",
    ip_address="192.168.1.100"
)

# Withdraw consent
consent.consent_given = False
consent.withdrawal_date = timezone.now()
consent.save()
```

**Consent Management API:**
```bash
# Record consent
curl -X POST http://127.0.0.1:8000/api/compliance/consent/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "purpose": "analytics_cookies",
    "consent_given": true,
    "legal_basis": "consent"
  }'

# Get user's consent status
curl -H "Authorization: Token your-token" \
  http://127.0.0.1:8000/api/compliance/consent/

# Withdraw consent
curl -X PATCH http://127.0.0.1:8000/api/compliance/consent/analytics_cookies/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"consent_given": false}'
```

#### Personal Data Inventory

**Data Processing Activities:**
```python
from foundation.apps.compliance.models import DataProcessingActivity

# Document data processing activity
activity = DataProcessingActivity.objects.create(
    organization=org,
    name="Customer Analytics",
    purpose="Analyze user behavior to improve services",
    legal_basis="legitimate_interest",
    data_categories=["usage_data", "demographic_data"],
    data_subjects=["customers", "website_visitors"],
    recipients=["analytics_team", "product_team"],
    retention_period="2 years",
    security_measures=["encryption", "access_controls"],
    transfer_countries=["US", "EU"],
    dpo_reviewed=True
)
```

### Data Retention Policies

#### Automatic Data Retention

**Configure Retention Policies:**
```python
# In settings or organization configuration
DATA_RETENTION_POLICIES = {
    'user_activities': {
        'retention_days': 365,
        'auto_delete': True
    },
    'audit_logs': {
        'retention_days': 2555,  # 7 years
        'auto_delete': False,    # Archive instead
        'archive_after_days': 365
    },
    'usage_metrics': {
        'retention_days': 1095,  # 3 years
        'auto_delete': True,
        'aggregate_after_days': 90  # Aggregate daily data to monthly
    },
    'personal_data': {
        'retention_days': 1095,  # 3 years
        'auto_delete_after_inactivity': True,
        'inactivity_threshold_days': 365
    }
}
```

**Retention Policy Implementation:**
```python
from foundation.apps.compliance.models import RetentionPolicy

# Create retention policy
policy = RetentionPolicy.objects.create(
    organization=org,
    data_type="customer_data",
    retention_period_days=1095,
    deletion_method="secure_delete",
    legal_basis="contract_completion",
    auto_delete=True,
    created_by=compliance_officer
)

# Apply retention policy
def apply_retention_policies():
    for policy in RetentionPolicy.objects.filter(auto_delete=True):
        cutoff_date = timezone.now() - timedelta(days=policy.retention_period_days)
        
        if policy.data_type == "user_activities":
            expired_data = UserActivity.objects.filter(
                timestamp__lt=cutoff_date,
                user__organization_memberships__organization=policy.organization
            )
            count = expired_data.count()
            expired_data.delete()
            
            # Log retention action
            ComplianceLog.objects.create(
                organization=policy.organization,
                action="data_retention",
                description=f"Deleted {count} expired user activities",
                retention_policy=policy
            )
```

#### Data Deletion and Anonymization

**Secure Data Deletion:**
```python
from foundation.apps.compliance.utils import secure_delete_user_data

def process_deletion_request(data_subject_request):
    user = User.objects.get(email=data_subject_request.email)
    
    # Collect all user data
    user_data = {
        'profile': UserProfile.objects.filter(user=user),
        'activities': UserActivity.objects.filter(user=user),
        'messages': Message.objects.filter(user=user),
        'files': UserFile.objects.filter(user=user)
    }
    
    # Create data export before deletion (if requested)
    if data_subject_request.export_before_deletion:
        export_path = create_data_export(user, user_data)
        data_subject_request.export_file_path = export_path
    
    # Secure deletion
    deletion_log = secure_delete_user_data(user, user_data)
    
    # Update request status
    data_subject_request.status = "completed"
    data_subject_request.completed_at = timezone.now()
    data_subject_request.deletion_log = deletion_log
    data_subject_request.save()
```

**Data Anonymization:**
```python
def anonymize_user_data(user):
    """Anonymize user data while preserving analytics value"""
    
    # Generate anonymous ID
    anonymous_id = f"anon_{uuid.uuid4().hex[:12]}"
    
    # Anonymize personal identifiers
    user.username = anonymous_id
    user.email = f"{anonymous_id}@anonymized.local"
    user.first_name = "Anonymized"
    user.last_name = "User"
    user.is_active = False
    user.save()
    
    # Anonymize related data
    UserProfile.objects.filter(user=user).update(
        phone="[ANONYMIZED]",
        address="[ANONYMIZED]"
    )
    
    # Keep aggregated analytics but remove personal identifiers
    UserActivity.objects.filter(user=user).update(
        ip_address="0.0.0.0",
        user_agent="[ANONYMIZED]"
    )
    
    return anonymous_id
```

### Audit Logging

#### Comprehensive Audit Trail

**Automatic Audit Logging:**
The foundation uses Django-Auditlog to automatically track changes to important models:

```python
from auditlog.models import LogEntry

# View audit logs for a user
logs = LogEntry.objects.get_for_object(user)

for log in logs:
    print(f"{log.timestamp}: {log.action} by {log.actor}")
    if log.changes:
        print(f"Changes: {log.changes}")
```

**Custom Audit Events:**
```python
from foundation.apps.compliance.models import ComplianceLog

# Log compliance-related events
ComplianceLog.objects.create(
    organization=org,
    user=user,
    action="data_access",
    description="User accessed personal data export",
    ip_address=request.META.get('REMOTE_ADDR'),
    metadata={
        'export_type': 'full_profile',
        'file_size': 2048,
        'gdpr_request_id': 'req_123'
    }
)
```

#### Audit Log API

**Query Audit Logs:**
```bash
# Get audit logs for organization
curl -H "Authorization: Token admin-token" \
  "http://127.0.0.1:8000/api/compliance/audit-logs/"

# Filter by date range
curl -H "Authorization: Token admin-token" \
  "http://127.0.0.1:8000/api/compliance/audit-logs/?timestamp__gte=2024-01-01&timestamp__lte=2024-01-31"

# Filter by action type
curl -H "Authorization: Token admin-token" \
  "http://127.0.0.1:8000/api/compliance/audit-logs/?action=data_access"
```

#### Audit Log Analysis

**Compliance Reporting:**
```python
def generate_compliance_report(organization, start_date, end_date):
    logs = ComplianceLog.objects.filter(
        organization=organization,
        timestamp__range=[start_date, end_date]
    )
    
    report = {
        'period': f"{start_date} to {end_date}",
        'total_events': logs.count(),
        'events_by_type': logs.values('action').annotate(
            count=Count('id')
        ).order_by('-count'),
        'data_access_events': logs.filter(
            action='data_access'
        ).count(),
        'data_deletion_events': logs.filter(
            action='data_deletion'
        ).count(),
        'privacy_violations': logs.filter(
            severity='critical'
        ).count()
    }
    
    return report
```

### HIPAA Compliance

#### Protected Health Information (PHI)

**PHI Classification and Handling:**
```python
from foundation.apps.compliance.models import PHIRecord

# Mark data as PHI
phi_record = PHIRecord.objects.create(
    organization=org,
    data_type="medical_record",
    location="database.patient_records",
    encryption_status="encrypted",
    access_controls=["role_based", "mfa_required"],
    retention_period_years=7,
    minimum_necessary=True
)

# Track PHI access
def log_phi_access(user, phi_record, purpose):
    ComplianceLog.objects.create(
        organization=phi_record.organization,
        user=user,
        action="phi_access",
        description=f"Accessed {phi_record.data_type}",
        metadata={
            'phi_record_id': phi_record.id,
            'access_purpose': purpose,
            'minimum_necessary_applied': True
        },
        severity="high"
    )
```

**HIPAA Business Associate Agreements:**
```python
from foundation.apps.compliance.models import BusinessAssociateAgreement

# Track third-party integrations requiring BAAs
baa = BusinessAssociateAgreement.objects.create(
    organization=org,
    vendor_name="Cloud Storage Provider",
    service_description="Document storage and backup",
    agreement_date=timezone.now().date(),
    expiration_date=timezone.now().date() + timedelta(days=365),
    phi_types_covered=["documents", "metadata"],
    security_requirements=["encryption", "access_logs", "data_backup"]
)
```

### SOC 2 Compliance

#### Security Controls

**Access Control Implementation:**
```python
from foundation.apps.compliance.models import SecurityControl

# Document security controls
control = SecurityControl.objects.create(
    organization=org,
    control_id="CC6.1",
    control_name="Logical Access Controls",
    description="System access is restricted to authorized users",
    implementation_status="implemented",
    testing_frequency="quarterly",
    last_tested=timezone.now().date(),
    control_owner=security_officer,
    evidence_location="access_control_policies.pdf"
)

# Track control testing
def test_security_control(control):
    # Perform control testing
    test_results = {
        'test_date': timezone.now().date(),
        'test_method': 'automated_scan',
        'findings': [],
        'status': 'passed'
    }
    
    # Update control
    control.last_tested = test_results['test_date']
    control.testing_results = test_results
    control.save()
    
    # Log testing activity
    ComplianceLog.objects.create(
        organization=control.organization,
        action="control_testing",
        description=f"Tested security control {control.control_id}",
        metadata=test_results
    )
```

#### Vendor Management

**Third-Party Risk Assessment:**
```python
from foundation.apps.compliance.models import VendorAssessment

# Assess third-party vendors
assessment = VendorAssessment.objects.create(
    organization=org,
    vendor_name="Payment Processor",
    service_category="financial",
    risk_level="high",
    soc2_compliant=True,
    assessment_date=timezone.now().date(),
    next_review_date=timezone.now().date() + timedelta(days=365),
    security_questionnaire_completed=True,
    contract_includes_security_terms=True
)
```

### Compliance Dashboard

#### Compliance Metrics API

**Get Compliance Status:**
```bash
# Get overall compliance status
curl -H "Authorization: Token admin-token" \
  http://127.0.0.1:8000/api/compliance/dashboard/

# Response:
{
  "gdpr_status": {
    "data_requests_pending": 3,
    "data_requests_completed": 47,
    "avg_response_time_days": 12,
    "consent_records": 1250,
    "retention_policies_active": 8
  },
  "hipaa_status": {
    "phi_records_protected": 5000,
    "access_violations": 0,
    "business_associates": 12,
    "audit_logs_retained": "7 years"
  },
  "soc2_status": {
    "controls_implemented": 45,
    "controls_tested": 42,
    "last_audit_date": "2024-01-15",
    "findings_open": 2
  },
  "overall_score": 94
}
```

#### Compliance Reporting

**Generate Compliance Reports:**
```python
def generate_gdpr_report(organization, start_date, end_date):
    """Generate GDPR compliance report"""
    
    # Data subject requests
    requests = DataSubjectRequest.objects.filter(
        organization=organization,
        created_at__range=[start_date, end_date]
    )
    
    # Consent records
    consents = ConsentRecord.objects.filter(
        organization=organization,
        created_at__range=[start_date, end_date]
    )
    
    # Data breaches
    breaches = SecurityIncident.objects.filter(
        organization=organization,
        incident_date__range=[start_date, end_date],
        affects_personal_data=True
    )
    
    report = {
        'report_type': 'GDPR Compliance',
        'period': f"{start_date} to {end_date}",
        'organization': organization.name,
        'data_subject_requests': {
            'total': requests.count(),
            'by_type': requests.values('request_type').annotate(count=Count('id')),
            'avg_response_time_days': requests.aggregate(
                avg=Avg('response_time_days')
            )['avg'] or 0,
            'compliance_rate': (
                requests.filter(completed_within_deadline=True).count() / 
                max(requests.count(), 1) * 100
            )
        },
        'consent_management': {
            'new_consents': consents.filter(consent_given=True).count(),
            'withdrawals': consents.filter(consent_given=False).count(),
            'purposes': list(consents.values_list('purpose', flat=True).distinct())
        },
        'data_breaches': {
            'total': breaches.count(),
            'reported_to_authority': breaches.filter(
                reported_to_authority=True
            ).count(),
            'affected_data_subjects': breaches.aggregate(
                total=Sum('affected_individuals_count')
            )['total'] or 0
        }
    }
    
    return report
```

### Breach Detection and Notification

#### Incident Management

**Security Incident Tracking:**
```python
from foundation.apps.compliance.models import SecurityIncident

# Report security incident
incident = SecurityIncident.objects.create(
    organization=org,
    incident_type="data_breach",
    severity="high",
    description="Unauthorized access to customer database",
    incident_date=timezone.now(),
    discovered_date=timezone.now(),
    affects_personal_data=True,
    affected_individuals_count=1500,
    data_types_affected=["names", "emails", "phone_numbers"],
    reported_by=security_officer,
    status="investigating"
)

# Update incident
incident.status = "contained"
incident.containment_date = timezone.now()
incident.save()

# Notify data protection authority (if required)
if incident.requires_authority_notification():
    incident.create_authority_notification()
```

#### Automated Breach Detection

**Anomaly Detection:**
```python
from foundation.apps.compliance.breach_detection import detect_anomalies

def monitor_for_breaches():
    """Monitor system for potential security breaches"""
    
    # Check for unusual access patterns
    unusual_access = detect_unusual_access_patterns()
    
    # Check for bulk data exports
    bulk_exports = detect_bulk_data_exports()
    
    # Check for failed login spikes
    login_anomalies = detect_login_anomalies()
    
    # Create incidents for detected anomalies
    for anomaly in unusual_access + bulk_exports + login_anomalies:
        if anomaly['risk_score'] > 0.8:
            SecurityIncident.objects.create(
                organization=anomaly['organization'],
                incident_type="potential_breach",
                severity=anomaly['severity'],
                description=anomaly['description'],
                incident_date=timezone.now(),
                discovered_date=timezone.now(),
                auto_detected=True,
                metadata=anomaly['details']
            )
```

---

## 12. Advanced Configuration

### Environment Configuration

#### Multi-Environment Setup

The foundation supports multiple environment configurations for different deployment stages:

**Environment Structure:**
```
foundation/config/settings/
├── base.py          # Shared settings
├── development.py   # Development environment
├── testing.py       # Testing environment
├── staging.py       # Staging environment
└── production.py    # Production environment
```

**Development Settings (development.py):**
```python
from .base import *

# Debug mode
DEBUG = True

# Database (SQLite for simplicity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache (Dummy cache for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend (Console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'foundation': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Development tools
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar settings
INTERNAL_IPS = ['127.0.0.1', '::1']
```

**Production Settings (production.py):**
```python
from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Security
DEBUG = False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Sessions and cookies
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Database (PostgreSQL)
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# Redis configuration
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Error monitoring with Sentry
if env('SENTRY_DSN', default=None):
    sentry_sdk.init(
        dsn=env('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True
    )

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/foundation/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler', 
            'filename': '/var/log/foundation/error.log',
            'maxBytes': 1024*1024*15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
        'foundation': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
    },
}
```

#### Environment Variable Management

**Complete .env Template:**
```bash
# Security
DJANGO_SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://username:password@localhost:5432/foundation_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password

# AWS S3 (if using for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
AWS_S3_REGION_NAME=us-east-1

# Error Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Social Authentication (Optional)
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Feature Flags
ENABLE_ANALYTICS=True
ENABLE_REAL_TIME_MESSAGING=True
ENABLE_CONTENT_MODERATION=True
ENABLE_ADVANCED_COMPLIANCE=False

# Rate Limiting
DEFAULT_RATE_LIMIT=1000/hour
API_RATE_LIMIT=10000/hour
ANONYMOUS_RATE_LIMIT=100/hour

# File Upload Limits
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,doc,docx,jpg,png,gif

# Organization Settings
DEFAULT_SUBSCRIPTION_TIER=starter
MAX_ORGS_PER_USER=5
TRIAL_PERIOD_DAYS=14

# Compliance
DATA_RETENTION_DAYS=2555
GDPR_COMPLIANCE=True
HIPAA_COMPLIANCE=False
SOC2_COMPLIANCE=True

# Monitoring
HEALTH_CHECK_ENABLED=True
METRICS_ENABLED=True
AUDIT_LOGGING=True
```

### Database Configuration

#### Database Optimization

**Connection Pooling with pgbouncer:**
```python
# Production database settings with connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default=5432),
        'OPTIONS': {
            'MAX_CONNS': 20,
            'OPTIONS': {
                'MAX_CONNS': 20,
            }
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# Read replica configuration
DATABASES['replica'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': env('DB_REPLICA_NAME'),
    'USER': env('DB_REPLICA_USER'),
    'PASSWORD': env('DB_REPLICA_PASSWORD'),
    'HOST': env('DB_REPLICA_HOST'),
    'PORT': env('DB_REPLICA_PORT', default=5432),
}

# Database routing for read replicas
class DatabaseRouter:
    """Route reads to replica, writes to primary"""
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ['analytics', 'compliance']:
            return 'replica'
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'

DATABASE_ROUTERS = ['foundation.config.routers.DatabaseRouter']
```

**Database Performance Settings:**
```python
# PostgreSQL performance optimization
DATABASES['default']['OPTIONS'] = {
    'CONN_MAX_AGE': 600,
    'OPTIONS': {
        'statement_timeout': 30000,  # 30 seconds
        'lock_timeout': 10000,       # 10 seconds
        'idle_in_transaction_session_timeout': 300000,  # 5 minutes
    }
}

# Database query debugging in development
if DEBUG:
    LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console'],
    }
```

#### Database Backup Configuration

**Automated Backup Script:**
```bash
#!/bin/bash
# backup_database.sh

set -e

# Configuration
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="/backups/postgresql"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/foundation_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Create database backup
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
    --verbose --clean --no-owner --no-acl \
    --format=custom > "${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_FILE}"

# Remove backups older than 30 days
find "${BACKUP_DIR}" -name "foundation_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: ${BACKUP_FILE}.gz"
```

### Caching Configuration

#### Redis Configuration

**Advanced Redis Setup:**
```python
# Redis configuration with multiple databases
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_DEFAULT_URL', default='redis://127.0.0.1:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        }
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_SESSIONS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
    'analytics': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_ANALYTICS_URL', default='redis://127.0.0.1:6379/2'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Use Redis for sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Cache key prefixes
KEY_PREFIX = env('CACHE_KEY_PREFIX', default='foundation')
CACHES['default']['KEY_PREFIX'] = KEY_PREFIX
```

**Cache Invalidation Strategies:**
```python
from django.core.cache import cache, caches
from django.core.cache.utils import make_template_fragment_key

class CacheManager:
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate all cache keys related to a user"""
        cache_keys = [
            f'user_profile_{user_id}',
            f'user_organizations_{user_id}',
            f'user_permissions_{user_id}',
            f'user_activities_{user_id}',
        ]
        cache.delete_many(cache_keys)
    
    @staticmethod
    def invalidate_organization_cache(org_id):
        """Invalidate organization-related cache"""
        cache_keys = [
            f'org_members_{org_id}',
            f'org_settings_{org_id}',
            f'org_usage_{org_id}',
        ]
        cache.delete_many(cache_keys)
    
    @staticmethod
    def warm_up_cache():
        """Warm up frequently accessed cache data"""
        from foundation.apps.accounts.models import Organization
        
        # Warm up organization data
        for org in Organization.objects.filter(is_active=True):
            cache.set(f'org_settings_{org.id}', org.settings, 3600)
            
        # Warm up system settings
        system_settings = get_system_settings()
        cache.set('system_settings', system_settings, 3600)
```

#### Query Optimization

**Database Query Caching:**
```python
from django.core.cache import cache
from django.db.models import Prefetch

class OptimizedQueryMixin:
    def get_cached_queryset(self, cache_key, queryset, timeout=300):
        """Cache queryset results"""
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
            
        # Convert queryset to list to cache it
        data = list(queryset)
        cache.set(cache_key, data, timeout)
        return data
    
    def get_user_organizations(self, user):
        """Get user organizations with caching"""
        cache_key = f'user_organizations_{user.id}'
        return self.get_cached_queryset(
            cache_key,
            user.organization_memberships.select_related('organization'),
            timeout=600
        )
```

### Monitoring and Logging

#### Structured Logging

**Advanced Logging Configuration:**
```python
import structlog

# Structlog configuration
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Django logging with structured logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'structlog.stdlib.ProcessorFormatter',
            'processor': structlog.processors.JSONRenderer(),
        },
        'console': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/foundation/app.log',
            'formatter': 'json',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/foundation/error.log',
            'formatter': 'json',
            'level': 'ERROR',
            'maxBytes': 1024*1024*10,
            'backupCount': 10,
        },
    },
    'loggers': {
        'foundation': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
```

**Application Logging:**
```python
import structlog

logger = structlog.get_logger(__name__)

class UserService:
    def create_user(self, user_data, organization):
        logger.info(
            "Creating new user",
            username=user_data['username'],
            email=user_data['email'],
            organization_id=organization.id,
            organization_name=organization.name
        )
        
        try:
            user = User.objects.create_user(**user_data)
            
            logger.info(
                "User created successfully",
                user_id=user.id,
                username=user.username,
                organization_id=organization.id
            )
            
            return user
            
        except Exception as e:
            logger.error(
                "Failed to create user",
                error=str(e),
                username=user_data.get('username'),
                organization_id=organization.id,
                exc_info=True
            )
            raise
```

#### Health Monitoring

**Comprehensive Health Checks:**
```python
from django.http import JsonResponse
from django.db import connections
from django.core.cache import cache
import redis
import psutil

def detailed_health_check(request):
    """Detailed system health check"""
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {},
        'metrics': {}
    }
    
    # Database health
    try:
        db_conn = connections['default']
        db_conn.cursor().execute("SELECT 1")
        health_data['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_data['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}
        health_data['status'] = 'degraded'
    
    # Redis health
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        health_data['checks']['redis'] = {'status': 'healthy'}
    except Exception as e:
        health_data['checks']['redis'] = {'status': 'unhealthy', 'error': str(e)}
        health_data['status'] = 'degraded'
    
    # System metrics
    health_data['metrics'] = {
        'cpu_usage_percent': psutil.cpu_percent(interval=1),
        'memory_usage_percent': psutil.virtual_memory().percent,
        'disk_usage_percent': psutil.disk_usage('/').percent,
        'active_connections': len(connections.all()),
    }
    
    # Application metrics
    from foundation.apps.accounts.models import User
    health_data['metrics']['total_users'] = User.objects.count()
    health_data['metrics']['active_sessions'] = len(cache.keys('django.contrib.sessions*'))
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return JsonResponse(health_data, status=status_code)
```

### Security Hardening

#### Advanced Security Configuration

**Security Headers:**
```python
# Security headers middleware
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' wss: https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        # Additional security headers
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
```

**Rate Limiting Configuration:**
```python
from django_ratelimit.decorators import ratelimit
from functools import wraps

def smart_ratelimit(view_func):
    """Smart rate limiting based on user type"""
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Different limits for different user types
        if request.user.is_authenticated:
            if request.user.is_superuser:
                limit = '10000/h'  # No practical limit for superusers
            elif hasattr(request.user, 'organization_memberships'):
                org = request.user.organization_memberships.first()
                if org and org.organization.subscription_tier == 'enterprise':
                    limit = '5000/h'  # Higher limit for enterprise
                else:
                    limit = '1000/h'  # Standard user limit
            else:
                limit = '500/h'  # Basic user limit
        else:
            limit = '100/h'  # Anonymous user limit
        
        # Apply rate limiting decorator
        rate_limited_view = ratelimit(
            key='user_or_ip', 
            rate=limit, 
            method=['POST', 'PUT', 'DELETE']
        )(view_func)
        
        return rate_limited_view(request, *args, **kwargs)
    
    return wrapper
```

#### API Security

**API Key Security:**
```python
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class SecureAPIKeyAuthentication(BaseAuthentication):
    """Enhanced API key authentication with additional security"""
    
    def authenticate(self, request):
        api_key = self.get_api_key(request)
        if not api_key:
            return None
            
        try:
            key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True,
                expires_at__gt=timezone.now()
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        
        # Check rate limits
        if not self.check_rate_limit(key_obj, request):
            raise AuthenticationFailed('API key rate limit exceeded')
        
        # Log API key usage
        self.log_api_key_usage(key_obj, request)
        
        # Update last used timestamp
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])
        
        return (key_obj.user, key_obj)
    
    def get_api_key(self, request):
        """Extract API key from request headers"""
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Api-Key '):
            return auth_header[8:]
        return request.META.get('HTTP_X_API_KEY')
    
    def check_rate_limit(self, key_obj, request):
        """Check if API key has exceeded rate limits"""
        cache_key = f'api_key_usage_{key_obj.id}'
        current_usage = cache.get(cache_key, 0)
        
        if current_usage >= key_obj.rate_limit_per_hour:
            return False
            
        cache.set(cache_key, current_usage + 1, 3600)
        return True
    
    def log_api_key_usage(self, key_obj, request):
        """Log API key usage for security monitoring"""
        from foundation.apps.compliance.models import ComplianceLog
        
        ComplianceLog.objects.create(
            organization=key_obj.user.organization_memberships.first().organization,
            user=key_obj.user,
            action='api_key_usage',
            description=f'API key used: {key_obj.name}',
            ip_address=request.META.get('REMOTE_ADDR'),
            metadata={
                'api_key_id': str(key_obj.id),
                'endpoint': request.path,
                'method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255]
            }
        )
```

### Performance Optimization

#### Database Query Optimization

**Query Optimization Techniques:**
```python
from django.db.models import Prefetch, Q, Count, Avg
from django.core.cache import cache

class OptimizedQueryManager:
    @staticmethod
    def get_user_dashboard_data(user):
        """Optimized query for user dashboard"""
        cache_key = f'dashboard_data_{user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Single query with all related data
        user_data = User.objects.select_related(
            'security_profile'
        ).prefetch_related(
            Prefetch(
                'organization_memberships',
                queryset=OrganizationMembership.objects.select_related(
                    'organization'
                ).filter(is_active=True)
            ),
            Prefetch(
                'user_activities',
                queryset=UserActivity.objects.filter(
                    timestamp__gte=timezone.now() - timedelta(days=7)
                ).order_by('-timestamp')[:10]
            ),
            'apikey_set'
        ).get(id=user.id)
        
        # Aggregate data in single queries
        dashboard_data = {
            'user': user_data,
            'organizations': list(user_data.organization_memberships.all()),
            'recent_activities': list(user_data.user_activities.all()),
            'api_keys': list(user_data.apikey_set.filter(is_active=True)),
            'stats': UserActivity.objects.filter(user=user).aggregate(
                total_activities=Count('id'),
                unique_actions=Count('action', distinct=True)
            )
        }
        
        cache.set(cache_key, dashboard_data, 300)  # Cache for 5 minutes
        return dashboard_data
```

**Bulk Operations:**
```python
from django.db import transaction

class BulkOperationsManager:
    @staticmethod
    @transaction.atomic
    def bulk_create_users(user_data_list, organization):
        """Efficiently create multiple users"""
        users_to_create = []
        memberships_to_create = []
        
        for user_data in user_data_list:
            user = User(**user_data)
            users_to_create.append(user)
        
        # Bulk create users
        created_users = User.objects.bulk_create(users_to_create)
        
        # Bulk create memberships
        for user in created_users:
            membership = OrganizationMembership(
                user=user,
                organization=organization,
                role='member'
            )
            memberships_to_create.append(membership)
        
        OrganizationMembership.objects.bulk_create(memberships_to_create)
        
        return created_users
    
    @staticmethod
    def bulk_update_user_status(user_ids, is_active):
        """Efficiently update user status"""
        User.objects.filter(id__in=user_ids).update(
            is_active=is_active,
            modified_at=timezone.now()
        )
        
        # Invalidate related caches
        for user_id in user_ids:
            cache.delete(f'user_profile_{user_id}')
```

#### Background Task Processing

**Celery Configuration:**
```python
from celery import Celery
from celery.schedules import crontab

# Celery configuration
app = Celery('foundation')

app.conf.update(
    # Broker settings
    broker_url=env('REDIS_URL', default='redis://localhost:6379/0'),
    result_backend=env('REDIS_URL', default='redis://localhost:6379/0'),
    
    # Task settings
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-expired-sessions': {
            'task': 'foundation.apps.core.tasks.cleanup_expired_sessions',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'generate-usage-reports': {
            'task': 'foundation.apps.analytics.tasks.generate_usage_reports',
            'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
        },
        'process-data-retention': {
            'task': 'foundation.apps.compliance.tasks.process_data_retention',
            'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
        },
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task routing
app.conf.task_routes = {
    'foundation.apps.analytics.tasks.*': {'queue': 'analytics'},
    'foundation.apps.compliance.tasks.*': {'queue': 'compliance'},
    'foundation.apps.messaging.tasks.*': {'queue': 'messaging'},
}
```

---

<function_calls>
<invoke name="mark_todo_as_done">
<parameter name="todo_ids">["4ab94f3c-fd5e-4b55-baac-abf63c2f2ea7"]
