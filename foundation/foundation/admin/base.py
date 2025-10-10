"""
Base admin mixins and utilities for Foundation admin
"""
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q, Sum, Avg
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
import json


class TimeStampedAdmin(admin.ModelAdmin):
    """Mixin for models with created/updated timestamps"""
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        readonly.extend(['created_at', 'updated_at'])
        return readonly
    
    def created_date(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    created_date.short_description = 'Created'
    created_date.admin_order_field = 'created_at'
    
    def updated_date(self, obj):
        if obj.updated_at:
            return obj.updated_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    updated_date.short_description = 'Updated'
    updated_date.admin_order_field = 'updated_at'


class StatusColorMixin:
    """Mixin to add color coding to status fields"""
    
    def colored_status(self, obj):
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'expired': 'gray',
            'success': 'green',
            'failed': 'red',
            'warning': 'orange',
        }
        status = getattr(obj, 'status', None)
        if not status:
            return '-'
        
        color = colors.get(status.lower(), 'blue')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status.upper()
        )
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'


class OrganizationScopedAdmin(admin.ModelAdmin):
    """Mixin to scope queryset by organization for multi-tenant models"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # Filter by user's organizations
        if hasattr(request.user, 'organization_memberships'):
            org_ids = request.user.organization_memberships.values_list('organization_id', flat=True)
            return qs.filter(organization_id__in=org_ids)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit organization choices to user's organizations"""
        if db_field.name == 'organization' and not request.user.is_superuser:
            if hasattr(request.user, 'organization_memberships'):
                org_ids = request.user.organization_memberships.values_list('organization_id', flat=True)
                kwargs['queryset'] = db_field.related_model.objects.filter(id__in=org_ids)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BulkActionMixin:
    """Mixin for bulk admin actions"""
    
    def bulk_activate(self, request, queryset):
        """Activate selected items"""
        count = queryset.update(is_active=True, updated_at=timezone.now())
        self.message_user(request, f'Successfully activated {count} items.')
    bulk_activate.short_description = 'Activate selected items'
    
    def bulk_deactivate(self, request, queryset):
        """Deactivate selected items"""
        count = queryset.update(is_active=False, updated_at=timezone.now())
        self.message_user(request, f'Successfully deactivated {count} items.')
    bulk_deactivate.short_description = 'Deactivate selected items'
    
    def bulk_approve(self, request, queryset):
        """Approve selected items"""
        count = queryset.update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user,
            updated_at=timezone.now()
        )
        self.message_user(request, f'Successfully approved {count} items.')
    bulk_approve.short_description = 'Approve selected items'
    
    def bulk_reject(self, request, queryset):
        """Reject selected items"""
        count = queryset.update(
            status='rejected',
            rejected_at=timezone.now(),
            rejected_by=request.user,
            updated_at=timezone.now()
        )
        self.message_user(request, f'Successfully rejected {count} items.')
    bulk_reject.short_description = 'Reject selected items'


class ReadOnlyInlineMixin:
    """Mixin to make inline admin read-only"""
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class StatsMixin:
    """Mixin to add statistics to admin change list"""
    
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        # Calculate metrics
        metrics = {
            'total': qs.count(),
        }
        
        # Add status counts if model has status field
        if hasattr(self.model, 'status'):
            status_counts = qs.values('status').annotate(count=Count('status'))
            metrics['status_breakdown'] = {item['status']: item['count'] for item in status_counts}
        
        # Add active/inactive counts if model has is_active field
        if hasattr(self.model, 'is_active'):
            metrics['active'] = qs.filter(is_active=True).count()
            metrics['inactive'] = qs.filter(is_active=False).count()
        
        # Add date-based metrics if model has created_at
        if hasattr(self.model, 'created_at'):
            today = timezone.now().date()
            metrics['created_today'] = qs.filter(created_at__date=today).count()
            metrics['created_this_week'] = qs.filter(
                created_at__date__gte=today - timezone.timedelta(days=7)
            ).count()
            metrics['created_this_month'] = qs.filter(
                created_at__date__gte=today - timezone.timedelta(days=30)
            ).count()
        
        response.context_data['summary'] = metrics
        return response


class EnhancedModelAdmin(ImportExportModelAdmin, TimeStampedAdmin, StatusColorMixin, BulkActionMixin, StatsMixin):
    """Enhanced base admin class with all features"""
    
    # Enable change list stats by default
    change_list_template = 'admin/change_list_with_stats.html'
    
    # Common configurations
    list_per_page = 25
    list_max_show_all = 500
    show_full_result_count = True
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Add bulk actions based on model fields
        if hasattr(self.model, 'is_active'):
            actions['bulk_activate'] = (self.bulk_activate, 'bulk_activate', self.bulk_activate.short_description)
            actions['bulk_deactivate'] = (self.bulk_deactivate, 'bulk_deactivate', self.bulk_deactivate.short_description)
        
        if hasattr(self.model, 'status'):
            if 'approved' in [choice[0] for choice in getattr(self.model, 'STATUS_CHOICES', [])]:
                actions['bulk_approve'] = (self.bulk_approve, 'bulk_approve', self.bulk_approve.short_description)
            if 'rejected' in [choice[0] for choice in getattr(self.model, 'STATUS_CHOICES', [])]:
                actions['bulk_reject'] = (self.bulk_reject, 'bulk_reject', self.bulk_reject.short_description)
        
        return actions
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        
        # Add common fields if they exist
        if hasattr(self.model, 'created_at') and 'created_date' not in list_display:
            list_display.append('created_date')
        
        if hasattr(self.model, 'status') and 'colored_status' not in list_display:
            list_display.append('colored_status')
        
        return list_display
    
    def get_list_filter(self, request):
        list_filter = list(super().get_list_filter(request))
        
        # Add common filters if fields exist
        if hasattr(self.model, 'is_active') and 'is_active' not in list_filter:
            list_filter.append('is_active')
        
        if hasattr(self.model, 'status') and 'status' not in list_filter:
            list_filter.append('status')
        
        if hasattr(self.model, 'created_at'):
            list_filter.append(('created_at', DateRangeFilter))
        
        if hasattr(self.model, 'updated_at'):
            list_filter.append(('updated_at', DateRangeFilter))
        
        return list_filter


class LinkMixin:
    """Mixin to add clickable links to related objects"""
    
    def link_to_object(self, obj, field_name, display_text=None):
        """Create a link to a related object"""
        related_obj = getattr(obj, field_name, None)
        if not related_obj:
            return '-'
        
        app_label = related_obj._meta.app_label
        model_name = related_obj._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[related_obj.pk])
        
        text = display_text or str(related_obj)
        return format_html('<a href="{}">{}</a>', url, text)
    
    def link_to_user(self, obj):
        """Create a link to the user"""
        return self.link_to_object(obj, 'user')
    link_to_user.short_description = 'User'
    
    def link_to_organization(self, obj):
        """Create a link to the organization"""
        return self.link_to_object(obj, 'organization')
    link_to_organization.short_description = 'Organization'