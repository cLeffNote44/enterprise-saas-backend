"""App configuration for foundation accounts."""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.accounts'
    verbose_name = 'Foundation: Accounts & Authentication'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        # Import signals if needed
        pass
