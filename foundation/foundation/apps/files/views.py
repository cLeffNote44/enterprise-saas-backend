"""Views for files."""
from rest_framework import viewsets, permissions
from .models import File, FileShare
from .serializers import FileSerializer, FileShareSerializer

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)
        return File.objects.filter(organization_id__in=org_ids)

class FileShareViewSet(viewsets.ModelViewSet):
    serializer_class = FileShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FileShare.objects.filter(shared_with_user=self.request.user)
