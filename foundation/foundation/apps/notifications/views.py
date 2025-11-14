"""
API views for notifications app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    NotificationTemplate, Notification, NotificationPreference,
    NotificationDelivery, DigestSchedule, NotificationChannel
)
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer,
    NotificationPreferenceSerializer, NotificationDeliverySerializer,
    DigestScheduleSerializer, NotificationChannelSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Only show notifications for current user."""
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()

        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        unread = self.get_queryset().filter(read_at__isnull=True)
        count = unread.count()

        for notification in unread:
            notification.mark_as_read()

        return Response({
            'message': f'{count} notifications marked as read',
            'count': count
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(read_at__isnull=True).count()

        return Response({
            'unread_count': count
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 24 hours)."""
        recent_time = timezone.now() - timezone.timedelta(hours=24)
        recent_notifications = self.get_queryset().filter(
            created_at__gte=recent_time
        )

        serializer = self.get_serializer(recent_notifications, many=True)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notification preferences.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only show preferences for current user."""
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create preference for current user."""
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user's preferences."""
        preference = self.get_object()

        if request.method == 'GET':
            serializer = self.get_serializer(preference)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(preference, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class NotificationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notification templates (read-only for users).
    """
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['channel', 'organization']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Filter templates by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        # Get global templates and organization-specific templates
        return NotificationTemplate.objects.filter(
            is_active=True
        ).filter(
            models.Q(organization__isnull=True) |
            models.Q(organization_id__in=org_ids)
        )


class NotificationDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notification deliveries (read-only).
    """
    serializer_class = NotificationDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['channel', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Only show deliveries for current user's notifications."""
        return NotificationDelivery.objects.filter(
            notification__recipient=self.request.user
        )


class DigestScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for digest schedules.
    """
    serializer_class = DigestScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only show schedules for current user."""
        return DigestSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set user to current user."""
        serializer.save(user=self.request.user)


class NotificationChannelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notification channels.
    """
    serializer_class = NotificationChannelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel_type', 'is_active']

    def get_queryset(self):
        """Filter channels by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return NotificationChannel.objects.filter(organization_id__in=org_ids)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a notification channel."""
        channel = self.get_object()

        # TODO: Implement actual channel testing logic
        return Response({
            'message': f'Test notification sent to {channel.name}',
            'success': True
        })
