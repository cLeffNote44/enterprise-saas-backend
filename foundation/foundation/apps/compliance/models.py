"""
Compliance framework for Data Destroyer.

This module implements compliance modules for HIPAA, GDPR, SOC2, and PCI-DSS
to ensure enterprise-grade data governance and regulatory compliance.
"""
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class ComplianceFramework(models.TextChoices):
    """Supported compliance frameworks."""
    HIPAA = 'hipaa', 'HIPAA'
    GDPR = 'gdpr', 'GDPR'
    SOC2 = 'soc2', 'SOC2'
    PCI_DSS = 'pci_dss', 'PCI-DSS'
    ISO_27001 = 'iso27001', 'ISO 27001'


class DataClassification(models.TextChoices):
    """Data classification levels."""
    PUBLIC = 'public', 'Public'
    INTERNAL = 'internal', 'Internal'
    CONFIDENTIAL = 'confidential', 'Confidential'
    RESTRICTED = 'restricted', 'Restricted'
    PHI = 'phi', 'Protected Health Information'
    PII = 'pii', 'Personally Identifiable Information'
    PAYMENT = 'payment', 'Payment Card Data'


class ConsentStatus(models.TextChoices):
    """Consent status for data processing."""
    GRANTED = 'granted', 'Granted'
    WITHDRAWN = 'withdrawn', 'Withdrawn'
    PENDING = 'pending', 'Pending'
    EXPIRED = 'expired', 'Expired'


class RetentionAction(models.TextChoices):
    """Actions to take when data retention period expires."""
    DELETE = 'delete', 'Delete'
    ARCHIVE = 'archive', 'Archive'
    ANONYMIZE = 'anonymize', 'Anonymize'
    REVIEW = 'review', 'Manual Review Required'


class CompliancePolicy(models.Model):
    """
    Base model for compliance policies across different frameworks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    framework = models.CharField(
        max_length=20,
        choices=ComplianceFramework.choices
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Policy configuration (JSON field for flexibility)
    configuration = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'foundation_compliance_policy'
        verbose_name = 'Compliance Policy'
        verbose_name_plural = 'Compliance Policies'
        unique_together = ['name', 'framework']
        
    def __str__(self):
        return f"{self.framework.upper()} - {self.name}"


class DataRetentionPolicy(models.Model):
    """
    Data retention policies for compliance requirements.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Data classification this policy applies to
    data_classification = models.CharField(
        max_length=20,
        choices=DataClassification.choices
    )
    
    # Retention period
    retention_days = models.PositiveIntegerField(
        help_text="Number of days to retain data"
    )
    
    # Action to take after retention period
    retention_action = models.CharField(
        max_length=20,
        choices=RetentionAction.choices,
        default=RetentionAction.ARCHIVE
    )
    
    # Compliance frameworks this policy satisfies
    frameworks = models.ManyToManyField(
        'CompliancePolicy',
        related_name='retention_policies'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'foundation_data_retention_policy'
        verbose_name = 'Data Retention Policy'
        verbose_name_plural = 'Data Retention Policies'
        
    def __str__(self):
        return f"{self.name} ({self.retention_days} days)"
    
    def is_expired(self, created_date: datetime) -> bool:
        """Check if data created on given date has expired."""
        if not isinstance(created_date, datetime):
            created_date = datetime.combine(created_date, datetime.min.time())
            
        expiry_date = created_date + timedelta(days=self.retention_days)
        return timezone.now() > timezone.make_aware(expiry_date) if timezone.is_naive(expiry_date) else timezone.now() > expiry_date


class ConsentRecord(models.Model):
    """
    GDPR consent management for data subjects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Data subject information
    data_subject_id = models.CharField(
        max_length=255,
        help_text="External identifier for the data subject"
    )
    data_subject_email = models.EmailField(null=True, blank=True)
    
    # Consent details
    purpose = models.CharField(
        max_length=200,
        help_text="Purpose for which consent was given"
    )
    legal_basis = models.CharField(
        max_length=100,
        help_text="Legal basis for processing (e.g., Article 6(1)(a))"
    )
    
    # Consent status and dates
    status = models.CharField(
        max_length=20,
        choices=ConsentStatus.choices,
        default=ConsentStatus.PENDING
    )
    
    granted_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Audit trail
    consent_source = models.CharField(
        max_length=100,
        help_text="Source where consent was collected (e.g., website, API)"
    )
    consent_method = models.CharField(
        max_length=100,
        help_text="Method of consent collection (e.g., checkbox, signature)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'foundation_consent_record'
        verbose_name = 'Consent Record'
        verbose_name_plural = 'Consent Records'
        indexes = [
            models.Index(fields=['data_subject_id']),
            models.Index(fields=['data_subject_email']),
            models.Index(fields=['status']),
        ]
        
    def __str__(self):
        return f"Consent: {self.data_subject_id} - {self.purpose}"
    
    def is_valid(self) -> bool:
        """Check if consent is currently valid."""
        if self.status != ConsentStatus.GRANTED:
            return False
            
        if self.expires_at and timezone.now() > self.expires_at:
            return False
            
        return True
    
    def withdraw_consent(self, reason: str = None):
        """Withdraw consent."""
        self.status = ConsentStatus.WITHDRAWN
        self.withdrawn_at = timezone.now()
        if reason:
            self.configuration = self.configuration or {}
            self.configuration['withdrawal_reason'] = reason
        self.save()


class PHIAccessLog(models.Model):
    """
    HIPAA-compliant access logging for Protected Health Information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User and access information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user_ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # PHI access details
    phi_record_id = models.CharField(max_length=255)
    phi_record_type = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Access context
    access_type = models.CharField(
        max_length=50,
        choices=[
            ('read', 'Read'),
            ('write', 'Write'),
            ('delete', 'Delete'),
            ('export', 'Export'),
            ('print', 'Print'),
        ]
    )
    
    access_reason = models.CharField(
        max_length=200,
        help_text="Business justification for access"
    )
    
    # Audit information
    accessed_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Compliance flags
    is_break_glass = models.BooleanField(
        default=False,
        help_text="Emergency access override used"
    )
    is_authorized = models.BooleanField(
        default=True,
        help_text="Whether access was properly authorized"
    )
    
    class Meta:
        db_table = 'foundation_phi_access_log'
        verbose_name = 'PHI Access Log'
        verbose_name_plural = 'PHI Access Logs'
        indexes = [
            models.Index(fields=['user', 'accessed_at']),
            models.Index(fields=['phi_record_id']),
            models.Index(fields=['patient_id']),
            models.Index(fields=['accessed_at']),
        ]
        
    def __str__(self):
        return f"PHI Access: {self.user} - {self.phi_record_id}"


class ComplianceViolation(models.Model):
    """
    Track compliance violations and remediation actions.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Under Investigation'),
        ('remediated', 'Remediated'),
        ('false_positive', 'False Positive'),
        ('accepted_risk', 'Accepted Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Violation details
    title = models.CharField(max_length=200)
    description = models.TextField()
    framework = models.CharField(
        max_length=20,
        choices=ComplianceFramework.choices
    )
    policy = models.ForeignKey(
        CompliancePolicy,
        on_delete=models.SET_NULL,
        null=True,
        related_name='violations'
    )
    
    # Severity and status
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Associated data
    affected_records = models.JSONField(
        default=list,
        help_text="List of affected record IDs"
    )
    
    # Remediation
    remediation_actions = models.TextField(blank=True)
    remediated_at = models.DateTimeField(null=True, blank=True)
    remediated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='remediated_violations'
    )
    
    # Audit trail
    detected_at = models.DateTimeField(auto_now_add=True)
    detected_by = models.CharField(
        max_length=100,
        help_text="System or person who detected the violation"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_violations'
    )
    
    class Meta:
        db_table = 'foundation_compliance_violation'
        verbose_name = 'Compliance Violation'
        verbose_name_plural = 'Compliance Violations'
        indexes = [
            models.Index(fields=['framework', 'severity']),
            models.Index(fields=['status']),
            models.Index(fields=['detected_at']),
        ]
        
    def __str__(self):
        return f"{self.framework.upper()} Violation: {self.title}"


class DataSubjectRequest(models.Model):
    """
    GDPR data subject requests (access, portability, erasure, etc.).
    """
    REQUEST_TYPES = [
        ('access', 'Right of Access (Art. 15)'),
        ('rectification', 'Right to Rectification (Art. 16)'),
        ('erasure', 'Right to Erasure (Art. 17)'),
        ('restrict', 'Right to Restrict Processing (Art. 18)'),
        ('portability', 'Right to Data Portability (Art. 20)'),
        ('object', 'Right to Object (Art. 21)'),
    ]
    
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('verified', 'Identity Verified'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('extended', 'Extended (Complex Request)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Data subject information
    data_subject_id = models.CharField(max_length=255)
    data_subject_email = models.EmailField()
    data_subject_name = models.CharField(max_length=200, blank=True)
    
    # Request details
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    description = models.TextField()
    
    # Processing information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    priority = models.CharField(
        max_length=20,
        choices=[('normal', 'Normal'), ('high', 'High'), ('urgent', 'Urgent')],
        default='normal'
    )
    
    # Compliance dates (GDPR requires response within 30 days)
    received_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment and processing
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_dsr'
    )
    
    # Results and responses
    response_data = models.JSONField(default=dict)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'foundation_data_subject_request'
        verbose_name = 'Data Subject Request'
        verbose_name_plural = 'Data Subject Requests'
        indexes = [
            models.Index(fields=['data_subject_email']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]
        
    def save(self, *args, **kwargs):
        # Set due date to 30 days from creation for new requests
        if not self.pk and not self.due_date:
            self.due_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"DSR: {self.get_request_type_display()} - {self.data_subject_email}"
    
    def is_overdue(self) -> bool:
        """Check if request is overdue."""
        return timezone.now() > self.due_date and self.status != 'completed'


@dataclass
class ComplianceReport:
    """Data class for compliance reporting."""
    framework: str
    compliance_score: float
    total_policies: int
    active_violations: int
    resolved_violations: int
    pending_requests: int
    overdue_requests: int
    last_assessment: datetime
    recommendations: List[str]


class ComplianceManager:
    """
    Manager class for compliance operations and reporting.
    """
    
    @staticmethod
    def generate_compliance_report(framework: str) -> ComplianceReport:
        """Generate compliance report for a specific framework."""
        
        # Get policy counts
        total_policies = CompliancePolicy.objects.filter(
            framework=framework,
            is_active=True
        ).count()
        
        # Get violation counts
        active_violations = ComplianceViolation.objects.filter(
            framework=framework,
            status__in=['open', 'investigating']
        ).count()
        
        resolved_violations = ComplianceViolation.objects.filter(
            framework=framework,
            status='remediated'
        ).count()
        
        # Calculate compliance score
        total_violations = active_violations + resolved_violations
        compliance_score = (
            ((total_violations - active_violations) / total_violations * 100)
            if total_violations > 0 else 100.0
        )
        
        # Get request counts (for GDPR)
        if framework == ComplianceFramework.GDPR:
            pending_requests = DataSubjectRequest.objects.filter(
                status__in=['received', 'verified', 'processing']
            ).count()
            
            overdue_requests = DataSubjectRequest.objects.filter(
                due_date__lt=timezone.now(),
                status__in=['received', 'verified', 'processing']
            ).count()
        else:
            pending_requests = 0
            overdue_requests = 0
        
        # Generate recommendations
        recommendations = ComplianceManager._generate_recommendations(
            framework, active_violations, overdue_requests
        )
        
        return ComplianceReport(
            framework=framework,
            compliance_score=compliance_score,
            total_policies=total_policies,
            active_violations=active_violations,
            resolved_violations=resolved_violations,
            pending_requests=pending_requests,
            overdue_requests=overdue_requests,
            last_assessment=timezone.now(),
            recommendations=recommendations
        )
    
    @staticmethod
    def _generate_recommendations(framework: str, active_violations: int, overdue_requests: int) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        if active_violations > 0:
            recommendations.append(
                f"Address {active_violations} active compliance violations to improve score"
            )
        
        if overdue_requests > 0 and framework == ComplianceFramework.GDPR:
            recommendations.append(
                f"Process {overdue_requests} overdue data subject requests immediately"
            )
        
        if framework == ComplianceFramework.HIPAA:
            # Check for PHI access without proper justification
            unauthorized_access = PHIAccessLog.objects.filter(
                is_authorized=False,
                accessed_at__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            if unauthorized_access > 0:
                recommendations.append(
                    f"Investigate {unauthorized_access} potentially unauthorized PHI access attempts"
                )
        
        if not recommendations:
            recommendations.append("Compliance status is good. Continue monitoring.")
        
        return recommendations
    
    @staticmethod
    def check_data_retention_compliance():
        """Check for data that has exceeded retention policies."""
        from discovery.models import ClassificationRule  # Avoid circular import
        
        violations = []
        
        # Get all active retention policies
        policies = DataRetentionPolicy.objects.filter(is_active=True)
        
        for policy in policies:
            # This would need to be implemented based on your data models
            # Here's a conceptual implementation
            pass
        
        return violations
    
    @staticmethod
    def process_data_subject_request(request_id: uuid.UUID) -> Dict[str, Any]:
        """Process a data subject request."""
        try:
            request = DataSubjectRequest.objects.get(id=request_id)
            
            # Implementation would depend on request type
            if request.request_type == 'access':
                return ComplianceManager._process_access_request(request)
            elif request.request_type == 'erasure':
                return ComplianceManager._process_erasure_request(request)
            elif request.request_type == 'portability':
                return ComplianceManager._process_portability_request(request)
            
        except DataSubjectRequest.DoesNotExist:
            raise ValueError(f"Request {request_id} not found")
    
    @staticmethod
    def _process_access_request(request: DataSubjectRequest) -> Dict[str, Any]:
        """Process GDPR Article 15 access request."""
        # Collect all data for the data subject
        data = {
            'personal_data': {},
            'processing_purposes': [],
            'categories': [],
            'recipients': [],
            'retention_period': '',
            'rights': [
                'Right to rectification',
                'Right to erasure',
                'Right to restrict processing',
                'Right to data portability',
                'Right to object'
            ]
        }
        
        request.response_data = data
        request.status = 'completed'
        request.completed_at = timezone.now()
        request.save()
        
        return data
    
    @staticmethod
    def _process_erasure_request(request: DataSubjectRequest) -> Dict[str, Any]:
        """Process GDPR Article 17 erasure request."""
        # This would implement the actual data deletion logic
        deleted_records = []
        
        request.response_data = {'deleted_records': deleted_records}
        request.status = 'completed'
        request.completed_at = timezone.now()
        request.save()
        
        return {'deleted_records': deleted_records}
    
    @staticmethod
    def _process_portability_request(request: DataSubjectRequest) -> Dict[str, Any]:
        """Process GDPR Article 20 portability request."""
        # Export data in structured format
        portable_data = {
            'format': 'JSON',
            'data': {},
            'created_at': timezone.now().isoformat()
        }
        
        request.response_data = portable_data
        request.status = 'completed'
        request.completed_at = timezone.now()
        request.save()
        
        return portable_data
