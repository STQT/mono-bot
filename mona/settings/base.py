"""
Базовые настройки Django для проекта mona.
Общие настройки для всех окружений.
"""
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'core',
    'bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise для статических файлов
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Поддержка локализации
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mona.urls'

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

WSGI_APPLICATION = 'mona.wsgi.application'
ASGI_APPLICATION = 'mona.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='mona_db'),
        'USER': env('DB_USER', default='mona_user'),
        'PASSWORD': env('DB_PASSWORD', default='mona_password'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# MongoDB Configuration
MONGODB_SETTINGS = {
    'host': env('MONGODB_HOST', default='mongodb'),
    'port': int(env('MONGODB_PORT', default='27017')),
    'db': env('MONGODB_DB', default='mona_mongodb'),
}

# Redis Configuration
REDIS_HOST = env('REDIS_HOST', default='redis')
REDIS_PORT = int(env('REDIS_PORT', default='6379'))

# Celery Configuration (будет настроено после определения TIME_ZONE)
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}

# Password validation
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
# Django использует стандартные ISO 639 коды, но мы храним кастомные коды в БД
# Маппинг: uz_latin -> uz, uz_cyrillic -> uz, ru -> ru
LANGUAGE_CODE = 'uz'  # Стандартный код для узбекского (Django требует стандартные коды)
LANGUAGES = [
    ('uz', 'O\'zbek (Lotin)'),  # Маппится на uz_latin в БД
    ('ru', 'Русский'),
]
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
TIME_ZONE = 'Asia/Tashkent'  # Временная зона Узбекистана
USE_I18N = True
USE_TZ = True
USE_L10N = True

# Celery Timezone (должно быть после определения TIME_ZONE)
CELERY_TIMEZONE = TIME_ZONE

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'core', 'static'),
]

# WhiteNoise configuration для статических файлов
# Используем CompressedStaticFilesStorage вместо CompressedManifestStaticFilesStorage
# для более надежной работы (manifest может вызывать проблемы если не собран правильно)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_BOT_USERNAME = env('TELEGRAM_BOT_USERNAME', default='')  # @username бота (без @)

# Webhook Settings (для production)
WEBHOOK_URL = env('WEBHOOK_URL', default='')
WEBHOOK_PATH = env('WEBHOOK_PATH', default=f'/webhook/{TELEGRAM_BOT_TOKEN}')
WEBHOOK_HOST = env('WEBHOOK_HOST', default='0.0.0.0')
WEBHOOK_PORT = int(env('WEBHOOK_PORT', default='8443'))

# Web App Settings
WEB_APP_URL = env('WEB_APP_URL', default='')  # HTTPS URL для Web App (можно использовать ngrok для тестирования)

# Scratch Card Points
ELECTRICIAN_POINTS = 50  # 50 dollars
SELLER_POINTS = 20  # 20 dollars

# QR Code Settings
QR_CODE_MAX_ATTEMPTS = 5  # Максимальное количество неудачных попыток в день

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS для Web App (если нужно)
CORS_ALLOWED_ORIGINS = [
    "https://web.telegram.org",
    "https://telegram.org",
]

# CSRF для Telegram Web App
CSRF_TRUSTED_ORIGINS = [
    "https://web.telegram.org",
    "https://telegram.org",
]

# Admin redirect after login
LOGIN_REDIRECT_URL = '/admin/'
LOGIN_URL = '/admin/login/'

