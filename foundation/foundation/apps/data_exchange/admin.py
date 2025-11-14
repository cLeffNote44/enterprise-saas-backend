"""Admin for data exchange."""
from django.contrib import admin
from .models import ImportJob, ExportJob

@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'organization', 'file_type', 'status', 'success_count', 'error_count', 'created_at']
    list_filter = ['status', 'file_type']
    readonly_fields = ['created_at', 'started_at', 'completed_at']

@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'organization', 'format', 'status', 'total_records', 'created_at']
    list_filter = ['status', 'format']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
