#!/usr/bin/env python
"""
Скрипт для запуска webhook сервера.
"""
import os
import django
import asyncio
import logging
from aiohttp import web

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'mona.settings.production'))
django.setup()

from django.conf import settings

# Sentry инициализируется здесь один раз для всего процесса бота.
# bot.py также вызывает sentry_sdk.init() — повторная инициализация
# безопасна (sentry-sdk пропускает дублирующий вызов).
_sentry_dsn = getattr(settings, 'SENTRY_DSN', '') or os.environ.get('SENTRY_DSN', '')
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.aiohttp import AioHttpIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[
            AioHttpIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        environment=os.environ.get('SENTRY_ENVIRONMENT', 'production'),
        send_default_pii=False,
    )

from bot.webhook import get_webhook_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Запускает webhook сервер."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    app = get_webhook_app()
    
    host = settings.WEBHOOK_HOST
    port = settings.WEBHOOK_PORT
    
    logger.info(f"Запуск webhook сервера на {host}:{port}")
    web.run_app(app, host=host, port=port)


if __name__ == '__main__':
    main()

