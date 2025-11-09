# Example Project Using Enterprise SaaS Foundation

This guide shows how to create a new SaaS application using the foundation.

## Quick Start: Building a Project Management SaaS

### 1. Project Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py          # Extends foundation settings
│   ├── urls.py              # Adds project-specific URLs
│   └── wsgi.py
└── extensions/              # Your custom apps
    ├── projects/            # Project management
    ├── tasks/               # Task tracking
    └── teams/               # Team collaboration
```

### 2. Settings Configuration

```python
# myproject/settings.py
from foundation.config.settings.base import *

# Project-specific apps
PROJECT_EXTENSIONS = [
    'extensions.projects',
    'extensions.tasks',
    'extensions.teams',
]

# Combine with foundation
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + FOUNDATION_APPS + PROJECT_EXTENSIONS

# Project-specific settings
PROJECT_NAME = 'MyProject SaaS'
MAX_PROJECTS_PER_ORG = 100
```

### 3. Create Your First App

```bash
cd myproject
python manage.py startapp projects extensions/projects
```

### 4. Define Models Using Foundation

```python
# extensions/projects/models.py
from django.db import models
from foundation.apps.accounts.models import Organization
from django.conf import settings

class Project(models.Model):
    """Project model inheriting multi-tenant structure."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project'

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task within a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('todo', 'To Do'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
        ],
        default='todo'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task'
```

### 5. Create APIs

```python
# extensions/projects/serializers.py
from rest_framework import serializers
from .models import Project, Task

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'project', 'title', 'description', 'assignee', 'status', 'due_date']
```

```python
# extensions/projects/views.py
from rest_framework import viewsets, permissions
from foundation.apps.accounts.permissions import IsOrganizationMember
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """API for projects."""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return Project.objects.filter(organization_id__in=org_ids)

    def perform_create(self, serializer):
        # Automatically set organization from user's context
        org = self.request.user.organization_memberships.first().organization
        serializer.save(organization=org, owner=self.request.user)
```

### 6. Register URLs

```python
# myproject/urls.py
from django.urls import path, include
from foundation.config.urls import urlpatterns as foundation_urls
from rest_framework.routers import DefaultRouter
from extensions.projects.views import ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = foundation_urls + [
    path('api/myproject/', include(router.urls)),
]
```

### 7. Leverage Foundation Features

#### Use Billing
```python
# Check if user's organization can create more projects
from foundation.apps.billing.models import Subscription

subscription = user.organization_memberships.first().organization.subscriptions.filter(
    status='active'
).first()

if subscription and subscription.plan.tier == 'starter':
    max_projects = 5
elif subscription and subscription.plan.tier == 'professional':
    max_projects = 50
else:
    max_projects = 100
```

#### Use Notifications
```python
# Notify user when task is assigned
from foundation.apps.notifications.models import Notification

Notification.objects.create(
    recipient=task.assignee,
    title="New Task Assigned",
    message=f"You've been assigned: {task.title}",
    category='tasks',
    action_url=f'/projects/{task.project.id}/tasks/{task.id}'
)
```

#### Use Feature Flags
```python
# Enable new features for specific users
from foundation.apps.feature_flags.models import FeatureFlag

gantt_chart_flag = FeatureFlag.objects.get(key='gantt_charts')
if gantt_chart_flag.is_enabled_for_user(user):
    # Show Gantt chart view
    pass
```

#### Use File Uploads
```python
# Attach files to tasks
from foundation.apps.files.models import File

file = File.objects.create(
    organization=task.project.organization,
    uploaded_by=user,
    name='design.pdf',
    file=uploaded_file
)

# Link to task (add a FileField or ManyToMany to your Task model)
task.attachments.add(file)
```

### 8. Add Compliance
```python
# Your app automatically inherits GDPR compliance
from foundation.apps.compliance.models import DataSubjectRequest

# Users can request their data
dsr = DataSubjectRequest.objects.create(
    organization=org,
    request_type='access',
    data_subject_email=user.email
)

# Process includes your custom models
result = dsr.process_request()  # Returns JSON with all user data
```

### 9. Testing

```python
# tests/test_projects.py
from foundation.testing.base import FoundationAPITestCase
from foundation.testing.factories import create_user_with_organization
from extensions.projects.models import Project

class ProjectAPITestCase(FoundationAPITestCase):
    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            organization=self.org,
            name="Test Project",
            owner=self.user
        )

    def test_list_projects(self):
        response = self.client.get('/api/myproject/projects/')
        self.assert_response_success(response)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_project(self):
        data = {
            'name': 'New Project',
            'description': 'Test description'
        }
        response = self.post_json('/api/myproject/projects/', data)
        self.assert_response_success(response, 201)
```

### 10. Deploy

All foundation deployment tools work for your project:

```bash
# Build Docker image
docker build -t myproject:latest .

# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Or use Terraform
cd terraform
terraform apply
```

## Complete Example

See the `/examples/project-management-saas/` directory for a complete, working example.

## Best Practices

1. **Always use Organization scoping**
   - Filter all queries by organization
   - Use foundation's permission classes

2. **Leverage existing features**
   - Don't rebuild authentication
   - Don't rebuild billing
   - Don't rebuild notifications

3. **Follow the pattern**
   - UUID primary keys
   - created_at/updated_at timestamps
   - Soft deletes where appropriate

4. **Use foundation testing utilities**
   - Import factories
   - Extend base test cases
   - Mock external services

5. **Security first**
   - Use foundation permissions
   - Add audit logging
   - Follow RBAC patterns

## Additional Resources

- Foundation API Reference: `/api/docs/`
- Foundation Documentation: `/COMPREHENSIVE_GUIDE.md`
- Foundation Source: `/foundation/foundation/apps/`
