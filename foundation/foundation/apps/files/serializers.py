"""Serializers for files."""
from rest_framework import serializers
from .models import File, FileVersion, FileShare

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'name', 'file', 'size_bytes', 'mime_type', 'is_safe', 'thumbnail', 'created_at']
        read_only_fields = ['id', 'size_bytes', 'mime_type', 'is_safe', 'created_at']

class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = ['id', 'version_number', 'size_bytes', 'uploaded_by', 'created_at']

class FileShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileShare
        fields = ['id', 'file', 'shared_with_user', 'permission', 'expires_at', 'created_at']
