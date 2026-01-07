"""
Core models for the mona project.
"""
import hashlib
import secrets
import string
import random
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator


class TelegramUser(models.Model):
    """Модель пользователя Telegram."""
    USER_TYPE_CHOICES = [
        ('electrician', 'Elektrik'),
        ('seller', 'Sotuvchi'),
    ]
    
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True, db_index=True, verbose_name='Viloyat')
    district = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name='Tuman')
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        null=True,
        blank=True
    )
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True, verbose_name='Faol', db_index=True)
    language = models.CharField(
        max_length=15,
        choices=[
            ('uz_latin', 'O\'zbek (Lotin)'),
            ('ru', 'Русский'),
        ],
        default='uz_latin',
        verbose_name='Til'
    )
    privacy_accepted = models.BooleanField(default=False, verbose_name='Maxfiylik siyosatiga rozilik')
    last_message_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Oxirgi xabar yuborilgan vaqt')
    blocked_bot_at = models.DateTimeField(null=True, blank=True, verbose_name='Botni bloklagan vaqt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Telegram foydalanuvchi'
        verbose_name_plural = 'Telegram foydalanuvchilar'
        ordering = ['region', 'district', '-created_at']
        permissions = [
            ('send_region_messages', 'Can send messages to users by region'),
            ('change_user_type_call_center', 'Call Center: Can change user type'),
        ]
    
    def update_location(self):
        """Автоматически определяет и сохраняет область и район по координатам."""
        if self.latitude is None or self.longitude is None:
            self.region = None
            self.district = None
            return
        
        from core.regions import get_region_by_coordinates, get_district_by_coordinates
        
        # Определяем область
        region_code = get_region_by_coordinates(self.latitude, self.longitude)
        self.region = region_code
        
        # Определяем район
        if region_code:
            district_code, district_name = get_district_by_coordinates(
                self.latitude, self.longitude, region_code
            )
            self.district = district_code if district_code else None
        else:
            self.district = None
    
    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического определения локации."""
        # Обновляем локацию при сохранении, если есть координаты
        if self.latitude is not None and self.longitude is not None:
            self.update_location()
        super().save(*args, **kwargs)
    
    def get_region(self):
        """Возвращает код области пользователя (из кэша или вычисляет)."""
        if self.region:
            return self.region
        # Если нет в кэше, вычисляем и сохраняем
        if self.latitude is not None and self.longitude is not None:
            self.update_location()
            self.save(update_fields=['region', 'district'])
        return self.region
    
    def get_region_display(self, language='ru'):
        """Возвращает название области пользователя."""
        region_code = self.get_region()
        if region_code is None:
            return None
        from core.regions import get_region_name
        return get_region_name(region_code, language)
    
    def get_district(self):
        """Возвращает код района пользователя (из кэша или вычисляет)."""
        if self.district:
            return self.district
        # Если нет в кэше, вычисляем и сохраняем
        if self.latitude is not None and self.longitude is not None:
            self.update_location()
            self.save(update_fields=['region', 'district'])
        return self.district
    
    def get_district_display(self, language='ru'):
        """Возвращает название района пользователя."""
        district_code = self.get_district()
        region_code = self.get_region()
        if district_code is None or region_code is None:
            return None
        from core.regions import get_district_name
        return get_district_name(district_code, region_code, language)
    
    def __str__(self):
        return f"{self.first_name or 'Unknown'} (@{self.username or 'no_username'})"


class QRCode(models.Model):
    """Модель QR-кода (скретч-карты)."""
    CODE_TYPE_CHOICES = [
        ('electrician', 'Elektrik (E)'),
        ('seller', 'Sotuvchi (D)'),
    ]
    
    code = models.CharField(max_length=255, unique=True, db_index=True)
    code_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES)
    hash_code = models.CharField(max_length=32, unique=True, db_index=True)
    serial_number = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Seriya raqami')
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
        verbose_name = 'QR-kod'
        verbose_name_plural = 'QR-kodlar'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['hash_code']),
            models.Index(fields=['is_scanned']),
        ]
        permissions = [
            ('view_qrcode_detail', 'Can view QR code details'),
            ('generate_qrcodes', 'Can generate QR codes'),
        ]
    
    def __str__(self):
        """Маскирует код для отображения (EABC123 -> EA***3)."""
        if len(self.code) > 5:
            # Для коротких кодов показываем первые 2 символа, маскируем середину, последний символ
            prefix = self.code[:2]  # E или D + первый символ
            suffix = self.code[-1]   # Последний символ
            masked = '*' * max(1, len(self.code) - 3)
            masked_code = f"{prefix}{masked}{suffix}"
        else:
            masked_code = self.code
        return f"{masked_code} ({self.get_code_type_display()})"
    
    @classmethod
    def generate_hash(cls, length=6):
        """
        Генерирует уникальный короткий хеш для QR-кода.
        
        Args:
            length: Длина хеша (минимум 6 символов, по умолчанию 6)
        
        Returns:
            str: Уникальный хеш-код из букв и цифр
        """
        # Используем буквы и цифры для более короткого кода
        characters = string.ascii_uppercase + string.digits
        
        # Убираем похожие символы для избежания путаницы (0, O, I, 1)
        characters = ''.join(c for c in characters if c not in '0O1I')
        
        max_attempts = 1000  # Защита от бесконечного цикла
        attempts = 0
        
        while attempts < max_attempts:
            # Генерируем случайный код заданной длины
            hash_code = ''.join(random.choice(characters) for _ in range(length))
            
            # Проверяем уникальность
            if not cls.objects.filter(hash_code=hash_code).exists():
                return hash_code
            
            attempts += 1
        
        # Если не удалось найти уникальный код за 1000 попыток, увеличиваем длину
        if attempts >= max_attempts:
            return cls.generate_hash(length + 1)
    
    @classmethod
    def generate_serial_number(cls, code_type):
        """
        Генерирует уникальный серийный номер для QR-кода.
        
        Args:
            code_type: Тип кода ('electrician' или 'seller')
        
        Returns:
            str: Уникальный серийный номер
        """
        prefix = 'E' if code_type == 'electrician' else 'D'
        
        # Получаем последний серийный номер для этого типа
        last_qr = cls.objects.filter(code_type=code_type).order_by('-id').first()
        
        if last_qr and last_qr.serial_number:
            # Извлекаем номер из последнего серийного номера
            try:
                last_num = int(last_qr.serial_number.replace(prefix, ''))
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
        
        # Форматируем с ведущими нулями (например, E000001, D000001)
        serial_number = f"{prefix}{new_num:06d}"
        
        # Проверяем уникальность
        max_attempts = 1000
        attempts = 0
        while cls.objects.filter(serial_number=serial_number).exists() and attempts < max_attempts:
            new_num += 1
            serial_number = f"{prefix}{new_num:06d}"
            attempts += 1
        
        return serial_number
    
    @classmethod
    def create_code(cls, code_type, points=None):
        """Создает новый QR-код."""
        from django.conf import settings
        
        hash_code = cls.generate_hash()
        serial_number = cls.generate_serial_number(code_type)
        prefix = 'E' if code_type == 'electrician' else 'D'
        code = f"{prefix}{hash_code}"
        
        if points is None:
            points = settings.ELECTRICIAN_POINTS if code_type == 'electrician' else settings.SELLER_POINTS
        
        return cls.objects.create(
            code=code,
            code_type=code_type,
            hash_code=hash_code,
            serial_number=serial_number,
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
        verbose_name = 'Skanerlash urinishi'
        verbose_name_plural = 'Skanerlash urinishlari'
        ordering = ['-attempted_at']
        unique_together = [['user', 'qr_code']]
    
    def __str__(self):
        status = 'Muvaffaqiyatli' if self.is_successful else 'Muvaffaqiyatsiz'
        # Для коротких кодов показываем полностью или первые символы
        code_display = self.qr_code.code if len(self.qr_code.code) <= 10 else f"{self.qr_code.code[:10]}..."
        return f"{self.user} - {code_display} - {status}"


class Gift(models.Model):
    """Модель подарка."""
    USER_TYPE_CHOICES = [
        ('electrician', 'Elektrik (E)'),
        ('seller', 'Sotuvchi (D)'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Nomi')
    description_uz_latin = models.TextField(blank=True, verbose_name='Tavsif (O\'zbek lotin)')
    description_ru = models.TextField(blank=True, verbose_name='Tavsif (Ruscha)')
    image = models.ImageField(upload_to='gifts/', verbose_name='Rasm')
    points_cost = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Ballar narxi'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Foydalanuvchi turi',
        help_text='Agar bo\'sh qoldirilsa, barcha foydalanuvchilar uchun ko\'rsatiladi'
    )
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sovg\'a'
        verbose_name_plural = 'Sovg\'alar'
        ordering = ['points_cost', 'name']
        indexes = [
            models.Index(fields=['user_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.points_cost} ball)"


class GiftRedemption(models.Model):
    """Модель получения подарка пользователем."""
    STATUS_CHOICES = [
        ('pending', 'So\'rov qabul qilindi'),  # Запрос принят к обработке
        ('approved', 'Mahsulot tayyorlash bosqichida'),  # Продукт находится в стадии подготовки
        ('sent', 'Mahsulot yetkazib berish xizmatiga topshirildi'),  # Продукт передан в службу доставки
        ('completed', 'Mahsulotni qabul qilganingizni tasdiqlang'),  # Подтверждение получения продукта
        ('rejected', 'So\'rov bekor qilindi (administrator bilan bog\'laning)'),  # Запрос отменен
        ('not_received', 'Sovg\'a berilmagan (foydalanuvchi olmadi)'),  # Подарок не выдан (пользователь не получил)
    ]
    
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='gift_redemptions',
        verbose_name='Foydalanuvchi'
    )
    gift = models.ForeignKey(
        Gift,
        on_delete=models.CASCADE,
        related_name='redemptions',
        verbose_name='Sovg\'a'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Holat'
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='So\'ralgan vaqt')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Qayta ishlangan vaqt')
    admin_notes = models.TextField(blank=True, verbose_name='Administrator eslatmalari')
    # Поле delivery_status удалено - теперь используется только status
    user_confirmed = models.BooleanField(default=False, verbose_name='Foydalanuvchi tomonidan tasdiqlandi')
    user_comment = models.TextField(blank=True, verbose_name='Foydalanuvchi sharhi')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Tasdiqlangan vaqt')
    
    class Meta:
        verbose_name = 'Sovg\'a olish'
        verbose_name_plural = 'Sovg\'a olishlar'
        ordering = ['-requested_at']
        permissions = [
            ('change_status_call_center', 'Call Center: Can change redemption status'),
            ('change_status_agent', 'Agent: Can change redemption status (sent/completed only)'),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.gift.name} ({self.get_status_display()})"


class BroadcastMessage(models.Model):
    """Модель для массовых рассылок."""
    STATUS_CHOICES = [
        ('pending', 'Yuborish kutilmoqda'),
        ('sending', 'Yuborilmoqda'),
        ('completed', 'Yakunlandi'),
        ('failed', 'Xatolik'),
    ]
    
    title = models.CharField(max_length=255, verbose_name='Yuborish nomi')
    message_text = models.TextField(verbose_name='Xabar matni')
    user_type_filter = models.CharField(
        max_length=20,
        choices=TelegramUser.USER_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Foydalanuvchi turi bo\'yicha filtr'
    )
    # Фильтрация по региону
    REGION_CHOICES = [
        ('', 'Barcha viloyatlar'),  # Все области
        ('tashkent_city', 'Toshkent shahri'),
        ('tashkent_region', 'Toshkent viloyati'),
        ('andijan', 'Andijon viloyati'),
        ('bukhara', 'Buxoro viloyati'),
        ('jizzakh', 'Jizzax viloyati'),
        ('kashkadarya', 'Qashqadaryo viloyati'),
        ('navoi', 'Navoiy viloyati'),
        ('namangan', 'Namangan viloyati'),
        ('samarkand', 'Samarqand viloyati'),
        ('surkhandarya', 'Surxondaryo viloyati'),
        ('syrdarya', 'Sirdaryo viloyati'),
        ('fergana', 'Farg\'ona viloyati'),
        ('khorezm', 'Xorazm viloyati'),
        ('karakalpakstan', 'Qoraqalpog\'iston Respublikasi'),
    ]
    region_filter = models.CharField(
        max_length=50,
        choices=REGION_CHOICES,
        null=True,
        blank=True,
        verbose_name='Viloyat bo\'yicha filtr',
        help_text='Tanlangan viloyatdagi foydalanuvchilarga xabar yuborish uchun viloyatni tanlang. Bo\'sh qoldirilsa, barcha viloyatlarga yuboriladi.'
    )
    # Фильтр по языку
    LANGUAGE_CHOICES = [
        ('uz_latin', 'O\'zbek (Lotin)'),
        ('uz_cyrillic', 'O\'zbek (Kirill)'),
        ('ru', 'Русский'),
    ]
    language_filter = models.CharField(
        max_length=15,
        choices=LANGUAGE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Til bo\'yicha filtr'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Holat'
    )
    total_users = models.IntegerField(default=0, verbose_name='Jami foydalanuvchilar')
    sent_count = models.IntegerField(default=0, verbose_name='Yuborildi')
    failed_count = models.IntegerField(default=0, verbose_name='Xatolar')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Yuborish boshlangan')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Yakunlangan')
    
    class Meta:
        verbose_name = 'Yuborish'
        verbose_name_plural = 'Yuborishlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Promotion(models.Model):
    """Модель для акций/баннеров в слайдере Web App."""
    title = models.CharField(max_length=255, verbose_name='Sarlavha')
    image = models.ImageField(upload_to='promotions/', verbose_name='Rasm')
    date = models.DateField(verbose_name='Sana')
    is_active = models.BooleanField(default=True, verbose_name='Faol', db_index=True)
    order = models.IntegerField(default=0, verbose_name='Tartib raqami', help_text='Kichikroq raqam yuqorida ko\'rsatiladi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')
    
    class Meta:
        verbose_name = 'Aksiya'
        verbose_name_plural = 'Aksiyalar'
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        if self.date:
            date_str = self.date.strftime('%d.%m.%Y')
        else:
            date_str = "Sana yo'q"
        return f"{self.title} ({date_str})"


class PrivacyPolicy(models.Model):
    """Модель для политики конфиденциальности."""
    pdf_uz_latin = models.FileField(blank=True, null=True, upload_to='privacy_policy/', verbose_name='PDF файл (O\'zbek lotin)', help_text='PDF файл политики конфиденциальности для узбекского языка (латиница)')
    pdf_ru = models.FileField(blank=True, null=True, upload_to='privacy_policy/', verbose_name='PDF файл (Ruscha)', help_text='PDF файл политики конфиденциальности для русского языка')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')
    
    class Meta:
        verbose_name = 'Maxfiylik siyosati'
        verbose_name_plural = 'Maxfiylik siyosati'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Maxfiylik siyosati (Yangilangan: {self.updated_at.strftime('%d.%m.%Y %H:%M')})"


class QRCodeGeneration(models.Model):
    """Модель для истории генерации QR-кодов."""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('processing', 'Jarayonda'),
        ('completed', 'Yakunlandi'),
        ('failed', 'Xatolik'),
    ]
    
    code_type = models.CharField(
        max_length=20,
        choices=QRCode.CODE_TYPE_CHOICES,
        verbose_name='QR-kod turi'
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='Miqdori')
    points = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Ballar')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Holat'
    )
    zip_file = models.FileField(
        upload_to='qrcodes/generations/',
        null=True,
        blank=True,
        verbose_name='ZIP fayl'
    )
    qr_codes = models.ManyToManyField(
        QRCode,
        related_name='generations',
        blank=True,
        verbose_name='QR-kodlar'
    )
    error_message = models.TextField(blank=True, verbose_name='Xatolik xabari')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_generations',
        verbose_name='Yaratgan foydalanuvchi'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Yakunlangan')
    
    class Meta:
        verbose_name = 'QR-kod generatsiyasi'
        verbose_name_plural = 'QR-kod generatsiyalari'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_code_type_display()} - {self.quantity} ta ({self.get_status_display()})"

