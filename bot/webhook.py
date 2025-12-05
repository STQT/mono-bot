"""
Webhook configuration for Telegram bot in production.
"""
import os
import logging
import django
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mona.settings')
django.setup()

from django.conf import settings
from .bot import dp, bot

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def on_startup(bot: Bot):
    """Выполняется при запуске webhook."""
    webhook_url = f"{settings.WEBHOOK_URL}/webhook/{settings.TELEGRAM_BOT_TOKEN}"
    
    try:
        # Устанавливаем webhook
        await bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        logger.info(f"Webhook установлен: {webhook_url}")
    except Exception as e:
        logger.error(f"Ошибка при установке webhook: {e}")


async def on_shutdown(bot: Bot):
    """Выполняется при остановке webhook."""
    try:
        await bot.delete_webhook()
        logger.info("Webhook удален")
    except Exception as e:
        logger.error(f"Ошибка при удалении webhook: {e}")


def create_webhook_app():
    """Создает aiohttp приложение для webhook."""
    app = web.Application()
    
    # Создаем обработчик webhook
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Регистрируем путь для webhook
    webhook_path = f"/webhook/{settings.TELEGRAM_BOT_TOKEN}"
    webhook_requests_handler.register(app, path=webhook_path)
    
    # Регистрируем startup и shutdown события
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))
    
    return app


async def health_check(request):
    """Health check endpoint."""
    return web.json_response({"status": "ok"})


def get_webhook_app():
    """Возвращает настроенное приложение для webhook."""
    app = create_webhook_app()
    
    # Добавляем health check
    app.router.add_get("/health", health_check)
    
    return app

