"""
Utility functions for core app.
"""
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils import timezone
from .models import QRCode


def generate_qr_code_image(qr_code_instance):
    """
    Генерирует изображение QR-кода с серийным номером, штрих-кодом и инструкцией.
    
    Args:
        qr_code_instance: Экземпляр модели QRCode
    
    Returns:
        str: Путь к сохраненному изображению
    """
    # Создаем директорию для QR-кодов, если её нет
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Создаем QR-код с ссылкой на бота
    bot_username = settings.TELEGRAM_BOT_USERNAME
    if bot_username:
        qr_data = f"https://t.me/{bot_username}?start=qr:{qr_code_instance.hash_code}"
    else:
        # Fallback на код, если username не установлен
        qr_data = qr_code_instance.code
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Создаем изображение QR-кода
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Размеры QR-кода
    qr_size = qr_img.size[0]
    
    # Параметры для текста
    padding = 40
    text_height = 30
    instruction_height = 60
    
    # Размеры итогового изображения
    total_width = qr_size + (padding * 2)
    total_height = qr_size + (padding * 3) + (text_height * 2) + instruction_height
    
    # Создаем новое изображение с белым фоном
    img = Image.new('RGB', (total_width, total_height), 'white')
    
    # Вставляем QR-код в центр
    qr_x = padding
    qr_y = padding + text_height
    img.paste(qr_img, (qr_x, qr_y))
    
    # Создаем объект для рисования
    draw = ImageDraw.Draw(img)
    
    # Пытаемся загрузить шрифт с поддержкой кириллицы
    font_large = None
    font_medium = None
    font_small = None
    
    # Список путей к шрифтам с поддержкой кириллицы
    font_paths = [
        # macOS
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows (если запускается на Windows)
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    
    # Пытаемся найти подходящий шрифт
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font_large = ImageFont.truetype(font_path, 24)
                font_medium = ImageFont.truetype(font_path, 18)
                font_small = ImageFont.truetype(font_path, 14)
                break
        except:
            continue
    
    # Если не нашли подходящий шрифт, используем стандартный
    if font_large is None:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Рисуем серийный номер вверху (только серийный номер, без лишнего текста)
    serial_text = f"Seriya raqami: {qr_code_instance.serial_number}"
    # Используем textlength для более точного расчета ширины
    try:
        text_bbox = draw.textbbox((0, 0), serial_text, font=font_large)
        text_width = text_bbox[2] - text_bbox[0]
    except:
        # Fallback для старых версий PIL
        text_width = draw.textlength(serial_text, font=font_large)
    text_x = (total_width - text_width) // 2
    text_y = 15  # Отступ сверху
    draw.text((text_x, text_y), serial_text, fill='black', font=font_large)
    
    # Рисуем штрих-код (текст кода) под QR-кодом
    barcode_text = qr_code_instance.code
    try:
        text_bbox = draw.textbbox((0, 0), barcode_text, font=font_medium)
        text_width = text_bbox[2] - text_bbox[0]
    except:
        text_width = draw.textlength(barcode_text, font=font_medium)
    text_x = (total_width - text_width) // 2
    text_y = qr_y + qr_size + 15
    draw.text((text_x, text_y), barcode_text, fill='black', font=font_medium)
    
    # Рисуем инструкцию внизу (на узбекском латиница)
    bot_username = settings.TELEGRAM_BOT_USERNAME
    if bot_username:
        instruction_text = f"QR-kodni skanerlang yoki botni oching @{bot_username}"
    else:
        instruction_text = "QR-kodni skanerlang yoki botni oching"
    
    instruction_text2 = f"va shtrix-kodni kiriting: {barcode_text}"
    
    # Первая строка инструкции
    try:
        text_bbox = draw.textbbox((0, 0), instruction_text, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
    except:
        text_width = draw.textlength(instruction_text, font=font_small)
    text_x = (total_width - text_width) // 2
    text_y = text_y + 25  # Отступ от штрих-кода
    draw.text((text_x, text_y), instruction_text, fill='black', font=font_small)
    
    # Вторая строка инструкции
    try:
        text_bbox = draw.textbbox((0, 0), instruction_text2, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
    except:
        text_width = draw.textlength(instruction_text2, font=font_small)
    text_x = (total_width - text_width) // 2
    text_y = text_y + 20  # Отступ между строками
    draw.text((text_x, text_y), instruction_text2, fill='black', font=font_small)
    
    # Сохраняем изображение
    filename = f"{qr_code_instance.code.replace('-', '_')}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)
    
    # Обновляем путь в модели
    qr_code_instance.image_path = filepath
    qr_code_instance.save(update_fields=['image_path'])
    
    return filepath


def generate_qr_codes_batch(code_type, quantity):
    """
    Генерирует несколько QR-кодов за раз.
    
    Args:
        code_type: Тип кода ('electrician' или 'seller')
        quantity: Количество QR-кодов для генерации
    
    Returns:
        list: Список созданных экземпляров QRCode
    """
    qr_codes = []
    
    for _ in range(quantity):
        qr_code = QRCode.create_code(code_type)
        generate_qr_code_image(qr_code)
        qr_codes.append(qr_code)
    
    return qr_codes

