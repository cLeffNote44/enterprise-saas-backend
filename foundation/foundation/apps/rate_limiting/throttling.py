"""
Custom throttling classes for rate limiting.
"""

from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache
from .models import RateLimit, CustomRateLimit, APIQuota


class TieredRateThrottle(SimpleRateThrottle):
    """
    Rate throttle based on organization subscription tier.
    """
    scope = 'tier'

    def get_cache_key(self, request, view):
        """Generate cache key based on organization and endpoint."""
        if not request.user or not request.user.is_authenticated:
            return self.get_ident(request)

        # Get user's organization
        org_membership = request.user.organization_memberships.first()
        if not org_membership:
            return self.get_ident(request)

        org = org_membership.organization
        endpoint = request.path

        return f'throttle_tier_{org.id}_{endpoint}'

    def get_rate(self):
        """Get rate limit based on organization tier."""
        if not hasattr(self, 'request') or not self.request.user.is_authenticated:
            return '100/hour'  # Default for unauthenticated

        org_membership = self.request.user.organization_memberships.first()
        if not org_membership:
            return '100/hour'

        org = org_membership.organization
        tier = org.subscription_tier

        # Tier-based limits
        tier_limits = {
            'starter': '1000/hour',
            'professional': '10000/hour',
            'enterprise': '100000/hour',
            'enterprise_plus': '1000000/hour',
        }

        return tier_limits.get(tier, '100/hour')


class OrganizationRateThrottle(SimpleRateThrottle):
    """
    Rate throttle per organization.
    """
    scope = 'organization'

    def get_cache_key(self, request, view):
        """Generate cache key based on organization."""
        if not request.user or not request.user.is_authenticated:
            return None

        org_membership = request.user.organization_memberships.first()
        if not org_membership:
            return None

        return f'throttle_org_{org_membership.organization_id}'


class APIKeyRateThrottle(SimpleRateThrottle):
    """
    Rate throttle for API key authentication.
    """
    scope = 'api_key'

    def get_cache_key(self, request, view):
        """Generate cache key based on API key."""
        # Check if request has API key
        if hasattr(request, 'auth') and hasattr(request.auth, 'id'):
            return f'throttle_apikey_{request.auth.id}'

        return None

    def get_rate(self):
        """Get rate limit for API key."""
        if not hasattr(self, 'request') or not hasattr(self.request, 'auth'):
            return '1000/hour'

        # Could customize based on API key type/tier
        return '10000/hour'


class QuotaThrottle:
    """
    Check API quota limits (monthly/daily caps).
    """

    def allow_request(self, request, view):
        """Check if request is within quota limits."""
        if not request.user or not request.user.is_authenticated:
            return True

        org_membership = request.user.organization_memberships.first()
        if not org_membership:
            return True

        org = org_membership.organization

        # Check active quotas
        active_quotas = APIQuota.objects.filter(
            organization=org,
            is_active=True,
            quota_type='requests'
        )

        for quota in active_quotas:
            if quota.is_exceeded() and not quota.allow_overage:
                return False

            # Increment usage
            quota.current_usage += 1
            quota.save(update_fields=['current_usage'])

        return True

    def wait(self):
        """Return wait time until quota resets."""
        return None
