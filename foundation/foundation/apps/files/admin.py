"""Admin for files."""
from django.contrib import admin
from .models import File, FileVersion, FileShare

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'uploaded_by', 'size_bytes', 'is_safe', 'created_at']
    list_filter = ['virus_scanned', 'is_safe', 'mime_type']
    search_fields = ['name', 'organization__name']

@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    list_display = ['file', 'version_number', 'uploaded_by', 'created_at']

@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    list_display = ['file', 'shared_with_user', 'permission', 'expires_at']
