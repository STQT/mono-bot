"""
Management command to run Telegram bot.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from bot.bot import start_bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR(
                    'ОШИБКА: TELEGRAM_BOT_TOKEN не установлен!\n'
                    'Установите токен в файле .env или в настройках Django.'
                )
            )
            return
        
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        try:
            start_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Бот остановлен пользователем'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при запуске бота: {e}'))

