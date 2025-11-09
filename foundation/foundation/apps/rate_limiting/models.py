"""
Rate limiting and API management models.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class RateLimit(models.Model):
    """
    Rate limit configurations for API endpoints.
    """
    LIMIT_TYPE_CHOICES = [
        ('per_user', 'Per User'),
        ('per_org', 'Per Organization'),
        ('per_ip', 'Per IP Address'),
        ('per_api_key', 'Per API Key'),
        ('global', 'Global'),
    ]

    WINDOW_CHOICES = [
        ('second', 'Second'),
        ('minute', 'Minute'),
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('month', 'Month'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Descriptive name for this rate limit")

    # Scope
    limit_type = models.CharField(max_length=20, choices=LIMIT_TYPE_CHOICES)
    endpoint_pattern = models.CharField(
        max_length=255,
        help_text="URL pattern (e.g., '/api/users/*' or '/api/billing/*')"
    )

    # Limit configuration
    max_requests = models.IntegerField(help_text="Maximum number of requests")
    window = models.CharField(max_length=20, choices=WINDOW_CHOICES)
    window_size = models.IntegerField(default=1, help_text="Size of the time window")

    # Tier-specific limits
    tier = models.CharField(
        max_length=50,
        blank=True,
        help_text="Subscription tier this limit applies to (empty = all tiers)"
    )

    # HTTP methods
    methods = models.JSONField(
        default=list,
        help_text="HTTP methods to limit (empty = all methods)"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_rate_limit'
        ordering = ['endpoint_pattern']
        indexes = [
            models.Index(fields=['endpoint_pattern', 'is_active']),
            models.Index(fields=['tier']),
        ]

    def __str__(self):
        return f"{self.name}: {self.max_requests}/{self.window_size} {self.window}(s)"


class CustomRateLimit(models.Model):
    """
    Custom rate limits for specific organizations or users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Target
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_rate_limits'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_rate_limits'
    )

    # Configuration
    rate_limit = models.ForeignKey(
        RateLimit,
        on_delete=models.CASCADE,
        related_name='custom_limits'
    )
    custom_max_requests = models.IntegerField(help_text="Custom request limit")

    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    reason = models.TextField(blank=True, help_text="Reason for custom limit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_custom_limits'
    )

    class Meta:
        db_table = 'foundation_custom_rate_limit'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        target = self.organization or self.user
        return f"Custom limit for {target}: {self.custom_max_requests} requests"


class APIUsage(models.Model):
    """
    Tracks API usage for analytics and billing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Who made the request
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='api_usage'
    )
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='api_usage'
    )
    api_key = models.ForeignKey(
        'accounts.APIKey',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage_records'
    )

    # Request details
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField(help_text="Response time in milliseconds")

    # Request metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_size_bytes = models.IntegerField(null=True, blank=True)
    response_size_bytes = models.IntegerField(null=True, blank=True)

    # Error tracking
    is_error = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_api_usage'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['organization', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"


class APIQuota(models.Model):
    """
    Monthly/daily API quotas for organizations.
    """
    QUOTA_TYPE_CHOICES = [
        ('requests', 'API Requests'),
        ('storage', 'Storage (GB)'),
        ('data_transfer', 'Data Transfer (GB)'),
        ('custom', 'Custom Metric'),
    ]

    PERIOD_CHOICES = [
        ('day', 'Daily'),
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='api_quotas'
    )

    # Quota configuration
    quota_type = models.CharField(max_length=50, choices=QUOTA_TYPE_CHOICES)
    limit = models.BigIntegerField(help_text="Maximum allowed in period")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)

    # Current usage
    current_usage = models.BigIntegerField(default=0)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Overage handling
    allow_overage = models.BooleanField(default=False)
    overage_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Cost per unit over quota"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_api_quota'
        ordering = ['organization', 'quota_type']
        unique_together = [['organization', 'quota_type', 'period_start']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['period_end']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.get_quota_type_display()}: {self.current_usage}/{self.limit}"

    def is_exceeded(self):
        """Check if quota is exceeded."""
        return self.current_usage >= self.limit

    def percentage_used(self):
        """Calculate percentage of quota used."""
        if self.limit == 0:
            return 0
        return (self.current_usage / self.limit) * 100


class WebhookEndpoint(models.Model):
    """
    Customer webhook endpoints for receiving events.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='webhook_endpoints'
    )

    # Endpoint configuration
    url = models.URLField()
    description = models.CharField(max_length=255, blank=True)

    # Authentication
    secret = models.CharField(max_length=255, help_text="Secret for HMAC signature")

    # Event filtering
    enabled_events = models.JSONField(
        default=list,
        help_text="List of event types to send to this endpoint"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Stats
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_failure_at = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_webhook_endpoint'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.url}"


class WebhookDelivery(models.Model):
    """
    Tracks webhook delivery attempts.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    # Event details
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()

    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attempt_count = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Response details
    response_status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'foundation_webhook_delivery'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['endpoint', 'status']),
            models.Index(fields=['event_type']),
            models.Index(fields=['next_retry_at']),
        ]

    def __str__(self):
        return f"{self.event_type} to {self.endpoint.url} - {self.get_status_display()}"

    def should_retry(self):
        """Check if delivery should be retried."""
        MAX_RETRIES = 5
        return self.status == 'failed' and self.attempt_count < MAX_RETRIES

    def calculate_next_retry(self):
        """Calculate next retry time using exponential backoff."""
        if not self.should_retry():
            return None

        # Exponential backoff: 1min, 5min, 25min, 2h, 10h
        delays = [60, 300, 1500, 7200, 36000]
        delay_seconds = delays[min(self.attempt_count, len(delays) - 1)]

        return timezone.now() + timedelta(seconds=delay_seconds)
