"""
Core models for the mona project.
"""
import hashlib
import secrets
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    """Модель пользователя Telegram."""
    USER_TYPE_CHOICES = [
        ('electrician', 'Электрик'),
        ('seller', 'Продавец'),
    ]
    
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        null=True,
        blank=True
    )
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name or 'Unknown'} (@{self.username or 'no_username'})"


class QRCode(models.Model):
    """Модель QR-кода (скретч-карты)."""
    CODE_TYPE_CHOICES = [
        ('electrician', 'Электрик (E-)'),
        ('seller', 'Продавец (D-)'),
    ]
    
    code = models.CharField(max_length=255, unique=True, db_index=True)
    code_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES)
    hash_code = models.CharField(max_length=64, unique=True, db_index=True)
    image_path = models.CharField(max_length=500, null=True, blank=True)
    points = models.IntegerField(validators=[MinValueValidator(0)])
    generated_at = models.DateTimeField(auto_now_add=True)
    scanned_at = models.DateTimeField(null=True, blank=True)
    scanned_by = models.ForeignKey(
        TelegramUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scanned_qrcodes'
    )
    is_scanned = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'QR-код'
        verbose_name_plural = 'QR-коды'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['hash_code']),
            models.Index(fields=['is_scanned']),
        ]
    
    def __str__(self):
        masked_code = self.code[:4] + '*' * (len(self.code) - 8) + self.code[-4:] if len(self.code) > 8 else self.code
        return f"{masked_code} ({self.get_code_type_display()})"
    
    @classmethod
    def generate_hash(cls):
        """Генерирует уникальный хеш для QR-кода."""
        while True:
            hash_code = secrets.token_hex(16)
            if not cls.objects.filter(hash_code=hash_code).exists():
                return hash_code
    
    @classmethod
    def create_code(cls, code_type, points=None):
        """Создает новый QR-код."""
        from django.conf import settings
        
        hash_code = cls.generate_hash()
        prefix = 'E-' if code_type == 'electrician' else 'D-'
        code = f"{prefix}{hash_code}"
        
        if points is None:
            points = settings.ELECTRICIAN_POINTS if code_type == 'electrician' else settings.SELLER_POINTS
        
        return cls.objects.create(
            code=code,
            code_type=code_type,
            hash_code=hash_code,
            points=points
        )


class QRCodeScanAttempt(models.Model):
    """Модель для отслеживания попыток сканирования QR-кода."""
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='scan_attempts'
    )
    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name='scan_attempts'
    )
    attempted_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Попытка сканирования'
        verbose_name_plural = 'Попытки сканирования'
        ordering = ['-attempted_at']
        unique_together = [['user', 'qr_code']]
    
    def __str__(self):
        status = 'Успешно' if self.is_successful else 'Неудачно'
        return f"{self.user} - {self.qr_code.code[:10]}... - {status}"


class Gift(models.Model):
    """Модель подарка."""
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='gifts/', verbose_name='Изображение')
    points_cost = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Стоимость в баллах'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Подарок'
        verbose_name_plural = 'Подарки'
        ordering = ['points_cost', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.points_cost} баллов)"


class GiftRedemption(models.Model):
    """Модель получения подарка пользователем."""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('completed', 'Выполнено'),
    ]
    
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='gift_redemptions',
        verbose_name='Пользователь'
    )
    gift = models.ForeignKey(
        Gift,
        on_delete=models.CASCADE,
        related_name='redemptions',
        verbose_name='Подарок'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Запрошено')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Обработано')
    admin_notes = models.TextField(blank=True, verbose_name='Заметки администратора')
    delivery_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Ожидает отправки'),
            ('sent', 'Отправлено'),
            ('delivered', 'Доставлено'),
        ],
        default='pending',
        verbose_name='Статус доставки'
    )
    user_confirmed = models.BooleanField(default=False, verbose_name='Подтверждено пользователем')
    user_comment = models.TextField(blank=True, verbose_name='Комментарий пользователя')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Подтверждено')
    
    class Meta:
        verbose_name = 'Получение подарка'
        verbose_name_plural = 'Получения подарков'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user} - {self.gift.name} ({self.get_status_display()})"

