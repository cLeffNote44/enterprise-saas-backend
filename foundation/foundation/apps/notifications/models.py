"""
Notification models.
"""

import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class NotificationTemplate(models.Model):
    """
    Templates for notifications across all channels.
    """
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App Notification'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)

    # Template content
    subject = models.CharField(max_length=255, blank=True, help_text="For email/push notifications")
    body_text = models.TextField(help_text="Plain text body")
    body_html = models.TextField(blank=True, help_text="HTML body for email")

    # Template variables (for documentation)
    available_variables = models.JSONField(
        default=list,
        help_text="List of available template variables"
    )

    # Organization-specific templates
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notification_templates',
        help_text="Leave empty for global templates"
    )

    # Versioning
    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates'
    )

    class Meta:
        db_table = 'foundation_notification_template'
        ordering = ['name']
        unique_together = [['name', 'version']]
        indexes = [
            models.Index(fields=['channel', 'is_active']),
            models.Index(fields=['organization']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_channel_display()}) v{self.version}"


class Notification(models.Model):
    """
    In-app notifications and notification records.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Notification content
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    # Categorization
    category = models.CharField(max_length=50, blank=True, help_text="e.g., 'billing', 'security', 'system'")
    action_url = models.URLField(blank=True, help_text="URL to navigate to when clicked")

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    # Related object (generic relation)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Template used (if any)
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['recipient', 'read_at']),
            models.Index(fields=['category']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.title} to {self.recipient.username}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.status = 'read'
            self.save(update_fields=['read_at', 'status'])


class NotificationPreference(models.Model):
    """
    User preferences for notification channels and categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    # Category preferences (JSON structure)
    # Example: {"billing": {"email": true, "sms": false}, "security": {"email": true, "sms": true}}
    category_preferences = models.JSONField(
        default=dict,
        help_text="Per-category channel preferences"
    )

    # Digest settings
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='daily'
    )
    digest_time = models.TimeField(default='09:00', help_text="Time to send digest")

    # Do Not Disturb
    dnd_enabled = models.BooleanField(default=False)
    dnd_start = models.TimeField(null=True, blank=True, help_text="DND start time")
    dnd_end = models.TimeField(null=True, blank=True, help_text="DND end time")

    # Contact information
    sms_phone = models.CharField(max_length=20, blank=True)
    push_device_tokens = models.JSONField(default=list, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_notification_preference'

    def __str__(self):
        return f"Preferences for {self.user.username}"

    def should_send(self, channel, category=None):
        """Check if notification should be sent via channel for category."""
        # Check if channel is globally enabled
        channel_enabled = getattr(self, f'{channel}_enabled', False)
        if not channel_enabled:
            return False

        # Check category-specific preferences
        if category and category in self.category_preferences:
            return self.category_preferences[category].get(channel, channel_enabled)

        return channel_enabled


class NotificationDelivery(models.Model):
    """
    Tracks delivery of notifications across all channels.
    """
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'In-App'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
        ('clicked', 'Clicked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    # Channel details
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    recipient_address = models.CharField(
        max_length=255,
        help_text="Email address, phone number, device token, etc."
    )

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    last_retry_at = models.DateTimeField(null=True, blank=True)

    # External tracking (from providers like SendGrid, Twilio, etc.)
    external_id = models.CharField(max_length=255, blank=True)
    external_data = models.JSONField(default=dict, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_notification_delivery'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification', 'channel']),
            models.Index(fields=['status']),
            models.Index(fields=['external_id']),
        ]

    def __str__(self):
        return f"{self.get_channel_display()} delivery for {self.notification.title}"


class DigestSchedule(models.Model):
    """
    Scheduled digest notifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='digest_schedules'
    )

    # Schedule details
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ]
    )
    send_time = models.TimeField(help_text="Time to send digest")
    send_day = models.IntegerField(
        null=True,
        blank=True,
        help_text="Day of week (0=Monday) or day of month"
    )

    # Content filters
    categories = models.JSONField(
        default=list,
        help_text="Categories to include in digest"
    )
    min_priority = models.CharField(
        max_length=20,
        choices=Notification.PRIORITY_CHOICES,
        default='normal',
        help_text="Minimum priority to include"
    )

    # Status
    is_active = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    next_send_at = models.DateTimeField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_digest_schedule'
        ordering = ['next_send_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['next_send_at']),
        ]

    def __str__(self):
        return f"{self.get_frequency_display()} digest for {self.user.username}"


class NotificationChannel(models.Model):
    """
    Configuration for external notification channels (Slack, webhooks, etc.).
    """
    CHANNEL_TYPE_CHOICES = [
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('discord', 'Discord'),
        ('custom', 'Custom Integration'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='notification_channels'
    )

    # Channel details
    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES)

    # Configuration
    webhook_url = models.URLField(blank=True)
    api_token = models.CharField(max_length=255, blank=True)
    configuration = models.JSONField(
        default=dict,
        help_text="Channel-specific configuration"
    )

    # Filtering
    categories = models.JSONField(
        default=list,
        help_text="Categories to send to this channel (empty = all)"
    )
    min_priority = models.CharField(
        max_length=20,
        choices=Notification.PRIORITY_CHOICES,
        default='normal'
    )

    # Status
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_notification_channel'
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['channel_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"
