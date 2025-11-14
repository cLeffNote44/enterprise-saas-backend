"""URLs for search."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SearchViewSet, SavedSearchViewSet

app_name = 'search'
router = DefaultRouter()
router.register(r'search', SearchViewSet, basename='search')
router.register(r'saved', SavedSearchViewSet, basename='saved-search')

urlpatterns = [path('', include(router.urls))]
