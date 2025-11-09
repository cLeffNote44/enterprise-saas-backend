"""Serializers for feature flags."""
from rest_framework import serializers
from .models import FeatureFlag, Experiment, ExperimentVariant, ExperimentEvent


class FeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureFlag
        fields = ['id', 'key', 'name', 'description', 'status', 'rollout_type',
                  'is_enabled', 'rollout_percentage', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExperimentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentVariant
        fields = ['id', 'name', 'key', 'description', 'traffic_allocation',
                  'configuration', 'is_active', 'is_control']
        read_only_fields = ['id']


class ExperimentSerializer(serializers.ModelSerializer):
    variants = ExperimentVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Experiment
        fields = ['id', 'name', 'key', 'description', 'status', 'hypothesis',
                  'success_metric', 'start_date', 'end_date', 'variants', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExperimentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentEvent
        fields = ['id', 'experiment', 'variant', 'event_type', 'event_value',
                  'metadata', 'timestamp']
        read_only_fields = ['id', 'timestamp']
