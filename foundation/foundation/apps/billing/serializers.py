"""
Serializers for billing app.
"""

from rest_framework import serializers
from .models import (
    SubscriptionPlan, Subscription, PaymentMethod, Invoice,
    InvoiceLineItem, Payment, UsageRecord, Coupon, DunningAttempt
)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans."""

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'tier', 'billing_interval', 'price', 'currency',
            'features', 'limits', 'is_active', 'trial_days', 'is_public',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_active = serializers.SerializerMethodField()
    days_until_renewal = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'organization', 'plan', 'plan_details', 'status',
            'current_period_start', 'current_period_end', 'trial_start', 'trial_end',
            'canceled_at', 'ended_at', 'cancel_at_period_end', 'is_active',
            'days_until_renewal', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active', 'days_until_renewal']

    def get_is_active(self, obj):
        return obj.is_active()

    def get_days_until_renewal(self, obj):
        return obj.days_until_renewal()


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods."""
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'organization', 'type', 'is_default', 'display_name',
            'card_last4', 'card_brand', 'card_exp_month', 'card_exp_year',
            'bank_name', 'account_last4', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'display_name']
        extra_kwargs = {
            'card_last4': {'write_only': True},
            'card_exp_month': {'write_only': True},
            'card_exp_year': {'write_only': True},
            'account_last4': {'write_only': True},
        }

    def get_display_name(self, obj):
        return str(obj)


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items."""

    class Meta:
        model = InvoiceLineItem
        fields = [
            'id', 'description', 'quantity', 'unit_price', 'amount',
            'usage_record', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'amount', 'created_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices."""
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'organization', 'subscription', 'invoice_number', 'status',
            'subtotal', 'tax', 'total', 'amount_paid', 'amount_due', 'currency',
            'invoice_date', 'due_date', 'paid_at', 'pdf_url', 'notes',
            'line_items', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'is_overdue', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        return obj.is_overdue()


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'payment_method', 'amount', 'currency', 'status',
            'failure_code', 'failure_message', 'processed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UsageRecordSerializer(serializers.ModelSerializer):
    """Serializer for usage records."""

    class Meta:
        model = UsageRecord
        fields = [
            'id', 'organization', 'subscription', 'metric', 'quantity', 'unit_price',
            'period_start', 'period_end', 'is_billed', 'billed_at',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'is_billed', 'billed_at', 'created_at']


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for coupons."""
    is_valid = serializers.SerializerMethodField()
    discount_display = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value', 'currency',
            'valid_from', 'valid_until', 'max_redemptions', 'times_redeemed',
            'applicable_plans', 'first_time_only', 'duration_months',
            'is_active', 'is_valid', 'discount_display', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_redeemed', 'is_valid', 'discount_display', 'created_at', 'updated_at']

    def get_is_valid(self, obj):
        return obj.is_valid()

    def get_discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount_value}%"
        return f"{obj.discount_value} {obj.currency}"


class DunningAttemptSerializer(serializers.ModelSerializer):
    """Serializer for dunning attempts."""

    class Meta:
        model = DunningAttempt
        fields = [
            'id', 'subscription', 'invoice', 'attempt_number', 'status',
            'scheduled_for', 'attempted_at', 'success', 'error_message',
            'email_sent', 'email_sent_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
