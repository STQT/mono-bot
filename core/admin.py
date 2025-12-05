"""
Admin configuration for core models.
"""
import zipfile
import os
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import (
    TelegramUser, QRCode, QRCodeScanAttempt,
    Gift, GiftRedemption
)
from .utils import generate_qr_code_image, generate_qr_codes_batch


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Админка для пользователей Telegram."""
    list_display = [
        'telegram_id', 'first_name', 'username', 'phone_number',
        'user_type', 'points', 'created_at'
    ]
    list_filter = ['user_type', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'phone_number']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
    ordering = ['-points', '-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name')
        }),
        ('Контактные данные', {
            'fields': ('phone_number', 'latitude', 'longitude')
        }),
        ('Тип и баллы', {
            'fields': ('user_type', 'points')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class QRCodeScanAttemptInline(admin.TabularInline):
    """Инлайн для попыток сканирования."""
    model = QRCodeScanAttempt
    extra = 0
    readonly_fields = ['user', 'attempted_at', 'is_successful']
    can_delete = False


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    """Админка для QR-кодов (только просмотр)."""
    list_display = [
        'masked_code', 'code_type', 'points', 'generated_at',
        'scanned_at', 'scanned_by_display', 'is_scanned'
    ]
    list_filter = ['code_type', 'is_scanned', 'generated_at']
    search_fields = ['code', 'hash_code']
    readonly_fields = [
        'code', 'code_type', 'hash_code', 'image_path',
        'points', 'generated_at', 'scanned_at', 'scanned_by', 'is_scanned'
    ]
    ordering = ['-generated_at']
    inlines = [QRCodeScanAttemptInline]
    
    def changelist_view(self, request, extra_context=None):
        """Добавляет кнопку для генерации QR-кодов."""
        extra_context = extra_context or {}
        extra_context['show_generate_button'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    def has_add_permission(self, request):
        """Отключаем добавление через админку."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Отключаем удаление."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Отключаем редактирование."""
        return False
    
    def masked_code(self, obj):
        """Маскирует часть кода для отображения."""
        if len(obj.code) > 8:
            return obj.code[:4] + '*' * (len(obj.code) - 8) + obj.code[-4:]
        return obj.code
    masked_code.short_description = 'Штрих-код'
    
    def scanned_by_display(self, obj):
        """Отображает пользователя, который отсканировал."""
        if obj.scanned_by:
            return f"{obj.scanned_by.first_name} (@{obj.scanned_by.username or 'N/A'})"
        return '-'
    scanned_by_display.short_description = 'Пользователь Telegram'
    
    def get_urls(self):
        """Добавляет кастомные URL для генерации QR-кодов."""
        urls = super().get_urls()
        custom_urls = [
            path('generate/', self.admin_site.admin_view(self.generate_qr_codes_view), name='core_qrcode_generate'),
            path('download-zip/', self.admin_site.admin_view(self.download_zip_view), name='core_qrcode_download_zip'),
        ]
        return custom_urls + urls
    
    def generate_qr_codes_view(self, request):
        """Представление для генерации QR-кодов."""
        if request.method == 'POST':
            code_type = request.POST.get('code_type')
            quantity = int(request.POST.get('quantity', 0))
            
            if code_type and quantity > 0:
                try:
                    qr_codes = generate_qr_codes_batch(code_type, quantity)
                    request.session['generated_qr_codes'] = [qr.id for qr in qr_codes]
                    messages.success(request, f'Успешно сгенерировано {quantity} QR-кодов!')
                    return redirect('admin:core_qrcode_download_zip')
                except Exception as e:
                    messages.error(request, f'Ошибка при генерации: {str(e)}')
            else:
                messages.error(request, 'Заполните все поля корректно!')
        
        return render(request, 'admin/core/qrcode/generate.html', {
            'title': 'Генерация QR-кодов',
        })
    
    def download_zip_view(self, request):
        """Представление для скачивания ZIP архива с QR-кодами."""
        qr_code_ids = request.session.get('generated_qr_codes', [])
        
        if not qr_code_ids:
            messages.warning(request, 'Нет сгенерированных QR-кодов для скачивания.')
            return redirect('admin:core_qrcode_changelist')
        
        qr_codes = QRCode.objects.filter(id__in=qr_code_ids)
        
        # Создаем ZIP архив
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="qrcodes.zip"'
        
        with zipfile.ZipFile(response, 'w') as zip_file:
            for qr_code in qr_codes:
                if qr_code.image_path and os.path.exists(qr_code.image_path):
                    zip_file.write(
                        qr_code.image_path,
                        os.path.basename(qr_code.image_path)
                    )
        
        # Очищаем сессию
        request.session.pop('generated_qr_codes', None)
        
        return response


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    """Админка для подарков."""
    list_display = ['name', 'points_cost', 'image_preview', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'image', 'image_preview')
        }),
        ('Настройки', {
            'fields': ('points_cost', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def image_preview(self, obj):
        """Превью изображения подарка."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Превью'


@admin.register(GiftRedemption)
class GiftRedemptionAdmin(admin.ModelAdmin):
    """Админка для получения подарков (CRM)."""
    list_display = [
        'user', 'gift', 'status', 'delivery_status', 'user_confirmed',
        'requested_at', 'processed_at'
    ]
    list_filter = ['status', 'delivery_status', 'user_confirmed', 'requested_at']
    search_fields = ['user__username', 'user__first_name', 'gift__name']
    readonly_fields = ['user', 'gift', 'requested_at', 'confirmed_at']
    
    fieldsets = (
        ('Информация о запросе', {
            'fields': ('user', 'gift', 'requested_at')
        }),
        ('Обработка', {
            'fields': ('status', 'delivery_status', 'processed_at', 'admin_notes')
        }),
        ('Подтверждение пользователем', {
            'fields': ('user_confirmed', 'user_comment', 'confirmed_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливает processed_at при изменении статуса."""
        if change and 'status' in form.changed_data:
            if obj.status != 'pending' and not obj.processed_at:
                from django.utils import timezone
                obj.processed_at = timezone.now()
        super().save_model(request, obj, form, change)


# Кастомная админка для дашборда
admin.site.site_header = 'Mona Admin Panel'
admin.site.site_title = 'Mona Admin'
admin.site.index_title = 'Панель управления'

