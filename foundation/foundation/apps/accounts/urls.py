"""URLs for foundation accounts app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views, enterprise_views

app_name = 'accounts'

# Main router for viewsets
router = DefaultRouter()
router.register(r'organizations', enterprise_views.OrganizationViewSet)
router.register(r'permissions', enterprise_views.PermissionListView, basename='permission')

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    
    # MFA endpoints
    path('auth/mfa/setup/', api_views.SetupMFAView.as_view(), name='mfa_setup'),
    path('auth/mfa/confirm/', api_views.ConfirmMFAView.as_view(), name='mfa_confirm'),
    path('auth/mfa/disable/', api_views.DisableMFAView.as_view(), name='mfa_disable'),
    path('auth/mfa/status/', api_views.MFAStatusView.as_view(), name='mfa_status'),
    
    # API Key management endpoints
    path('auth/api-keys/', api_views.ListAPIKeysView.as_view(), name='api_keys_list'),
    path('auth/api-keys/generate/', api_views.GenerateAPIKeyView.as_view(), name='api_keys_generate'),
    path('auth/api-keys/<int:key_id>/revoke/', api_views.RevokeAPIKeyView.as_view(), name='api_keys_revoke'),
    path('auth/api-keys/<int:key_id>/rotate/', api_views.RotateAPIKeyView.as_view(), name='api_keys_rotate'),
    
    # Webhook signature validation
    path('webhooks/validate-signature/', api_views.validate_webhook_signature, name='webhook_validate'),
    
    # Enterprise endpoints
    path('enterprise/my-organizations/', enterprise_views.UserOrganizationsView.as_view(), name='user-organizations'),
    path('enterprise/switch-organization/', enterprise_views.OrganizationSwitchView.as_view(), name='organization-switch'),
]
