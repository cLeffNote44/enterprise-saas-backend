"""
Signals for billing app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Subscription, Invoice, Payment


@receiver(post_save, sender=Payment)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    """Update invoice amounts when a payment is made."""
    if created and instance.status == 'succeeded':
        invoice = instance.invoice
        invoice.amount_paid += instance.amount
        invoice.amount_due = invoice.total - invoice.amount_paid

        if invoice.amount_due <= 0:
            invoice.status = 'paid'
            invoice.paid_at = timezone.now()

        invoice.save()


@receiver(post_save, sender=Subscription)
def update_organization_tier(sender, instance, **kwargs):
    """Update organization tier when subscription changes."""
    if instance.is_active():
        org = instance.organization
        org.subscription_tier = instance.plan.tier
        org.subscription_status = instance.status
        org.save(update_fields=['subscription_tier', 'subscription_status'])
