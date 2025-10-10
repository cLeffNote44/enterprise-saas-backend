"""URLs for foundation messaging app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'messaging'

router = DefaultRouter()
# Add messaging viewsets here when ready

urlpatterns = [
    path('api/', include(router.urls)),
    # Additional messaging URLs will be added here
]
