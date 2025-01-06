"""
Django settings for erp project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
import environ
import logging
import structlog
import dj_database_url
import sys

# Initialize environ
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(BASE_DIR / '.env')

# Add this near the top after imports
logger = logging.getLogger(__name__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Environment-specific settings
ENVIRONMENT = env('ENVIRONMENT', default='development')
IS_HEROKU = 'DYNO' in os.environ

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Update DEBUG setting
DEBUG = env.bool('DEBUG', default=False)
if 'test' in sys.argv:
    DEBUG = True

# Update ALLOWED_HOSTS to include Heroku domains
ALLOWED_HOSTS = [
    'django-casspea.herokuapp.com',
    '.herokuapp.com',
    'casspea.co.uk',
    'www.casspea.co.uk',
]

if DEBUG:
    ALLOWED_HOSTS += ['localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'storages',

    # Custom apps
    'allergens',
    'addresses',
    'flavours',
    'carts',
    'products',
    'users',
    'discounts',
    'checkout',
    'orders',
    'shipping',
    'mails',
    'leads',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Make sure this is second
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=env('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=not DEBUG,
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = [
    'https://main.d29kjbfnh50hd9.amplifyapp.com',
    'https://casspea.co.uk',
    'https://www.casspea.co.uk',
    'https://www2.casspea.co.uk',
    'https://api.casspea.co.uk',
    'https://new.casspea.co.uk',
]

# Allow localhost for CORS when in development
if DEBUG:
    CORS_ALLOWED_ORIGINS.append('http://localhost:3000')

CORS_ALLOW_CREDENTIALS = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://main.d29kjbfnh50hd9.amplifyapp.com',
    'https://casspea.co.uk',
    'https://www.casspea.co.uk',
    'https://www2.casspea.co.uk',
    'https://api.casspea.co.uk',
    'https://new.casspea.co.uk',
]

if DEBUG:
    CSRF_TRUSTED_ORIGINS.append('http://localhost:3000')

# Add this at the bottom of settings.py
AUTH_USER_MODEL = 'users.CustomUser'

# Add REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'CassPea API',
    'DESCRIPTION': 'CassPea Chocolate API documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json_formatter': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        },
        'plain_console': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.dev.ConsoleRenderer(),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_formatter',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    }
}

# Structlog configuration
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Storage Configuration
# ------------------------------------------------------------------------------
USE_S3 = env.bool('USE_S3', default=True)

# Base Static/Media Settings
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = Path('/vol/web/static')
MEDIA_ROOT = Path('/vol/web/media')

if USE_S3:
    # AWS S3 Configuration
    AWS_CONFIG = {
        'AWS_ACCESS_KEY_ID': env('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': env('AWS_SECRET_ACCESS_KEY'),
        'AWS_STORAGE_BUCKET_NAME': env('AWS_STORAGE_BUCKET_NAME', default='casspea-v2'),
        'AWS_S3_REGION_NAME': env('AWS_S3_REGION_NAME', default='eu-west-2'),
        'AWS_DEFAULT_ACL': 'public-read',
        'AWS_QUERYSTRING_AUTH': False,
        'AWS_S3_OBJECT_PARAMETERS': {
            'CacheControl': 'max-age=86400',
        },
        # Optional performance settings
        'AWS_S3_ADDRESSING_STYLE': 'virtual',  # Path-style is deprecated
        'AWS_IS_GZIPPED': True,  # Enable gzip compression
        'AWS_S3_FILE_OVERWRITE': False,  # Prevent accidental overrides
    }

    # Update settings with AWS config
    locals().update(AWS_CONFIG)

    # Set custom domain for CDN/S3
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # Storage Configuration using Django 4.2+ style
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
            'OPTIONS': {
                'location': 'media',
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
            }
        },
        'staticfiles': {
            'BACKEND': 'storages.backends.s3boto3.S3StaticStorage',
            'OPTIONS': {
                'location': 'static',
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
            }
        }
    }

    # URLs for assets
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

else:
    # Local Storage Configuration
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {
                'location': str(MEDIA_ROOT),
                'base_url': '/media/',
            }
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
            'OPTIONS': {
                'location': str(STATIC_ROOT),
                'base_url': '/static/',
            }
        }
    }

    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

# Ensure storage directories exist
for directory in [STATIC_ROOT, MEDIA_ROOT]:
    directory.mkdir(parents=True, exist_ok=True)


# Stripe settings
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'casspea_sessionid'  # Custom name to avoid conflicts
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days in seconds
SESSION_COOKIE_SECURE = True if not DEBUG else False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True  # Important!

# Email settings
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'info@casspea.co.uk'
DEFAULT_FROM_EMAIL_NAME = 'CassPea'
CONTACT_EMAIL = 'info@casspea.co.uk'
SERVER_EMAIL = 'errors@casspea.co.uk'
ADMINS = [('Carlos Blanco', 'carlosblancosierra@gmail.com')]
STAFF_EMAILS = ['info@casspea.co.uk', 'sandy.gomezc@gmail.com','carlosblancosierra@gmail.com']

# Site URL for tracking
SITE_URL = 'https://casspea.co.uk'

# Use WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# HTTPS settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# Security settings for Heroku
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Update storage configuration for Heroku
if not DEBUG and USE_S3:
    # Keep your existing S3 configuration
    pass
else:
    # Local and Heroku (without S3) storage configuration
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {
                'location': str(MEDIA_ROOT),
                'base_url': '/media/',
            }
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
            'OPTIONS': {
                'location': str(STATIC_ROOT),
                'base_url': STATIC_URL,
            }
        }
    }

# Add Heroku logging configuration
if IS_HEROKU:
    LOGGING['handlers']['console']['formatter'] = 'json_formatter'
    LOGGING['loggers']['django']['level'] = 'WARNING'
    LOGGING['loggers']['django.server']['level'] = 'WARNING'

# Update CORS settings for Heroku
if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]
    CSRF_TRUSTED_ORIGINS += [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
    ]

