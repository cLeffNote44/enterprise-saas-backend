"""
API views for rate limiting app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import (
    RateLimit, APIUsage, APIQuota, WebhookEndpoint, WebhookDelivery
)
from .serializers import (
    RateLimitSerializer, APIUsageSerializer, APIQuotaSerializer,
    WebhookEndpointSerializer, WebhookDeliverySerializer
)


class RateLimitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for rate limits (read-only for users).
    """
    queryset = RateLimit.objects.filter(is_active=True)
    serializer_class = RateLimitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['limit_type', 'tier']

    @action(detail=False, methods=['get'])
    def my_limits(self, request):
        """Get rate limits applicable to the current user's organization."""
        org_membership = request.user.organization_memberships.first()
        if not org_membership:
            return Response({'limits': []})

        org = org_membership.organization
        tier = org.subscription_tier

        limits = RateLimit.objects.filter(
            is_active=True
        ).filter(
            models.Q(tier='') | models.Q(tier=tier)
        )

        serializer = self.get_serializer(limits, many=True)
        return Response(serializer.data)


class APIUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for API usage analytics.
    """
    serializer_class = APIUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['endpoint', 'method', 'status_code', 'is_error']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter usage by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        return APIUsage.objects.filter(
            models.Q(user=user) | models.Q(organization_id__in=org_ids)
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary for current period."""
        user = request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        # Last 24 hours
        since = timezone.now() - timedelta(hours=24)

        usage = APIUsage.objects.filter(
            organization_id__in=org_ids,
            timestamp__gte=since
        )

        summary = {
            'total_requests': usage.count(),
            'error_count': usage.filter(is_error=True).count(),
            'avg_response_time': usage.aggregate(
                avg=models.Avg('response_time_ms')
            )['avg'] or 0,
            'by_endpoint': {},
        }

        # Group by endpoint
        endpoints = usage.values('endpoint').annotate(
            count=models.Count('id'),
            avg_time=models.Avg('response_time_ms')
        )

        for endpoint in endpoints:
            summary['by_endpoint'][endpoint['endpoint']] = {
                'count': endpoint['count'],
                'avg_response_time': endpoint['avg_time']
            }

        return Response(summary)


class APIQuotaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for API quotas.
    """
    serializer_class = APIQuotaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quota_type', 'period']

    def get_queryset(self):
        """Filter quotas by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        return APIQuota.objects.filter(
            organization_id__in=org_ids,
            is_active=True
        )

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current period quotas."""
        user = request.user
        org_membership = user.organization_memberships.first()

        if not org_membership:
            return Response({'quotas': []})

        current_quotas = APIQuota.objects.filter(
            organization=org_membership.organization,
            is_active=True,
            period_end__gte=timezone.now()
        )

        serializer = self.get_serializer(current_quotas, many=True)
        return Response(serializer.data)


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """
    ViewSet for webhook endpoints.
    """
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

    def get_queryset(self):
        """Filter webhooks by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        return WebhookEndpoint.objects.filter(organization_id__in=org_ids)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send a test webhook."""
        endpoint = self.get_object()

        # Create a test delivery
        delivery = WebhookDelivery.objects.create(
            endpoint=endpoint,
            event_type='test.webhook',
            payload={'message': 'This is a test webhook'},
            status='pending'
        )

        # TODO: Implement actual webhook sending logic

        return Response({
            'message': 'Test webhook queued',
            'delivery_id': delivery.id
        })


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for webhook deliveries.
    """
    serializer_class = WebhookDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'event_type']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter deliveries by user's webhook endpoints."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        return WebhookDelivery.objects.filter(
            endpoint__organization_id__in=org_ids
        )

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Manually retry a failed webhook delivery."""
        delivery = self.get_object()

        if delivery.status != 'failed':
            return Response(
                {'error': 'Can only retry failed deliveries'},
                status=status.HTTP_400_BAD_REQUEST
            )

        delivery.status = 'pending'
        delivery.next_retry_at = timezone.now()
        delivery.save()

        return Response({
            'message': 'Delivery queued for retry',
            'delivery': WebhookDeliverySerializer(delivery).data
        })
