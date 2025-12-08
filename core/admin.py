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
    Gift, GiftRedemption, BroadcastMessage
)
from .utils import generate_qr_code_image, generate_qr_codes_batch


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Админка для пользователей Telegram."""
    list_display = [
        'user_display', 'phone_number', 'user_type_badge', 
        'points_display', 'language_badge', 'status_badge', 'created_at'
    ]
    list_filter = ['user_type', 'is_active', 'language', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'phone_number']
    readonly_fields = [
        'telegram_id', 'created_at', 'updated_at',
        'last_message_sent_at', 'blocked_bot_at'
    ]
    ordering = ['-points', '-created_at']
    actions = ['send_personal_message_action', 'mark_as_active', 'mark_as_inactive']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def user_display(self, obj):
        """Отображает пользователя с иконкой и ссылкой."""
        icon = "⚡" if obj.user_type == 'electrician' else "🛒"
        name = obj.first_name or "Пользователь"
        username = f"@{obj.username}" if obj.username else ""
        return format_html(
            '<span style="font-size: 18px;">{}</span> <strong>{}</strong> <span style="color: #718096;">{}</span><br>'
            '<span style="color: #718096; font-size: 12px;">ID: {}</span>',
            icon, name, username, obj.telegram_id
        )
    user_display.short_description = 'Пользователь'
    user_display.admin_order_field = 'first_name'
    
    def user_type_badge(self, obj):
        """Отображает тип пользователя с цветным badge."""
        if obj.user_type == 'electrician':
            return format_html(
                '<span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">⚡ Elektrik</span>'
            )
        elif obj.user_type == 'seller':
            return format_html(
                '<span style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">🛒 Sotuvchi</span>'
            )
        return '-'
    user_type_badge.short_description = 'Тип'
    user_type_badge.admin_order_field = 'user_type'
    
    def points_display(self, obj):
        """Отображает баллы с цветом."""
        points_formatted = f"{obj.points:,}"
        return format_html(
            '<span style="color: #667eea; font-weight: 700; font-size: 16px;">{}</span>',
            points_formatted
        )
    points_display.short_description = 'Баллы'
    points_display.admin_order_field = 'points'
    
    def language_badge(self, obj):
        """Отображает язык с цветным badge."""
        colors = {
            'uz_latin': ('#dbeafe', '#1e40af', '🇺🇿'),
            'uz_cyrillic': ('#fef3c7', '#92400e', '🇺🇿'),
            'ru': ('#fee2e2', '#991b1b', '🇷🇺'),
        }
        bg, text, flag = colors.get(obj.language, ('#f3f4f6', '#374151', '🌐'))
        label = dict(obj._meta.get_field('language').choices).get(obj.language, obj.language)
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 12px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">{} {}</span>',
            bg, text, flag, label.split('(')[0].strip()
        )
    language_badge.short_description = 'Язык'
    language_badge.admin_order_field = 'language'
    
    def status_badge(self, obj):
        """Отображает статус активности."""
        if obj.is_active:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">✅ Активен</span>'
            )
        else:
            return format_html(
                '<span style="background: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">❌ Неактивен</span>'
            )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'is_active'
    
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
        ('Настройки', {
            'fields': ('language',)
        }),
        ('Активность', {
            'fields': ('is_active', 'last_message_sent_at', 'blocked_bot_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def send_personal_message_action(self, request, queryset):
        """Действие для отправки персонального сообщения."""
        from django.shortcuts import render
        from django import forms
        
        class MessageForm(forms.Form):
            message = forms.CharField(widget=forms.Textarea, label='Текст сообщения')
            parse_mode = forms.ChoiceField(
                choices=[('', 'Без форматирования'), ('HTML', 'HTML'), ('Markdown', 'Markdown')],
                required=False,
                label='Режим парсинга'
            )
        
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message_text = form.cleaned_data['message']
                parse_mode = form.cleaned_data['parse_mode'] or None
                
                import asyncio
                from django.conf import settings
                from aiogram import Bot
                from core.messaging import send_personal_message
                
                async def send_messages():
                    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                    try:
                        sent = 0
                        failed = 0
                        for user in queryset:
                            success, error = await send_personal_message(
                                bot=bot,
                                telegram_id=user.telegram_id,
                                text=message_text,
                                parse_mode=parse_mode
                            )
                            if success:
                                sent += 1
                            else:
                                failed += 1
                        return sent, failed
                    finally:
                        await bot.session.close()
                
                sent, failed = asyncio.run(send_messages())
                self.message_user(
                    request,
                    f'Отправлено: {sent}, Ошибок: {failed}',
                    level=messages.SUCCESS if failed == 0 else messages.WARNING
                )
                return redirect('admin:core_telegramuser_changelist')
        else:
            form = MessageForm()
        
        return render(request, 'admin/core/telegramuser/send_message.html', {
            'form': form,
            'users': queryset,
            'title': 'Отправить сообщение пользователям'
        })
    send_personal_message_action.short_description = 'Отправить персональное сообщение выбранным пользователям'
    
    def mark_as_active(self, request, queryset):
        """Пометить пользователей как активных."""
        queryset.update(is_active=True, blocked_bot_at=None)
        self.message_user(request, f'{queryset.count()} пользователей помечено как активные')
    mark_as_active.short_description = 'Пометить как активных'
    
    def mark_as_inactive(self, request, queryset):
        """Пометить пользователей как неактивных."""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} пользователей помечено как неактивные')
    mark_as_inactive.short_description = 'Пометить как неактивных'


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
        'qr_display', 'code_type_badge', 'points_display', 
        'status_badge', 'scanned_by_display', 'generated_at'
    ]
    list_filter = ['code_type', 'is_scanned', 'generated_at']
    search_fields = ['code', 'hash_code', 'serial_number']
    readonly_fields = [
        'code', 'code_type', 'hash_code', 'serial_number', 'image_path',
        'points', 'generated_at', 'scanned_at', 'scanned_by', 'is_scanned'
    ]
    ordering = ['-generated_at']
    inlines = [QRCodeScanAttemptInline]
    list_per_page = 50
    date_hierarchy = 'generated_at'
    
    def qr_display(self, obj):
        """Отображает QR-код с серийным номером."""
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong style="font-size: 16px;">📱 #{}</strong><br>'
            '<span style="color: #718096; font-size: 12px; font-family: monospace;">{}</span>',
            obj.serial_number,
            self.masked_code(obj)
        )
    qr_display.short_description = 'QR-код'
    qr_display.admin_order_field = 'serial_number'
    
    def code_type_badge(self, obj):
        """Отображает тип кода."""
        if obj.code_type == 'electrician':
            return format_html(
                '<span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">⚡ E-</span>'
            )
        elif obj.code_type == 'seller':
            return format_html(
                '<span style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">🛒 D-</span>'
            )
        return '-'
    code_type_badge.short_description = 'Тип'
    code_type_badge.admin_order_field = 'code_type'
    
    def points_display(self, obj):
        """Отображает баллы."""
        points_formatted = f"{obj.points:,}"
        return format_html(
            '<span style="color: #667eea; font-weight: 700; font-size: 16px;">{}</span>',
            points_formatted
        )
    points_display.short_description = 'Баллы'
    points_display.admin_order_field = 'points'
    
    def status_badge(self, obj):
        """Отображает статус сканирования."""
        if obj.is_scanned:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">✅ Использован</span>'
            )
        else:
            return format_html(
                '<span style="background: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">⏳ Не использован</span>'
            )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'is_scanned'
    
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
        if len(obj.code) > 5:
            # Для коротких кодов: E-ABC123 -> E-AB***3
            prefix = obj.code[:3]  # E- или D- + первый символ
            suffix = obj.code[-1]   # Последний символ
            masked = '*' * max(1, len(obj.code) - 4)
            return f"{prefix}{masked}{suffix}"
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
    list_display = ['gift_display', 'points_cost_display', 'image_preview', 'status_badge', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    list_per_page = 25
    
    def gift_display(self, obj):
        """Отображает подарок с иконкой."""
        return format_html(
            '<span style="font-size: 20px;">🎁</span> <strong style="font-size: 16px;">{}</strong>',
            obj.name
        )
    gift_display.short_description = 'Подарок'
    gift_display.admin_order_field = 'name'
    
    def points_cost_display(self, obj):
        """Отображает стоимость с цветом."""
        points_formatted = f"{obj.points_cost:,}"
        return format_html(
            '<span style="color: #667eea; font-weight: 700; font-size: 16px;">{}</span> баллов',
            points_formatted
        )
    points_cost_display.short_description = 'Стоимость'
    points_cost_display.admin_order_field = 'points_cost'
    
    def status_badge(self, obj):
        """Отображает статус активности."""
        if obj.is_active:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">✅ Активен</span>'
            )
        else:
            return format_html(
                '<span style="background: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">❌ Неактивен</span>'
            )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'is_active'
    
    def image_preview(self, obj):
        """Превью изображения подарка."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Превью'
    
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


@admin.register(GiftRedemption)
class GiftRedemptionAdmin(admin.ModelAdmin):
    """Админка для получения подарков (CRM)."""
    list_display = [
        'redemption_display', 'status_badge', 'delivery_status_badge', 
        'user_confirmed_badge', 'requested_at', 'processed_at'
    ]
    list_filter = ['status', 'delivery_status', 'user_confirmed', 'requested_at']
    search_fields = ['user__username', 'user__first_name', 'gift__name']
    readonly_fields = ['user', 'gift', 'requested_at', 'confirmed_at']
    list_per_page = 50
    date_hierarchy = 'requested_at'
    
    def redemption_display(self, obj):
        """Отображает информацию о заказе."""
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong style="font-size: 16px;">🎁 {}</strong><br>'
            '<span style="color: #718096; font-size: 14px;">👤 {}</span>',
            obj.gift.name,
            obj.user.first_name or f"ID: {obj.user.telegram_id}"
        )
    redemption_display.short_description = 'Заказ'
    redemption_display.admin_order_field = 'gift__name'
    
    def status_badge(self, obj):
        """Отображает статус заказа."""
        colors = {
            'pending': ('#fff3cd', '#856404', '⏳'),
            'approved': ('#d4edda', '#155724', '✅'),
            'rejected': ('#f8d7da', '#721c24', '❌'),
            'completed': ('#d1ecf1', '#0c5460', '✔️'),
        }
        bg, text, icon = colors.get(obj.status, ('#f3f4f6', '#374151', '📋'))
        label = dict(obj._meta.get_field('status').choices).get(obj.status, obj.status)
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 12px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">{} {}</span>',
            bg, text, icon, label
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'
    
    def delivery_status_badge(self, obj):
        """Отображает статус доставки."""
        colors = {
            'pending': ('#fff3cd', '#856404', '⏳'),
            'sent': ('#dbeafe', '#1e40af', '📦'),
            'delivered': ('#d4edda', '#155724', '✅'),
        }
        bg, text, icon = colors.get(obj.delivery_status, ('#f3f4f6', '#374151', '📋'))
        label = dict(obj._meta.get_field('delivery_status').choices).get(obj.delivery_status, obj.delivery_status)
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 12px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">{} {}</span>',
            bg, text, icon, label
        )
    delivery_status_badge.short_description = 'Доставка'
    delivery_status_badge.admin_order_field = 'delivery_status'
    
    def user_confirmed_badge(self, obj):
        """Отображает подтверждение пользователем."""
        if obj.user_confirmed is True:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">✅ Подтверждено</span>'
            )
        elif obj.user_confirmed is False:
            return format_html(
                '<span style="background: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 12px; '
                'font-size: 12px; font-weight: 600;">⚠️ Не подтверждено</span>'
            )
        return format_html(
            '<span style="background: #f3f4f6; color: #6b7280; padding: 4px 12px; border-radius: 12px; '
            'font-size: 12px; font-weight: 600;">-</span>'
        )
    user_confirmed_badge.short_description = 'Подтверждение'
    user_confirmed_badge.admin_order_field = 'user_confirmed'
    
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


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    """Админка для массовых рассылок."""
    list_display = [
        'title', 'status', 'user_type_filter', 'total_users',
        'sent_count', 'failed_count', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'user_type_filter', 'created_at']
    search_fields = ['title', 'message_text']
    readonly_fields = [
        'status', 'total_users', 'sent_count', 'failed_count',
        'created_at', 'started_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'message_text', 'user_type_filter')
        }),
        ('Статистика', {
            'fields': (
                'status', 'total_users', 'sent_count', 'failed_count',
                'created_at', 'started_at', 'completed_at'
            )
        }),
    )
    
    actions = ['send_broadcast_action']
    
    def send_broadcast_action(self, request, queryset):
        """Действие для отправки рассылки."""
        import subprocess
        from django.contrib import messages
        
        for broadcast in queryset:
            if broadcast.status != 'pending':
                self.message_user(
                    request,
                    f'Рассылка "{broadcast.title}" уже была отправлена',
                    level=messages.WARNING
                )
                continue
            
            # Запускаем команду отправки в фоне
            try:
                subprocess.Popen([
                    'python', 'manage.py', 'send_broadcast', str(broadcast.id)
                ])
                self.message_user(
                    request,
                    f'Рассылка "{broadcast.title}" запущена',
                    level=messages.SUCCESS
                )
            except Exception as e:
                self.message_user(
                    request,
                    f'Ошибка при запуске рассылки: {e}',
                    level=messages.ERROR
                )
    send_broadcast_action.short_description = 'Отправить выбранные рассылки'


# Кастомная админка для дашборда
admin.site.site_header = 'Mona Admin Panel'
admin.site.site_title = 'Mona Admin'
admin.site.index_title = 'Панель управления'

