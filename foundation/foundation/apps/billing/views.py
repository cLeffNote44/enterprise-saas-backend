"""
API views for billing app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    SubscriptionPlan, Subscription, PaymentMethod, Invoice,
    Payment, UsageRecord, Coupon, DunningAttempt
)
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer, PaymentMethodSerializer,
    InvoiceSerializer, PaymentSerializer, UsageRecordSerializer,
    CouponSerializer, DunningAttemptSerializer
)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for subscription plans.
    Read-only for customers (plans are managed in admin).
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True, is_public=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tier', 'billing_interval']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['price']


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for subscriptions.
    Users can view and manage their organization's subscriptions.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'plan__tier']
    ordering_fields = ['created_at', 'current_period_end']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter subscriptions by user's organizations."""
        user = self.request.user
        # Get all organizations where user is a member
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return Subscription.objects.filter(organization_id__in=org_ids)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a subscription at period end."""
        subscription = self.get_object()
        subscription.cancel_at_period_end = True
        subscription.canceled_at = timezone.now()
        subscription.save()

        return Response({
            'message': 'Subscription will be canceled at the end of the current period',
            'subscription': SubscriptionSerializer(subscription).data
        })

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reactivate a canceled subscription."""
        subscription = self.get_object()

        if subscription.cancel_at_period_end:
            subscription.cancel_at_period_end = False
            subscription.canceled_at = None
            subscription.save()

            return Response({
                'message': 'Subscription reactivated successfully',
                'subscription': SubscriptionSerializer(subscription).data
            })

        return Response(
            {'error': 'Subscription is not marked for cancellation'},
            status=status.HTTP_400_BAD_REQUEST
        )


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for payment methods.
    Users can manage their organization's payment methods.
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['type', 'is_default']
    ordering = ['-is_default', '-created_at']

    def get_queryset(self):
        """Filter payment methods by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return PaymentMethod.objects.filter(organization_id__in=org_ids)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set a payment method as default."""
        payment_method = self.get_object()
        payment_method.is_default = True
        payment_method.save()  # save() method handles unsetting other defaults

        return Response({
            'message': 'Payment method set as default',
            'payment_method': PaymentMethodSerializer(payment_method).data
        })


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for invoices.
    Read-only - invoices are generated automatically.
    """
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['invoice_number']
    ordering_fields = ['invoice_date', 'due_date', 'total']
    ordering = ['-invoice_date']

    def get_queryset(self):
        """Filter invoices by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return Invoice.objects.filter(organization_id__in=org_ids)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download invoice PDF."""
        invoice = self.get_object()

        if invoice.pdf_url:
            return Response({
                'pdf_url': invoice.pdf_url
            })

        return Response(
            {'error': 'PDF not yet generated'},
            status=status.HTTP_404_NOT_FOUND
        )


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for payments.
    Read-only - payments are processed automatically or via Stripe.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter payments by user's organizations through invoices."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return Payment.objects.filter(invoice__organization_id__in=org_ids)


class UsageRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for usage records.
    """
    serializer_class = UsageRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['metric', 'is_billed']
    ordering = ['-period_start']

    def get_queryset(self):
        """Filter usage records by user's organizations."""
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return UsageRecord.objects.filter(organization_id__in=org_ids)

    @action(detail=False, methods=['get'])
    def current_period(self, request):
        """Get usage for the current billing period."""
        user = request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        # Get active subscriptions
        active_subs = Subscription.objects.filter(
            organization_id__in=org_ids,
            status__in=['trialing', 'active']
        )

        usage_data = []
        for sub in active_subs:
            usage = UsageRecord.objects.filter(
                subscription=sub,
                period_start__gte=sub.current_period_start,
                period_end__lte=sub.current_period_end
            )
            usage_data.extend(UsageRecordSerializer(usage, many=True).data)

        return Response(usage_data)


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for coupons.
    Read-only - users can validate coupons but not create them.
    """
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'code'

    @action(detail=True, methods=['post'])
    def validate(self, request, code=None):
        """Validate a coupon code."""
        try:
            coupon = self.get_object()

            if coupon.is_valid():
                return Response({
                    'valid': True,
                    'coupon': CouponSerializer(coupon).data
                })
            else:
                return Response({
                    'valid': False,
                    'reason': 'Coupon is no longer valid'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'reason': 'Coupon not found'
            }, status=status.HTTP_404_NOT_FOUND)
