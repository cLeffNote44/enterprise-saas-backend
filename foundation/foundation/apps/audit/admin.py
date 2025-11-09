"""Admin for audit app."""
from django.contrib import admin
from .models import StructuredLog, ChangeHistory, AdminAction, ImpersonationLog, GeoLocation, LogRetentionPolicy

@admin.register(StructuredLog)
class StructuredLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'logger_name', 'user', 'organization', 'message_preview']
    list_filter = ['level', 'logger_name', 'timestamp']
    search_fields = ['message', 'user__username', 'organization__name']
    readonly_fields = ['timestamp', 'delete_after']
    date_hierarchy = 'timestamp'

    def message_preview(self, obj):
        return obj.message[:100]

@admin.register(ChangeHistory)
class ChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'content_type', 'field_name', 'change_type']
    list_filter = ['change_type', 'content_type', 'timestamp']
    date_hierarchy = 'timestamp'

@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'admin_user', 'action', 'model_name', 'object_repr']
    list_filter = ['action', 'timestamp']
    date_hierarchy = 'timestamp'

@admin.register(ImpersonationLog)
class ImpersonationLogAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'target_user', 'started_at', 'ended_at', 'is_active', 'reason']
    list_filter = ['is_active', 'started_at']
    readonly_fields = ['started_at', 'ended_at']

@admin.register(GeoLocation)
class GeoLocationAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'country_name', 'city', 'isp']
    search_fields = ['ip_address', 'city', 'country_name']

@admin.register(LogRetentionPolicy)
class LogRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'log_type', 'retention_days', 'archive_before_delete', 'is_active']
    list_filter = ['log_type', 'is_active']
