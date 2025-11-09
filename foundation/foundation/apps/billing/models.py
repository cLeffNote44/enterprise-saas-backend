"""
Billing and subscription models.
"""

import uuid
from decimal import Decimal
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class SubscriptionPlan(models.Model):
    """
    Subscription plans with pricing information.
    Extends the tier system from Organization with pricing details.
    """
    BILLING_INTERVAL_CHOICES = [
        ('month', 'Monthly'),
        ('year', 'Yearly'),
        ('quarter', 'Quarterly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Plan name (e.g., 'Professional Monthly')")
    tier = models.CharField(
        max_length=50,
        choices=[
            ('starter', 'Starter'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
            ('enterprise_plus', 'Enterprise Plus'),
        ],
        help_text="Subscription tier level"
    )
    billing_interval = models.CharField(
        max_length=20,
        choices=BILLING_INTERVAL_CHOICES,
        default='month'
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Base price for the plan"
    )
    currency = models.CharField(max_length=3, default='USD')

    # Stripe integration
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)

    # Features and limits (inherited from tier but can be customized)
    features = models.JSONField(default=dict, help_text="Plan features as JSON")
    limits = models.JSONField(default=dict, help_text="Usage limits as JSON")

    # Plan settings
    is_active = models.BooleanField(default=True)
    trial_days = models.IntegerField(default=14, help_text="Trial period in days")
    is_public = models.BooleanField(default=True, help_text="Show in public pricing page")

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_subscription_plan'
        ordering = ['price']
        unique_together = [['tier', 'billing_interval']]
        indexes = [
            models.Index(fields=['tier', 'is_active']),
            models.Index(fields=['stripe_price_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_billing_interval_display()})"


class Subscription(models.Model):
    """
    Organization subscriptions.
    """
    STATUS_CHOICES = [
        ('trialing', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('incomplete', 'Incomplete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Billing
    cancel_at_period_end = models.BooleanField(default=False)

    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'foundation_subscription'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['stripe_subscription_id']),
            models.Index(fields=['current_period_end']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.plan.name}"

    def is_active(self):
        """Check if subscription is currently active."""
        return self.status in ['trialing', 'active']

    def days_until_renewal(self):
        """Calculate days until next renewal."""
        if self.current_period_end:
            return (self.current_period_end - timezone.now()).days
        return None


class PaymentMethod(models.Model):
    """
    Payment methods (credit cards, bank accounts, etc.).
    """
    TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )

    # Payment method details
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_default = models.BooleanField(default=False)

    # Card details (last 4 digits, brand, expiry)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)

    # Bank account details
    bank_name = models.CharField(max_length=100, blank=True)
    account_last4 = models.CharField(max_length=4, blank=True)

    # Stripe integration
    stripe_payment_method_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_payment_method'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_default']),
            models.Index(fields=['stripe_payment_method_id']),
        ]

    def __str__(self):
        if self.type == 'card':
            return f"{self.card_brand} ****{self.card_last4}"
        return f"{self.get_type_display()}"

    def save(self, *args, **kwargs):
        """Ensure only one default payment method per organization."""
        if self.is_default:
            PaymentMethod.objects.filter(
                organization=self.organization,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    Invoices for subscriptions and one-time charges.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('void', 'Void'),
        ('uncollectible', 'Uncollectible'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )

    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')

    # Dates
    invoice_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)

    # Stripe integration
    stripe_invoice_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Files
    pdf_url = models.URLField(blank=True, help_text="URL to generated PDF invoice")

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_invoice'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['stripe_invoice_id']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.organization.name}"

    def is_overdue(self):
        """Check if invoice is overdue."""
        return self.status == 'open' and self.due_date < timezone.now()


class InvoiceLineItem(models.Model):
    """
    Line items for invoices.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='line_items'
    )

    # Item details
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # For usage-based billing
    usage_record = models.ForeignKey(
        'UsageRecord',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='line_items'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_invoice_line_item'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.description} - {self.amount}"

    def save(self, *args, **kwargs):
        """Calculate amount from quantity and unit_price."""
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment records for invoices.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)

    # Error handling
    failure_code = models.CharField(max_length=50, blank=True)
    failure_message = models.TextField(blank=True)

    # Metadata
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_payment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]

    def __str__(self):
        return f"Payment {self.amount} {self.currency} - {self.get_status_display()}"


class UsageRecord(models.Model):
    """
    Usage records for metered billing.
    """
    METRIC_CHOICES = [
        ('api_calls', 'API Calls'),
        ('storage', 'Storage (GB)'),
        ('users', 'Active Users'),
        ('data_processed', 'Data Processed (GB)'),
        ('custom', 'Custom Metric'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )

    # Usage details
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    # Billing
    is_billed = models.BooleanField(default=False)
    billed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_usage_record'
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['organization', 'metric']),
            models.Index(fields=['subscription', 'is_billed']),
            models.Index(fields=['period_start', 'period_end']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.get_metric_display()}: {self.quantity}"


class Coupon(models.Model):
    """
    Discount coupons and promotional codes.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('amount', 'Fixed Amount'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)

    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='USD', help_text="For fixed amount discounts")

    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)

    # Usage limits
    max_redemptions = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this coupon can be used"
    )
    times_redeemed = models.IntegerField(default=0)

    # Restrictions
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        related_name='coupons',
        help_text="Leave empty for all plans"
    )
    first_time_only = models.BooleanField(
        default=False,
        help_text="Only applicable to first-time customers"
    )

    # Duration (for subscriptions)
    duration_months = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of months the discount applies. Leave empty for one-time discount."
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Stripe integration
    stripe_coupon_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_coupon'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]

    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percent' else self.currency}"

    def is_valid(self):
        """Check if coupon is currently valid."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        if self.max_redemptions and self.times_redeemed >= self.max_redemptions:
            return False
        return True


class DunningAttempt(models.Model):
    """
    Tracks payment retry attempts for failed payments (dunning management).
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('exhausted', 'Exhausted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='dunning_attempts'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='dunning_attempts'
    )

    # Attempt details
    attempt_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Schedule
    scheduled_for = models.DateTimeField()
    attempted_at = models.DateTimeField(null=True, blank=True)

    # Results
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    # Actions taken
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'foundation_dunning_attempt'
        ordering = ['attempt_number']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['scheduled_for']),
        ]

    def __str__(self):
        return f"Attempt {self.attempt_number} for {self.subscription}"
