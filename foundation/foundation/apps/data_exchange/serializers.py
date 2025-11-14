"""Serializers for data exchange."""
from rest_framework import serializers
from .models import ImportJob, ExportJob

class ImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportJob
        fields = ['id', 'source_file', 'file_type', 'target_model', 'status',
                  'total_rows', 'success_count', 'error_count', 'created_at']
        read_only_fields = ['id', 'status', 'total_rows', 'success_count', 'error_count']

class ExportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportJob
        fields = ['id', 'source_model', 'format', 'filters', 'fields', 'status',
                  'total_records', 'download_url', 'expires_at', 'created_at']
        read_only_fields = ['id', 'status', 'total_records', 'download_url']
