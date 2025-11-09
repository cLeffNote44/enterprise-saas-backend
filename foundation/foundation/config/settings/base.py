"""Base settings for the Enterprise SaaS Foundation."""
from pathlib import Path
from typing import List
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Environment setup
env = environ.Env()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="foundation-secret-key-change-in-production",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS: List[str] = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# Add development hosts when DEBUG is enabled
if DEBUG:
    ALLOWED_HOSTS += ["localhost", "127.0.0.1", "testserver", "*"]

# Application definition

# Foundation core apps (always included)
FOUNDATION_APPS = [
    'foundation.apps.accounts.apps.AccountsConfig',
    'foundation.apps.compliance.apps.ComplianceConfig',
    'foundation.apps.analytics.apps.AnalyticsConfig',
    'foundation.apps.messaging.apps.MessagingConfig',
    'foundation.apps.moderation.apps.ModerationConfig',
    'foundation.apps.core.apps.CoreConfig',
    # Phase 1 & 2 additions
    'foundation.apps.billing.apps.BillingConfig',
    'foundation.apps.notifications.apps.NotificationsConfig',
    'foundation.apps.rate_limiting.apps.RateLimitingConfig',
    'foundation.apps.feature_flags.apps.FeatureFlagsConfig',
    'foundation.apps.files.apps.FilesConfig',
    'foundation.apps.data_exchange.apps.DataExchangeConfig',
    'foundation.apps.search.apps.SearchConfig',
]

# Django built-in apps
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth", 
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required for allauth
]

# Third-party apps
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "channels",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "axes",
    "auditlog",
    # Enterprise infrastructure
    "django_redis",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_email",
    "django_prometheus",
]

# Project-specific extensions (to be overridden)
PROJECT_EXTENSIONS = []

# Combine all apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + FOUNDATION_APPS + PROJECT_EXTENSIONS

# Add development-only apps
if DEBUG:
    INSTALLED_APPS += [
        "django_extensions",
        "debug_toolbar",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # CORS should be early
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static file serving
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "foundation.apps.core.middleware.SecurityHeadersMiddleware",  # Security headers
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",  # Brute force protection
    "auditlog.middleware.AuditlogMiddleware",  # Audit logging
    "allauth.account.middleware.AccountMiddleware",  # Django-allauth
    "django_otp.middleware.OTPMiddleware",  # Multi-factor authentication
]

# Add debug toolbar middleware in development
if DEBUG:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

ROOT_URLCONF = "foundation.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foundation.config.wsgi.application"

# Channels ASGI configuration
ASGI_APPLICATION = "foundation.config.asgi.application"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # Django-axes for brute force protection
    "django.contrib.auth.backends.ModelBackend",  # Default Django auth
    "allauth.account.auth_backends.AuthenticationBackend",  # Django-allauth
]

# Database
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = env("DJANGO_STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))

# Media files (user uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = env("DJANGO_MEDIA_ROOT", default=str(BASE_DIR / "media"))

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "foundation.apps.accounts.security.APIKeyAuthentication",  # Custom API key auth
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# DRF Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "Enterprise SaaS Foundation API",
    "DESCRIPTION": "API for enterprise-grade SaaS applications",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# CORS configuration (development)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS: List[str] = env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])

# Django Axes configuration for brute-force protection
AXES_FAILURE_LIMIT = 5
AXES_LOCK_OUT_AT_FAILURE = True
AXES_COOLOFF_TIME = 1  # hours

# Django Debug Toolbar configuration
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

# ==============================================================================
# ENTERPRISE INFRASTRUCTURE CONFIGURATION
# ==============================================================================

# Redis Configuration
REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

# Cache Configuration with Redis
if DEBUG:
    # Use dummy cache in development when Redis is not available
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 50,
                    "retry_on_timeout": True,
                },
                "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            },
            "KEY_PREFIX": "foundation",
            "TIMEOUT": 300,  # 5 minutes default
        }
    }

# Session backend using Redis in production, database in debug
if DEBUG:
    SESSION_ENGINE = "django.contrib.sessions.backends.db"
else:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = not DEBUG  # Require HTTPS in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Celery Configuration for Background Tasks
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 60  # 1 minute
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_RESULT_EXPIRES = 3600  # 1 hour

# Django Cachalot - ORM caching
CACHALOT_ENABLED = not DEBUG  # Disable in debug mode
CACHALOT_CACHE = "default"
CACHALOT_TIMEOUT = 300  # 5 minutes

# Multi-Factor Authentication (django-otp)
OTP_TOTP_ISSUER = "Enterprise SaaS Foundation"
OTP_LOGIN_URL = "/auth/login/"
OTP_EMAIL_SUBJECT = "Your login token"
OTP_EMAIL_BODY_TEMPLATE = "Your login token is: {token}"

# Django Allauth Configuration (SSO)
SITE_ID = 1
ALAUTH_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"
# Updated to new format (replaces deprecated ACCOUNT_AUTHENTICATION_METHOD)
ACCOUNT_LOGIN_METHODS = {"email"}  # Use email for login
# Updated to new format (replaces deprecated ACCOUNT_EMAIL_REQUIRED)
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]  # Required fields
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# Updated to new format (replaces deprecated ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT)
ACCOUNT_RATE_LIMITS = {
    "login_failed": "3/5m",  # 3 attempts per 5 minutes
    "login": "30/h",  # 30 successful logins per hour
    "signup": "5/h",  # 5 signups per hour
}
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = True
SOCIALACCOUNT_AUTO_SIGNUP = False

# API Key Management
API_KEY_ROTATION_DAYS = env.int("API_KEY_ROTATION_DAYS", default=90)
API_WEBHOOK_SECRET = env("API_WEBHOOK_SECRET", default="")

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_UPGRADE_INSECURE_REQUESTS = not DEBUG

# Channels Configuration for Real-time features
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}

# ==============================================================================
# SECURITY HARDENING
# ==============================================================================

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# CSRF Protection
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Production Security Settings (disabled in DEBUG mode)
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
