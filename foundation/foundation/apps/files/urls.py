"""URLs for files."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, FileShareViewSet

app_name = 'files'
router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')
router.register(r'shares', FileShareViewSet, basename='share')

urlpatterns = [path('', include(router.urls))]
