#!/usr/bin/env python
"""
Script to set the admin password non-interactively
"""
import os
import sys
import django

# Add the foundation directory to the Python path
sys.path.insert(0, '/app/foundation')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foundation.config.settings.docker')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    print("Password for admin user set successfully to 'admin123'")
except User.DoesNotExist:
    print("Admin user does not exist. Please create it first.")
    sys.exit(1)