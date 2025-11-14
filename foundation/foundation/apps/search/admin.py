"""Admin for search."""
from django.contrib import admin
from .models import SearchIndex, SearchQuery, SavedSearch

@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'organization', 'updated_at']
    list_filter = ['content_type']
    search_fields = ['title', 'content']

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'timestamp']
    search_fields = ['query']
    date_hierarchy = 'timestamp'

@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
