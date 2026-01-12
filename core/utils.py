"""
Utility functions for core app.
"""
import os
import time
import threading
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.utils import timezone
from .models import QRCode

# Семафор для ограничения одновременных операций Playwright
_playwright_semaphore = threading.Semaphore(3)  # Максимум 3 одновременных операции


def generate_qr_code_image(qr_code_instance):
    """
    Генерирует изображение с кодом (только текст, без QR-кода).
    Использует HTML/CSS и Playwright для рендеринга в PNG.
    Высокое качество изображения для печати.
    
    Примечание: Для работы необходимо установить браузеры Playwright:
    python -m playwright install chromium
    
    Args:
        qr_code_instance: Экземпляр модели QRCode
    
    Returns:
        str: Путь к сохраненному изображению
    """
    # Используем семафор для ограничения одновременных операций
    with _playwright_semaphore:
        # Создаем директорию для QR-кодов, если её нет
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Тексты для отображения
        code_text = qr_code_instance.code
        serial_text = f"Seriya raqami: {qr_code_instance.serial_number}"
        
        # Получаем username бота для инструкции
        bot_username = settings.TELEGRAM_BOT_USERNAME
        if bot_username:
            instruction_text = f"Botga o'ting @{bot_username} va kodni kiriting"
        else:
            instruction_text = "Botga o'ting va kodni kiriting"
        
        # Создаем HTML с CSS
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    width: 1000px;
                    height: 600px;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
                    border: 4px solid black;
                    padding: 40px;
                }}
                .serial {{
                    font-size: 28px;
                    color: black;
                    margin-bottom: 40px;
                    text-align: center;
                }}
                .code {{
                    font-size: 150px;
                    font-weight: bold;
                    color: black;
                    letter-spacing: 8px;
                    margin-bottom: 40px;
                    text-align: center;
                    line-height: 1;
                }}
                .instruction {{
                    font-size: 20px;
                    color: black;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="serial">{serial_text}</div>
            <div class="code">{code_text}</div>
            <div class="instruction">{instruction_text}</div>
        </body>
        </html>
        """
        
        # Сохраняем HTML во временный файл
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html_path = f.name
        
        try:
            # Генерируем изображение с помощью Playwright
            # ВРЕМЕННО ЗАКОММЕНТИРОВАНО
            # filename = f"{qr_code_instance.code.replace('-', '_')}.png"
            # filepath = os.path.join(qr_dir, filename)
            # 
            # with sync_playwright() as p:
            #     browser = p.chromium.launch(headless=True)
            #     try:
            #         page = browser.new_page()
            #         page.set_viewport_size({"width": 1000, "height": 600})
            #         page.goto(f"file://{temp_html_path}")
            #         page.screenshot(path=filepath, full_page=False)
            #     finally:
            #         browser.close()
            # 
            # # Обновляем путь в модели
            # qr_code_instance.image_path = filepath
            # qr_code_instance.save(update_fields=['image_path'])
            # 
            # # Небольшая задержка для освобождения ресурсов
            # time.sleep(0.1)
            # 
            # return filepath
            pass
        finally:
            # Удаляем временный HTML файл
            try:
                os.unlink(temp_html_path)
            except:
                pass


def generate_qr_code_images_batch(qr_code_instances):
    """
    Генерирует изображения для списка QR-кодов, переиспользуя один браузер.
    Это более эффективно, чем создание браузера для каждого QR-кода.
    
    Args:
        qr_code_instances: Список экземпляров QRCode
    
    Returns:
        list: Список путей к сохраненным изображениям
    """
    if not qr_code_instances:
        return []
    
    import logging
    logger = logging.getLogger(__name__)
    
    # Создаем директорию для QR-кодов, если её нет
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Получаем username бота для инструкции
    bot_username = settings.TELEGRAM_BOT_USERNAME
    if bot_username:
        instruction_text = f"Botga o'ting @{bot_username} va kodni kiriting"
    else:
        instruction_text = "Botga o'ting va kodni kiriting"
    
    filepaths = []
    import tempfile
    temp_files = []
    
    # Сначала генерируем все изображения с помощью Playwright
    # ВРЕМЕННО ЗАКОММЕНТИРОВАНО
    # try:
    #     # Используем один браузер для всех QR-кодов
    #     # Семафор ограничивает одновременные операции Playwright
    #     logger.info(f"Начало батчевой генерации изображений для {len(qr_code_instances)} QR-кодов")
    #     
    #     with _playwright_semaphore:
    #         with sync_playwright() as p:
    #             browser = None
    #             try:
    #                 browser = p.chromium.launch(headless=True)
    #                 logger.debug("Браузер запущен для батчевой генерации")
    #                 
    #                 for idx, qr_code_instance in enumerate(qr_code_instances, 1):
    #                     try:
    #                         # Тексты для отображения
    #                         code_text = qr_code_instance.code
    #                         serial_text = f"Seriya raqami: {qr_code_instance.serial_number}"
    #                         
    #                         # Создаем HTML с CSS
    #                         html_content = f"""
    #                         <!DOCTYPE html>
    #                         <html>
    #                         <head>
    #                             <meta charset="UTF-8">
    #                             <style>
    #                                 * {{
    #                                     margin: 0;
    #                                     padding: 0;
    #                                     box-sizing: border-box;
    #                                 }}
    #                                 body {{
    #                                     width: 1000px;
    #                                     height: 600px;
    #                                     background: white;
    #                                     display: flex;
    #                                     flex-direction: column;
    #                                     justify-content: center;
    #                                     align-items: center;
    #                                     font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
    #                                     border: 4px solid black;
    #                                     padding: 40px;
    #                                 }}
    #                                 .serial {{
    #                                     font-size: 28px;
    #                                     color: black;
    #                                     margin-bottom: 40px;
    #                                     text-align: center;
    #                                 }}
    #                                 .code {{
    #                                     font-size: 150px;
    #                                     font-weight: bold;
    #                                     color: black;
    #                                     letter-spacing: 8px;
    #                                     margin-bottom: 40px;
    #                                     text-align: center;
    #                                     line-height: 1;
    #                                 }}
    #                                 .instruction {{
    #                                     font-size: 20px;
    #                                     color: black;
    #                                     text-align: center;
    #                                 }}
    #                             </style>
    #                         </head>
    #                         <body>
    #                             <div class="serial">{serial_text}</div>
    #                             <div class="code">{code_text}</div>
    #                             <div class="instruction">{instruction_text}</div>
    #                         </body>
    #                         </html>
    #                         """
    #                         
    #                         # Сохраняем HTML во временный файл
    #                         with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
    #                             f.write(html_content)
    #                             temp_html_path = f.name
    #                             temp_files.append(temp_html_path)
    #                         
    #                         # Генерируем изображение
    #                         filename = f"{qr_code_instance.code.replace('-', '_')}.png"
    #                         filepath = os.path.join(qr_dir, filename)
    #                         
    #                         page = None
    #                         try:
    #                             page = browser.new_page()
    #                             page.set_viewport_size({"width": 1000, "height": 600})
    #                             page.goto(f"file://{temp_html_path}")
    #                             page.screenshot(path=filepath, full_page=False)
    #                             filepaths.append(filepath)
    #                             
    #                             # Только устанавливаем путь в памяти, НЕ сохраняем в БД здесь
    #                             # Сохранение будет сделано после полного выхода из Playwright контекста
    #                             qr_code_instance.image_path = filepath
    #                             
    #                             if idx % 50 == 0:
    #                                 logger.info(f"Сгенерировано {idx}/{len(qr_code_instances)} изображений")
    #                         except Exception as e:
    #                             # Логируем ошибку, но продолжаем с другими QR-кодами
    #                             logger.error(f"Ошибка при генерации изображения для QR-кода {qr_code_instance.code} ({idx}/{len(qr_code_instances)}): {e}")
    #                             raise
    #                         finally:
    #                             if page:
    #                                 try:
    #                                     page.close()
    #                                 except:
    #                                     pass
    #                             # Небольшая задержка для освобождения ресурсов
    #                             if idx < len(qr_code_instances):
    #                                 time.sleep(0.1)
    #                     
    #                     except Exception as e:
    #                         logger.error(f"Ошибка при обработке QR-кода {idx}/{len(qr_code_instances)}: {e}")
    #                         # Продолжаем с другими QR-кодами
    #                         continue
    #                 
    #                 logger.info(f"Батчевая генерация изображений завершена: сгенерировано {len(filepaths)}/{len(qr_code_instances)} изображений")
    #                 
    #             finally:
    #                 if browser:
    #                     try:
    #                         browser.close()
    #                         logger.debug("Браузер закрыт")
    #                     except:
    #                         pass
    # finally:
    #     # Удаляем временные HTML файлы
    #     for temp_file in temp_files:
    #         try:
    #             os.unlink(temp_file)
    #         except:
    #             pass
    
    # ВАЖНО: После полного выхода из всех контекстных менеджеров Playwright сохраняем в БД
    # Используем отдельный поток для гарантии, что мы вне async контекста Playwright
    qr_codes_to_update = [qr for qr in qr_code_instances if qr.image_path]
    if qr_codes_to_update:
        logger.info(f"Сохранение путей к изображениям в БД для {len(qr_codes_to_update)} QR-кодов...")
        
        # Используем threading для выполнения сохранения в отдельном потоке
        # Это гарантирует, что мы полностью вне async контекста Playwright
        # и Django ORM может работать в чистом синхронном контексте
        saved_count = [0]  # Используем список для изменяемого значения в замыкании
        error_occurred = [False]
        
        def save_to_db():
            try:
                # Используем bulk_update для массового сохранения
                QRCode.objects.bulk_update(qr_codes_to_update, ['image_path'], batch_size=100)
                saved_count[0] = len(qr_codes_to_update)
                logger.info(f"Сохранено {saved_count[0]} путей к изображениям в БД с помощью bulk_update")
            except Exception as e:
                logger.error(f"Ошибка при bulk_update путей изображений: {e}")
                error_occurred[0] = True
                # Fallback: сохраняем по одному в транзакции
                logger.info("Пробуем сохранить по одному в транзакции...")
                from django.db import transaction
                saved = 0
                for qr_code_instance in qr_codes_to_update:
                    try:
                        with transaction.atomic():
                            qr_code_instance.save(update_fields=['image_path'])
                        saved += 1
                    except Exception as save_error:
                        logger.error(f"Ошибка при сохранении пути изображения для QR-кода {qr_code_instance.code}: {save_error}")
                saved_count[0] = saved
                logger.info(f"Сохранено {saved_count[0]}/{len(qr_codes_to_update)} путей к изображениям в БД по одному")
        
        # Выполняем сохранение в отдельном потоке для гарантии синхронного контекста
        save_thread = threading.Thread(target=save_to_db)
        save_thread.start()
        save_thread.join()  # Ждем завершения сохранения
        
        if error_occurred[0] and saved_count[0] < len(qr_codes_to_update):
            logger.warning(f"Не все QR-коды были сохранены: {saved_count[0]}/{len(qr_codes_to_update)}")
    
    return filepaths


def generate_qr_codes_batch(code_type, quantity, points=None):
    """
    Генерирует несколько QR-кодов за раз.
    
    Args:
        code_type: Тип кода ('electrician' или 'seller')
        quantity: Количество QR-кодов для генерации
        points: Количество баллов (опционально, используется значение по умолчанию если не указано)
    
    Returns:
        list: Список созданных экземпляров QRCode
    """
    qr_codes = []
    
    for _ in range(quantity):
        qr_code = QRCode.create_code(code_type, points=points)
        generate_qr_code_image(qr_code)
        qr_codes.append(qr_code)
    
    return qr_codes


