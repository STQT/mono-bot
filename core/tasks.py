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
from .utils import generate_qr_code_image, generate_qr_codes_batch, generate_qr_code_images_batch
from .messaging import send_message_to_user, TELEGRAM_MESSAGE_DELAY

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_qr_codes_batch_task(self, prev_result=None, **kwargs):
    """
    Генерирует один батч QR-кодов.
    
    Args:
        prev_result: Результат предыдущей задачи в цепочке (если есть)
        **kwargs: Может содержать generation_id, batch_start, batch_size
    """
    try:
        # Если есть результат предыдущей задачи, извлекаем параметры из него
        if prev_result and isinstance(prev_result, dict):
            generation_id = prev_result.get('generation_id') or kwargs.get('generation_id')
            batch_start = prev_result.get('batch_start') or kwargs.get('batch_start')
            batch_size = prev_result.get('batch_size') or kwargs.get('batch_size')
        else:
            # Иначе используем параметры из kwargs
            generation_id = kwargs.get('generation_id')
            batch_start = kwargs.get('batch_start')
            batch_size = kwargs.get('batch_size')
        
        # Проверяем, что все необходимые параметры есть
        if generation_id is None:
            raise ValueError("generation_id должен быть передан")
        if batch_start is None:
            raise ValueError("batch_start должен быть передан")
        if batch_size is None:
            raise ValueError("batch_size должен быть передан")
        
        generation = QRCodeGeneration.objects.get(id=generation_id)
        
        # Генерируем QR-коды для этого батча
        qr_codes = []
        batch_end = min(batch_start + batch_size, generation.quantity)
        
        # Сначала создаем все QR-коды в БД
        for i in range(batch_start, batch_end):
            qr_code = QRCode.create_code(
                code_type=generation.code_type,
                points=generation.points
            )
            qr_codes.append(qr_code)
        
        # Затем генерируем изображения батчем (переиспользуя один браузер)
        # Это значительно эффективнее, чем создавать браузер для каждого QR-кода
        # ВРЕМЕННО ЗАКОММЕНТИРОВАНО
        # try:
        #     generate_qr_code_images_batch(qr_codes)
        # except Exception as e:
        #     logger.error(f"Ошибка при генерации изображений для батча {batch_start}-{batch_end}: {e}")
        #     # Если батчевая генерация не удалась, пробуем по одному
        #     logger.info(f"Пробуем генерировать изображения по одному...")
        #     for qr_code in qr_codes:
        #         try:
        #             generate_qr_code_image(qr_code)
        #         except Exception as img_error:
        #             logger.error(f"Ошибка при генерации изображения для QR-кода {qr_code.code}: {img_error}")
        #             # Продолжаем с другими QR-кодами даже если один не удался
        
        # Добавляем QR-коды к генерации
        generation.qr_codes.add(*qr_codes)
        
        logger.info(
            f"Батч QR-кодов для генерации {generation_id}: "
            f"сгенерировано {len(qr_codes)} кодов (индексы {batch_start}-{batch_end-1})"
        )
        
        return {
            'generation_id': generation_id,
            'batch_start': batch_start,
            'batch_end': batch_end,
            'generated': len(qr_codes)
        }
        
    except QRCodeGeneration.DoesNotExist:
        logger.error(f"Генерация {generation_id} не найдена")
        return {'error': f'Generation {generation_id} not found'}
    except Exception as e:
        logger.error(f"Ошибка при генерации батча QR-кодов: {e}")
        raise


@shared_task(bind=True)
def finalize_qr_generation_task(self, prev_result=None, **kwargs):
    """
    Завершает генерацию QR-кодов и создает ZIP архив.
    
    Args:
        prev_result: Результат предыдущей задачи в цепочке (если есть)
        **kwargs: Может содержать generation_id
    """
    try:
        # Если есть результат предыдущей задачи, извлекаем generation_id из него
        if prev_result and isinstance(prev_result, dict):
            generation_id = prev_result.get('generation_id') or kwargs.get('generation_id')
        else:
            generation_id = kwargs.get('generation_id')
        
        # Проверяем, что generation_id есть
        if generation_id is None:
            raise ValueError("generation_id должен быть передан")
        
        generation = QRCodeGeneration.objects.get(id=generation_id)
        
        # Получаем все QR-коды для этой генерации
        qr_codes = list(generation.qr_codes.all())
        
        if not qr_codes:
            generation.status = 'failed'
            generation.error_message = 'Не было сгенерировано ни одного QR-кода'
            generation.save(update_fields=['status', 'error_message'])
            return {'error': 'No QR codes generated'}
        
        # Создаем ZIP архив
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
        zip_filename = f"qrcodes_{generation.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, 'qrcodes', 'generations', zip_filename)
        
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        
        logger.info(f"Создание ZIP архива для генерации {generation_id}: {len(qr_codes)} QR-кодов")
        
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
        
        logger.info(
            f"Генерация QR-кодов {generation_id} завершена: "
            f"сгенерировано {len(qr_codes)} кодов, ZIP архив создан"
        )
        
        return {
            'generation_id': generation_id,
            'total_generated': len(qr_codes),
            'zip_file': zip_filename
        }
        
    except QRCodeGeneration.DoesNotExist:
        logger.error(f"Генерация {generation_id} не найдена")
        return {'error': f'Generation {generation_id} not found'}
    except Exception as e:
        logger.error(f"Ошибка при завершении генерации QR-кодов: {e}")
        try:
            generation = QRCodeGeneration.objects.get(id=generation_id)
            generation.status = 'failed'
            generation.error_message = str(e)
            generation.save(update_fields=['status', 'error_message'])
        except:
            pass
        raise


@shared_task(bind=True)
def generate_qr_codes_task(self, generation_id):
    """
    Асинхронная задача для генерации QR-кодов.
    Разбивает большую генерацию на батчи для избежания таймаутов.
    
    Args:
        generation_id: ID объекта QRCodeGeneration
    """
    try:
        generation = QRCodeGeneration.objects.get(id=generation_id)
        generation.status = 'processing'
        generation.save(update_fields=['status'])
        
        # Размер батча (можно настроить через settings)
        BATCH_SIZE = getattr(settings, 'QR_CODE_BATCH_SIZE', 1000)
        
        # Если количество меньше или равно размеру батча, генерируем сразу
        if generation.quantity <= BATCH_SIZE:
            logger.info(f"Генерация {generation_id}: небольшое количество ({generation.quantity}), генерируем сразу")
            
            # Генерируем QR-коды
            qr_codes = []
            for _ in range(generation.quantity):
                qr_code = QRCode.create_code(
                    code_type=generation.code_type,
                    points=generation.points
                )
                # ВРЕМЕННО ЗАКОММЕНТИРОВАНО
                # generate_qr_code_image(qr_code)
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
            
            logger.info(f"Генерация {generation_id} завершена: {generation.quantity} QR-кодов")
            return f"Successfully generated {generation.quantity} QR codes"
        else:
            # Большое количество - разбиваем на батчи
            total_batches = (generation.quantity + BATCH_SIZE - 1) // BATCH_SIZE
            
            logger.info(
                f"Генерация {generation_id}: большое количество ({generation.quantity}), "
                f"разбиваем на {total_batches} батчей по {BATCH_SIZE} кодов"
            )
            
            # Создаем цепочку задач для батчей
            tasks = []
            for batch_num in range(total_batches):
                batch_start = batch_num * BATCH_SIZE
                # Передаем параметры как именованные аргументы
                # При использовании chain() результат предыдущей задачи будет передан как prev_result
                task = generate_qr_codes_batch_task.s(
                    generation_id=generation_id,
                    batch_start=batch_start,
                    batch_size=BATCH_SIZE
                )
                tasks.append(task)
            
            # Добавляем задачу завершения в конец цепочки
            # Она получит generation_id из результата последней задачи батча
            tasks.append(finalize_qr_generation_task.s(generation_id=generation_id))
            
            # Запускаем цепочку задач последовательно
            chain(*tasks).apply_async()
            
            logger.info(
                f"Запущена цепочка из {total_batches + 1} задач для генерации {generation_id}"
            )
            
            return {
                'generation_id': generation_id,
                'total_quantity': generation.quantity,
                'total_batches': total_batches,
                'batch_size': BATCH_SIZE
            }
        
    except QRCodeGeneration.DoesNotExist:
        logger.error(f"Генерация {generation_id} не найдена")
        return f"Generation {generation_id} not found"
    except Exception as e:
        logger.error(f"Ошибка при запуске генерации QR-кодов: {e}")
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
        
        photo_path = None
        if broadcast.image:
            try:
                photo_path = broadcast.image.path
            except (ValueError, OSError):
                pass

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
                            parse_mode='HTML',
                            photo_path=photo_path,
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

