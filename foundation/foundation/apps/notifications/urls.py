"""
URL configuration for notifications app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, NotificationPreferenceViewSet,
    NotificationTemplateViewSet, NotificationDeliveryViewSet,
    DigestScheduleViewSet, NotificationChannelViewSet
)

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='preference')
router.register(r'templates', NotificationTemplateViewSet, basename='template')
router.register(r'deliveries', NotificationDeliveryViewSet, basename='delivery')
router.register(r'digests', DigestScheduleViewSet, basename='digest')
router.register(r'channels', NotificationChannelViewSet, basename='channel')

urlpatterns = [
    path('', include(router.urls)),
]
