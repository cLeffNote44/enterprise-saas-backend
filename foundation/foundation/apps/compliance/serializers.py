"""
Serializers for compliance models.
"""
from rest_framework import serializers
from .models import (
    CompliancePolicy, DataRetentionPolicy, ConsentRecord, PHIAccessLog,
    ComplianceViolation, DataSubjectRequest
)


class CompliancePolicySerializer(serializers.ModelSerializer):
    """Serializer for compliance policies."""
    class Meta:
        model = CompliancePolicy
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    """Serializer for data retention policies."""
    class Meta:
        model = DataRetentionPolicy
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class ConsentRecordSerializer(serializers.ModelSerializer):
    """Serializer for consent records."""
    class Meta:
        model = ConsentRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PHIAccessLogSerializer(serializers.ModelSerializer):
    """Serializer for PHI access logs."""
    class Meta:
        model = PHIAccessLog
        fields = '__all__'
        read_only_fields = ['accessed_at']


class ComplianceViolationSerializer(serializers.ModelSerializer):
    """Serializer for compliance violations."""
    class Meta:
        model = ComplianceViolation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reported_at']


class DataSubjectRequestSerializer(serializers.ModelSerializer):
    """Serializer for data subject requests."""
    class Meta:
        model = DataSubjectRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'submitted_at']


class ComplianceReportSerializer(serializers.Serializer):
    """Serializer for compliance reports."""
    framework = serializers.CharField()
    framework_name = serializers.CharField()
    compliance_score = serializers.FloatField()
    total_policies = serializers.IntegerField()
    active_violations = serializers.IntegerField()
    resolved_violations = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    overdue_requests = serializers.IntegerField()
    last_assessment = serializers.DateTimeField()
    recommendations = serializers.ListField(child=serializers.CharField())