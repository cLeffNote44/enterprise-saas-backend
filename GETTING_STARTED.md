# 🚀 Getting Started

Welcome to the **Enterprise SaaS Foundation**! This guide will have you up and running with your first SaaS application in under 10 minutes.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 15+** ([Download](https://www.postgresql.org/download/))
- **Redis 7.0+** ([Download](https://redis.io/download))
- **Git** ([Download](https://git-scm.com/downloads))
- **Docker** (Optional, recommended) ([Download](https://www.docker.com/get-started))

## ⚡ Quick Start (Docker - Recommended)

The fastest way to get started is using Docker Compose:

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/enterprise-saas-backend.git
cd enterprise-saas-backend
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and configure your settings:

```bash
# Required settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://foundation:foundation@db:5432/foundation

# Redis
REDIS_URL=redis://redis:6379/0

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Optional: Payment processing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Step 3: Start the Application

```bash
docker-compose up -d
```

This will start:
- Django web server (http://localhost:8000)
- PostgreSQL database
- Redis cache
- Celery worker (async tasks)
- Celery beat (scheduled tasks)

### Step 4: Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### Step 5: Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### Step 6: Access Your Application

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/schema/swagger-ui/
- **Health Check**: http://localhost:8000/health/

**🎉 Congratulations! Your SaaS backend is now running!**

## 🔧 Manual Setup (Without Docker)

### Step 1: Clone and Setup Virtual Environment

```bash
git clone https://github.com/yourusername/enterprise-saas-backend.git
cd enterprise-saas-backend

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements/dev.txt
```

### Step 2: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE foundation;
CREATE USER foundation WITH PASSWORD 'foundation';
ALTER ROLE foundation SET client_encoding TO 'utf8';
ALTER ROLE foundation SET default_transaction_isolation TO 'read committed';
ALTER ROLE foundation SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE foundation TO foundation;
\q
```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://foundation:foundation@localhost:5432/foundation
REDIS_URL=redis://localhost:6379/0
```

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 6: Start Development Server

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A foundation worker -l info

# Terminal 3: Celery Beat
celery -A foundation beat -l info
```

## 📱 Building Your First SaaS App

Let's build a simple project management SaaS to demonstrate the foundation's capabilities.

### Step 1: Create Your Custom App

```bash
cd foundation/apps
python ../../manage.py startapp projects
```

### Step 2: Define Your Models

Edit `foundation/apps/projects/models.py`:

```python
from django.db import models
from django.conf import settings
from foundation.apps.accounts.models import Organization

class Project(models.Model):
    """Project model."""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects_project'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task model."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects_task'
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return self.title
```

### Step 3: Create Serializers

Create `foundation/apps/projects/serializers.py`:

```python
from rest_framework import serializers
from .models import Project, Task

class TaskSerializer(serializers.ModelSerializer):
    assignee_name = serializers.CharField(source='assignee.get_full_name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority',
            'assignee', 'assignee_name', 'is_completed',
            'due_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status',
            'created_by', 'created_by_name', 'tasks',
            'task_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Automatically set organization and creator
        validated_data['organization'] = self.context['request'].user.organization
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
```

### Step 4: Create ViewSets

Create `foundation/apps/projects/views.py`:

```python
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """Project management endpoints."""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']

    def get_queryset(self):
        # Automatically filter by user's organization
        return Project.objects.filter(
            organization=self.request.user.organization
        ).prefetch_related('tasks')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark project as completed."""
        project = self.get_object()
        project.status = 'completed'
        project.save()
        return Response({'status': 'project completed'})


class TaskViewSet(viewsets.ModelViewSet):
    """Task management endpoints."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'is_completed', 'assignee']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        # Filter by user's organization through project
        return Task.objects.filter(
            project__organization=self.request.user.organization
        ).select_related('project', 'assignee')

    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        """Toggle task completion status."""
        task = self.get_object()
        task.is_completed = not task.is_completed
        task.save()
        return Response({'status': 'toggled', 'is_completed': task.is_completed})
```

### Step 5: Configure URLs

Create `foundation/apps/projects/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
```

### Step 6: Register App

Edit `foundation/config/settings/base.py`:

```python
PROJECT_APPS = [
    'foundation.apps.projects',  # Add this line
]
```

Edit `foundation/config/urls.py`:

```python
urlpatterns = [
    # ... existing patterns ...
    path('api/projects/', include('foundation.apps.projects.urls')),  # Add this
]
```

### Step 7: Create Admin Interface

Create `foundation/apps/projects/admin.py`:

```python
from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'organization', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'priority', 'assignee', 'is_completed', 'due_date']
    list_filter = ['priority', 'is_completed', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
```

### Step 8: Create and Run Migrations

```bash
python manage.py makemigrations projects
python manage.py migrate
```

### Step 9: Test Your API

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Create a project
curl -X POST http://localhost:8000/api/projects/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Project",
    "description": "Building an awesome SaaS app",
    "status": "active"
  }'

# List projects
curl -X GET http://localhost:8000/api/projects/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create a task
curl -X POST http://localhost:8000/api/projects/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "title": "Setup development environment",
    "priority": "high",
    "due_date": "2024-12-31"
  }'
```

**🎉 Congratulations! You've built your first SaaS feature on the foundation!**

## 🧪 Running Tests

The foundation includes comprehensive tests and test utilities.

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=foundation --cov-report=html
```

### Run Specific Tests

```bash
# Test specific app
pytest foundation/apps/accounts/

# Test specific file
pytest foundation/apps/accounts/tests/test_models.py

# Run in parallel
pytest -n auto
```

### Writing Tests for Your App

Create `foundation/apps/projects/tests/test_models.py`:

```python
from foundation.testing.base import FoundationTestCase
from foundation.testing.factories import UserFactory, OrganizationFactory
from ..models import Project, Task

class ProjectModelTest(FoundationTestCase):
    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            organization=self.org,
            name="Test Project",
            created_by=self.user
        )

    def test_project_creation(self):
        """Test project can be created."""
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.status, "planning")

    def test_project_organization_isolation(self):
        """Test projects are isolated by organization."""
        other_org = OrganizationFactory(name="Other Org")
        other_project = Project.objects.create(
            organization=other_org,
            name="Other Project",
            created_by=self.user
        )

        # Should only see projects in own organization
        org_projects = Project.objects.filter(organization=self.org)
        self.assertEqual(org_projects.count(), 1)
        self.assertNotIn(other_project, org_projects)
```

Create `foundation/apps/projects/tests/test_api.py`:

```python
from rest_framework import status
from foundation.testing.base import FoundationAPITestCase
from ..models import Project

class ProjectAPITest(FoundationAPITestCase):
    def test_create_project(self):
        """Test creating a project via API."""
        data = {
            'name': 'API Test Project',
            'description': 'Created via API',
            'status': 'active'
        }
        response = self.post_json('/api/projects/projects/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Test Project')

        # Verify in database
        self.assertTrue(
            Project.objects.filter(
                name='API Test Project',
                organization=self.org
            ).exists()
        )

    def test_list_projects(self):
        """Test listing projects."""
        # Create test data
        Project.objects.create(
            organization=self.org,
            name="Project 1",
            created_by=self.user
        )
        Project.objects.create(
            organization=self.org,
            name="Project 2",
            created_by=self.user
        )

        response = self.get_json('/api/projects/projects/')

        self.assertEqual(len(response.data['results']), 2)
```

## 📚 Next Steps

Now that you have the basics down, explore these advanced features:

### 1. Add Billing to Your App

```python
from foundation.apps.billing.models import Subscription

# Check if user has active subscription
if Subscription.objects.filter(
    organization=request.user.organization,
    status='active'
).exists():
    # Allow premium features
    pass
```

See [Billing Documentation](FEATURES.md#-billing--subscriptions) for more details.

### 2. Add Notifications

```python
from foundation.apps.notifications.services import NotificationService

# Send notification
NotificationService.send(
    user=user,
    title="New Task Assigned",
    message=f"You've been assigned to task: {task.title}",
    priority="high",
    action_url=f"/tasks/{task.id}"
)
```

See [Notification Documentation](FEATURES.md#-notifications) for more details.

### 3. Implement Feature Flags

```python
from foundation.apps.feature_flags.models import FeatureFlag

# Check if feature is enabled
if FeatureFlag.objects.is_enabled('advanced_analytics', user):
    # Show advanced analytics
    pass
```

See [Feature Flags Documentation](FEATURES.md#-feature-flags--ab-testing) for more details.

### 4. Add File Uploads

```python
from foundation.apps.files.models import File

# Upload file
file = File.objects.create(
    organization=request.user.organization,
    uploaded_by=request.user,
    file=request.FILES['file'],
    content_type=content_type
)
```

See [File Management Documentation](FEATURES.md#-file-management) for more details.

### 5. Set Up Webhooks

```python
from foundation.apps.webhooks.models import Webhook

# Register webhook
webhook = Webhook.objects.create(
    organization=organization,
    url="https://example.com/webhooks/",
    events=['project.created', 'task.completed']
)
```

See [Webhook Documentation](FEATURES.md#-webhooks) for more details.

## 🎓 Learning Resources

- **[Architecture Guide](ARCHITECTURE.md)** - Understand the system design
- **[Feature Documentation](FEATURES.md)** - Explore all available features
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to production
- **[Example Projects](EXAMPLE_PROJECT.md)** - See complete examples

## 🆘 Getting Help

- **Documentation**: https://docs.yourcompany.com
- **GitHub Issues**: https://github.com/yourusername/enterprise-saas-backend/issues
- **Community Discord**: https://discord.gg/yourserver
- **Email Support**: support@yourcompany.com

### Enterprise Support

Get 24/7 priority support, dedicated success manager, and custom feature development:

📧 enterprise@yourcompany.com

## 💡 Tips & Best Practices

### Security

1. ✅ **Always use HTTPS in production**
2. ✅ **Keep SECRET_KEY secret** (never commit to git)
3. ✅ **Set DEBUG=False in production**
4. ✅ **Use environment variables for sensitive data**
5. ✅ **Enable rate limiting for all public endpoints**

### Performance

1. ✅ **Use select_related() and prefetch_related()** for query optimization
2. ✅ **Enable caching** for frequently accessed data
3. ✅ **Use Celery** for long-running tasks
4. ✅ **Optimize database indexes**
5. ✅ **Use CDN** for static files

### Development

1. ✅ **Write tests** for all new features
2. ✅ **Use migrations** for all database changes
3. ✅ **Follow Django/DRF best practices**
4. ✅ **Document your code**
5. ✅ **Use the provided test factories**

## 🎯 Common Tasks

### Add a New API Endpoint

```python
# In your views.py
@action(detail=True, methods=['post'])
def custom_action(self, request, pk=None):
    obj = self.get_object()
    # Your logic here
    return Response({'status': 'success'})
```

### Add Custom Permissions

```python
from rest_framework import permissions

class IsProjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
```

### Schedule a Periodic Task

```python
# In your tasks.py
from celery import shared_task
from celery.schedules import crontab

@shared_task
def cleanup_old_data():
    # Your cleanup logic
    pass

# In settings.py
CELERY_BEAT_SCHEDULE = {
    'cleanup-every-day': {
        'task': 'foundation.apps.projects.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
}
```

### Add Custom Validation

```python
class ProjectSerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value
```

---

**Ready to build something amazing?** Start coding and deploy your SaaS in hours, not months! 🚀
