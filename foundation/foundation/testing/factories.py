"""
Model factories for testing.

Usage:
    from foundation.testing.factories import UserFactory, OrganizationFactory

    user = UserFactory()
    org = OrganizationFactory()
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from foundation.apps.accounts.models import Organization, Role, OrganizationMembership
from foundation.apps.billing.models import SubscriptionPlan, Subscription, Invoice
from foundation.apps.notifications.models import Notification, NotificationTemplate
from foundation.apps.feature_flags.models import FeatureFlag, Experiment, ExperimentVariant

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'testpass123'
        self.set_password(password)
        self.save()


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""
    is_staff = True
    is_superuser = True
    username = factory.Sequence(lambda n: f'admin{n}')


class OrganizationFactory(DjangoModelFactory):
    """Factory for creating test organizations."""
    class Meta:
        model = Organization

    name = factory.Faker('company')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    subscription_tier = 'professional'
    subscription_status = 'active'
    is_active = True


class RoleFactory(DjangoModelFactory):
    """Factory for creating roles."""
    class Meta:
        model = Role

    organization = factory.SubFactory(OrganizationFactory)
    name = factory.Sequence(lambda n: f'Role {n}')
    description = factory.Faker('sentence')
    is_default = False


class OrganizationMembershipFactory(DjangoModelFactory):
    """Factory for organization memberships."""
    class Meta:
        model = OrganizationMembership

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)
    role = factory.SubFactory(RoleFactory, organization=factory.SelfAttribute('..organization'))
    is_admin = False


class SubscriptionPlanFactory(DjangoModelFactory):
    """Factory for subscription plans."""
    class Meta:
        model = SubscriptionPlan

    name = factory.Sequence(lambda n: f'Plan {n}')
    tier = 'professional'
    billing_interval = 'month'
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    currency = 'USD'
    is_active = True


class SubscriptionFactory(DjangoModelFactory):
    """Factory for subscriptions."""
    class Meta:
        model = Subscription

    organization = factory.SubFactory(OrganizationFactory)
    plan = factory.SubFactory(SubscriptionPlanFactory)
    status = 'active'
    current_period_start = factory.Faker('date_time_this_month')
    current_period_end = factory.Faker('date_time_this_month')


class InvoiceFactory(DjangoModelFactory):
    """Factory for invoices."""
    class Meta:
        model = Invoice

    organization = factory.SubFactory(OrganizationFactory)
    subscription = factory.SubFactory(SubscriptionFactory, organization=factory.SelfAttribute('..organization'))
    invoice_number = factory.Sequence(lambda n: f'INV-{n:05d}')
    status = 'paid'
    subtotal = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    tax = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    total = factory.LazyAttribute(lambda obj: obj.subtotal + obj.tax)
    amount_paid = factory.LazyAttribute(lambda obj: obj.total)
    amount_due = 0
    invoice_date = factory.Faker('date_time_this_month')
    due_date = factory.Faker('date_time_this_month')


class NotificationFactory(DjangoModelFactory):
    """Factory for notifications."""
    class Meta:
        model = Notification

    recipient = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence')
    message = factory.Faker('paragraph')
    priority = 'normal'
    status = 'pending'


class NotificationTemplateFactory(DjangoModelFactory):
    """Factory for notification templates."""
    class Meta:
        model = NotificationTemplate

    name = factory.Sequence(lambda n: f'template_{n}')
    channel = 'email'
    subject = factory.Faker('sentence')
    body_text = factory.Faker('paragraph')
    is_active = True


class FeatureFlagFactory(DjangoModelFactory):
    """Factory for feature flags."""
    class Meta:
        model = FeatureFlag

    key = factory.Sequence(lambda n: f'flag_{n}')
    name = factory.Sequence(lambda n: f'Feature Flag {n}')
    status = 'active'
    rollout_type = 'boolean'
    is_enabled = True


class ExperimentFactory(DjangoModelFactory):
    """Factory for experiments."""
    class Meta:
        model = Experiment

    name = factory.Sequence(lambda n: f'Experiment {n}')
    key = factory.Sequence(lambda n: f'experiment_{n}')
    status = 'running'
    hypothesis = factory.Faker('sentence')
    success_metric = 'conversion_rate'


class ExperimentVariantFactory(DjangoModelFactory):
    """Factory for experiment variants."""
    class Meta:
        model = ExperimentVariant

    experiment = factory.SubFactory(ExperimentFactory)
    name = factory.Sequence(lambda n: f'Variant {n}')
    key = factory.Sequence(lambda n: f'variant_{n}')
    traffic_allocation = 50
    is_active = True


# Helper functions for common test scenarios

def create_user_with_organization(username='testuser', org_name='Test Org'):
    """Create a user with an organization membership."""
    user = UserFactory(username=username)
    org = OrganizationFactory(name=org_name)
    membership = OrganizationMembershipFactory(user=user, organization=org, is_admin=True)
    return user, org, membership


def create_organization_with_subscription(tier='professional'):
    """Create an organization with an active subscription."""
    org = OrganizationFactory(subscription_tier=tier)
    plan = SubscriptionPlanFactory(tier=tier)
    subscription = SubscriptionFactory(organization=org, plan=plan)
    return org, subscription


def create_complete_test_environment():
    """Create a complete test environment with user, org, subscription, etc."""
    user, org, membership = create_user_with_organization()
    plan = SubscriptionPlanFactory(tier=org.subscription_tier)
    subscription = SubscriptionFactory(organization=org, plan=plan)
    invoice = InvoiceFactory(organization=org, subscription=subscription)

    return {
        'user': user,
        'organization': org,
        'membership': membership,
        'subscription': subscription,
        'invoice': invoice,
    }
