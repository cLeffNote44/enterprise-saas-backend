from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.billing'
    verbose_name = 'Billing & Subscriptions'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import foundation.apps.billing.signals  # noqa: F401
        except ImportError:
            pass
