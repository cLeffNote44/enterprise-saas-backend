"""
Base test classes with helpful utilities.

Usage:
    from foundation.testing.base import FoundationTestCase, FoundationAPITestCase

    class MyTestCase(FoundationTestCase):
        def test_something(self):
            user, org = self.create_user_and_org()
"""

from django.test import TestCase, TransactionTestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .factories import (
    UserFactory, OrganizationFactory, OrganizationMembershipFactory,
    create_user_with_organization, create_organization_with_subscription
)


class FoundationTestCase(TestCase):
    """Base test case with common utilities."""

    def setUp(self):
        super().setUp()
        self.user, self.org, self.membership = create_user_with_organization()

    def create_user(self, **kwargs):
        """Create a test user."""
        return UserFactory(**kwargs)

    def create_organization(self, **kwargs):
        """Create a test organization."""
        return OrganizationFactory(**kwargs)

    def create_user_and_org(self, username='testuser', org_name='Test Org'):
        """Create a user with organization membership."""
        return create_user_with_organization(username, org_name)

    def assert_field_error(self, form, field, expected_error):
        """Assert that a form field has a specific error."""
        self.assertIn(field, form.errors)
        self.assertIn(expected_error, str(form.errors[field]))


class FoundationTransactionTestCase(TransactionTestCase):
    """Base transaction test case for tests that need database transactions."""

    def setUp(self):
        super().setUp()
        self.user, self.org, self.membership = create_user_with_organization()


class FoundationAPITestCase(APITestCase):
    """Base API test case with authentication helpers."""

    def setUp(self):
        super().setUp()
        self.user, self.org, self.membership = create_user_with_organization()
        self.client = APIClient()
        self.authenticate()

    def authenticate(self, user=None):
        """Authenticate the test client."""
        user = user or self.user
        self.client.force_authenticate(user=user)

    def logout(self):
        """Logout the test client."""
        self.client.force_authenticate(user=None)

    def create_api_key(self, organization=None):
        """Create an API key for testing."""
        from foundation.apps.accounts.models import APIKey
        org = organization or self.org
        return APIKey.generate_key(organization=org, name='Test API Key')

    def authenticate_with_api_key(self, api_key):
        """Authenticate using an API key."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {api_key.key}')

    def assert_response_success(self, response, status_code=200):
        """Assert that API response was successful."""
        self.assertEqual(response.status_code, status_code,
                        f"Expected {status_code}, got {response.status_code}. Response: {response.data}")

    def assert_response_error(self, response, status_code=400):
        """Assert that API response was an error."""
        self.assertGreaterEqual(response.status_code, status_code)

    def assert_pagination(self, response):
        """Assert that response contains pagination."""
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)

    def get_json(self, url, **kwargs):
        """GET request expecting JSON response."""
        response = self.client.get(url, **kwargs)
        self.assert_response_success(response)
        return response.data

    def post_json(self, url, data, **kwargs):
        """POST request with JSON data."""
        response = self.client.post(url, data, format='json', **kwargs)
        return response

    def put_json(self, url, data, **kwargs):
        """PUT request with JSON data."""
        response = self.client.put(url, data, format='json', **kwargs)
        return response

    def patch_json(self, url, data, **kwargs):
        """PATCH request with JSON data."""
        response = self.client.patch(url, data, format='json', **kwargs)
        return response


class MockServiceMixin:
    """Mixin for mocking external services."""

    def mock_stripe(self):
        """Mock Stripe API calls."""
        from unittest.mock import patch, MagicMock

        patcher = patch('stripe.Customer.create')
        mock = patcher.start()
        mock.return_value = MagicMock(id='cus_test123')
        self.addCleanup(patcher.stop)
        return mock

    def mock_sendgrid(self):
        """Mock SendGrid email sending."""
        from unittest.mock import patch, MagicMock

        patcher = patch('sendgrid.SendGridAPIClient.send')
        mock = patcher.start()
        mock.return_value = MagicMock(status_code=202)
        self.addCleanup(patcher.stop)
        return mock

    def mock_twilio(self):
        """Mock Twilio SMS sending."""
        from unittest.mock import patch, MagicMock

        patcher = patch('twilio.rest.Client.messages.create')
        mock = patcher.start()
        mock.return_value = MagicMock(sid='SM_test123')
        self.addCleanup(patcher.stop)
        return mock


# Example test demonstrating usage

class ExampleTestCase(FoundationAPITestCase, MockServiceMixin):
    """Example test case showing best practices."""

    def test_user_creation(self):
        """Test creating a user."""
        user = self.create_user(username='newuser')
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('testpass123'))

    def test_api_authentication(self):
        """Test API authentication."""
        response = self.client.get('/api/accounts/api/organizations/')
        self.assert_response_success(response)

    def test_with_mocked_stripe(self):
        """Test with mocked Stripe."""
        mock_stripe = self.mock_stripe()

        # Your code that calls Stripe
        # mock_stripe will intercept the call

        mock_stripe.assert_called_once()
