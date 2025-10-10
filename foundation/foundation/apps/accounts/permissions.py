"""
Custom permissions for the accounts app and enterprise features.
"""
from rest_framework import permissions
from django.contrib.auth import get_user_model

from .models import APIKey
from .enterprise import Organization, OrganizationMembership

User = get_user_model()


class HasValidAPIKey(permissions.BasePermission):
    """Permission to check for valid API key."""
    
    def has_permission(self, request, view):
        # Allow if user is authenticated
        if request.user.is_authenticated:
            return True
        
        # Check for API key in headers
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return False
        
        try:
            api_key_obj = APIKey.objects.get(
                key=api_key,
                is_active=True
            )
            # Check if API key is expired
            if api_key_obj.is_expired():
                return False
            
            # Record API key usage
            api_key_obj.record_usage(request)
            
            # Attach user to request for downstream processing
            request.user = api_key_obj.user
            return True
        except APIKey.DoesNotExist:
            return False


class IsDataManager(permissions.BasePermission):
    """Permission for data managers only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check through organization memberships
        for membership in request.user.organization_memberships.filter(status='active'):
            if membership.roles.filter(name='Data Manager', is_active=True).exists():
                return True
        return False


class IsAnalyst(permissions.BasePermission):
    """Permission for analysts only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check through organization memberships
        for membership in request.user.organization_memberships.filter(status='active'):
            if membership.roles.filter(name='Analyst', is_active=True).exists():
                return True
        return False


class IsComplianceOfficer(permissions.BasePermission):
    """Permission for compliance officers only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check through organization memberships
        for membership in request.user.organization_memberships.filter(status='active'):
            if membership.roles.filter(name='Compliance Officer', is_active=True).exists():
                return True
        return False


class IsOrganizationMember(permissions.BasePermission):
    """Permission for organization members."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get organization from URL parameters
        organization_slug = view.kwargs.get('organization_slug') or view.kwargs.get('slug')
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            return organization.memberships.filter(
                user=request.user,
                status='active'
            ).exists()
        except Organization.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        if not request.user.is_authenticated:
            return False
        
        # For organization objects
        if isinstance(obj, Organization):
            return obj.memberships.filter(
                user=request.user,
                status='active'
            ).exists()
        
        # For objects that belong to an organization
        if hasattr(obj, 'organization'):
            return obj.organization.memberships.filter(
                user=request.user,
                status='active'
            ).exists()
        
        return False


class IsOrganizationAdmin(permissions.BasePermission):
    """Permission for organization administrators."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get organization from URL parameters
        organization_slug = view.kwargs.get('organization_slug') or view.kwargs.get('slug')
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            membership = organization.memberships.get(
                user=request.user,
                status='active'
            )
            return membership.is_admin
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        if not request.user.is_authenticated:
            return False
        
        # For organization objects
        if isinstance(obj, Organization):
            try:
                membership = obj.memberships.get(
                    user=request.user,
                    status='active'
                )
                return membership.is_admin
            except OrganizationMembership.DoesNotExist:
                return False
        
        # For objects that belong to an organization
        if hasattr(obj, 'organization'):
            try:
                membership = obj.organization.memberships.get(
                    user=request.user,
                    status='active'
                )
                return membership.is_admin
            except OrganizationMembership.DoesNotExist:
                return False
        
        return False


class HasOrganizationPermission(permissions.BasePermission):
    """Permission that checks specific organization-level permissions."""
    
    def __init__(self, permission_name):
        self.permission_name = permission_name
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get organization from URL parameters
        organization_slug = view.kwargs.get('organization_slug') or view.kwargs.get('slug')
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            membership = organization.memberships.get(
                user=request.user,
                status='active'
            )
            return membership.has_permission(self.permission_name)
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False


class CanInviteUsers(HasOrganizationPermission):
    """Permission for users who can invite others to organization."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        organization_slug = view.kwargs.get('organization_slug') or view.kwargs.get('slug')
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            membership = organization.memberships.get(
                user=request.user,
                status='active'
            )
            return membership.is_admin or membership.can_invite_users
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False


class CanManageRoles(HasOrganizationPermission):
    """Permission for users who can manage roles in organization."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        organization_slug = view.kwargs.get('organization_slug') or view.kwargs.get('slug')
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            membership = organization.memberships.get(
                user=request.user,
                status='active'
            )
            return membership.is_admin or membership.can_manage_roles
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False


class CanAccessBilling(HasOrganizationPermission):
    """Permission for users who can access billing information."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        organization_slug = view.kwargs.get('organization_slug') or view.kwargs.get('slug')
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            membership = organization.memberships.get(
                user=request.user,
                status='active'
            )
            return membership.is_admin or membership.can_access_billing
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return False


class IsDataOwner(permissions.BasePermission):
    """Permission for data owners - users who can manage data sources."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has data ownership role
        return (
            request.user.is_superuser or
            any(
                membership.roles.filter(
                    name__in=['Admin', 'Data Manager', 'Data Owner'],
                    is_active=True
                ).exists()
                for membership in request.user.organization_memberships.filter(status='active')
            )
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user owns or can manage the data object."""
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if object has an owner field
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        # Check role-based permissions
        return self.has_permission(request, view)


class IsReadOnlyOrOwner(permissions.BasePermission):
    """
    Permission that allows read access to anyone but write access only to owners.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require special access
        return self.has_write_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the owner or admins
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        
        return request.user.is_superuser
    
    def has_write_permission(self, request, view):
        """Override this method to customize write permissions."""
        return True


class RequiresSubscription(permissions.BasePermission):
    """Permission that requires an active subscription."""
    
    def __init__(self, required_tier=None):
        self.required_tier = required_tier
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get current organization context
        organization_slug = (
            view.kwargs.get('organization_slug') or 
            view.kwargs.get('slug') or
            request.session.get('current_organization_slug')
        )
        
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            
            # Check if subscription is active
            if not organization.is_subscription_active():
                return False
            
            # Check subscription tier if required
            if self.required_tier:
                tier_order = {
                    'starter': 1,
                    'professional': 2,
                    'enterprise': 3,
                    'enterprise_plus': 4
                }
                
                current_tier_level = tier_order.get(organization.subscription_tier, 0)
                required_tier_level = tier_order.get(self.required_tier, 999)
                
                return current_tier_level >= required_tier_level
            
            return True
        except Organization.DoesNotExist:
            return False


class HasFeatureEnabled(permissions.BasePermission):
    """Permission that checks if a feature is enabled for the organization."""
    
    def __init__(self, feature_name):
        self.feature_name = feature_name
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get current organization context
        organization_slug = (
            view.kwargs.get('organization_slug') or 
            view.kwargs.get('slug') or
            request.session.get('current_organization_slug')
        )
        
        if not organization_slug:
            return False
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            return organization.is_feature_enabled(self.feature_name)
        except Organization.DoesNotExist:
            return False
