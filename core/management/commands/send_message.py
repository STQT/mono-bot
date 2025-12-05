"""
Management command для отправки персонального сообщения.
"""
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot
from core.messaging import send_personal_message


class Command(BaseCommand):
    help = 'Отправляет персональное сообщение пользователю'

    def add_arguments(self, parser):
        parser.add_argument(
            'telegram_id',
            type=int,
            help='Telegram ID пользователя'
        )
        parser.add_argument(
            'message',
            type=str,
            help='Текст сообщения'
        )
        parser.add_argument(
            '--parse-mode',
            type=str,
            choices=['HTML', 'Markdown'],
            help='Режим парсинга (HTML или Markdown)',
            default=None
        )

    def handle(self, *args, **options):
        telegram_id = options['telegram_id']
        message_text = options['message']
        parse_mode = options.get('parse_mode')
        
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN не установлен!')
            )
            return
        
        async def send():
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            try:
                success, error = await send_personal_message(
                    bot=bot,
                    telegram_id=telegram_id,
                    text=message_text,
                    parse_mode=parse_mode
                )
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'Сообщение успешно отправлено пользователю {telegram_id}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка при отправке: {error}')
                    )
            finally:
                await bot.session.close()
        
        asyncio.run(send())

