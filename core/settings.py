from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DB_PORT=(int, 5432),
    DB_CONN_MAX_AGE=(int, 30),
    DB_CONN_HEALTH_CHECKS=(bool, True),
    DB_CONNECT_TIMEOUT=(int, 10),
    DB_KEEPALIVES_IDLE=(int, 30),
    DB_KEEPALIVES_INTERVAL=(int, 10),
    DB_KEEPALIVES_COUNT=(int, 3),
    EXCHANGE_RATE_TIMEOUT=(float, 5.0),
)

ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    environ.Env.read_env(
        ENV_FILE,
        overwrite=True,
    )


# ============================================================
# DJANGO CORE
# ============================================================

DEBUG = env.bool(
    "DJANGO_DEBUG",
    default=False,
)

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default=None,
)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "unsafe-dev-only-secret-key"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY is required when DJANGO_DEBUG=False"
        )


ALLOWED_HOSTS = [
    host.strip()
    for host in env(
        "DJANGO_ALLOWED_HOSTS",
        default="localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "inventory",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "core.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


WSGI_APPLICATION = "core.wsgi.application"


# ============================================================
# DATABASE - POSTGRESQL / SUPABASE
# ============================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env(
            "DB_NAME",
            default="postgres",
        ),
        "USER": env(
            "DB_USER",
            default="postgres",
        ),
        "PASSWORD": env(
            "DB_PASSWORD",
            default="",
        ),
        "HOST": env(
            "DB_HOST",
            default="",
        ),
        "PORT": env.int(
            "DB_PORT",
            default=5432,
        ),

        # Keep DB sessions short enough for a serverless Cloud Run
        # instance while still avoiding a new TLS connection per request.
        "CONN_MAX_AGE": env.int(
            "DB_CONN_MAX_AGE",
            default=30,
        ),

        # Django 4.2 checks a persistent connection before reusing it.
        # If Supabase/Supavisor closed a stale connection, Django opens a
        # fresh one instead of failing the next request immediately.
        "CONN_HEALTH_CHECKS": env.bool(
            "DB_CONN_HEALTH_CHECKS",
            default=True,
        ),

        "OPTIONS": {
            "sslmode": env(
                "DB_SSLMODE",
                default="require",
            ),

            # PostgreSQL connection establishment timeout in seconds.
            "connect_timeout": env.int(
                "DB_CONNECT_TIMEOUT",
                default=10,
            ),

            # TCP keepalives help detect dead/stale network connections.
            "keepalives": 1,
            "keepalives_idle": env.int(
                "DB_KEEPALIVES_IDLE",
                default=30,
            ),
            "keepalives_interval": env.int(
                "DB_KEEPALIVES_INTERVAL",
                default=10,
            ),
            "keepalives_count": env.int(
                "DB_KEEPALIVES_COUNT",
                default=3,
            ),

            # Makes connections easy to identify in PostgreSQL/Supabase logs.
            "application_name": "bookstore-inventory-api",
        },
    }
}


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.LimitOffsetPagination"
    ),
    "PAGE_SIZE": 10,
    "COERCE_DECIMAL_TO_STRING": False,
    "EXCEPTION_HANDLER": "core.exceptions.api_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# ============================================================
# OPENAPI / SWAGGER
# ============================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "Bookstore Inventory API",
    "DESCRIPTION": (
        "REST API for bookstore inventory management and suggested "
        "selling-price calculation using current USD exchange rates."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = []


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
