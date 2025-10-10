"""
Docker-specific settings for Enterprise SaaS Foundation
"""
import os
from pathlib import Path
import environ
from .base import *  # noqa

# Environment setup
env = environ.Env()
environ.Env.read_env(env_file=os.environ.get("ENV_FILE", ".env"))

# Override base settings for Docker
DEBUG = env.bool("DJANGO_DEBUG", default=True)
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-docker-dev-key-change-in-production")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# Database configuration for PostgreSQL
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://foundation:foundation@db:5432/foundation"
    )
}

# Redis cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": "foundation",
        "TIMEOUT": 300,
    }
}

# Celery configuration
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Email configuration for MailHog
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@foundation.local")
SERVER_EMAIL = env("SERVER_EMAIL", default="server@foundation.local")

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files configuration (MinIO)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Storage configuration for MinIO
if env.bool("USE_MINIO", default=True):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
    
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="minioadmin")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="minioadmin")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="foundation-dev")
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://minio:9000")
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=None)
    AWS_DEFAULT_ACL = env("AWS_DEFAULT_ACL", default="public-read")
    AWS_S3_USE_SSL = env.bool("AWS_S3_USE_SSL", default=False)
    AWS_S3_VERIFY = env.bool("AWS_S3_VERIFY", default=False)
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_QUERYSTRING_AUTH = env.bool("AWS_QUERYSTRING_AUTH", default=False)
    AWS_S3_FILE_OVERWRITE = False

# Admin UI Configuration (Jazzmin)
JAZZMIN_SETTINGS = {
    "site_title": "Foundation Admin",
    "site_header": "Foundation Admin",
    "site_brand": "Enterprise SaaS Foundation",
    "site_logo": None,
    "welcome_sign": "Welcome to Foundation Admin",
    "copyright": "Enterprise SaaS Foundation",
    "search_model": "auth.User",
    "user_avatar": None,
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Analytics", "url": "/admin/analytics/", "new_window": False},
        {"model": "auth.User"},
        {"app": "accounts"},
    ],
    
    # Side Menu
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "accounts", "compliance", "analytics"],
    
    # UI Customization
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Theme
    "theme": "default",
    "dark_mode_theme": None,
    
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "accounts.Organization": "fas fa-building",
        "accounts.APIKey": "fas fa-key",
        "compliance.CompliancePolicy": "fas fa-shield-alt",
        "analytics.AnalyticsSnapshot": "fas fa-chart-line",
    },
    
    # Default Icons
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    
    # Related Modal
    "related_modal_active": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# Add Docker-specific apps to INSTALLED_APPS
DOCKER_APPS = [
    "jazzmin",  # Must be before django.contrib.admin
]

# Reconstruct INSTALLED_APPS with Jazzmin first
INSTALLED_APPS = DOCKER_APPS + [app for app in INSTALLED_APPS if app not in DOCKER_APPS]

# Add additional Docker apps
INSTALLED_APPS += [
    "import_export",
    "rangefilter",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
]

# Health Check Settings
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,  # in MB
}

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": env("LOG_LEVEL", default="INFO"),
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "foundation": {
            "handlers": ["console"],
            "level": env("LOG_LEVEL", default="DEBUG" if DEBUG else "INFO"),
            "propagate": False,
        },
    },
}

# Security settings for Docker development
if DEBUG:
    # Disable some security features for local development
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
else:
    # Production security settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# CORS settings for Docker
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add Docker internal IPs for debug toolbar
if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]