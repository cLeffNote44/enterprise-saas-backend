"""
Admin configuration for accounts app models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from rangefilter.filters import DateRangeFilter

from foundation.apps.accounts.models import (
    APIKey, UserActivity, UserSecurityProfile
)
from foundation.apps.accounts.enterprise import (
    Organization, OrganizationMembership, Department, Role, DataAccessPolicy
)
from .base import EnhancedModelAdmin, LinkMixin


# Unregister default User admin
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin, LinkMixin):
    """Enhanced User admin with organization info"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 
                    'is_staff', 'organization_count', 'last_login']
    list_filter = BaseUserAdmin.list_filter + [('date_joined', DateRangeFilter)]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def organization_count(self, obj):
        count = OrganizationMembership.objects.filter(user=obj).count()
        if count > 0:
            url = f"{reverse('admin:accounts_organizationmembership_changelist')}?user__id__exact={obj.id}"
            return format_html('<a href="{}">{} orgs</a>', url, count)
        return '0'
    organization_count.short_description = 'Organizations'
    
    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)
        if obj:
            # Add custom inlines for user details
            pass
        return inlines


class OrganizationMembershipInline(admin.TabularInline):
    """Inline for organization memberships"""
    model = OrganizationMembership
    extra = 0
    fields = ['user', 'role', 'department', 'is_admin', 'joined_at']
    readonly_fields = ['joined_at']
    autocomplete_fields = ['user', 'role']


@admin.register(Organization)
class OrganizationAdmin(EnhancedModelAdmin, LinkMixin):
    """Admin for Organization model"""
    
    list_display = ['name', 'slug', 'subscription_tier', 'member_count', 
                    'is_active', 'created_date', 'monthly_revenue']
    list_filter = ['subscription_tier', 'is_active', 'industry', 
                   ('created_at', DateRangeFilter)]
    search_fields = ['name', 'slug', 'primary_contact_email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'usage_stats']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'website')
        }),
        ('Contact Details', {
            'fields': ('primary_contact_email', 'primary_contact_name', 
                      'billing_email', 'technical_contact_email')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'max_users', 'storage_quota_gb', 
                      'api_rate_limit', 'custom_domain')
        }),
        ('Business Details', {
            'fields': ('industry', 'company_size', 'country', 'timezone')
        }),
        ('Settings', {
            'fields': ('is_active', 'enforce_2fa', 'allow_api_access', 
                      'data_retention_days')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrganizationMembershipInline]
    
    def member_count(self, obj):
        return obj.memberships.count()
    member_count.short_description = 'Members'
    
    def monthly_revenue(self, obj):
        # Calculate based on subscription tier
        tier_pricing = {
            'free': 0,
            'starter': 29,
            'professional': 99,
            'enterprise': 299,
            'enterprise_plus': 999
        }
        base_price = tier_pricing.get(obj.subscription_tier, 0)
        return format_html('${:,.2f}', base_price)
    monthly_revenue.short_description = 'MRR'
    
    def usage_stats(self, obj):
        """Display usage statistics"""
        stats = {
            'Members': obj.memberships.count(),
            'Departments': obj.departments.count(),
            'Active Users': obj.memberships.filter(user__last_login__isnull=False).count(),
        }
        html = '<table>'
        for key, value in stats.items():
            html += f'<tr><td><strong>{key}:</strong></td><td>{value}</td></tr>'
        html += '</table>'
        return format_html(html)
    usage_stats.short_description = 'Usage Statistics'


@admin.register(Department)
class DepartmentAdmin(EnhancedModelAdmin):
    """Admin for Department model"""
    
    list_display = ['name', 'organization', 'parent', 'member_count', 'is_active']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'organization__name']
    autocomplete_fields = ['organization', 'parent', 'manager']
    
    def member_count(self, obj):
        return OrganizationMembership.objects.filter(department=obj).count()
    member_count.short_description = 'Members'


@admin.register(Role)
class RoleAdmin(EnhancedModelAdmin):
    """Admin for Role model"""
    
    list_display = ['name', 'organization', 'permission_count', 'member_count', 
                    'is_system_role', 'created_date']
    list_filter = ['organization', 'is_system_role', ('created_at', DateRangeFilter)]
    search_fields = ['name', 'organization__name']
    filter_horizontal = ['permissions']
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'
    
    def member_count(self, obj):
        return OrganizationMembership.objects.filter(role=obj).count()
    member_count.short_description = 'Members'


@admin.register(APIKey)
class APIKeyAdmin(EnhancedModelAdmin, LinkMixin):
    """Admin for API Key model"""
    
    list_display = ['name', 'link_to_user', 'key_prefix', 'is_active', 
                    'last_used', 'expires_at', 'created_date']
    list_filter = ['is_active', ('created_at', DateRangeFilter), 
                   ('expires_at', DateRangeFilter)]
    search_fields = ['name', 'user__username', 'user__email', 'key_prefix']
    readonly_fields = ['key_prefix', 'hashed_key', 'created_at', 'last_used', 
                      'usage_count', 'rate_limit_info']
    
    fieldsets = (
        ('Key Information', {
            'fields': ('name', 'user', 'key_prefix', 'description')
        }),
        ('Permissions', {
            'fields': ('scopes', 'allowed_ips', 'allowed_origins')
        }),
        ('Limits & Expiry', {
            'fields': ('rate_limit', 'daily_limit', 'expires_at', 'is_active')
        }),
        ('Usage', {
            'fields': ('last_used', 'usage_count', 'rate_limit_info'),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': ('hashed_key', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rate_limit_info(self, obj):
        """Display rate limit information"""
        if obj.rate_limit:
            return format_html(
                '<strong>Rate Limit:</strong> {} requests/hour<br>'
                '<strong>Daily Limit:</strong> {} requests/day',
                obj.rate_limit or 'Unlimited',
                obj.daily_limit or 'Unlimited'
            )
        return 'No limits'
    rate_limit_info.short_description = 'Rate Limiting'
    
    actions = ['deactivate_keys', 'activate_keys', 'rotate_keys']
    
    def deactivate_keys(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {count} API keys.')
    deactivate_keys.short_description = 'Deactivate selected API keys'
    
    def activate_keys(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'Activated {count} API keys.')
    activate_keys.short_description = 'Activate selected API keys'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin for User Activity tracking"""
    
    list_display = ['user', 'action', 'ip_address', 'user_agent_display', 'timestamp']
    list_filter = ['action', ('timestamp', DateRangeFilter)]
    search_fields = ['user__username', 'user__email', 'ip_address', 'action']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 
                      'session_key', 'extra_data', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def user_agent_display(self, obj):
        if obj.user_agent:
            # Truncate long user agent strings
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    user_agent_display.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        # Prevent manual creation of activity logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Make activity logs read-only
        return False


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(EnhancedModelAdmin, LinkMixin):
    """Admin for Organization Membership"""
    
    list_display = ['link_to_user', 'link_to_organization', 'role', 
                    'department', 'is_admin', 'joined_at']
    list_filter = ['is_admin', 'organization', 'role', 'department', 
                   ('joined_at', DateRangeFilter)]
    search_fields = ['user__username', 'user__email', 'organization__name']
    autocomplete_fields = ['user', 'organization', 'role', 'department']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optimize queries with select_related
        return qs.select_related('user', 'organization', 'role', 'department')


@admin.register(UserSecurityProfile)
class UserSecurityProfileAdmin(EnhancedModelAdmin):
    """Admin for User Security Profile"""
    
    list_display = ['user', 'two_factor_enabled', 'backup_codes_generated', 
                    'failed_login_attempts', 'account_locked_until', 'last_password_change']
    list_filter = ['two_factor_enabled', 'backup_codes_generated', 
                   ('last_password_change', DateRangeFilter)]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['recovery_codes_used', 'security_questions_set', 
                      'last_security_audit']
    
    actions = ['unlock_accounts', 'reset_2fa', 'force_password_reset']
    
    def unlock_accounts(self, request, queryset):
        count = queryset.update(
            account_locked_until=None,
            failed_login_attempts=0
        )
        self.message_user(request, f'Unlocked {count} accounts.')
    unlock_accounts.short_description = 'Unlock selected accounts'
    
    def reset_2fa(self, request, queryset):
        count = queryset.update(
            two_factor_enabled=False,
            two_factor_method=None
        )
        self.message_user(request, f'Reset 2FA for {count} accounts.')
    reset_2fa.short_description = 'Reset 2FA for selected users'