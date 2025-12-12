"""
Локальные настройки для разработки.
Используется когда DJANGO_SETTINGS_MODULE=mona.settings.local
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

# Разрешаем все хосты для ngrok и локальной разработки
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0', '*'])

# WhiteNoise настройки для разработки
# В разработке используем более простой storage без манифеста
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True  # Использовать finders в разработке для автоматического обновления
WHITENOISE_AUTOREFRESH = True  # Автоматически обновлять при изменениях в разработке
WHITENOISE_ROOT = None  # Не использовать root для статических файлов
# Для работы через ngrok важно правильно настроить статические файлы
WHITENOISE_MANIFEST_STRICT = False  # Не требовать строгого соответствия манифеста
WHITENOISE_ADD_HEADERS_FUNCTION = None  # Отключаем дополнительные заголовки для ngrok

# Настройки для работы с ngrok
# Отключаем проверку CSRF для ngrok (только для разработки!)
CSRF_COOKIE_SECURE = False  # Для работы через ngrok без SSL сертификата
SESSION_COOKIE_SECURE = False  # Для работы через ngrok без SSL сертификата

# Расширяем CSRF_TRUSTED_ORIGINS для ngrok доменов
# В разработке можно добавлять домены динамически через переменную окружения
# или просто разрешить все через middleware (см. ниже)
CSRF_TRUSTED_ORIGINS = CSRF_TRUSTED_ORIGINS + [
    # Добавьте ваш ngrok домен сюда, например:
    # 'https://your-ngrok-domain.ngrok-free.app',
]

# Middleware для автоматического добавления ngrok доменов в CSRF_TRUSTED_ORIGINS
# Это позволяет работать с любым ngrok доменом без ручной настройки
import re
from django.utils.deprecation import MiddlewareMixin

class NgrokCSRFMiddleware(MiddlewareMixin):
    """Middleware для автоматического добавления ngrok доменов в CSRF_TRUSTED_ORIGINS"""
    def process_request(self, request):
        host = request.get_host()
        # Проверяем, является ли домен ngrok доменом
        ngrok_patterns = [
            r'\.ngrok-free\.app$',
            r'\.ngrok\.io$',
            r'\.ngrok\.app$',
        ]
        if any(re.search(pattern, host) for pattern in ngrok_patterns):
            scheme = 'https' if request.is_secure() else 'http'
            origin = f"{scheme}://{host}"
            if origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(origin)
    
    def process_response(self, request, response):
        # Добавляем заголовок для обхода страницы предупреждения ngrok
        host = request.get_host()
        ngrok_patterns = [
            r'\.ngrok-free\.app$',
            r'\.ngrok\.io$',
            r'\.ngrok\.app$',
        ]
        if any(re.search(pattern, host) for pattern in ngrok_patterns):
            # Добавляем заголовок для обхода предупреждения ngrok
            response['ngrok-skip-browser-warning'] = 'true'
        return response

# Добавляем middleware после SecurityMiddleware
MIDDLEWARE.insert(1, 'mona.settings.local.NgrokCSRFMiddleware')

# Дополнительные настройки для разработки
# Можно добавить debug_toolbar если нужно:
# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Email backend для разработки (консоль)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Логирование для разработки
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'bot': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

