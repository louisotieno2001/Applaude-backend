# backend/applaude_api/settings/production.py
from .base import *
import os

DEBUG = False

# Secrets are loaded from environment variables set by Elastic Beanstalk
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')

# --- PRODUCTION SECURITY SETTINGS ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- DATABASE CONFIGURATION ---
# Database URL is provided by Elastic Beanstalk environment properties
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}

# --- Redis for Celery ---
CELERY_BROKER_URL = os.environ.get("REDIS_URL")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL")

# --- Cache Configuration ---
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# django-ratelimit configuration - use default Redis cache for rate limiting
RATELIMIT_USE_CACHE = 'default'

# --- Static Files ---
# Nginx (configured via .platform hooks) will serve files from STATIC_ROOT
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
