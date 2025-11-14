"""
URL configuration for rate limiting app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RateLimitViewSet, APIUsageViewSet, APIQuotaViewSet,
    WebhookEndpointViewSet, WebhookDeliveryViewSet
)

app_name = 'rate_limiting'

router = DefaultRouter()
router.register(r'limits', RateLimitViewSet, basename='rate-limit')
router.register(r'usage', APIUsageViewSet, basename='api-usage')
router.register(r'quotas', APIQuotaViewSet, basename='api-quota')
router.register(r'webhooks', WebhookEndpointViewSet, basename='webhook')
router.register(r'webhook-deliveries', WebhookDeliveryViewSet, basename='webhook-delivery')

urlpatterns = [
    path('', include(router.urls)),
]
