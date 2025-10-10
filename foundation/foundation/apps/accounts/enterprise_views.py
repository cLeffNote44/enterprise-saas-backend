"""
API views for enterprise features including multi-tenancy and RBAC.
"""
from typing import Dict, Any
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView

from .enterprise import (
    Organization, Department, Role, RolePermission,
    OrganizationMembership, DataAccessPolicy,
    EnterpriseManager, SubscriptionTier
)
from .enterprise_serializers import (
    OrganizationSerializer, OrganizationCreateSerializer,
    DepartmentSerializer, RoleSerializer, OrganizationMembershipSerializer,
    DataAccessPolicySerializer, InviteUserSerializer,
    OrganizationStatsSerializer, UserOrganizationSerializer,
    BulkRoleAssignmentSerializer, AccessEvaluationSerializer,
    FeatureFlagUpdateSerializer, UsageLimitUpdateSerializer,
    PermissionSerializer
)
from .permissions import IsOrganizationAdmin, IsOrganizationMember

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for enterprise API views."""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrganizationViewSet(ModelViewSet):
    """
    ViewSet for managing organizations.
    Only organization admins can manage organization settings.
    """
    queryset = Organization.objects.all()
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOrganizationAdmin]
        else:
            permission_classes = [IsOrganizationMember]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter organizations based on user membership."""
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        
        return Organization.objects.filter(
            memberships__user=user,
            memberships__status='active'
        ).distinct()
    
    def perform_create(self, serializer):
        """Create organization with current user as admin."""
        organization = serializer.save(created_by=self.request.user)
        
        # Create organization membership for creator
        membership = OrganizationMembership.objects.create(
            user=self.request.user,
            organization=organization,
            is_admin=True,
            status='active',
            joined_at=timezone.now(),
            can_invite_users=True,
            can_manage_roles=True,
            can_access_billing=True
        )
        
        # Assign admin role
        admin_role = organization.roles.get(name='Admin')
        membership.roles.add(admin_role)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, slug=None):
        """Get organization statistics."""
        organization = self.get_object()
        
        # Calculate statistics
        memberships = organization.memberships.all()
        stats = {
            'total_members': memberships.count(),
            'active_members': memberships.filter(status='active').count(),
            'invited_members': memberships.filter(status='invited').count(),
            'total_departments': organization.departments.filter(is_active=True).count(),
            'total_roles': organization.roles.filter(is_active=True).count(),
            'total_policies': organization.data_access_policies.filter(is_active=True).count(),
            'subscription_tier': organization.subscription_tier,
            'subscription_status': organization.status,
            'trial_days_remaining': self._get_trial_days_remaining(organization),
            'feature_usage': self._get_feature_usage(organization),
            'compliance_frameworks': organization.compliance_frameworks,
        }
        
        serializer = OrganizationStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_features(self, request, slug=None):
        """Update organization feature flags."""
        organization = self.get_object()
        serializer = FeatureFlagUpdateSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if serializer.is_valid():
            # Update feature flags
            organization.feature_flags.update(serializer.validated_data['feature_flags'])
            organization.save(update_fields=['feature_flags'])
            
            return Response({'status': 'Features updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_limits(self, request, slug=None):
        """Update organization usage limits."""
        organization = self.get_object()
        serializer = UsageLimitUpdateSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if serializer.is_valid():
            # Update usage limits
            organization.usage_limits.update(serializer.validated_data['usage_limits'])
            organization.save(update_fields=['usage_limits'])
            
            return Response({'status': 'Usage limits updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_trial_days_remaining(self, organization) -> int:
        """Calculate trial days remaining."""
        if not organization.trial_ends_at:
            return 0
        
        remaining = organization.trial_ends_at - timezone.now()
        return max(0, remaining.days)
    
    def _get_feature_usage(self, organization) -> Dict[str, Any]:
        """Get feature usage statistics."""
        # This would typically fetch actual usage metrics
        # For now, return basic counts
        return {
            'data_sources_used': 0,  # TODO: Implement actual counting
            'api_calls_this_month': 0,
            'storage_used_gb': 0,
            'last_activity': timezone.now().isoformat()
        }


class DepartmentViewSet(ModelViewSet):
    """ViewSet for managing departments within an organization."""
    serializer_class = DepartmentSerializer
    permission_classes = [IsOrganizationMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter departments by organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        # Check user has access to organization
        if not organization.memberships.filter(
            user=self.request.user,
            status='active'
        ).exists():
            return Department.objects.none()
        
        return organization.departments.filter(is_active=True)
    
    def perform_create(self, serializer):
        """Create department in specific organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        serializer.save(organization=organization)


class RoleViewSet(ModelViewSet):
    """ViewSet for managing roles within an organization."""
    serializer_class = RoleSerializer
    permission_classes = [IsOrganizationMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter roles by organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        # Check user has access to organization
        if not organization.memberships.filter(
            user=self.request.user,
            status='active'
        ).exists():
            return Role.objects.none()
        
        return organization.roles.filter(is_active=True)
    
    def perform_create(self, serializer):
        """Create role in specific organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        serializer.save(
            organization=organization,
            created_by=self.request.user
        )
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of system roles."""
        role = self.get_object()
        if role.is_system_role:
            return Response(
                {'error': 'System roles cannot be deleted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, organization_slug=None, pk=None):
        """Assign permissions to role."""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        # Validate permissions exist
        permissions = Permission.objects.filter(id__in=permission_ids)
        if len(permissions) != len(permission_ids):
            return Response(
                {'error': 'One or more permissions are invalid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clear existing permissions and add new ones
        with transaction.atomic():
            RolePermission.objects.filter(role=role).delete()
            for permission in permissions:
                role.add_permission(permission, request.user)
        
        return Response({'status': 'Permissions assigned successfully'})


class OrganizationMembershipViewSet(ModelViewSet):
    """ViewSet for managing organization memberships."""
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [IsOrganizationMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter memberships by organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        # Check user has access to organization
        if not organization.memberships.filter(
            user=self.request.user,
            status='active'
        ).exists():
            return OrganizationMembership.objects.none()
        
        return organization.memberships.all().select_related(
            'user', 'department', 'invited_by'
        ).prefetch_related('roles')
    
    @action(detail=False, methods=['post'])
    def invite(self, request, organization_slug=None):
        """Invite user to organization."""
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        # Check if user can invite others
        user_membership = organization.memberships.get(
            user=request.user,
            status='active'
        )
        if not (user_membership.is_admin or user_membership.can_invite_users):
            return Response(
                {'error': 'You do not have permission to invite users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = InviteUserSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if serializer.is_valid():
            # Get roles and department
            role_ids = serializer.validated_data.get('role_ids', [])
            roles = Role.objects.filter(
                id__in=role_ids,
                organization=organization,
                is_active=True
            ) if role_ids else []
            
            department_id = serializer.validated_data.get('department_id')
            department = Department.objects.get(
                id=department_id,
                organization=organization
            ) if department_id else None
            
            # Create invitation
            membership = EnterpriseManager.invite_user(
                organization=organization,
                email=serializer.validated_data['email'],
                invited_by=request.user,
                roles=list(roles),
                department=department
            )
            
            # Set additional permissions
            membership.can_invite_users = serializer.validated_data.get('can_invite_users', False)
            membership.can_manage_roles = serializer.validated_data.get('can_manage_roles', False)
            membership.can_access_billing = serializer.validated_data.get('can_access_billing', False)
            membership.save()
            
            response_serializer = OrganizationMembershipSerializer(membership)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, organization_slug=None, pk=None):
        """Activate membership (accept invitation)."""
        membership = self.get_object()
        
        # Only the invited user can activate their own membership
        if membership.user != request.user:
            return Response(
                {'error': 'You can only activate your own membership'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if membership.status != 'invited':
            return Response(
                {'error': 'Membership is not in invited status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.activate_membership()
        serializer = OrganizationMembershipSerializer(membership)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_assign_roles(self, request, organization_slug=None):
        """Bulk assign roles to multiple users."""
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        # Check permissions
        user_membership = organization.memberships.get(
            user=request.user,
            status='active'
        )
        if not (user_membership.is_admin or user_membership.can_manage_roles):
            return Response(
                {'error': 'You do not have permission to manage roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = BulkRoleAssignmentSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            role_ids = serializer.validated_data['role_ids']
            action = serializer.validated_data['action']
            
            # Get memberships and roles
            memberships = OrganizationMembership.objects.filter(
                id__in=user_ids,
                organization=organization,
                status='active'
            )
            roles = Role.objects.filter(
                id__in=role_ids,
                organization=organization,
                is_active=True
            )
            
            # Perform bulk assignment
            with transaction.atomic():
                for membership in memberships:
                    if action == 'add':
                        membership.roles.add(*roles)
                    elif action == 'remove':
                        membership.roles.remove(*roles)
                    elif action == 'replace':
                        membership.roles.set(roles)
            
            return Response({
                'status': f'Roles {action}ed successfully',
                'affected_users': len(memberships)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DataAccessPolicyViewSet(ModelViewSet):
    """ViewSet for managing data access policies."""
    serializer_class = DataAccessPolicySerializer
    permission_classes = [IsOrganizationAdmin]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter policies by organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        return organization.data_access_policies.filter(is_active=True)
    
    def perform_create(self, serializer):
        """Create policy in specific organization."""
        organization_slug = self.kwargs.get('organization_slug')
        organization = get_object_or_404(Organization, slug=organization_slug)
        serializer.save(
            organization=organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def evaluate(self, request, organization_slug=None, pk=None):
        """Evaluate policy against specific user and resource."""
        policy = self.get_object()
        serializer = AccessEvaluationSerializer(
            data=request.data,
            context={'organization': policy.organization}
        )
        
        if serializer.is_valid():
            resource = serializer.validated_data['resource']
            user_id = serializer.validated_data.get('user_id')
            context = serializer.validated_data.get('context', {})
            
            # Use current user if no user_id provided
            user = User.objects.get(id=user_id) if user_id else request.user
            
            # Evaluate policy
            result = policy.evaluate(user, resource, context)
            
            return Response({
                'resource': resource,
                'user': user.username,
                'access_granted': result,
                'policy': policy.name,
                'evaluated_at': timezone.now().isoformat()
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrganizationsView(APIView):
    """Get user's organization memberships."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all organizations for current user."""
        memberships = OrganizationMembership.objects.filter(
            user=request.user,
            status='active'
        ).select_related('organization').prefetch_related('roles')
        
        data = []
        for membership in memberships:
            data.append({
                'organization': OrganizationSerializer(membership.organization).data,
                'membership': OrganizationMembershipSerializer(membership).data
            })
        
        serializer = UserOrganizationSerializer(data, many=True)
        return Response(serializer.data)


class AccessEvaluationView(APIView):
    """Evaluate user access to resources."""
    permission_classes = [IsOrganizationMember]
    
    def post(self, request, organization_slug):
        """Evaluate access for organization member."""
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        serializer = AccessEvaluationSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if serializer.is_valid():
            resource = serializer.validated_data['resource']
            user_id = serializer.validated_data.get('user_id')
            context = serializer.validated_data.get('context', {})
            
            # Use current user if no user_id provided
            user = User.objects.get(id=user_id) if user_id else request.user
            
            # Add request context
            context.update({
                'request_time': timezone.now(),
                'user_ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
            })
            
            # Evaluate access using Enterprise Manager
            access_granted = EnterpriseManager.evaluate_data_access(
                user=user,
                organization=organization,
                resource=resource,
                context=context
            )
            
            return Response({
                'resource': resource,
                'user': user.username,
                'organization': organization.name,
                'access_granted': access_granted,
                'evaluated_at': timezone.now().isoformat(),
                'context': context
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PermissionListView(ReadOnlyModelViewSet):
    """List available permissions for role assignment."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsOrganizationMember]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter permissions by search query."""
        queryset = Permission.objects.all()
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(codename__icontains=search)
            )
        
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type__model=content_type)
        
        return queryset.order_by('content_type__model', 'codename')


class OrganizationSwitchView(APIView):
    """Switch user's current organization context."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Switch to specified organization."""
        organization_slug = request.data.get('organization_slug')
        
        if not organization_slug:
            return Response(
                {'error': 'organization_slug is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            organization = Organization.objects.get(slug=organization_slug)
            membership = OrganizationMembership.objects.get(
                user=request.user,
                organization=organization,
                status='active'
            )
        except (Organization.DoesNotExist, OrganizationMembership.DoesNotExist):
            return Response(
                {'error': 'Organization not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Record access
        membership.record_access()
        
        # Set session variable for current organization
        request.session['current_organization'] = str(organization.id)
        
        return Response({
            'organization': OrganizationSerializer(organization).data,
            'membership': OrganizationMembershipSerializer(membership).data,
            'switched_at': timezone.now().isoformat()
        })


class OrganizationActivityView(APIView):
    """Get organization activity and audit logs."""
    permission_classes = [IsOrganizationAdmin]
    
    def get(self, request, organization_slug):
        """Get recent activity for organization."""
        organization = get_object_or_404(Organization, slug=organization_slug)
        
        # Get recent memberships
        recent_memberships = organization.memberships.filter(
            joined_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('user', 'invited_by').order_by('-joined_at')[:10]
        
        # Get recent role changes (simplified)
        recent_roles = organization.roles.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:10]
        
        # Get recent policy changes
        recent_policies = organization.data_access_policies.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:10]
        
        activity = {
            'recent_members': OrganizationMembershipSerializer(
                recent_memberships,
                many=True
            ).data,
            'recent_roles': RoleSerializer(recent_roles, many=True).data,
            'recent_policies': DataAccessPolicySerializer(
                recent_policies,
                many=True
            ).data,
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(activity)
