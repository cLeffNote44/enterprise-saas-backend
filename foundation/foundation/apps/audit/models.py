"""Enhanced audit models."""
import uuid
import json
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class StructuredLog(models.Model):
    """Structured JSON logging for advanced querying."""
    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, db_index=True)
    logger_name = models.CharField(max_length=255, db_index=True)
    message = models.TextField()

    # Context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey('accounts.Organization', on_delete=models.SET_NULL, null=True, blank=True)
    request_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)

    # Structured data
    extra_data = models.JSONField(default=dict, blank=True)
    stack_trace = models.TextField(blank=True)

    # Retention
    retention_days = models.IntegerField(default=90)
    delete_after = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'foundation_structured_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['organization', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        if not self.delete_after:
            self.delete_after = self.timestamp + timezone.timedelta(days=self.retention_days)
        super().save(*args, **kwargs)


class ChangeHistory(models.Model):
    """Field-level change tracking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What changed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Who changed it
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    organization = models.ForeignKey('accounts.Organization', on_delete=models.SET_NULL, null=True, blank=True)

    # Change details
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    change_type = models.CharField(
        max_length=20,
        choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')]
    )

    # Context
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'foundation_change_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]


class AdminAction(models.Model):
    """Track admin actions."""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('custom', 'Custom Action'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )

    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=500)

    # Changes
    change_message = models.TextField(blank=True)
    changes_json = models.JSONField(default=dict, blank=True)

    # Context
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'foundation_admin_action'
        ordering = ['-timestamp']


class ImpersonationLog(models.Model):
    """Track when admins impersonate users."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Who is impersonating
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impersonations_as_admin'
    )

    # Who is being impersonated
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impersonations_as_target'
    )

    # Session details
    session_key = models.CharField(max_length=40, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Reason and context
    reason = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    # Actions taken during impersonation
    actions_log = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'foundation_impersonation_log'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['admin_user', 'is_active']),
            models.Index(fields=['target_user', 'started_at']),
        ]

    def end_session(self):
        """End the impersonation session."""
        self.ended_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['ended_at', 'is_active'])


class GeoLocation(models.Model):
    """IP geolocation cache."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)

    # Location data
    country = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # ISP info
    isp = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_geolocation'


class LogRetentionPolicy(models.Model):
    """Configure log retention policies."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    # Policy configuration
    log_type = models.CharField(
        max_length=50,
        choices=[
            ('audit', 'Audit Logs'),
            ('access', 'Access Logs'),
            ('error', 'Error Logs'),
            ('security', 'Security Logs'),
            ('all', 'All Logs'),
        ]
    )
    retention_days = models.IntegerField()

    # Archive settings
    archive_before_delete = models.BooleanField(default=True)
    archive_location = models.CharField(max_length=500, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_cleanup_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_log_retention_policy'
