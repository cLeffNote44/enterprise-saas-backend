"""Development settings for the Enterprise SaaS Foundation."""

from .base import *  # noqa: F401, F403

# Development overrides
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use dummy cache for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Development logging
LOGGING["loggers"] = {  # noqa: F405
    "foundation": {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": False,
    },
    "django": {
        "handlers": ["console"],
        "level": "INFO",
        "propagate": False,
    },
}

# Django extensions configuration for development
if "django_extensions" in INSTALLED_APPS:  # noqa: F405
    GRAPH_MODELS = {
        "all_applications": True,
        "group_models": True,
    }

# Disable CSRF in development for API testing
CSRF_COOKIE_SECURE = False

# Allow all origins for CORS in development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Development security (less strict)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
