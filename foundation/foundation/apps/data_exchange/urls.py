"""URLs for data exchange."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportJobViewSet, ExportJobViewSet

app_name = 'data_exchange'
router = DefaultRouter()
router.register(r'imports', ImportJobViewSet, basename='import')
router.register(r'exports', ExportJobViewSet, basename='export')

urlpatterns = [path('', include(router.urls))]
