"""
Compliance API views for enterprise data governance and regulatory compliance.
"""
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import (
    CompliancePolicy, DataRetentionPolicy, ConsentRecord, PHIAccessLog,
    ComplianceViolation, DataSubjectRequest, ComplianceManager,
    ComplianceFramework, DataClassification, ConsentStatus
)
from .serializers import (
    CompliancePolicySerializer, DataRetentionPolicySerializer,
    ConsentRecordSerializer, PHIAccessLogSerializer,
    ComplianceViolationSerializer, DataSubjectRequestSerializer,
    ComplianceReportSerializer
)

User = get_user_model()


class ComplianceDashboardView(APIView):
    """
    Real-time compliance dashboard with overview metrics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: ComplianceReportSerializer(many=True)},
        summary="Get compliance dashboard overview",
        description="Get real-time compliance status across all frameworks"
    )
    def get(self, request):
        """Get compliance dashboard data."""
        # Generate reports for all frameworks
        reports = []
        
        for framework_code, framework_name in ComplianceFramework.choices:
            report = ComplianceManager.generate_compliance_report(framework_code)
            reports.append({
                'framework': framework_code,
                'framework_name': framework_name,
                'compliance_score': report.compliance_score,
                'total_policies': report.total_policies,
                'active_violations': report.active_violations,
                'resolved_violations': report.resolved_violations,
                'pending_requests': report.pending_requests,
                'overdue_requests': report.overdue_requests,
                'last_assessment': report.last_assessment,
                'recommendations': report.recommendations
            })
        
        # Add summary metrics
        summary = {
            'total_frameworks': len(reports),
            'average_compliance_score': sum(r['compliance_score'] for r in reports) / len(reports) if reports else 0,
            'total_violations': sum(r['active_violations'] for r in reports),
            'total_overdue_requests': sum(r['overdue_requests'] for r in reports),
            'frameworks_at_risk': len([r for r in reports if r['compliance_score'] < 80])
        }
        
        return Response({
            'summary': summary,
            'frameworks': reports,
            'generated_at': timezone.now()
        })


class CompliancePolicyViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for compliance policies.
    """
    queryset = CompliancePolicy.objects.all()
    serializer_class = CompliancePolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['framework', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'framework']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DataRetentionPolicyViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for data retention policies.
    """
    queryset = DataRetentionPolicy.objects.all()
    serializer_class = DataRetentionPolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['data_classification', 'retention_action', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'retention_days']
    
    @action(detail=False, methods=['post'])
    def check_compliance(self, request):
        """Check data retention compliance across all policies."""
        violations = ComplianceManager.check_data_retention_compliance()
        return Response({
            'violations_found': len(violations),
            'violations': violations,
            'checked_at': timezone.now()
        })


class ConsentRecordViewSet(viewsets.ModelViewSet):
    """
    GDPR consent management operations.
    """
    queryset = ConsentRecord.objects.all()
    serializer_class = ConsentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'data_subject_email']
    search_fields = ['data_subject_id', 'data_subject_email', 'purpose']
    ordering_fields = ['created_at', 'granted_at', 'expires_at']
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """Withdraw consent for a data subject."""
        consent = self.get_object()
        reason = request.data.get('reason', 'User requested withdrawal')
        
        consent.withdraw_consent(reason)
        
        return Response({
            'message': 'Consent withdrawn successfully',
            'withdrawn_at': consent.withdrawn_at,
            'reason': reason
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get consents expiring in the next 30 days."""
        thirty_days = timezone.now() + timezone.timedelta(days=30)
        expiring = ConsentRecord.objects.filter(
            expires_at__lte=thirty_days,
            status=ConsentStatus.GRANTED
        )
        
        serializer = self.get_serializer(expiring, many=True)
        return Response({
            'count': expiring.count(),
            'consents': serializer.data
        })


class PHIAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    HIPAA PHI access logs (read-only for audit purposes).
    """
    queryset = PHIAccessLog.objects.all()
    serializer_class = PHIAccessLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'access_type', 'is_break_glass', 'is_authorized']
    search_fields = ['phi_record_id', 'patient_id', 'access_reason']
    ordering_fields = ['accessed_at']
    
    @action(detail=False, methods=['get'])
    def unauthorized_access(self, request):
        """Get potentially unauthorized PHI access attempts."""
        unauthorized = PHIAccessLog.objects.filter(
            is_authorized=False,
            accessed_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-accessed_at')
        
        serializer = self.get_serializer(unauthorized, many=True)
        return Response({
            'count': unauthorized.count(),
            'unauthorized_access': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def break_glass_usage(self, request):
        """Get emergency break-glass access usage."""
        break_glass = PHIAccessLog.objects.filter(
            is_break_glass=True,
            accessed_at__gte=timezone.now() - timezone.timedelta(days=90)
        ).order_by('-accessed_at')
        
        serializer = self.get_serializer(break_glass, many=True)
        return Response({
            'count': break_glass.count(),
            'break_glass_access': serializer.data
        })


class ComplianceViolationViewSet(viewsets.ModelViewSet):
    """
    Compliance violation tracking and remediation.
    """
    queryset = ComplianceViolation.objects.all()
    serializer_class = ComplianceViolationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['framework', 'severity', 'status', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['detected_at', 'severity']
    
    @action(detail=True, methods=['post'])
    def remediate(self, request, pk=None):
        """Mark violation as remediated."""
        violation = self.get_object()
        remediation_actions = request.data.get('remediation_actions', '')
        
        violation.status = 'remediated'
        violation.remediated_at = timezone.now()
        violation.remediated_by = request.user
        violation.remediation_actions = remediation_actions
        violation.save()
        
        return Response({
            'message': 'Violation marked as remediated',
            'remediated_at': violation.remediated_at,
            'remediated_by': violation.remediated_by.username
        })
    
    @action(detail=False, methods=['get'])
    def critical_violations(self, request):
        """Get critical violations requiring immediate attention."""
        critical = ComplianceViolation.objects.filter(
            severity='critical',
            status__in=['open', 'investigating']
        ).order_by('-detected_at')
        
        serializer = self.get_serializer(critical, many=True)
        return Response({
            'count': critical.count(),
            'critical_violations': serializer.data
        })


class DataSubjectRequestViewSet(viewsets.ModelViewSet):
    """
    GDPR data subject request management.
    """
    queryset = DataSubjectRequest.objects.all()
    serializer_class = DataSubjectRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['request_type', 'status', 'priority', 'assigned_to']
    search_fields = ['data_subject_email', 'data_subject_name', 'description']
    ordering_fields = ['received_at', 'due_date', 'priority']
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign request to a user."""
        dsr = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        try:
            assigned_user = User.objects.get(id=assigned_to_id)
            dsr.assigned_to = assigned_user
            dsr.save()
            
            return Response({
                'message': f'Request assigned to {assigned_user.username}',
                'assigned_to': assigned_user.username
            })
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process the data subject request."""
        dsr = self.get_object()
        
        try:
            result = ComplianceManager.process_data_subject_request(dsr.id)
            return Response({
                'message': 'Request processed successfully',
                'result': result
            })
        except Exception as e:
            return Response({
                'error': f'Failed to process request: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue data subject requests."""
        overdue = DataSubjectRequest.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['received', 'verified', 'processing']
        ).order_by('due_date')
        
        serializer = self.get_serializer(overdue, many=True)
        return Response({
            'count': overdue.count(),
            'overdue_requests': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """Get requests due within the next 7 days."""
        seven_days = timezone.now() + timezone.timedelta(days=7)
        due_soon = DataSubjectRequest.objects.filter(
            due_date__lte=seven_days,
            status__in=['received', 'verified', 'processing']
        ).order_by('due_date')
        
        serializer = self.get_serializer(due_soon, many=True)
        return Response({
            'count': due_soon.count(),
            'due_soon': serializer.data
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_phi_access(request):
    """
    Log PHI access for HIPAA compliance.
    """
    required_fields = ['phi_record_id', 'phi_record_type', 'access_type', 'access_reason']
    
    for field in required_fields:
        if field not in request.data:
            return Response({
                'error': f'Missing required field: {field}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get client IP and user agent
    user_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or \
              request.META.get('REMOTE_ADDR', 'unknown')
    user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
    
    # Create PHI access log
    phi_log = PHIAccessLog.objects.create(
        user=request.user,
        user_ip=user_ip,
        user_agent=user_agent,
        phi_record_id=request.data['phi_record_id'],
        phi_record_type=request.data['phi_record_type'],
        patient_id=request.data.get('patient_id'),
        access_type=request.data['access_type'],
        access_reason=request.data['access_reason'],
        session_id=request.session.session_key,
        is_break_glass=request.data.get('is_break_glass', False),
        is_authorized=request.data.get('is_authorized', True)
    )
    
    return Response({
        'message': 'PHI access logged successfully',
        'log_id': str(phi_log.id),
        'accessed_at': phi_log.accessed_at
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_compliance_violation(request):
    """
    Create a new compliance violation record.
    """
    required_fields = ['title', 'description', 'framework', 'severity']
    
    for field in required_fields:
        if field not in request.data:
            return Response({
                'error': f'Missing required field: {field}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    violation = ComplianceViolation.objects.create(
        title=request.data['title'],
        description=request.data['description'],
        framework=request.data['framework'],
        severity=request.data['severity'],
        affected_records=request.data.get('affected_records', []),
        detected_by=f"API User: {request.user.username}"
    )
    
    return Response({
        'message': 'Compliance violation created successfully',
        'violation_id': str(violation.id),
        'detected_at': violation.detected_at
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def compliance_metrics(request):
    """
    Get high-level compliance metrics for executive dashboard.
    """
    # Framework-specific metrics
    framework_metrics = {}
    
    for framework_code, framework_name in ComplianceFramework.choices:
        violations = ComplianceViolation.objects.filter(framework=framework_code)
        
        framework_metrics[framework_code] = {
            'name': framework_name,
            'total_violations': violations.count(),
            'active_violations': violations.filter(status__in=['open', 'investigating']).count(),
            'critical_violations': violations.filter(severity='critical', status__in=['open', 'investigating']).count(),
            'policies': CompliancePolicy.objects.filter(framework=framework_code, is_active=True).count()
        }
    
    # GDPR-specific metrics
    gdpr_metrics = {
        'total_requests': DataSubjectRequest.objects.count(),
        'pending_requests': DataSubjectRequest.objects.filter(
            status__in=['received', 'verified', 'processing']
        ).count(),
        'overdue_requests': DataSubjectRequest.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['received', 'verified', 'processing']
        ).count(),
        'active_consents': ConsentRecord.objects.filter(status=ConsentStatus.GRANTED).count()
    }
    
    # HIPAA-specific metrics
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    hipaa_metrics = {
        'phi_access_count': PHIAccessLog.objects.filter(accessed_at__gte=thirty_days_ago).count(),
        'break_glass_usage': PHIAccessLog.objects.filter(
            is_break_glass=True,
            accessed_at__gte=thirty_days_ago
        ).count(),
        'unauthorized_access': PHIAccessLog.objects.filter(
            is_authorized=False,
            accessed_at__gte=thirty_days_ago
        ).count()
    }
    
    return Response({
        'framework_metrics': framework_metrics,
        'gdpr_metrics': gdpr_metrics,
        'hipaa_metrics': hipaa_metrics,
        'generated_at': timezone.now()
    })


class ComplianceReportsView(APIView):
    """
    Generate comprehensive compliance reports for all frameworks.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: ComplianceReportSerializer(many=True)},
        summary="Generate compliance reports",
        description="Generate detailed compliance reports for all enabled frameworks"
    )
    def get(self, request):
        """Generate compliance reports."""
        framework = request.query_params.get('framework')
        
        if framework:
            # Generate report for specific framework
            try:
                report = ComplianceManager.generate_compliance_report(framework)
                return Response({
                    'framework': framework,
                    'compliance_score': report.compliance_score,
                    'total_policies': report.total_policies,
                    'active_violations': report.active_violations,
                    'resolved_violations': report.resolved_violations,
                    'pending_requests': report.pending_requests,
                    'overdue_requests': report.overdue_requests,
                    'last_assessment': report.last_assessment,
                    'recommendations': report.recommendations
                })
            except Exception as e:
                return Response({
                    'error': f'Failed to generate report: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Generate reports for all frameworks
            reports = []
            for framework_code, framework_name in ComplianceFramework.choices:
                try:
                    report = ComplianceManager.generate_compliance_report(framework_code)
                    reports.append({
                        'framework': framework_code,
                        'framework_name': framework_name,
                        'compliance_score': report.compliance_score,
                        'total_policies': report.total_policies,
                        'active_violations': report.active_violations,
                        'resolved_violations': report.resolved_violations,
                        'pending_requests': report.pending_requests,
                        'overdue_requests': report.overdue_requests,
                        'last_assessment': report.last_assessment,
                        'recommendations': report.recommendations
                    })
                except Exception as e:
                    reports.append({
                        'framework': framework_code,
                        'framework_name': framework_name,
                        'error': f'Failed to generate report: {str(e)}'
                    })
            
            return Response({
                'reports': reports,
                'generated_at': timezone.now()
            })


class ComplianceMetricsView(APIView):
    """
    Get compliance metrics and KPIs for dashboards.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: dict},
        summary="Get compliance metrics",
        description="Get high-level compliance metrics and KPIs for dashboard display"
    )
    def get(self, request):
        """Get compliance metrics."""
        return compliance_metrics(request)
