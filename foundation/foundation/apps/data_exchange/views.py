"""Views for data exchange."""
from rest_framework import viewsets, permissions
from .models import ImportJob, ExportJob
from .serializers import ImportJobSerializer, ExportJobSerializer

class ImportJobViewSet(viewsets.ModelViewSet):
    serializer_class = ImportJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return ImportJob.objects.filter(organization_id__in=org_ids)

class ExportJobViewSet(viewsets.ModelViewSet):
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return ExportJob.objects.filter(organization_id__in=org_ids)
