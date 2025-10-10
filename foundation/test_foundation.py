#!/usr/bin/env python
"""
Basic test script to validate foundation functionality.
This tests core features without requiring full test setup.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foundation.config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.management import execute_from_command_line
from foundation.apps.accounts.models import APIKey
from foundation.apps.accounts.enterprise import Organization, OrganizationMembership

User = get_user_model()

def test_core_functionality():
    """Test basic foundation components."""
    print("🧪 Testing Foundation Core Functionality")
    
    # Test 1: Database connectivity
    try:
        user_count = User.objects.count()
        print(f"✅ Database connectivity: {user_count} users in system")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Test 2: User creation
    try:
        # Use timestamp to ensure uniqueness
        import time
        timestamp = str(int(time.time()))
        test_user = User.objects.create_user(
            username=f'foundation_test_{timestamp}', 
            email=f'test_{timestamp}@foundation.local',
            password='test_password_123'
        )
        print(f"✅ User creation: Created user {test_user.username}")
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return False
    
    # Test 3: Organization system
    try:
        org = Organization.objects.create(
            name="Test Organization",
            slug=f"test-org-{timestamp}",
            primary_contact_email=f"test_{timestamp}@organization.local",
            subscription_tier="starter",
            created_by=test_user
        )
        print(f"✅ Organization system: Created org {org.name}")
    except Exception as e:
        print(f"❌ Organization error: {e}")
        return False
    
    # Test 4: Organization membership
    try:
        membership = OrganizationMembership.objects.create(
            user=test_user,
            organization=org,
            is_admin=True
        )
        print(f"✅ Organization membership: User added as admin")
    except Exception as e:
        print(f"❌ Membership error: {e}")
        return False
    
    # Test 5: API Key generation
    try:
        api_key, raw_key = APIKey.generate_key(
            user=test_user,
            name="Test API Key",
            expires_in_days=30
        )
        print(f"✅ API Key system: Generated key {api_key.name} with prefix {api_key.key_prefix}")
    except Exception as e:
        print(f"❌ API Key error: {e}")
        return False
    
    # Cleanup
    try:
        api_key.delete()
        membership.delete()
        org.delete()
        test_user.delete()
        print("✅ Cleanup: Test data removed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    print("\n🎉 Foundation core functionality test completed successfully!")
    return True

def test_settings():
    """Test settings configuration."""
    print("\n⚙️ Testing Foundation Settings")
    
    from django.conf import settings
    
    # Check core apps are installed
    foundation_apps = [app for app in settings.INSTALLED_APPS if 'foundation' in app]
    print(f"✅ Foundation apps installed: {len(foundation_apps)} apps")
    
    # Check database configuration
    db_engine = settings.DATABASES['default']['ENGINE']
    print(f"✅ Database engine: {db_engine}")
    
    # Check cache configuration
    cache_backend = settings.CACHES['default']['BACKEND']
    print(f"✅ Cache backend: {cache_backend}")
    
    # Check middleware
    foundation_middleware = [mw for mw in settings.MIDDLEWARE if 'foundation' in mw]
    print(f"✅ Foundation middleware: {len(foundation_middleware)} middleware")
    
    return True

def run_tests():
    """Run all foundation tests."""
    print("=" * 60)
    print("🏗️ Enterprise SaaS Foundation Validation")
    print("=" * 60)
    
    success = True
    
    # Test settings
    if not test_settings():
        success = False
    
    # Test core functionality
    if not test_core_functionality():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 All foundation tests passed! Foundation is ready for use.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return success

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
