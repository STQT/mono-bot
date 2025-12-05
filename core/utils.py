"""
Utility functions for core app.
"""
import os
import qrcode
from django.conf import settings
from django.utils import timezone
from .models import QRCode


def generate_qr_code_image(qr_code_instance):
    """
    Генерирует изображение QR-кода и сохраняет его.
    
    Args:
        qr_code_instance: Экземпляр модели QRCode
    
    Returns:
        str: Путь к сохраненному изображению
    """
    # Создаем директорию для QR-кодов, если её нет
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_code_instance.code)
    qr.make(fit=True)
    
    # Создаем изображение
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохраняем изображение (заменяем дефисы на подчеркивания для безопасности имени файла)
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

