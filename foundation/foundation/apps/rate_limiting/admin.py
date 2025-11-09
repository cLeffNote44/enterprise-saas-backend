"""
Admin interface for rate limiting app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    RateLimit, CustomRateLimit, APIUsage, APIQuota,
    WebhookEndpoint, WebhookDelivery
)


@admin.register(RateLimit)
class RateLimitAdmin(admin.ModelAdmin):
    list_display = ['name', 'endpoint_pattern', 'limit_display', 'tier', 'is_active']
    list_filter = ['limit_type', 'window', 'tier', 'is_active']
    search_fields = ['name', 'endpoint_pattern']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Scope', {
            'fields': ('limit_type', 'endpoint_pattern', 'tier', 'methods')
        }),
        ('Limit Configuration', {
            'fields': ('max_requests', 'window', 'window_size')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def limit_display(self, obj):
        return f"{obj.max_requests}/{obj.window_size} {obj.window}(s)"
    limit_display.short_description = 'Limit'


@admin.register(CustomRateLimit)
class CustomRateLimitAdmin(admin.ModelAdmin):
    list_display = ['target_display', 'rate_limit', 'custom_max_requests', 'is_active', 'valid_until']
    list_filter = ['is_active']
    search_fields = ['organization__name', 'user__username', 'reason']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Target', {
            'fields': ('organization', 'user')
        }),
        ('Configuration', {
            'fields': ('rate_limit', 'custom_max_requests')
        }),
        ('Validity', {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
        ('Metadata', {
            'fields': ('reason', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def target_display(self, obj):
        return str(obj.organization or obj.user)
    target_display.short_description = 'Target'


@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'user', 'organization', 'method', 'endpoint',
        'status_code', 'response_time_ms', 'is_error'
    ]
    list_filter = ['method', 'is_error', 'status_code', 'timestamp']
    search_fields = ['endpoint', 'user__username', 'organization__name', 'ip_address']
    readonly_fields = ['timestamp', 'created_at']
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Request Details', {
            'fields': ('user', 'organization', 'api_key', 'endpoint', 'method')
        }),
        ('Response', {
            'fields': ('status_code', 'response_time_ms', 'is_error', 'error_message')
        }),
        ('Metadata', {
            'fields': (
                'ip_address', 'user_agent', 'request_size_bytes',
                'response_size_bytes'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(APIQuota)
class APIQuotaAdmin(admin.ModelAdmin):
    list_display = [
        'organization', 'quota_type', 'usage_display', 'period',
        'period_end', 'is_exceeded_display'
    ]
    list_filter = ['quota_type', 'period', 'is_active']
    search_fields = ['organization__name']
    readonly_fields = ['created_at', 'updated_at', 'percentage_used']

    fieldsets = (
        ('Organization', {
            'fields': ('organization', 'is_active')
        }),
        ('Quota Configuration', {
            'fields': ('quota_type', 'limit', 'period')
        }),
        ('Current Period', {
            'fields': ('current_usage', 'percentage_used', 'period_start', 'period_end')
        }),
        ('Overage', {
            'fields': ('allow_overage', 'overage_rate'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def usage_display(self, obj):
        percentage = obj.percentage_used()
        color = 'green' if percentage < 80 else ('orange' if percentage < 100 else 'red')
        return format_html(
            '<span style="color: {};">{} / {} ({:.1f}%)</span>',
            color, obj.current_usage, obj.limit, percentage
        )
    usage_display.short_description = 'Usage'

    def is_exceeded_display(self, obj):
        if obj.is_exceeded():
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_exceeded_display.short_description = 'Exceeded'


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = [
        'organization', 'url', 'is_active', 'last_success_at',
        'consecutive_failures'
    ]
    list_filter = ['is_active']
    search_fields = ['organization__name', 'url']
    readonly_fields = [
        'last_success_at', 'last_failure_at', 'consecutive_failures',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Endpoint Configuration', {
            'fields': ('organization', 'url', 'description', 'is_active')
        }),
        ('Authentication', {
            'fields': ('secret',)
        }),
        ('Event Filtering', {
            'fields': ('enabled_events',)
        }),
        ('Statistics', {
            'fields': ('last_success_at', 'last_failure_at', 'consecutive_failures'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'endpoint', 'event_type', 'status', 'attempt_count',
        'response_status_code', 'created_at'
    ]
    list_filter = ['status', 'event_type']
    search_fields = ['endpoint__url', 'event_type']
    readonly_fields = [
        'created_at', 'sent_at', 'succeeded_at', 'failed_at'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Delivery Details', {
            'fields': ('endpoint', 'event_type', 'status', 'payload')
        }),
        ('Attempts', {
            'fields': ('attempt_count', 'next_retry_at')
        }),
        ('Response', {
            'fields': (
                'response_status_code', 'response_time_ms', 'response_body',
                'response_headers'
            ),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'succeeded_at', 'failed_at'),
            'classes': ('collapse',)
        }),
    )
