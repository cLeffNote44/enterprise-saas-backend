from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.feature_flags'
    verbose_name = 'Feature Flags & Experimentation'
