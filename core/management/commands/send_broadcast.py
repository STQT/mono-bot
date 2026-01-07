"""
Management command для отправки массовых рассылок.
"""
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot
from core.models import BroadcastMessage
from core.messaging import send_broadcast_message


class Command(BaseCommand):
    help = 'Отправляет массовую рассылку'

    def add_arguments(self, parser):
        parser.add_argument(
            'broadcast_id',
            type=int,
            help='ID рассылки для отправки'
        )

    def handle(self, *args, **options):
        broadcast_id = options['broadcast_id']
        
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN не установлен!')
            )
            return
        
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        except BroadcastMessage.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Рассылка с ID {broadcast_id} не найдена')
            )
            return
        
        if broadcast.status != 'pending':
            self.stdout.write(
                self.style.WARNING(
                    f'Рассылка уже была отправлена (статус: {broadcast.get_status_display()})'
                )
            )
            return
        
        # Определяем, использовать ли Celery для больших рассылок
        LARGE_BROADCAST_THRESHOLD = 20000  # Порог для использования Celery
        
        # Предварительно оцениваем количество пользователей
        from core.models import TelegramUser
        users_query = TelegramUser.objects.filter(is_active=True)
        if broadcast.user_type_filter:
            users_query = users_query.filter(user_type=broadcast.user_type_filter)
        if broadcast.language_filter:
            users_query = users_query.filter(language=broadcast.language_filter)
        
        estimated_users = users_query.count()
        
        # Если пользователей много, используем Celery
        if estimated_users >= LARGE_BROADCAST_THRESHOLD:
            from core.tasks import send_broadcast_chained
            send_broadcast_chained.delay(broadcast.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Рассылка запущена через Celery ({estimated_users} пользователей). '
                    f'Проверьте статус в админке.'
                )
            )
        else:
            # Для небольших рассылок используем обычный метод
            async def run_broadcast():
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                try:
                    result = await send_broadcast_message(
                        broadcast=broadcast,
                        bot=bot,
                        user_type_filter=broadcast.user_type_filter
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Рассылка завершена!\n'
                            f'Всего: {result["total"]}\n'
                            f'Отправлено: {result["sent"]}\n'
                            f'Ошибок: {result["failed"]}'
                        )
                    )
                finally:
                    await bot.session.close()
            
            asyncio.run(run_broadcast())

