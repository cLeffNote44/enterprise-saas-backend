"""
Advanced rate limiting and API management.

This app provides:
- Tiered rate limiting based on subscription plans
- API usage tracking and analytics
- Custom rate limits per organization
- API quota management
- Webhook management and delivery
"""

default_app_config = 'foundation.apps.rate_limiting.apps.RateLimitingConfig'
