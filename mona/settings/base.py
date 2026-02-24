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
    'jazzmin',  # Jazzmin должен быть перед django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'simple_history',  # История изменений моделей
    'rangefilter',  # Фильтр по диапазону дат в админке
    'core',
    'bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise для статических файлов
    'core.middleware.NoCacheMiddleware',  # Отключение кеша для Telegram Web App
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Поддержка локализации
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',  # Отслеживание пользователя для истории
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

# Cache Configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
    }
}

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
# Маппинг: uz_latin -> uz, ru -> ru
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

# Настройки для загрузки больших файлов (видео инструкции)
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB - файлы больше этого размера будут сохраняться на диск
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB - максимальный размер данных в запросе
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Увеличиваем лимит полей в форме

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_BOT_USERNAME = env('TELEGRAM_BOT_USERNAME', default='')  # @username бота (без @)
TELEGRAM_BOT_ADMIN_USERNAME = env('TELEGRAM_BOT_ADMIN_USERNAME', default='')  # @username администратора (без @)

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
QR_CODE_BATCH_SIZE = 200  # Размер батча для генерации QR-кодов (для избежания таймаутов)

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

# Jazzmin Configuration
JAZZMIN_SETTINGS = {
    # Заголовок сайта
    "site_title": "Mono Admin",
    "site_header": "Mono Admin Panel",
    "site_brand": "Mono Admin",
    "site_logo": None,  # Можно добавить путь к логотипу
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    
    # Цветовая схема
    "theme": "default",  # Можно использовать "dark" для темной темы
    "dark_mode_theme": None,
    
    # Настройки боковой панели
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],  # QRCodeGeneration скрыт через has_module_permission
    # Показывать приложения по пермишну
    "show_ui_builder": False,
    # Настройки для отображения моделей по правам доступа
    "default_model_icon": "fas fa-circle",
    
    # Иконки
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.TelegramUser": "fas fa-user-tie",
        "core.QRCode": "fas fa-qrcode",
        "core.Gift": "fas fa-gift",
        "core.GiftRedemption": "fas fa-shopping-cart",
        "core.BroadcastMessage": "fas fa-bullhorn",
    },
    
    # Настройки меню
    "order_with_respect_to": [
        "core",
        "auth",
    ],
    
    # Кастомные ссылки в меню
    "custom_links": {
        "core": [
            {
                "name": "Boshqaruv paneli",
                "url": "/admin/dashboard/",
                "icon": "fas fa-chart-line",
                "permissions": ["auth.view_user"]
            },
            {
                "name": "Promo-kodni yaratish",
                "url": "/admin/core/qrcode/generate/",
                "icon": "fas fa-qrcode",
                "permissions": ["core.generate_qrcodes"]
            }
        ]
    },
    
    # Настройки прав доступа
    "permissions": {
        "custom_links": ["auth.view_user", "core.generate_qrcodes"],
    },
    
    # Настройки UI
    "custom_css": None,
    "custom_js": "core_admin/js/changelist_filters.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    
    # Настройки футера
    "copyright": "Mono Admin Panel",
    
    # Настройки поиска
    "search_model": ["auth.User", "core.TelegramUser"],
    
    # Настройки пользовательского интерфейса
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Главная", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Дашборд", "url": "dashboard", "permissions": ["auth.view_user"]},
    ],
    
    # Настройки языков
    "language_chooser": False,
    
    # Настройки изменений
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    
    # Настройки списков
    "list_per_page": 25,
    "list_max_show_all": 100,
    
    # Настройки действий
    "actions_on_top": True,
    "actions_on_bottom": True,
    "actions_selection_counter": True,
    
    # Настройки фильтров
    "related_modal_active": False,
    
    # Настройки форм
    "show_related": True,
}

# Настройки UI для Jazzmin (опционально)
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

