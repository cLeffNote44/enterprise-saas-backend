"""
Admin interface for notifications app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    NotificationDelivery, DigestSchedule, NotificationChannel
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'version', 'is_active', 'organization', 'created_at']
    list_filter = ['channel', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'channel', 'organization', 'version', 'is_active', 'description')
        }),
        ('Content', {
            'fields': ('subject', 'body_text', 'body_html')
        }),
        ('Variables', {
            'fields': ('available_variables',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'priority', 'status', 'category', 'created_at', 'read_at']
    list_filter = ['priority', 'status', 'category']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['created_at', 'read_at', 'sent_at', 'delivered_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'title', 'message', 'priority', 'category', 'action_url')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'delivered_at', 'read_at')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Template', {
            'fields': ('template',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_sent']

    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f"{queryset.count()} notifications marked as read.")
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_sent(self, request, queryset):
        queryset.update(status='sent')
        self.message_user(request, f"{queryset.count()} notifications marked as sent.")
    mark_as_sent.short_description = "Mark selected as sent"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'email_enabled', 'sms_enabled', 'push_enabled',
        'in_app_enabled', 'digest_enabled'
    ]
    list_filter = ['email_enabled', 'sms_enabled', 'push_enabled', 'digest_enabled']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channel Preferences', {
            'fields': ('email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled')
        }),
        ('Category Preferences', {
            'fields': ('category_preferences',),
            'classes': ('collapse',)
        }),
        ('Digest Settings', {
            'fields': ('digest_enabled', 'digest_frequency', 'digest_time')
        }),
        ('Do Not Disturb', {
            'fields': ('dnd_enabled', 'dnd_start', 'dnd_end'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('sms_phone', 'push_device_tokens'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class NotificationDeliveryInline(admin.TabularInline):
    model = NotificationDelivery
    extra = 0
    readonly_fields = ['channel', 'status', 'sent_at', 'delivered_at', 'error_message']
    fields = ['channel', 'recipient_address', 'status', 'sent_at', 'delivered_at', 'error_message']
    can_delete = False


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'notification', 'channel', 'recipient_address', 'status',
        'sent_at', 'delivered_at', 'retry_count'
    ]
    list_filter = ['channel', 'status']
    search_fields = ['notification__title', 'recipient_address', 'external_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Delivery Details', {
            'fields': ('notification', 'channel', 'recipient_address', 'status')
        }),
        ('Timing', {
            'fields': ('sent_at', 'delivered_at', 'failed_at', 'clicked_at')
        }),
        ('Error Information', {
            'fields': ('error_code', 'error_message', 'retry_count', 'last_retry_at'),
            'classes': ('collapse',)
        }),
        ('External Tracking', {
            'fields': ('external_id', 'external_data'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DigestSchedule)
class DigestScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'frequency', 'send_time', 'is_active', 'last_sent_at', 'next_send_at']
    list_filter = ['frequency', 'is_active']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_sent_at', 'created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user', 'is_active')
        }),
        ('Schedule', {
            'fields': ('frequency', 'send_time', 'send_day')
        }),
        ('Content Filters', {
            'fields': ('categories', 'min_priority')
        }),
        ('Status', {
            'fields': ('last_sent_at', 'next_send_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'channel_type', 'is_active', 'last_used_at']
    list_filter = ['channel_type', 'is_active']
    search_fields = ['name', 'organization__name']
    readonly_fields = ['last_used_at', 'created_at', 'updated_at']

    fieldsets = (
        ('Channel Information', {
            'fields': ('organization', 'name', 'channel_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('webhook_url', 'api_token', 'configuration')
        }),
        ('Filtering', {
            'fields': ('categories', 'min_priority'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('last_used_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
