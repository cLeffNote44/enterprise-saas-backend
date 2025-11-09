from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foundation.apps.notifications'
    verbose_name = 'Notifications'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import foundation.apps.notifications.signals  # noqa: F401
        except ImportError:
            pass
