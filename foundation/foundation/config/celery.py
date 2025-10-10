"""
Celery configuration for Enterprise SaaS Foundation
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foundation.config.settings.docker')

# Create Celery app
app = Celery('foundation')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Configure task routing
app.conf.task_routes = {
    'foundation.apps.analytics.*': {'queue': 'analytics'},
    'foundation.apps.messaging.*': {'queue': 'messaging'},
    'foundation.apps.compliance.*': {'queue': 'compliance'},
    'foundation.apps.moderation.*': {'queue': 'moderation'},
}

# Default queue
app.conf.task_default_queue = 'default'

# Task time limits
app.conf.task_time_limit = 300  # 5 minutes
app.conf.task_soft_time_limit = 240  # 4 minutes

# Result expiration
app.conf.result_expires = 3600  # 1 hour

# Serialization
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Timezone
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Cleanup old analytics events daily at 2 AM
    'cleanup-old-analytics': {
        'task': 'foundation.apps.analytics.tasks.cleanup_old_events',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'analytics'}
    },
    
    # Check compliance policies every 6 hours
    'check-compliance-policies': {
        'task': 'foundation.apps.compliance.tasks.check_compliance_policies',
        'schedule': crontab(minute=0, hour='*/6'),
        'options': {'queue': 'compliance'}
    },
    
    # Send daily digest emails at 9 AM
    'send-daily-digest': {
        'task': 'foundation.apps.messaging.tasks.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),
        'options': {'queue': 'messaging'}
    },
    
    # Generate analytics reports weekly on Monday at 3 AM
    'generate-weekly-analytics': {
        'task': 'foundation.apps.analytics.tasks.generate_weekly_report',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),
        'options': {'queue': 'analytics'}
    },
    
    # Health check every 5 minutes
    'health-check': {
        'task': 'foundation.apps.core.tasks.health_check',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'default'}
    },
}

# Worker configuration
app.conf.worker_prefetch_multiplier = 4
app.conf.worker_max_tasks_per_child = 1000
app.conf.worker_disable_rate_limits = False

# Error handling
app.conf.task_reject_on_worker_lost = True
app.conf.task_ignore_result = False

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
    return 'Debug task completed!'


@app.task
def test_task():
    """Simple test task"""
    return 'Test task executed successfully!'


# Signal handlers for monitoring
from celery.signals import task_success, task_failure, task_retry

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Log successful task completion"""
    from django.utils import timezone
    print(f"Task {sender.name} completed successfully at {timezone.now()}")

@task_failure.connect  
def task_failure_handler(sender=None, exception=None, traceback=None, **kwargs):
    """Log task failures"""
    from django.utils import timezone
    print(f"Task {sender.name} failed at {timezone.now()}: {exception}")

@task_retry.connect
def task_retry_handler(sender=None, reason=None, **kwargs):
    """Log task retries"""
    from django.utils import timezone
    print(f"Task {sender.name} retried at {timezone.now()}: {reason}")