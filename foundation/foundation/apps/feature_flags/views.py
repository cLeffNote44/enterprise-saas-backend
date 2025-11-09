"""Views for feature flags."""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FeatureFlag, Experiment, ExperimentEvent
from .serializers import (
    FeatureFlagSerializer, ExperimentSerializer, ExperimentEventSerializer
)


class FeatureFlagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FeatureFlag.objects.filter(status='active')
    serializer_class = FeatureFlagSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_flags(self, request):
        """Get all flags enabled for current user."""
        user = request.user
        flags = {}

        for flag in self.get_queryset():
            flags[flag.key] = flag.is_enabled_for_user(user)

        return Response(flags)

    @action(detail=True, methods=['get'])
    def check(self, request, pk=None):
        """Check if flag is enabled for current user."""
        flag = self.get_object()
        is_enabled = flag.is_enabled_for_user(request.user)

        return Response({
            'key': flag.key,
            'is_enabled': is_enabled
        })


class ExperimentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Experiment.objects.filter(status='running')
    serializer_class = ExperimentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def variant(self, request, pk=None):
        """Get assigned variant for current user."""
        experiment = self.get_object()
        variant = experiment.get_variant_for_user(request.user)

        if not variant:
            return Response({'variant': None})

        return Response({
            'experiment': experiment.key,
            'variant': variant.key,
            'configuration': variant.configuration
        })

    @action(detail=True, methods=['post'])
    def track(self, request, pk=None):
        """Track an event for experiment analytics."""
        experiment = self.get_object()
        variant = experiment.get_variant_for_user(request.user)

        if not variant:
            return Response({'error': 'No variant assigned'}, status=400)

        event = ExperimentEvent.objects.create(
            experiment=experiment,
            variant=variant,
            user=request.user,
            event_type=request.data.get('event_type'),
            event_value=request.data.get('event_value'),
            metadata=request.data.get('metadata', {})
        )

        return Response(ExperimentEventSerializer(event).data)
