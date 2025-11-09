"""Serializers for search."""
from rest_framework import serializers
from .models import SearchIndex, SearchQuery, SavedSearch

class SearchIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchIndex
        fields = ['id', 'title', 'content', 'keywords', 'updated_at']

class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ['id', 'name', 'query', 'created_at']
