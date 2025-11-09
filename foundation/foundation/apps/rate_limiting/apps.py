from django.apps import AppConfig


class RateLimitingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.rate_limiting'
    verbose_name = 'Rate Limiting & API Management'
