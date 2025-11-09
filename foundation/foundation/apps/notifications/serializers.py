"""
Serializers for notifications app.
"""

from rest_framework import serializers
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    NotificationDelivery, DigestSchedule, NotificationChannel
)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'channel', 'subject', 'body_text', 'body_html',
            'available_variables', 'organization', 'version', 'is_active',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'title', 'message', 'priority', 'category',
            'action_url', 'status', 'read_at', 'sent_at', 'delivered_at',
            'is_read', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'read_at', 'sent_at', 'delivered_at', 'is_read', 'created_at']

    def get_is_read(self, obj):
        return obj.read_at is not None


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'email_enabled', 'sms_enabled', 'push_enabled',
            'in_app_enabled', 'category_preferences', 'digest_enabled',
            'digest_frequency', 'digest_time', 'dnd_enabled', 'dnd_start',
            'dnd_end', 'sms_phone', 'push_device_tokens', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NotificationDeliverySerializer(serializers.ModelSerializer):
    """Serializer for notification deliveries."""

    class Meta:
        model = NotificationDelivery
        fields = [
            'id', 'notification', 'channel', 'recipient_address', 'status',
            'sent_at', 'delivered_at', 'failed_at', 'clicked_at',
            'error_code', 'error_message', 'retry_count', 'external_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DigestScheduleSerializer(serializers.ModelSerializer):
    """Serializer for digest schedules."""

    class Meta:
        model = DigestSchedule
        fields = [
            'id', 'user', 'frequency', 'send_time', 'send_day', 'categories',
            'min_priority', 'is_active', 'last_sent_at', 'next_send_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_sent_at', 'created_at', 'updated_at']


class NotificationChannelSerializer(serializers.ModelSerializer):
    """Serializer for notification channels."""

    class Meta:
        model = NotificationChannel
        fields = [
            'id', 'organization', 'name', 'channel_type', 'webhook_url',
            'configuration', 'categories', 'min_priority', 'is_active',
            'last_used_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_used_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_token': {'write_only': True},
        }
