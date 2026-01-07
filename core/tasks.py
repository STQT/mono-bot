"""
Celery tasks for core app.
"""
import os
import zipfile
import asyncio
import logging
from celery import shared_task, chain
from django.conf import settings
from django.utils import timezone
from aiogram import Bot
from .models import QRCode, QRCodeGeneration, BroadcastMessage, TelegramUser
from .utils import generate_qr_code_image, generate_qr_codes_batch
from .messaging import send_message_to_user, TELEGRAM_MESSAGE_DELAY

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_qr_codes_task(self, generation_id):
    """
    Асинхронная задача для генерации QR-кодов.
    
    Args:
        generation_id: ID объекта QRCodeGeneration
    """
    try:
        generation = QRCodeGeneration.objects.get(id=generation_id)
        generation.status = 'processing'
        generation.save(update_fields=['status'])
        
        # Генерируем QR-коды
        qr_codes = []
        for _ in range(generation.quantity):
            qr_code = QRCode.create_code(
                code_type=generation.code_type,
                points=generation.points
            )
            generate_qr_code_image(qr_code)
            qr_codes.append(qr_code)
        
        # Сохраняем QR-коды в генерацию
        generation.qr_codes.set(qr_codes)
        
        # Создаем ZIP архив
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
        zip_filename = f"qrcodes_{generation.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', 'generations', zip_filename)
        
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for qr_code in qr_codes:
                if qr_code.image_path and os.path.exists(qr_code.image_path):
                    zip_file.write(
                        qr_code.image_path,
                        os.path.basename(qr_code.image_path)
                    )
        
        # Сохраняем путь к ZIP файлу
        generation.zip_file.name = f"qrcodes/generations/{zip_filename}"
        generation.status = 'completed'
        generation.completed_at = timezone.now()
        generation.save(update_fields=['zip_file', 'status', 'completed_at'])
        
        return f"Successfully generated {generation.quantity} QR codes"
        
    except QRCodeGeneration.DoesNotExist:
        return f"Generation {generation_id} not found"
    except Exception as e:
        # Сохраняем ошибку
        try:
            generation = QRCodeGeneration.objects.get(id=generation_id)
            generation.status = 'failed'
            generation.error_message = str(e)
            generation.save(update_fields=['status', 'error_message'])
        except:
            pass
        raise


@shared_task(bind=True)
def send_broadcast_batch(self, broadcast_id, user_ids, batch_number, total_batches):
    """
    Отправляет батч сообщений пользователям.
    
    Args:
        broadcast_id: ID объекта BroadcastMessage
        user_ids: Список ID пользователей для отправки
        batch_number: Номер текущего батча
        total_batches: Общее количество батчей
    """
    try:
        broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        
        # Получаем пользователей
        users = list(TelegramUser.objects.filter(id__in=user_ids))
        
        async def send_batch():
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            try:
                sent = 0
                failed = 0
                
                for i, user in enumerate(users):
                    try:
                        success, error = await send_message_to_user(
                            bot=bot,
                            user=user,
                            text=broadcast.message_text,
                            parse_mode='HTML'
                        )
                        
                        if success:
                            sent += 1
                        else:
                            failed += 1
                            logger.warning(f"Не удалось отправить пользователю {user.telegram_id}: {error}")
                        
                        # Соблюдаем лимит Telegram API
                        if i < len(users) - 1:
                            await asyncio.sleep(TELEGRAM_MESSAGE_DELAY)
                            
                    except Exception as e:
                        logger.error(f"Ошибка при отправке пользователю {user.telegram_id}: {e}")
                        failed += 1
                
                return sent, failed
            finally:
                await bot.session.close()
        
        sent, failed = asyncio.run(send_batch())
        
        # Обновляем статистику рассылки
        broadcast.sent_count += sent
        broadcast.failed_count += failed
        broadcast.save(update_fields=['sent_count', 'failed_count'])
        
        logger.info(
            f"Батч {batch_number}/{total_batches} рассылки '{broadcast.title}' завершен: "
            f"отправлено {sent}, ошибок {failed}"
        )
        
        return {
            'batch_number': batch_number,
            'sent': sent,
            'failed': failed
        }
        
    except BroadcastMessage.DoesNotExist:
        logger.error(f"Рассылка {broadcast_id} не найдена")
        return {'error': f'Broadcast {broadcast_id} not found'}
    except Exception as e:
        logger.error(f"Ошибка при отправке батча {batch_number}: {e}")
        # Обновляем статистику ошибок
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
            broadcast.failed_count += len(user_ids)
            broadcast.save(update_fields=['failed_count'])
        except:
            pass
        raise


@shared_task(bind=True)
def send_broadcast_chained(self, broadcast_id):
    """
    Запускает цепочку задач для отправки большой рассылки.
    Разбивает пользователей на батчи и отправляет последовательно.
    
    Args:
        broadcast_id: ID объекта BroadcastMessage
    """
    try:
        broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        
        # Получаем список пользователей с применением фильтров
        users_query = TelegramUser.objects.filter(is_active=True)
        
        # Фильтр по типу пользователя
        if broadcast.user_type_filter:
            users_query = users_query.filter(user_type=broadcast.user_type_filter)
        
        # Фильтр по языку
        if broadcast.language_filter:
            users_query = users_query.filter(language=broadcast.language_filter)
        
        # Фильтр по региону
        if broadcast.region_filter:
            from core.regions import get_region_by_coordinates
            
            users_with_location = list(users_query.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ))
            
            filtered_user_ids = []
            for user in users_with_location:
                user_region = get_region_by_coordinates(user.latitude, user.longitude)
                if user_region == broadcast.region_filter:
                    filtered_user_ids.append(user.id)
            
            if filtered_user_ids:
                users_query = users_query.filter(id__in=filtered_user_ids)
            else:
                users_query = users_query.none()
        
        user_ids = list(users_query.values_list('id', flat=True))
        total_users = len(user_ids)
        
        # Обновляем статистику рассылки
        broadcast.total_users = total_users
        broadcast.status = 'sending'
        broadcast.started_at = timezone.now()
        broadcast.save(update_fields=['total_users', 'status', 'started_at'])
        
        # Размер батча (можно настроить через settings)
        BATCH_SIZE = getattr(settings, 'BROADCAST_BATCH_SIZE', 1000)
        
        # Разбиваем на батчи
        batches = []
        for i in range(0, total_users, BATCH_SIZE):
            batch_user_ids = user_ids[i:i + BATCH_SIZE]
            batches.append(batch_user_ids)
        
        total_batches = len(batches)
        
        logger.info(
            f"Начало рассылки '{broadcast.title}' для {total_users} пользователей "
            f"({total_batches} батчей по {BATCH_SIZE} пользователей)"
        )
        
        # Создаем цепочку задач
        if batches:
            # Создаем задачи для каждого батча
            tasks = []
            for batch_num, batch_user_ids in enumerate(batches, 1):
                task = send_broadcast_batch.s(
                    broadcast_id=broadcast_id,
                    user_ids=batch_user_ids,
                    batch_number=batch_num,
                    total_batches=total_batches
                )
                tasks.append(task)
            
            # Добавляем задачу завершения в конец цепочки
            tasks.append(finalize_broadcast.s(broadcast_id=broadcast_id))
            
            # Запускаем цепочку задач последовательно
            chain(*tasks).apply_async()
            
            logger.info(f"Запущена цепочка из {total_batches + 1} задач для рассылки {broadcast_id}")
        else:
            # Если нет пользователей, завершаем рассылку
            broadcast.status = 'completed'
            broadcast.completed_at = timezone.now()
            broadcast.save(update_fields=['status', 'completed_at'])
            logger.info(f"Рассылка '{broadcast.title}' не имеет пользователей для отправки")
        
        return {
            'total_users': total_users,
            'total_batches': total_batches,
            'batch_size': BATCH_SIZE
        }
        
    except BroadcastMessage.DoesNotExist:
        logger.error(f"Рассылка {broadcast_id} не найдена")
        return {'error': f'Broadcast {broadcast_id} not found'}
    except Exception as e:
        logger.error(f"Ошибка при запуске рассылки {broadcast_id}: {e}")
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
            broadcast.status = 'failed'
            broadcast.save(update_fields=['status'])
        except:
            pass
        raise


@shared_task(bind=True)
def finalize_broadcast(self, broadcast_id):
    """
    Завершает рассылку после отправки всех батчей.
    
    Args:
        broadcast_id: ID объекта BroadcastMessage
    """
    try:
        broadcast = BroadcastMessage.objects.get(id=broadcast_id)
        broadcast.status = 'completed'
        broadcast.completed_at = timezone.now()
        broadcast.save(update_fields=['status', 'completed_at'])
        
        logger.info(
            f"Рассылка '{broadcast.title}' завершена: "
            f"отправлено {broadcast.sent_count}, ошибок {broadcast.failed_count} из {broadcast.total_users}"
        )
        
        return {
            'total': broadcast.total_users,
            'sent': broadcast.sent_count,
            'failed': broadcast.failed_count
        }
    except BroadcastMessage.DoesNotExist:
        logger.error(f"Рассылка {broadcast_id} не найдена")
        return {'error': f'Broadcast {broadcast_id} not found'}

