"""Data import/export models."""
import uuid
from django.db import models
from django.conf import settings


class ImportJob(models.Model):
    """Bulk data import jobs."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='import_jobs')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Job details
    source_file = models.FileField(upload_to='imports/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=[('csv', 'CSV'), ('xlsx', 'Excel'), ('json', 'JSON')])
    target_model = models.CharField(max_length=100, help_text="Model to import data into")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)

    # Results
    errors = models.JSONField(default=list, blank=True)
    result_file = models.FileField(upload_to='import_results/%Y/%m/%d/', null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'foundation_import_job'
        ordering = ['-created_at']

    def __str__(self):
        return f"Import {self.id} - {self.status}"


class ExportJob(models.Model):
    """Data export jobs."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, related_name='export_jobs')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Export configuration
    source_model = models.CharField(max_length=100)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    filters = models.JSONField(default=dict, blank=True, help_text="Export filters")
    fields = models.JSONField(default=list, blank=True, help_text="Fields to export")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)

    # Result
    result_file = models.FileField(upload_to='exports/%Y/%m/%d/', null=True, blank=True)
    download_url = models.URLField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'foundation_export_job'
        ordering = ['-created_at']

    def __str__(self):
        return f"Export {self.id} - {self.format}"
