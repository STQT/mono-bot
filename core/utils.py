"""
Utility functions for core app.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils import timezone
from .models import QRCode


def generate_qr_code_image(qr_code_instance):
    """
    Генерирует изображение с кодом (только текст, без QR-кода).
    Высокое качество изображения для печати.
    
    Args:
        qr_code_instance: Экземпляр модели QRCode
    
    Returns:
        str: Путь к сохраненному изображению
    """
    # Создаем директорию для QR-кодов, если её нет
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Параметры для высокого качества (DPI для печати)
    dpi = 300  # Высокое разрешение для печати
    scale_factor = dpi / 72  # Масштаб для перевода из точек в пиксели
    
    # Параметры для текста (в точках, затем умножим на scale_factor)
    padding_pt = 40
    code_font_size_pt = 72  # Крупный шрифт для кода
    serial_font_size_pt = 24  # Шрифт для серийного номера
    instruction_font_size_pt = 14  # Шрифт для инструкции
    
    # Конвертируем в пиксели с учетом DPI
    padding = int(padding_pt * scale_factor)
    code_font_size = int(code_font_size_pt * scale_factor)
    serial_font_size = int(serial_font_size_pt * scale_factor)
    instruction_font_size = int(instruction_font_size_pt * scale_factor)
    
    # Создаем объект для рисования (временно для измерения текста)
    temp_img = Image.new('RGB', (100, 100), 'white')
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Пытаемся загрузить шрифт с поддержкой кириллицы и латиницы
    font_code = None
    font_serial = None
    font_instruction = None
    
    # Список путей к шрифтам с поддержкой кириллицы
    font_paths = [
        # macOS
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
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
                font_code = ImageFont.truetype(font_path, code_font_size)
                font_serial = ImageFont.truetype(font_path, serial_font_size)
                font_instruction = ImageFont.truetype(font_path, instruction_font_size)
                break
        except:
            continue
    
    # Если не нашли подходящий шрифт, используем стандартный
    if font_code is None:
        font_code = ImageFont.load_default()
        font_serial = ImageFont.load_default()
        font_instruction = ImageFont.load_default()
    
    # Тексты для отображения
    code_text = qr_code_instance.code
    serial_text = f"Seriya raqami: {qr_code_instance.serial_number}"
    
    # Измеряем размеры текстов
    try:
        code_bbox = temp_draw.textbbox((0, 0), code_text, font=font_code)
        code_width = code_bbox[2] - code_bbox[0]
        code_height = code_bbox[3] - code_bbox[1]
    except:
        code_width = temp_draw.textlength(code_text, font=font_code)
        code_height = code_font_size
    
    try:
        serial_bbox = temp_draw.textbbox((0, 0), serial_text, font=font_serial)
        serial_width = serial_bbox[2] - serial_bbox[0]
        serial_height = serial_bbox[3] - serial_bbox[1]
    except:
        serial_width = temp_draw.textlength(serial_text, font=font_serial)
        serial_height = serial_font_size
    
    # Вычисляем размеры изображения
    max_text_width = max(code_width, serial_width)
    total_width = int(max_text_width + (padding * 2))
    total_height = int(padding + serial_height + padding + code_height + padding)
    
    # Создаем новое изображение с белым фоном и высоким разрешением
    img = Image.new('RGB', (total_width, total_height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Рисуем рамку вокруг изображения (опционально, для красоты)
    border_width = int(2 * scale_factor)
    draw.rectangle(
        [(border_width, border_width), (total_width - border_width, total_height - border_width)],
        outline='black',
        width=border_width
    )
    
    # Рисуем серийный номер вверху
    serial_x = (total_width - serial_width) // 2
    serial_y = padding
    draw.text((serial_x, serial_y), serial_text, fill='black', font=font_serial)
    
    # Рисуем код по центру (крупным шрифтом)
    code_x = (total_width - code_width) // 2
    code_y = serial_y + serial_height + padding
    draw.text((code_x, code_y), code_text, fill='black', font=font_code)
    
    # Сохраняем изображение с высоким качеством
    filename = f"{qr_code_instance.code.replace('-', '_')}.png"
    filepath = os.path.join(qr_dir, filename)
    
    # Сохраняем с высоким DPI для качества печати
    img.save(filepath, 'PNG', dpi=(dpi, dpi), quality=95)
    
    # Обновляем путь в модели
    qr_code_instance.image_path = filepath
    qr_code_instance.save(update_fields=['image_path'])
    
    return filepath


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

