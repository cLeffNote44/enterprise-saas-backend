"""Admin for feature flags."""
from django.contrib import admin
from .models import (
    FeatureFlag, FeatureFlagAssignment, Experiment,
    ExperimentVariant, ExperimentAssignment, ExperimentEvent
)


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'status', 'rollout_type', 'is_enabled', 'rollout_percentage']
    list_filter = ['status', 'rollout_type']
    search_fields = ['name', 'key']
    filter_horizontal = ['depends_on']


@admin.register(FeatureFlagAssignment)
class FeatureFlagAssignmentAdmin(admin.ModelAdmin):
    list_display = ['flag', 'user', 'organization', 'is_enabled', 'created_at']
    list_filter = ['is_enabled']


class ExperimentVariantInline(admin.TabularInline):
    model = ExperimentVariant
    extra = 2


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'status', 'start_date', 'end_date', 'winner_variant']
    list_filter = ['status']
    search_fields = ['name', 'key']
    inlines = [ExperimentVariantInline]


@admin.register(ExperimentEvent)
class ExperimentEventAdmin(admin.ModelAdmin):
    list_display = ['experiment', 'variant', 'event_type', 'event_value', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    date_hierarchy = 'timestamp'
