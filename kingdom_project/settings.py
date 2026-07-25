import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-fd-%v#u$jz%d32s1sbt1abxk2vua7v%0pe_e-9w^q0!=c0184h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Add this setting near your ALLOWED_HOSTS configuration
CSRF_TRUSTED_ORIGINS = [
    'https://pefathikaroadcathedral-production-c4e2f9.up.railway.app',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kingdom_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # 🌟 Instructs the rendering engines to read your new directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kingdom_project.wsgi.application'


# =====================================================
# 🗄️ DYNAMIC DATABASE HANDSHAKE CONTROL MATRIX
# =====================================================
# Intercepts standard database routing strings cleanly to maintain environment isolation
database_env_url = os.environ.get('DATABASE_URL_PUBLIC') or os.environ.get('DATABASE_URL')

if database_env_url:
    # 📡 LIVE PRODUCTION ENVIRONMENT: Parsed securely via cloud public network lines
    DATABASES = {
        'default': dj_database_url.parse(database_env_url, conn_max_age=600)
    }
else:
    # 💻 LOCAL DEVELOPMENT ENVIRONMENT: Fallback to standalone SQLite configuration for offline work
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

# =====================================================
# 🖼️ SECURE MULTIMEDIA UPLOAD MANAGEMENT ROUTES
# =====================================================
# The web browser directory prefix routing path for uploaded assets
MEDIA_URL = '/media/'

# The absolute local directory track where files are safely stored on your machine
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_ROOT = BASE_DIR / 'staticfiles'  # 📂 Where Railway gathers all styles during build
