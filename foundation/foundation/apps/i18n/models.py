"""Internationalization models."""
import uuid
from django.db import models
from django.conf import settings


class Language(models.Model):
    """Supported languages."""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_rtl = models.BooleanField(default=False)

    class Meta:
        db_table = 'foundation_language'


class Translation(models.Model):
    """Dynamic content translations."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, db_index=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    value = models.TextField()
    context = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'foundation_translation'
        unique_together = [['key', 'language', 'context']]


class UserLanguagePreference(models.Model):
    """User language preferences."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=100, default='UTC')

    class Meta:
        db_table = 'foundation_user_language_preference'
