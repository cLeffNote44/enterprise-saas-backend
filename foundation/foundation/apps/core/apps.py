"""App configuration for foundation core utilities."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core utilities app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.core'
    verbose_name = 'Foundation: Core Utilities'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        # Import signals if needed
        pass
