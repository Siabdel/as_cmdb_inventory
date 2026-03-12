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

print(f"✅ ALLOWED_HOSTS configuré: {ALLOWED_HOSTS}")  # Debug temporaire

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
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='inventory_db'),
        'USER': env('DB_USER', default='inventory_user'),
        'PASSWORD': env('DB_PASSWORD', default='inventory_password'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5433'),
    }
}

# Log the database connection settings
logger = logging.getLogger(__name__)
logger.info(f"Database settings: {DATABASES['default']}")

# Add detailed logging for database connection


def log_database_connection():
    """DB test - Docker safe"""
    connection = None
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    
    if db_host == 'localhost' and not os.environ.get('DOCKER_ENV'):
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
STATIC_ROOT = BASE_DIR / 'static'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# DRF Spectacular Configuration (OpenAPI 3 documentation)
SPECTACULAR_SETTINGS = {
    'TITLE': 'CMDB Inventory API',
    'DESCRIPTION': 'API REST pour la gestion d\'inventaire matériel',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
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
