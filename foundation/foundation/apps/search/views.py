"""Views for search."""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import SearchIndex, SearchQuery, SavedSearch
from .serializers import SearchIndexSerializer, SavedSearchSerializer


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def query(self, request):
        """Perform a search query."""
        q = request.query_params.get('q', '')
        user = request.user
        org_ids = user.organization_memberships.values_list('organization_id', flat=True)

        results = SearchIndex.objects.filter(
            Q(title__icontains=q) | Q(content__icontains=q),
            organization_id__in=org_ids
        )[:50]

        # Log search query
        SearchQuery.objects.create(
            user=user,
            query=q,
            results_count=results.count()
        )

        serializer = SearchIndexSerializer(results, many=True)
        return Response(serializer.data)


class SavedSearchViewSet(viewsets.ModelViewSet):
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
