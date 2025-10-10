"""
Enterprise SaaS Foundation Admin
Enhanced admin interface with dashboards, bulk actions, and analytics
"""
from django.contrib import admin
from django.contrib.admin import AdminSite

class FoundationAdminSite(AdminSite):
    site_header = 'Foundation Admin'
    site_title = 'Foundation Admin Portal'
    index_title = 'Welcome to Enterprise SaaS Foundation'

# Create custom admin site instance
foundation_admin_site = FoundationAdminSite(name='foundation_admin')

# Import and register admin classes
from .accounts import *  # noqa
from .analytics import *  # noqa
from .compliance import *  # noqa
from .moderation import *  # noqa