"""URLs for feature flags."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeatureFlagViewSet, ExperimentViewSet

app_name = 'feature_flags'

router = DefaultRouter()
router.register(r'flags', FeatureFlagViewSet, basename='flag')
router.register(r'experiments', ExperimentViewSet, basename='experiment')

urlpatterns = [
    path('', include(router.urls)),
]
