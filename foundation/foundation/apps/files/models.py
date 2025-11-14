"""File management models."""
import uuid
from django.db import models
from django.conf import settings


class File(models.Model):
    """Uploaded files with metadata and versioning."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')

    # File details
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    size_bytes = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)

    # Security
    virus_scanned = models.BooleanField(default=False)
    virus_scan_result = models.CharField(max_length=50, blank=True)
    is_safe = models.BooleanField(default=False)

    # Processing
    is_processed = models.BooleanField(default=False)
    thumbnail = models.FileField(upload_to='thumbnails/%Y/%m/%d/', null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_file'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return self.name


class FileVersion(models.Model):
    """File version history."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    file_path = models.FileField(upload_to='versions/%Y/%m/%d/')
    size_bytes = models.BigIntegerField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_file_version'
        ordering = ['-version_number']
        unique_together = [['file', 'version_number']]


class FileShare(models.Model):
    """File sharing permissions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shares')
    shared_with_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    permission = models.CharField(max_length=20, choices=[('view', 'View'), ('edit', 'Edit')], default='view')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_file_share'
