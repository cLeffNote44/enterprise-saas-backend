"""
Signals for notifications app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Notification, NotificationPreference


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create default notification preferences for new users."""
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


@receiver(post_save, sender=Notification)
def handle_new_notification(sender, instance, created, **kwargs):
    """Handle newly created notifications."""
    if created:
        # TODO: Implement actual notification sending logic
        # This would trigger email, SMS, push notifications based on user preferences
        pass
