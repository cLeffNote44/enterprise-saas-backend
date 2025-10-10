"""
Enterprise features for Data Destroyer including multi-tenancy, 
advanced RBAC, and organization management.
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class SubscriptionTier(models.TextChoices):
    """Subscription tiers for organizations."""
    STARTER = 'starter', 'Starter'
    PROFESSIONAL = 'professional', 'Professional' 
    ENTERPRISE = 'enterprise', 'Enterprise'
    ENTERPRISE_PLUS = 'enterprise_plus', 'Enterprise Plus'


class OrganizationStatus(models.TextChoices):
    """Organization status options."""
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    TRIAL = 'trial', 'Trial'
    INACTIVE = 'inactive', 'Inactive'


class Organization(models.Model):
    """
    Multi-tenant organization model for enterprise customers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    
    # Subscription and billing
    subscription_tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.STARTER
    )
    status = models.CharField(
        max_length=20,
        choices=OrganizationStatus.choices,
        default=OrganizationStatus.TRIAL
    )
    
    # Contact information
    primary_contact_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Compliance and security settings
    compliance_frameworks = models.JSONField(
        default=list,
        help_text="List of compliance frameworks (HIPAA, GDPR, etc.)"
    )
    data_residency_region = models.CharField(
        max_length=50,
        blank=True,
        help_text="Data residency requirement (e.g., 'EU', 'US')"
    )
    
    # Feature flags and limits
    feature_flags = models.JSONField(
        default=dict,
        help_text="Feature enablement flags"
    )
    usage_limits = models.JSONField(
        default=dict,
        help_text="Usage limits for various features"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_organizations'
    )
    
    # Billing and subscription
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_ends_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'foundation_organization'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.subscription_tier})"
    
    def is_trial_expired(self) -> bool:
        """Check if trial period has expired."""
        if not self.trial_ends_at:
            return False
        return timezone.now() > self.trial_ends_at
    
    def is_subscription_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status != OrganizationStatus.ACTIVE:
            return False
        if self.subscription_ends_at and timezone.now() > self.subscription_ends_at:
            return False
        return True
    
    def get_feature_limit(self, feature: str) -> Optional[int]:
        """Get usage limit for a specific feature."""
        return self.usage_limits.get(feature)
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled for this organization."""
        return self.feature_flags.get(feature, False)
    
    def get_compliance_frameworks(self) -> List[str]:
        """Get list of enabled compliance frameworks."""
        return self.compliance_frameworks
    
    def add_compliance_framework(self, framework: str):
        """Add a compliance framework."""
        if framework not in self.compliance_frameworks:
            self.compliance_frameworks.append(framework)
            self.save(update_fields=['compliance_frameworks'])
    
    def remove_compliance_framework(self, framework: str):
        """Remove a compliance framework."""
        if framework in self.compliance_frameworks:
            self.compliance_frameworks.remove(framework)
            self.save(update_fields=['compliance_frameworks'])


class Department(models.Model):
    """
    Organizational departments for grouping users and permissions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Hierarchy support
    parent_department = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_departments'
    )
    
    # Department settings
    is_active = models.BooleanField(default=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'foundation_department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        unique_together = ['organization', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
    
    def get_all_sub_departments(self):
        """Get all sub-departments recursively."""
        sub_departments = []
        for dept in self.sub_departments.all():
            sub_departments.append(dept)
            sub_departments.extend(dept.get_all_sub_departments())
        return sub_departments


class Role(models.Model):
    """
    Custom roles for advanced RBAC system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='roles'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Role configuration
    is_system_role = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted"
    )
    is_active = models.BooleanField(default=True)
    
    # Permissions
    permissions = models.ManyToManyField(
        Permission,
        through='RolePermission',
        related_name='custom_roles'
    )
    
    # Data access controls
    data_access_level = models.CharField(
        max_length=50,
        choices=[
            ('none', 'No Access'),
            ('read', 'Read Only'),
            ('write', 'Read/Write'),
            ('admin', 'Full Admin'),
        ],
        default='read'
    )
    
    # Resource constraints
    resource_constraints = models.JSONField(
        default=dict,
        help_text="JSON object defining resource access constraints"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_roles'
    )
    
    class Meta:
        db_table = 'foundation_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        unique_together = ['organization', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
    
    def has_permission(self, permission_codename: str) -> bool:
        """Check if role has a specific permission."""
        return self.permissions.filter(codename=permission_codename).exists()
    
    def add_permission(self, permission: Permission, granted_by: User = None):
        """Add permission to role."""
        RolePermission.objects.get_or_create(
            role=self,
            permission=permission,
            defaults={'granted_by': granted_by}
        )
    
    def remove_permission(self, permission: Permission):
        """Remove permission from role."""
        RolePermission.objects.filter(
            role=self,
            permission=permission
        ).delete()


class RolePermission(models.Model):
    """
    Through model for Role-Permission relationship with audit trail.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    # Permission constraints
    resource_filter = models.JSONField(
        default=dict,
        help_text="Additional constraints on this permission"
    )
    
    # Audit fields
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        db_table = 'foundation_rolepermission'
        unique_together = ['role', 'permission']


class OrganizationMembership(models.Model):
    """
    User membership in organizations with role assignments.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('invited', 'Invited'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    
    # Role and department assignments
    roles = models.ManyToManyField(
        Role,
        related_name='members',
        blank=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    
    # Membership details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited'
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="Organization administrator privileges"
    )
    
    # Access controls
    can_invite_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    can_access_billing = models.BooleanField(default=False)
    
    # Audit fields
    joined_at = models.DateTimeField(null=True, blank=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations'
    )
    
    # Session and access tracking
    last_access = models.DateTimeField(null=True, blank=True)
    access_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'foundation_organizationmembership'
        verbose_name = 'Organization Membership'
        verbose_name_plural = 'Organization Memberships'
        unique_together = ['user', 'organization']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} @ {self.organization.name}"
    
    def activate_membership(self):
        """Activate the membership (accept invitation)."""
        self.status = 'active'
        self.joined_at = timezone.now()
        self.save(update_fields=['status', 'joined_at'])
    
    def get_all_permissions(self):
        """Get all permissions from assigned roles."""
        permissions = set()
        for role in self.roles.filter(is_active=True):
            for perm in role.permissions.all():
                permissions.add(perm)
        return list(permissions)
    
    def has_permission(self, permission_codename: str) -> bool:
        """Check if user has specific permission in this organization."""
        if self.is_admin:
            return True
        
        for role in self.roles.filter(is_active=True):
            if role.has_permission(permission_codename):
                return True
        return False
    
    def record_access(self):
        """Record user access to organization."""
        self.last_access = timezone.now()
        self.access_count += 1
        self.save(update_fields=['last_access', 'access_count'])


class DataAccessPolicy(models.Model):
    """
    Fine-grained data access policies for organizations.
    """
    POLICY_TYPES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('conditional', 'Conditional'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='data_access_policies'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Policy configuration
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    resource_pattern = models.CharField(
        max_length=255,
        help_text="Resource pattern (e.g., 'documents.*', 'users.profile')"
    )
    conditions = models.JSONField(
        default=dict,
        help_text="Conditions for policy evaluation"
    )
    
    # Scope
    applies_to_roles = models.ManyToManyField(Role, blank=True)
    applies_to_departments = models.ManyToManyField(Department, blank=True)
    
    # Policy settings
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(
        default=100,
        help_text="Lower numbers = higher priority"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        db_table = 'foundation_dataaccesspolicy'
        verbose_name = 'Data Access Policy'
        verbose_name_plural = 'Data Access Policies'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
    
    def evaluate(self, user: User, resource: str, context: Dict[str, Any] = None) -> bool:
        """
        Evaluate policy against user, resource, and context.
        
        Args:
            user: User requesting access
            resource: Resource being accessed
            context: Additional context for evaluation
            
        Returns:
            bool: True if access should be allowed
        """
        # Check if resource matches pattern
        import re
        pattern = self.resource_pattern.replace('*', '.*')
        if not re.match(pattern, resource):
            return True  # Policy doesn't apply
        
        # Get user's membership
        try:
            membership = user.organization_memberships.get(
                organization=self.organization,
                status='active'
            )
        except OrganizationMembership.DoesNotExist:
            return False  # User not in organization
        
        # Check if policy applies to user's roles or department
        user_roles = set(membership.roles.all())
        applicable_roles = set(self.applies_to_roles.all())
        
        if applicable_roles and not user_roles.intersection(applicable_roles):
            if not (membership.department and 
                   membership.department in self.applies_to_departments.all()):
                return True  # Policy doesn't apply to this user
        
        # Evaluate conditions
        context = context or {}
        context.update({
            'user': user,
            'membership': membership,
            'organization': self.organization,
            'resource': resource
        })
        
        if self.policy_type == 'allow':
            return self._evaluate_conditions(context)
        elif self.policy_type == 'deny':
            return not self._evaluate_conditions(context)
        else:  # conditional
            return self._evaluate_conditions(context)
    
    def _evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions."""
        if not self.conditions:
            return True
        
        # Simple condition evaluation
        # In production, you'd want a more sophisticated rule engine
        for condition_key, condition_value in self.conditions.items():
            if condition_key == 'time_range':
                # Check if current time is within allowed range
                current_hour = timezone.now().hour
                start, end = condition_value.get('start', 0), condition_value.get('end', 23)
                if not (start <= current_hour <= end):
                    return False
            
            elif condition_key == 'ip_whitelist':
                # Check if user's IP is in whitelist
                user_ip = context.get('user_ip')
                if user_ip and user_ip not in condition_value:
                    return False
            
            elif condition_key == 'department_required':
                # Check if user is in required department
                membership = context.get('membership')
                required_dept = condition_value
                if not (membership.department and 
                       membership.department.name == required_dept):
                    return False
        
        return True


class EnterpriseManager:
    """
    Manager class for enterprise operations.
    """
    
    @staticmethod
    def create_organization(
        name: str,
        slug: str,
        primary_contact_email: str,
        subscription_tier: str = SubscriptionTier.STARTER,
        created_by: User = None
    ) -> Organization:
        """Create a new organization with default settings."""
        
        # Set default feature flags based on tier
        feature_flags = EnterpriseManager._get_default_feature_flags(subscription_tier)
        
        # Set default usage limits
        usage_limits = EnterpriseManager._get_default_usage_limits(subscription_tier)
        
        # Set trial period
        trial_ends_at = timezone.now() + timedelta(days=30)
        
        org = Organization.objects.create(
            name=name,
            slug=slug,
            primary_contact_email=primary_contact_email,
            subscription_tier=subscription_tier,
            status=OrganizationStatus.TRIAL,
            feature_flags=feature_flags,
            usage_limits=usage_limits,
            trial_ends_at=trial_ends_at,
            created_by=created_by
        )
        
        # Create default roles
        EnterpriseManager._create_default_roles(org, created_by)
        
        # Create default department
        Department.objects.create(
            organization=org,
            name="General",
            description="Default department for all users"
        )
        
        return org
    
    @staticmethod
    def _get_default_feature_flags(tier: str) -> Dict[str, bool]:
        """Get default feature flags for subscription tier."""
        base_features = {
            'data_discovery': True,
            'basic_compliance': True,
            'api_access': True,
        }
        
        if tier in [SubscriptionTier.PROFESSIONAL, SubscriptionTier.ENTERPRISE, SubscriptionTier.ENTERPRISE_PLUS]:
            base_features.update({
                'advanced_analytics': True,
                'custom_workflows': True,
                'sso_integration': True,
            })
        
        if tier in [SubscriptionTier.ENTERPRISE, SubscriptionTier.ENTERPRISE_PLUS]:
            base_features.update({
                'multi_tenancy': True,
                'advanced_rbac': True,
                'audit_logging': True,
                'compliance_dashboard': True,
            })
        
        if tier == SubscriptionTier.ENTERPRISE_PLUS:
            base_features.update({
                'white_labeling': True,
                'dedicated_support': True,
                'custom_integrations': True,
            })
        
        return base_features
    
    @staticmethod
    def _get_default_usage_limits(tier: str) -> Dict[str, int]:
        """Get default usage limits for subscription tier."""
        limits = {
            SubscriptionTier.STARTER: {
                'users': 5,
                'data_sources': 2,
                'api_calls_per_month': 10000,
                'storage_gb': 10,
            },
            SubscriptionTier.PROFESSIONAL: {
                'users': 25,
                'data_sources': 10,
                'api_calls_per_month': 100000,
                'storage_gb': 100,
            },
            SubscriptionTier.ENTERPRISE: {
                'users': 100,
                'data_sources': 50,
                'api_calls_per_month': 1000000,
                'storage_gb': 1000,
            },
            SubscriptionTier.ENTERPRISE_PLUS: {
                'users': -1,  # Unlimited
                'data_sources': -1,
                'api_calls_per_month': -1,
                'storage_gb': -1,
            }
        }
        
        return limits.get(tier, limits[SubscriptionTier.STARTER])
    
    @staticmethod
    def _create_default_roles(org: Organization, created_by: User = None):
        """Create default roles for organization."""
        default_roles = [
            {
                'name': 'Admin',
                'description': 'Full administrative access',
                'data_access_level': 'admin',
                'is_system_role': True,
            },
            {
                'name': 'Data Manager',
                'description': 'Manage data discovery and classification',
                'data_access_level': 'write',
                'is_system_role': True,
            },
            {
                'name': 'Compliance Officer',
                'description': 'Manage compliance policies and violations',
                'data_access_level': 'write',
                'is_system_role': True,
            },
            {
                'name': 'Analyst',
                'description': 'View reports and analytics',
                'data_access_level': 'read',
                'is_system_role': True,
            },
        ]
        
        for role_data in default_roles:
            Role.objects.create(
                organization=org,
                created_by=created_by,
                **role_data
            )
    
    @staticmethod
    def invite_user(
        organization: Organization,
        email: str,
        invited_by: User,
        roles: List[Role] = None,
        department: Department = None
    ) -> OrganizationMembership:
        """Invite a user to join an organization."""
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email}
        )
        
        # Create membership
        membership = OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            invited_by=invited_by,
            department=department,
            status='invited'
        )
        
        # Assign roles
        if roles:
            membership.roles.set(roles)
        
        # TODO: Send invitation email
        
        return membership
    
    @staticmethod
    def evaluate_data_access(
        user: User,
        organization: Organization,
        resource: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """
        Evaluate if user has access to a resource based on data access policies.
        """
        # Get applicable policies
        policies = DataAccessPolicy.objects.filter(
            organization=organization,
            is_active=True
        ).order_by('priority')
        
        # Default to deny
        access_granted = False
        
        for policy in policies:
            result = policy.evaluate(user, resource, context)
            
            if policy.policy_type == 'allow' and result:
                access_granted = True
            elif policy.policy_type == 'deny' and result:
                access_granted = False
                break  # Deny policies are final
        
        return access_granted
