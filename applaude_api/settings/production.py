# backend/applaude_api/settings/production.py
from .base import *
import os
import dj_database_url

DEBUG = False

# Secrets are loaded from environment variables set by Render
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-secret-key-change-in-production')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'applaude-backend-x4p6.onrender.com,localhost,127.0.0.1,.onrender.com').split(',')
# CORS Configuration for Production
CORS_ALLOWED_ORIGINS = [
    "https://vite-react-one-sable-18.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://applaude-backend-x4p6.onrender.com",
    "https://vite-react-git-main-louisotieno2001s-projects.vercel.app",
    "https://vite-react-18rjwwr33-louisotieno2001s-projects.vercel.app",
]

# Allow all origins if explicitly set in environment
CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 't')

# Ensure CORS applies to auth endpoints
CORS_URLS_REGEX = r'^/api/.*$'

# --- PRODUCTION SECURITY SETTINGS ---
# Temporarily commented out for debugging 400 errors
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# --- DATABASE CONFIGURATION ---
# Use DATABASE_URL provided by Render (supports PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
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
