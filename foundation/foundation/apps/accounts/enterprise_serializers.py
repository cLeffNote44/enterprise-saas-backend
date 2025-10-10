"""
Serializers for enterprise features including multi-tenancy and RBAC.
"""
from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from .enterprise import (
    Organization, Department, Role, RolePermission,
    OrganizationMembership, DataAccessPolicy,
    SubscriptionTier, OrganizationStatus
)

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    total_members = serializers.SerializerMethodField()
    is_trial_expired = serializers.SerializerMethodField()
    is_subscription_active = serializers.SerializerMethodField()
    compliance_frameworks = serializers.JSONField()
    feature_flags = serializers.JSONField()
    usage_limits = serializers.JSONField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'subscription_tier', 'status',
            'primary_contact_email', 'phone_number', 'website',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'compliance_frameworks',
            'data_residency_region', 'feature_flags', 'usage_limits',
            'created_at', 'updated_at', 'trial_ends_at',
            'subscription_ends_at', 'total_members', 'is_trial_expired',
            'is_subscription_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_members(self, obj) -> int:
        """Get total number of active members."""
        return obj.memberships.filter(status='active').count()
    
    def get_is_trial_expired(self, obj) -> bool:
        """Check if trial period has expired."""
        return obj.is_trial_expired()
    
    def get_is_subscription_active(self, obj) -> bool:
        """Check if subscription is active."""
        return obj.is_subscription_active()


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations."""
    
    class Meta:
        model = Organization
        fields = [
            'name', 'slug', 'primary_contact_email', 'subscription_tier',
            'phone_number', 'website', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country',
            'data_residency_region'
        ]
    
    def validate_slug(self, value):
        """Validate organization slug is unique."""
        if Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Organization with this slug already exists.")
        return value


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    
    member_count = serializers.SerializerMethodField()
    sub_departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'parent_department',
            'is_active', 'created_at', 'updated_at',
            'member_count', 'sub_departments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj) -> int:
        """Get number of active members in department."""
        return obj.members.filter(status='active').count()
    
    def get_sub_departments(self, obj):
        """Get sub-departments."""
        return DepartmentSerializer(
            obj.sub_departments.filter(is_active=True),
            many=True,
            context=self.context
        ).data


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model."""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission through model."""
    
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.IntegerField(write_only=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'permission', 'permission_id', 'resource_filter',
            'granted_at', 'granted_by_name'
        ]


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    member_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_system_role', 'is_active',
            'data_access_level', 'resource_constraints', 'permissions',
            'permission_ids', 'created_at', 'updated_at', 'created_by_name',
            'member_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system_role']
    
    def get_member_count(self, obj) -> int:
        """Get number of members with this role."""
        return obj.members.filter(status='active').count()
    
    def create(self, validated_data):
        """Create role with permissions."""
        permission_ids = validated_data.pop('permission_ids', [])
        role = super().create(validated_data)
        
        # Add permissions
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            for permission in permissions:
                role.add_permission(permission, self.context['request'].user)
        
        return role
    
    def update(self, instance, validated_data):
        """Update role and permissions."""
        permission_ids = validated_data.pop('permission_ids', None)
        role = super().update(instance, validated_data)
        
        # Update permissions if provided
        if permission_ids is not None:
            # Clear existing permissions
            RolePermission.objects.filter(role=role).delete()
            
            # Add new permissions
            permissions = Permission.objects.filter(id__in=permission_ids)
            for permission in permissions:
                role.add_permission(permission, self.context['request'].user)
        
        return role


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMembership model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_names = serializers.SerializerMethodField()
    invited_by_name = serializers.CharField(source='invited_by.username', read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = [
            'id', 'user_email', 'user_name', 'status', 'is_admin',
            'department', 'department_name', 'roles', 'role_names',
            'can_invite_users', 'can_manage_roles', 'can_access_billing',
            'joined_at', 'invited_at', 'invited_by_name', 'last_access',
            'access_count'
        ]
        read_only_fields = [
            'id', 'user_email', 'user_name', 'joined_at', 'invited_at',
            'invited_by_name', 'last_access', 'access_count'
        ]
    
    def get_role_names(self, obj):
        """Get list of role names."""
        return [role.name for role in obj.roles.all()]


class InviteUserSerializer(serializers.Serializer):
    """Serializer for inviting users to organization."""
    
    email = serializers.EmailField()
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True
    )
    department_id = serializers.UUIDField(required=False, allow_null=True)
    can_invite_users = serializers.BooleanField(default=False)
    can_manage_roles = serializers.BooleanField(default=False)
    can_access_billing = serializers.BooleanField(default=False)
    
    def validate_email(self, value):
        """Validate email address."""
        organization = self.context['organization']
        
        # Check if user is already a member
        if OrganizationMembership.objects.filter(
            organization=organization,
            user__email=value
        ).exists():
            raise serializers.ValidationError(
                "User is already a member of this organization."
            )
        
        return value
    
    def validate_role_ids(self, value):
        """Validate role IDs belong to organization."""
        if not value:
            return value
        
        organization = self.context['organization']
        roles = Role.objects.filter(
            id__in=value,
            organization=organization,
            is_active=True
        )
        
        if len(roles) != len(value):
            raise serializers.ValidationError(
                "One or more roles are invalid or inactive."
            )
        
        return value
    
    def validate_department_id(self, value):
        """Validate department belongs to organization."""
        if not value:
            return value
        
        organization = self.context['organization']
        try:
            Department.objects.get(
                id=value,
                organization=organization,
                is_active=True
            )
        except Department.DoesNotExist:
            raise serializers.ValidationError(
                "Department does not exist or is inactive."
            )
        
        return value


class DataAccessPolicySerializer(serializers.ModelSerializer):
    """Serializer for DataAccessPolicy model."""
    
    applies_to_role_names = serializers.SerializerMethodField()
    applies_to_department_names = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DataAccessPolicy
        fields = [
            'id', 'name', 'description', 'policy_type', 'resource_pattern',
            'conditions', 'applies_to_roles', 'applies_to_departments',
            'applies_to_role_names', 'applies_to_department_names',
            'is_active', 'priority', 'created_at', 'updated_at',
            'created_by_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_applies_to_role_names(self, obj):
        """Get list of role names this policy applies to."""
        return [role.name for role in obj.applies_to_roles.all()]
    
    def get_applies_to_department_names(self, obj):
        """Get list of department names this policy applies to."""
        return [dept.name for dept in obj.applies_to_departments.all()]


class OrganizationStatsSerializer(serializers.Serializer):
    """Serializer for organization statistics."""
    
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    invited_members = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    total_roles = serializers.IntegerField()
    total_policies = serializers.IntegerField()
    subscription_tier = serializers.CharField()
    subscription_status = serializers.CharField()
    trial_days_remaining = serializers.IntegerField()
    feature_usage = serializers.DictField()
    compliance_frameworks = serializers.ListField()


class UserOrganizationSerializer(serializers.Serializer):
    """Serializer for user's organization memberships."""
    
    organization = OrganizationSerializer()
    membership = OrganizationMembershipSerializer()
    
    class Meta:
        fields = ['organization', 'membership']


class BulkRoleAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk role assignment."""
    
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=['add', 'remove', 'replace'])
    
    def validate_user_ids(self, value):
        """Validate user IDs belong to organization."""
        organization = self.context['organization']
        memberships = OrganizationMembership.objects.filter(
            id__in=value,
            organization=organization,
            status='active'
        )
        
        if len(memberships) != len(value):
            raise serializers.ValidationError(
                "One or more users are not active members of this organization."
            )
        
        return value
    
    def validate_role_ids(self, value):
        """Validate role IDs belong to organization."""
        organization = self.context['organization']
        roles = Role.objects.filter(
            id__in=value,
            organization=organization,
            is_active=True
        )
        
        if len(roles) != len(value):
            raise serializers.ValidationError(
                "One or more roles are invalid or inactive."
            )
        
        return value


class AccessEvaluationSerializer(serializers.Serializer):
    """Serializer for access evaluation requests."""
    
    resource = serializers.CharField(max_length=255)
    user_id = serializers.UUIDField(required=False)
    context = serializers.DictField(required=False, default=dict)
    
    def validate_user_id(self, value):
        """Validate user exists and is member of organization."""
        if not value:
            return value
        
        organization = self.context['organization']
        try:
            OrganizationMembership.objects.get(
                user_id=value,
                organization=organization,
                status='active'
            )
        except OrganizationMembership.DoesNotExist:
            raise serializers.ValidationError(
                "User is not an active member of this organization."
            )
        
        return value


class FeatureFlagUpdateSerializer(serializers.Serializer):
    """Serializer for updating feature flags."""
    
    feature_flags = serializers.DictField(
        child=serializers.BooleanField()
    )
    
    def validate_feature_flags(self, value):
        """Validate feature flags are allowed for subscription tier."""
        organization = self.context['organization']
        tier = organization.subscription_tier
        
        # Define feature restrictions per tier
        tier_features = {
            SubscriptionTier.STARTER: [
                'data_discovery', 'basic_compliance', 'api_access'
            ],
            SubscriptionTier.PROFESSIONAL: [
                'data_discovery', 'basic_compliance', 'api_access',
                'advanced_analytics', 'custom_workflows', 'sso_integration'
            ],
            SubscriptionTier.ENTERPRISE: [
                'data_discovery', 'basic_compliance', 'api_access',
                'advanced_analytics', 'custom_workflows', 'sso_integration',
                'multi_tenancy', 'advanced_rbac', 'audit_logging',
                'compliance_dashboard'
            ],
            SubscriptionTier.ENTERPRISE_PLUS: [
                # All features allowed
            ]
        }
        
        allowed_features = tier_features.get(tier, [])
        
        # If Enterprise Plus, allow all features
        if tier == SubscriptionTier.ENTERPRISE_PLUS:
            return value
        
        # Check if any restricted features are being enabled
        for feature, enabled in value.items():
            if enabled and feature not in allowed_features:
                raise serializers.ValidationError(
                    f"Feature '{feature}' is not available for {tier} tier."
                )
        
        return value


class UsageLimitUpdateSerializer(serializers.Serializer):
    """Serializer for updating usage limits."""
    
    usage_limits = serializers.DictField(
        child=serializers.IntegerField()
    )
    
    def validate_usage_limits(self, value):
        """Validate usage limits are within allowed ranges."""
        organization = self.context['organization']
        tier = organization.subscription_tier
        
        # Define maximum limits per tier
        tier_limits = {
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
                # Unlimited (-1)
            }
        }
        
        max_limits = tier_limits.get(tier, tier_limits[SubscriptionTier.STARTER])
        
        # If Enterprise Plus, allow unlimited
        if tier == SubscriptionTier.ENTERPRISE_PLUS:
            return value
        
        # Check if any limits exceed maximum allowed
        for limit_name, limit_value in value.items():
            max_allowed = max_limits.get(limit_name)
            if max_allowed is not None and limit_value > max_allowed:
                raise serializers.ValidationError(
                    f"Limit '{limit_name}' cannot exceed {max_allowed} for {tier} tier."
                )
        
        return value
