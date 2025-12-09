"""
Celery tasks for core app.
"""
import os
import zipfile
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import QRCode, QRCodeGeneration
from .utils import generate_qr_code_image, generate_qr_codes_batch


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

