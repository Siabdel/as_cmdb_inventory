import os
import logging
from pathlib import Path
from decouple import config
import dj_database_url
import environ
import traceback
from django.db import connections
from django.db.utils import OperationalError
import traceback


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True, cast=bool)

# En haut de settings.py, AVANT tout autre code

ALLOWED_HOSTS = []
raw_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
if raw_hosts:
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'drf_spectacular',
]

LOCAL_APPS = [
    'inventory',
    'stock',
    'maintenance',
    'scanner.apps.ScannerConfig',  # ← important pour le ready()
    'cmdb_admin',
]

# URL de base encodée dans le QR (à adapter en prod)
QR_CODE_BASE_URL = os.environ.get('INVENTORY_QR_CODE_BASE_URL', 'http://localhost:8000')

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Required for session auth
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Doit être en haut, avant CommonMiddleware
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Required for user auth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventory_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'inventory_project.wsgi.application'
ASGI_APPLICATION = 'inventory_project.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
# settings.py du projet inventory

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ.get('INVENTORY_DB_NAME', 'inventory_db'),      # ← préfixe INVENTORY_
        'USER':     os.environ.get('INVENTORY_DB_USER', 'inventory_user'),
        'PASSWORD': os.environ.get('INVENTORY_DB_PASSWORD', ''),
        'HOST':     os.environ.get('INVENTORY_DB_HOST', 'localhost'),
        'PORT':     os.environ.get('INVENTORY_DB_PORT', '5432'),
    }
}


# Log the database connection settings
logger = logging.getLogger(__name__)
logger.info(f"Database settings: {DATABASES['default']}")

# Add detailed logging for database connection


def log_database_connection():
    """DB test - Docker safe"""
    connection = None
    db_host = os.environ.get('INVENTORY_DB_HOST', 'localhost')
    db_port = os.environ.get('INVENTORY_DB_PORT', '5432')
    
    if db_host == 'localhost' and not os.environ.get('INVENTORY_DOCKER_ENV'):
        logger.info("DB test skipped - local dev")
        return  # ← DANS fonction (4 espaces indent)
    
    try:
        connection = connections['default']
        connection.ensure_connection()
        logger.info(f"✅ DB {db_host}:{db_port} OK")
        return True
    except Exception as e:
        logger.warning(f"⚠️ DB not ready: {e}")
        return False
    finally:
        if connection:
            try:
                connection.close()
            except:
                pass

# Commente TEMPORAIREMENTdef log_database_connection():
# log_database_connection()

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    # os.path.join(BASE_DIR, 'media'),
    #  os.path.join(BASE_DIR, 'media', 'upload'),
]

##
# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:3001',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'accept',
    'origin',
    'user-agent',
    'dnt',
    'cache-control',
    'x-requested-with',
]


# DRF Configuration
REST_FRAMEWORK = {
    # ── Authentication ───────────────────────
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    
    # ── Permissions ──────────────────────────
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    # ── Schema ───────────────────────────────
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # ── Pagination ───────────────────────────
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,

    # ── Filters ──────────────────────────────
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ── Configuration Spectacular ─────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'AS CMDB Inventory API',
    'DESCRIPTION': 'API REST pour la gestion d\'inventaire matériel IT — reconditionnement',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
}

# DRF Spectacular Configuration (OpenAPI 3 documentation)

SPECTACULAR_SETTINGS = {
    'TITLE': 'CMDB Inventory API',
    'DESCRIPTION': 'API REST pour la gestion d\'inventaire matériel',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Assets', 'description': 'Gestion des équipements'},
        {'name': 'Categories', 'description': 'Gestion des catégories'},
        {'name': 'Locations', 'description': 'Gestion des emplacements'},
        {'name': 'Brands', 'description': 'Gestion des marques'},
        {'name': 'Tags', 'description': 'Gestion des étiquettes'},
        {'name': 'Movements', 'description': 'Gestion des mouvements'},
        {'name': 'Maintenance', 'description': 'Gestion de la maintenance'},
        {'name': 'Dashboard', 'description': 'Statistiques et tableaux de bord'},
        {'name': 'Auth', 'description': 'Authentification'},
    ],
}
