"""Main URL configuration for the Enterprise SaaS Foundation."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView, 
    SpectacularSwaggerView,
)
from foundation.health import HealthLiveView, HealthReadyView

# Base URL patterns that all projects get
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health checks
    path('health/live/', HealthLiveView.as_view(), name='health-live'),
    path('health/ready/', HealthReadyView.as_view(), name='health-ready'),
    path('health/', HealthReadyView.as_view(), name='health'),
    
    # Django health check app
    path('health/checks/', include('health_check.urls')),
    
    # Prometheus metrics
    path('metrics/', include('django_prometheus.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Foundation Apps APIs
    path('api/accounts/', include('foundation.apps.accounts.urls')),
    path('api/compliance/', include('foundation.apps.compliance.urls')),
    path('api/analytics/', include('foundation.apps.analytics.urls')),
    path('api/messaging/', include('foundation.apps.messaging.urls')),
    path('api/moderation/', include('foundation.apps.moderation.urls')),
    
    # Authentication URLs (django-allauth)
    path('auth/', include('allauth.urls')),
]

# Add static/media URLs in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Extension URL patterns (to be added by projects)
# Projects can extend this by importing and adding to urlpatterns
