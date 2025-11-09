"""
Feature flags and experimentation models.
"""

import uuid
import hashlib
from django.db import models
from django.conf import settings
from django.utils import timezone


class FeatureFlag(models.Model):
    """
    Feature flags for gradual rollouts and A/B testing.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    ROLLOUT_TYPE_CHOICES = [
        ('boolean', 'Boolean (On/Off)'),
        ('percentage', 'Percentage Rollout'),
        ('whitelist', 'Whitelist'),
        ('segment', 'User Segment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, help_text="Unique flag key")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Status and type
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rollout_type = models.CharField(max_length=20, choices=ROLLOUT_TYPE_CHOICES, default='boolean')

    # Boolean flag
    is_enabled = models.BooleanField(default=False)

    # Percentage rollout (0-100)
    rollout_percentage = models.IntegerField(
        default=0,
        help_text="Percentage of users to enable feature for (0-100)"
    )

    # Segment-based targeting
    required_tier = models.CharField(
        max_length=50,
        blank=True,
        help_text="Minimum subscription tier required"
    )

    # Scheduling
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Dependencies
    depends_on = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_flags',
        help_text="Flags that must be enabled for this flag to work"
    )

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_flags'
    )

    class Meta:
        db_table = 'foundation_feature_flag'
        ordering = ['name']
        indexes = [
            models.Index(fields=['key', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.key})"

    def is_enabled_for_user(self, user):
        """Check if flag is enabled for a specific user."""
        if self.status != 'active':
            return False

        # Check date range
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False

        # Check dependencies
        for dep_flag in self.depends_on.all():
            if not dep_flag.is_enabled_for_user(user):
                return False

        # Check rollout type
        if self.rollout_type == 'boolean':
            return self.is_enabled

        elif self.rollout_type == 'percentage':
            # Use consistent hashing for percentage rollout
            hash_key = f"{self.key}:{user.id}"
            hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
            return (hash_value % 100) < self.rollout_percentage

        elif self.rollout_type == 'whitelist':
            return FeatureFlagAssignment.objects.filter(
                flag=self,
                user=user,
                is_enabled=True
            ).exists()

        elif self.rollout_type == 'segment':
            # Check user segment criteria
            if self.required_tier:
                org_membership = user.organization_memberships.first()
                if not org_membership:
                    return False
                if org_membership.organization.subscription_tier != self.required_tier:
                    return False

            return True

        return False

    def is_enabled_for_organization(self, organization):
        """Check if flag is enabled for an organization."""
        if self.status != 'active':
            return False

        if self.rollout_type == 'boolean':
            return self.is_enabled

        # Check organization-level assignment
        return FeatureFlagAssignment.objects.filter(
            flag=self,
            organization=organization,
            is_enabled=True
        ).exists()


class FeatureFlagAssignment(models.Model):
    """
    Explicit assignments of feature flags to users or organizations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    # Assignment target (user or organization)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='flag_assignments'
    )
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='flag_assignments'
    )

    # Assignment value
    is_enabled = models.BooleanField()

    # Metadata
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assignments'
    )

    class Meta:
        db_table = 'foundation_feature_flag_assignment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['flag', 'user']),
            models.Index(fields=['flag', 'organization']),
        ]

    def __str__(self):
        target = self.user or self.organization
        return f"{self.flag.key} -> {target}: {self.is_enabled}"


class Experiment(models.Model):
    """
    A/B testing experiments.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Experiment configuration
    hypothesis = models.TextField(help_text="What are you testing?")
    success_metric = models.CharField(
        max_length=100,
        help_text="Primary metric to measure success"
    )

    # Timing
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Targeting
    target_percentage = models.IntegerField(
        default=100,
        help_text="Percentage of users to include in experiment"
    )
    required_tier = models.CharField(max_length=50, blank=True)

    # Results
    winner_variant = models.ForeignKey(
        'ExperimentVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_experiments'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_experiments'
    )

    class Meta:
        db_table = 'foundation_experiment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.key})"

    def get_variant_for_user(self, user):
        """Get the assigned variant for a user."""
        # Check if user has explicit assignment
        assignment = ExperimentAssignment.objects.filter(
            experiment=self,
            user=user
        ).first()

        if assignment:
            return assignment.variant

        # Assign variant based on hash
        variants = self.variants.filter(is_active=True).order_by('id')
        if not variants:
            return None

        # Use consistent hashing
        hash_key = f"{self.key}:{user.id}"
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)

        # Calculate cumulative weights
        total_weight = sum(v.traffic_allocation for v in variants)
        if total_weight == 0:
            return variants.first()

        threshold = (hash_value % total_weight)
        cumulative = 0

        for variant in variants:
            cumulative += variant.traffic_allocation
            if threshold < cumulative:
                # Create assignment
                ExperimentAssignment.objects.create(
                    experiment=self,
                    user=user,
                    variant=variant
                )
                return variant

        return variants.first()


class ExperimentVariant(models.Model):
    """
    Variants for A/B testing experiments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    # Variant details
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Traffic allocation
    traffic_allocation = models.IntegerField(
        default=50,
        help_text="Percentage of experiment traffic to allocate to this variant"
    )

    # Configuration
    configuration = models.JSONField(
        default=dict,
        help_text="Variant-specific configuration"
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_control = models.BooleanField(default=False, help_text="Is this the control variant?")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_experiment_variant'
        ordering = ['experiment', 'created_at']
        unique_together = [['experiment', 'key']]
        indexes = [
            models.Index(fields=['experiment', 'is_active']),
        ]

    def __str__(self):
        return f"{self.experiment.name} - {self.name}"


class ExperimentAssignment(models.Model):
    """
    Tracks which users are assigned to which experiment variants.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experiment_assignments'
    )
    variant = models.ForeignKey(
        ExperimentVariant,
        on_delete=models.CASCADE,
        related_name='assignments'
    )

    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foundation_experiment_assignment'
        ordering = ['-assigned_at']
        unique_together = [['experiment', 'user']]
        indexes = [
            models.Index(fields=['experiment', 'variant']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.variant.name}"


class ExperimentEvent(models.Model):
    """
    Tracks events for experiment analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name='events'
    )
    variant = models.ForeignKey(
        ExperimentVariant,
        on_delete=models.CASCADE,
        related_name='events'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experiment_events'
    )

    # Event details
    event_type = models.CharField(max_length=100)
    event_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = 'foundation_experiment_event'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['experiment', 'variant', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.variant.name}"
