"""URLs for foundation compliance app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'compliance'

router = DefaultRouter()
# Add compliance viewsets here when ready

urlpatterns = [
    path('api/', include(router.urls)),
    # Additional compliance URLs will be added here
]
