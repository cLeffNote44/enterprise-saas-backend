"""
URL configuration for billing app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanViewSet, SubscriptionViewSet, PaymentMethodViewSet,
    InvoiceViewSet, PaymentViewSet, UsageRecordViewSet, CouponViewSet
)

app_name = 'billing'

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='plan')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'usage', UsageRecordViewSet, basename='usage')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
]
