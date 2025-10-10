"""App configuration for foundation compliance."""
from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    """Configuration for the compliance app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.compliance'
    verbose_name = 'Foundation: Compliance & Governance'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        # Import signals if needed
        pass
