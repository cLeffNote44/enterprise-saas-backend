from django.contrib import admin
from .models import Language, Translation, UserLanguagePreference

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'is_rtl']

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ['key', 'language', 'context']
    list_filter = ['language']
    search_fields = ['key', 'value']

@admin.register(UserLanguagePreference)
class UserLanguagePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'timezone']
