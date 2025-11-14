"""
Serializers for rate limiting app.
"""

from rest_framework import serializers
from .models import (
    RateLimit, CustomRateLimit, APIUsage, APIQuota,
    WebhookEndpoint, WebhookDelivery
)


class RateLimitSerializer(serializers.ModelSerializer):
    """Serializer for rate limits."""

    class Meta:
        model = RateLimit
        fields = [
            'id', 'name', 'limit_type', 'endpoint_pattern', 'max_requests',
            'window', 'window_size', 'tier', 'methods', 'is_active',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class APIUsageSerializer(serializers.ModelSerializer):
    """Serializer for API usage records."""

    class Meta:
        model = APIUsage
        fields = [
            'id', 'user', 'organization', 'api_key', 'endpoint', 'method',
            'status_code', 'response_time_ms', 'ip_address', 'is_error',
            'error_message', 'timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at']


class APIQuotaSerializer(serializers.ModelSerializer):
    """Serializer for API quotas."""
    percentage_used = serializers.SerializerMethodField()
    is_exceeded = serializers.SerializerMethodField()

    class Meta:
        model = APIQuota
        fields = [
            'id', 'organization', 'quota_type', 'limit', 'period',
            'current_usage', 'period_start', 'period_end', 'allow_overage',
            'overage_rate', 'is_active', 'percentage_used', 'is_exceeded',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'percentage_used', 'is_exceeded', 'created_at', 'updated_at']

    def get_percentage_used(self, obj):
        return obj.percentage_used()

    def get_is_exceeded(self, obj):
        return obj.is_exceeded()


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for webhook endpoints."""

    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'organization', 'url', 'description', 'enabled_events',
            'is_active', 'last_success_at', 'last_failure_at',
            'consecutive_failures', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_success_at', 'last_failure_at',
            'consecutive_failures', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'secret': {'write_only': True},
        }


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for webhook deliveries."""

    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'endpoint', 'event_type', 'payload', 'status',
            'attempt_count', 'next_retry_at', 'response_status_code',
            'response_time_ms', 'error_message', 'created_at', 'sent_at',
            'succeeded_at', 'failed_at'
        ]
        read_only_fields = [
            'id', 'status', 'attempt_count', 'response_status_code',
            'response_time_ms', 'error_message', 'created_at', 'sent_at',
            'succeeded_at', 'failed_at'
        ]
