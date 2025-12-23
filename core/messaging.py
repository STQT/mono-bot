"""
Утилиты для отправки сообщений через Telegram бота.
"""
import asyncio
import logging
from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramAPIError
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from .models import TelegramUser, BroadcastMessage

logger = logging.getLogger(__name__)

# Лимиты Telegram API
# 30 сообщений в секунду для broadcast
TELEGRAM_BROADCAST_RATE_LIMIT = 30  # сообщений в секунду
TELEGRAM_MESSAGE_DELAY = 1.0 / TELEGRAM_BROADCAST_RATE_LIMIT  # ~0.033 секунды между сообщениями


async def send_message_to_user(
    bot: Bot,
    user: TelegramUser,
    text: str,
    parse_mode: Optional[str] = None,
    disable_notification: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Отправляет сообщение конкретному пользователю.
    
    Args:
        bot: Экземпляр бота
        user: Пользователь Telegram
        text: Текст сообщения
        parse_mode: Режим парсинга (HTML, Markdown)
        disable_notification: Отключить уведомление
    
    Returns:
        tuple: (успешно ли отправлено, сообщение об ошибке если есть)
    """
    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=text,
            parse_mode=parse_mode,
            disable_notification=disable_notification
        )
        
        # Обновляем время последнего сообщения
        @sync_to_async
        def update_user_success():
            user.last_message_sent_at = timezone.now()
            user.is_active = True
            user.blocked_bot_at = None
            user.save(update_fields=['last_message_sent_at', 'is_active', 'blocked_bot_at'])
        
        await update_user_success()
        
        return True, None
        
    except TelegramForbiddenError as e:
        # Пользователь заблокировал бота
        logger.warning(f"Пользователь {user.telegram_id} заблокировал бота: {e}")
        
        @sync_to_async
        def update_user_blocked():
            user.is_active = False
            user.blocked_bot_at = timezone.now()
            user.save(update_fields=['is_active', 'blocked_bot_at'])
        
        await update_user_blocked()
        return False, "Пользователь заблокировал бота"
        
    except TelegramBadRequest as e:
        # Неверный запрос (пользователь не найден и т.д.)
        logger.warning(f"Ошибка при отправке пользователю {user.telegram_id}: {e}")
        
        @sync_to_async
        def update_user_inactive():
            user.is_active = False
            user.save(update_fields=['is_active'])
        
        await update_user_inactive()
        return False, f"Ошибка запроса: {str(e)}"
        
    except TelegramAPIError as e:
        # Другие ошибки API
        logger.error(f"Ошибка Telegram API для пользователя {user.telegram_id}: {e}")
        return False, f"Ошибка API: {str(e)}"
        
    except Exception as e:
        # Неожиданные ошибки
        logger.error(f"Неожиданная ошибка при отправке пользователю {user.telegram_id}: {e}")
        return False, f"Неожиданная ошибка: {str(e)}"


async def send_broadcast_message(
    broadcast: BroadcastMessage,
    bot: Bot,
    user_type_filter: Optional[str] = None
) -> dict:
    """
    Отправляет массовое сообщение всем активным пользователям.
    
    Args:
        broadcast: Объект рассылки
        bot: Экземпляр бота
        user_type_filter: Фильтр по типу пользователя (опционально)
    
    Returns:
        dict: Статистика отправки
    """
    # Получаем активных пользователей
    @sync_to_async
    def get_users():
        users_query = TelegramUser.objects.filter(is_active=True)
        if user_type_filter:
            users_query = users_query.filter(user_type=user_type_filter)
        return list(users_query)
    
    users = await get_users()
    total_users = len(users)
    
    # Обновляем статистику рассылки
    @sync_to_async
    def update_broadcast_start():
        broadcast.total_users = total_users
        broadcast.status = 'sending'
        broadcast.started_at = timezone.now()
        broadcast.save(update_fields=['total_users', 'status', 'started_at'])
    
    await update_broadcast_start()
    
    sent_count = 0
    failed_count = 0
    
    logger.info(f"Начало рассылки '{broadcast.title}' для {total_users} пользователей")
    
    # Отправляем сообщения с учетом лимитов
    for i, user in enumerate(users):
        try:
            success, error = await send_message_to_user(
                bot=bot,
                user=user,
                text=broadcast.message_text,
                parse_mode='HTML'
            )
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
                logger.warning(f"Не удалось отправить пользователю {user.telegram_id}: {error}")
            
            # Обновляем статистику каждые 10 сообщений
            if (i + 1) % 10 == 0:
                @sync_to_async
                def update_broadcast_progress():
                    broadcast.sent_count = sent_count
                    broadcast.failed_count = failed_count
                    broadcast.save(update_fields=['sent_count', 'failed_count'])
                
                await update_broadcast_progress()
            
            # Соблюдаем лимит Telegram API (30 сообщений в секунду)
            # Добавляем небольшую задержку между сообщениями
            if i < total_users - 1:  # Не ждем после последнего сообщения
                await asyncio.sleep(TELEGRAM_MESSAGE_DELAY)
                
        except Exception as e:
            logger.error(f"Критическая ошибка при отправке пользователю {user.telegram_id}: {e}")
            failed_count += 1
            # Помечаем пользователя как неактивного при критической ошибке
            @sync_to_async
            def mark_user_inactive():
                user.is_active = False
                user.save(update_fields=['is_active'])
            
            await mark_user_inactive()
    
    # Завершаем рассылку
    @sync_to_async
    def update_broadcast_complete():
        broadcast.sent_count = sent_count
        broadcast.failed_count = failed_count
        broadcast.status = 'completed'
        broadcast.completed_at = timezone.now()
        broadcast.save(update_fields=['sent_count', 'failed_count', 'status', 'completed_at'])
    
    await update_broadcast_complete()
    
    logger.info(
        f"Рассылка '{broadcast.title}' завершена: "
        f"отправлено {sent_count}, ошибок {failed_count} из {total_users}"
    )
    
    return {
        'total': total_users,
        'sent': sent_count,
        'failed': failed_count
    }


async def send_personal_message(
    bot: Bot,
    telegram_id: int,
    text: str,
    parse_mode: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Отправляет персональное сообщение конкретному пользователю.
    
    Args:
        bot: Экземпляр бота
        telegram_id: Telegram ID пользователя
        text: Текст сообщения
        parse_mode: Режим парсинга (HTML, Markdown)
    
    Returns:
        tuple: (успешно ли отправлено, сообщение об ошибке если есть)
    """
    @sync_to_async
    def get_user():
        try:
            return TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return None
    
    user = await get_user()
    if user is None:
        return False, "Пользователь не найден"
    
    return await send_message_to_user(
        bot=bot,
        user=user,
        text=text,
        parse_mode=parse_mode
    )

