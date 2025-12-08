"""
Продакшн настройки.
Используется когда DJANGO_SETTINGS_MODULE=mona.settings.production
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Security settings для production
if not DEBUG:
    # Настройки для работы за прокси (nginx)
    # Django должен доверять заголовкам от прокси-сервера
    # Внешний nginx передает X-Forwarded-Proto: https
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    
    # Отключаем SECURE_SSL_REDIRECT, так как внешний nginx уже делает редирект с HTTP на HTTPS
    # Если включить SECURE_SSL_REDIRECT=True, Django будет пытаться редиректить HTTP->HTTPS,
    # но так как запрос от прокси приходит по HTTP, это создаст бесконечный цикл редиректов
    SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
    
    # Cookie security (работают только если SECURE_PROXY_SSL_HEADER настроен правильно)
    SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
    CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
    
    # Другие security настройки
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Логирование для production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'bot': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Создаем директорию для логов если её нет
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# WhiteNoise настройки для production
# WhiteNoise автоматически сжимает и кеширует статические файлы
# STATICFILES_STORAGE уже настроен в base.py как CompressedStaticFilesStorage
# WhiteNoise middleware уже добавлен в base.py после SecurityMiddleware

# Дополнительные настройки WhiteNoise для production
WHITENOISE_USE_FINDERS = False  # Не использовать finders в production (только из STATIC_ROOT)
WHITENOISE_AUTOREFRESH = False  # Не проверять изменения файлов в production (только при collectstatic)

