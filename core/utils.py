"""
Utility functions for core app.
"""
import os
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.utils import timezone
from .models import QRCode


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
        filename = f"{qr_code_instance.code.replace('-', '_')}.png"
        filepath = os.path.join(qr_dir, filename)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1000, "height": 600})
            page.goto(f"file://{temp_html_path}")
            page.screenshot(path=filepath, full_page=False)
            browser.close()
        
        # Обновляем путь в модели
        qr_code_instance.image_path = filepath
        qr_code_instance.save(update_fields=['image_path'])
        
        return filepath
    finally:
        # Удаляем временный HTML файл
        try:
            os.unlink(temp_html_path)
        except:
            pass


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


