"""
Admin interface for billing app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SubscriptionPlan, Subscription, PaymentMethod, Invoice,
    InvoiceLineItem, Payment, UsageRecord, Coupon, DunningAttempt
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'billing_interval', 'price', 'currency', 'is_active', 'is_public']
    list_filter = ['tier', 'billing_interval', 'is_active', 'is_public']
    search_fields = ['name', 'stripe_price_id', 'stripe_product_id']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tier', 'billing_interval', 'description', 'is_active', 'is_public')
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'trial_days')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id', 'stripe_product_id'),
            'classes': ('collapse',)
        }),
        ('Features & Limits', {
            'fields': ('features', 'limits'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['organization', 'plan', 'status', 'current_period_end', 'cancel_at_period_end']
    list_filter = ['status', 'plan__tier', 'cancel_at_period_end']
    search_fields = ['organization__name', 'stripe_subscription_id', 'stripe_customer_id']
    readonly_fields = ['created_at', 'updated_at', 'days_until_renewal']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Subscription Details', {
            'fields': ('organization', 'plan', 'status')
        }),
        ('Current Period', {
            'fields': ('current_period_start', 'current_period_end', 'days_until_renewal')
        }),
        ('Trial Period', {
            'fields': ('trial_start', 'trial_end'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancel_at_period_end', 'canceled_at', 'ended_at'),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['organization', 'type', 'display_details', 'is_default', 'created_at']
    list_filter = ['type', 'is_default']
    search_fields = ['organization__name', 'stripe_payment_method_id']
    readonly_fields = ['created_at', 'updated_at']

    def display_details(self, obj):
        if obj.type == 'card':
            return f"{obj.card_brand} ****{obj.card_last4}"
        elif obj.type == 'bank_account':
            return f"{obj.bank_name} ****{obj.account_last4}"
        return obj.get_type_display()
    display_details.short_description = 'Details'


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    readonly_fields = ['amount', 'created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'organization', 'status', 'total', 'currency', 'due_date', 'is_overdue']
    list_filter = ['status', 'currency']
    search_fields = ['invoice_number', 'organization__name', 'stripe_invoice_id']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    date_hierarchy = 'invoice_date'
    inlines = [InvoiceLineItemInline]

    fieldsets = (
        ('Invoice Details', {
            'fields': ('organization', 'subscription', 'invoice_number', 'status')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax', 'total', 'amount_paid', 'amount_due', 'currency')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'paid_at', 'is_overdue')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_invoice_id', 'pdf_url'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue(self, obj):
        if obj.is_overdue():
            return format_html('<span style="color: red;">Yes</span>')
        return 'No'
    is_overdue.short_description = 'Overdue'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['invoice__invoice_number', 'stripe_payment_intent_id', 'stripe_charge_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Payment Details', {
            'fields': ('invoice', 'payment_method', 'amount', 'currency', 'status')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('failure_code', 'failure_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['organization', 'metric', 'quantity', 'period_start', 'period_end', 'is_billed']
    list_filter = ['metric', 'is_billed']
    search_fields = ['organization__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'period_start'

    fieldsets = (
        ('Usage Details', {
            'fields': ('organization', 'subscription', 'metric', 'quantity', 'unit_price')
        }),
        ('Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Billing', {
            'fields': ('is_billed', 'billed_at')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_display', 'is_valid_status', 'times_redeemed', 'max_redemptions', 'is_active']
    list_filter = ['discount_type', 'is_active', 'first_time_only']
    search_fields = ['code', 'stripe_coupon_id']
    readonly_fields = ['times_redeemed', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_plans']

    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'currency', 'duration_months')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Usage', {
            'fields': ('max_redemptions', 'times_redeemed')
        }),
        ('Restrictions', {
            'fields': ('applicable_plans', 'first_time_only'),
            'classes': ('collapse',)
        }),
        ('Stripe Integration', {
            'fields': ('stripe_coupon_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def discount_display(self, obj):
        if obj.discount_type == 'percent':
            return f"{obj.discount_value}%"
        return f"{obj.discount_value} {obj.currency}"
    discount_display.short_description = 'Discount'

    def is_valid_status(self, obj):
        if obj.is_valid():
            return format_html('<span style="color: green;">Valid</span>')
        return format_html('<span style="color: red;">Invalid</span>')
    is_valid_status.short_description = 'Status'


@admin.register(DunningAttempt)
class DunningAttemptAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'invoice', 'attempt_number', 'status', 'scheduled_for', 'success']
    list_filter = ['status', 'success', 'email_sent']
    search_fields = ['subscription__organization__name', 'invoice__invoice_number']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_for'

    fieldsets = (
        ('Attempt Details', {
            'fields': ('subscription', 'invoice', 'attempt_number', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_for', 'attempted_at')
        }),
        ('Results', {
            'fields': ('success', 'error_message')
        }),
        ('Notifications', {
            'fields': ('email_sent', 'email_sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
