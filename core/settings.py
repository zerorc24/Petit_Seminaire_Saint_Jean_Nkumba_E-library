from pathlib import Path
import os
import dj_database_url

# -------------------------------
# BASE DIR
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


# -------------------------------
# SECURITY
# -------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'unsafe-secret-key')

DEBUG = True

ALLOWED_HOSTS = ['*']

# -------------------------------
# APPLICATIONS
# -------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'library',
    'pwa',
]


# -------------------------------
# MIDDLEWARE
# -------------------------------
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


# -------------------------------
# AUTH SYSTEM (IMPORTANT)
# -------------------------------
AUTH_USER_MODEL = 'library.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"


# -------------------------------
# URL CONFIG
# -------------------------------
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'


# -------------------------------
# TEMPLATES
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


# -------------------------------
# DATABASE
# -------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}


# -------------------------------
# PASSWORD VALIDATION
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------------------
# INTERNATIONALIZATION
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -------------------------------
# STATIC FILES
# -------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# -------------------------------
# MEDIA FILES
# -------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# -------------------------------
# EMAIL (DEV MODE)
# -------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'pssjnteam@gmail.com'
EMAIL_HOST_PASSWORD = 'hnhb adoe kcqk ypmz'


# -------------------------------
# SECURITY (DEV SAFE)
# -------------------------------
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# -------------------------------
# DEFAULT AUTO FIELD
# -------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------------------
# CSRF TRUST
# -------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://petit-seminaire-saint-jean-nkumba-e.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/icon-512.png',
        'media': '(device-width: 320px) and (device-height: 568px)'
    }
]

PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'
PWA_APP_NAME = 'Petit Seminaire'
PWA_APP_DESCRIPTION = "Digital Library System"
PWA_APP_THEME_COLOR = '#000000'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'portrait'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'

PWA_APP_ICONS = [
    {
        'src': '/static/images/icon-192.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/images/icon-512.png',
        'sizes': '512x512'
    }
]

PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'