"""Search models."""
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class SearchIndex(models.Model):
    """Generic search index for any model."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Indexed object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Search fields
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    keywords = models.JSONField(default=list, help_text="Extracted keywords")

    # Metadata
    organization = models.ForeignKey('accounts.Organization', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_search_index'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['organization']),
        ]

    def __str__(self):
        return self.title


class SearchQuery(models.Model):
    """Track search queries for analytics."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    query = models.CharField(max_length=255, db_index=True)
    results_count = models.IntegerField(default=0)
    clicked_result = models.UUIDField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_search_query'
        ordering = ['-timestamp']

    def __str__(self):
        return self.query


class SavedSearch(models.Model):
    """User-saved searches."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100)
    query = models.JSONField(help_text="Search query parameters")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_saved_search'

    def __str__(self):
        return f"{self.user.username} - {self.name}"
