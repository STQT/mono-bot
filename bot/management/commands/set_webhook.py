"""
Management command to set Telegram webhook.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from bot.bot import bot


class Command(BaseCommand):
    help = 'Устанавливает webhook для Telegram бота'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='URL для webhook (если не указан, используется из настроек)',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Удалить webhook вместо установки',
        )

    def handle(self, *args, **options):
        import asyncio
        
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN не установлен!')
            )
            return
        
        async def set_webhook():
            try:
                if options['delete']:
                    await bot.delete_webhook()
                    self.stdout.write(
                        self.style.SUCCESS('Webhook успешно удален')
                    )
                else:
                    webhook_url = options.get('url') or f"{settings.WEBHOOK_URL}/webhook/{settings.TELEGRAM_BOT_TOKEN}"
                    
                    await bot.set_webhook(
                        url=webhook_url,
                        allowed_updates=["message", "callback_query"],
                        drop_pending_updates=True
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Webhook успешно установлен: {webhook_url}')
                    )
                    
                    # Проверяем информацию о webhook
                    webhook_info = await bot.get_webhook_info()
                    self.stdout.write(f'Webhook info: {webhook_info.url}')
                    self.stdout.write(f'Pending updates: {webhook_info.pending_update_count}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка: {e}')
                )
        
        asyncio.run(set_webhook())

