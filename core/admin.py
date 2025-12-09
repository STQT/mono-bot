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
    Gift, GiftRedemption, BroadcastMessage, Promotion, QRCodeGeneration, PrivacyPolicy
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
    
    def has_view_permission(self, request, obj=None):
        """Проверяет права доступа к просмотру QR-кода."""
        # Superuser всегда имеет доступ
        if request.user.is_superuser:
            return True
        
        # Проверяем custom permission
        if request.user.has_perm('core.view_qrcode_detail'):
            return True
        
        return False
    
    def get_list_display_links(self, request, list_display):
        """Скрывает ссылки на детальный просмотр для пользователей без permission."""
        if not self.has_view_permission(request):
            # Если нет доступа к просмотру, не показываем ссылки
            return (None,)
        # По умолчанию Django использует первый элемент list_display как ссылку
        return super().get_list_display_links(request, list_display)
    
    def get_fields(self, request, obj=None):
        """Возвращает список полей для отображения, заменяя code на masked_code_display для пользователей без прав."""
        fields = list(super().get_fields(request, obj))
        
        # Если пользователь не имеет прав на просмотр деталей, заменяем code на masked_code_display
        if obj and not self.has_view_permission(request, obj):
            if 'code' in fields:
                fields.remove('code')
            if 'masked_code_display' not in fields:
                # Вставляем masked_code_display на место code
                try:
                    code_index = fields.index('code')
                    fields.insert(code_index, 'masked_code_display')
                except ValueError:
                    # Если code не найден, просто добавляем в начало
                    fields.insert(0, 'masked_code_display')
        
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        """Возвращает список readonly полей, добавляя маскированное поле code для пользователей без прав."""
        readonly = list(super().get_readonly_fields(request, obj))
        
        # Если пользователь не имеет прав на просмотр деталей, маскируем код
        if obj and not self.has_view_permission(request, obj):
            # Убираем code из readonly, так как мы заменим его на masked_code
            if 'code' in readonly:
                readonly.remove('code')
            # Добавляем masked_code вместо code
            if 'masked_code_display' not in readonly:
                readonly.append('masked_code_display')
        
        return readonly
    
    def masked_code_display(self, obj):
        """Отображает замаскированный код для пользователей без прав."""
        if obj:
            masked = self.masked_code(obj)
            return format_html(
                '<div style="font-family: monospace; font-size: 14px; color: #333;">'
                '<strong>{}</strong></div>',
                masked
            )
        return '-'
    masked_code_display.short_description = 'Code'
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Переопределяем детальный просмотр для проверки прав доступа и маскирования кода."""
        from django.template.response import TemplateResponse
        
        obj = self.get_object(request, object_id)
        
        # Проверяем права доступа
        if not self.has_view_permission(request, obj):
            # Если нет доступа, показываем кастомный шаблон с сообщением
            extra_context = extra_context or {}
            extra_context['no_access'] = True
            extra_context['is_superuser'] = request.user.is_superuser
            extra_context['has_permission'] = request.user.has_perm('core.view_qrcode_detail')
            extra_context['title'] = 'Доступ запрещен'
            extra_context['opts'] = self.model._meta
            extra_context['has_view_permission'] = False
            extra_context['has_add_permission'] = False
            extra_context['has_change_permission'] = False
            extra_context['has_delete_permission'] = False
            
            return TemplateResponse(
                request,
                'admin/core/qrcode/no_access.html',
                extra_context,
                status=403
            )
        
        return super().change_view(request, object_id, form_url, extra_context)
    
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
        """Добавляет кнопку для генерации QR-кодов и информацию о доступе."""
        extra_context = extra_context or {}
        extra_context['show_generate_button'] = True
        extra_context['has_view_permission'] = self.has_view_permission(request)
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
        ]
        return custom_urls + urls
    
    def generate_qr_codes_view(self, request):
        """Представление для генерации QR-кодов."""
        if request.method == 'POST':
            code_type = request.POST.get('code_type')
            quantity = int(request.POST.get('quantity', 0))
            points = request.POST.get('points')
            
            if code_type and quantity > 0:
                try:
                    # Определяем баллы
                    if points:
                        points = int(points)
                    else:
                        # Используем значения по умолчанию
                        points = settings.ELECTRICIAN_POINTS if code_type == 'electrician' else settings.SELLER_POINTS
                    
                    # Создаем запись о генерации
                    generation = QRCodeGeneration.objects.create(
                        code_type=code_type,
                        quantity=quantity,
                        points=points,
                        created_by=request.user if request.user.is_authenticated else None,
                        status='pending'
                    )
                    
                    # Запускаем Celery задачу
                    from core.tasks import generate_qr_codes_task
                    generate_qr_codes_task.delay(generation.id)
                    
                    messages.success(request, f'Генерация QR-кодов запущена! Вы будете перенаправлены на страницу со списком генераций.')
                    return redirect('admin:core_qrcodegeneration_changelist')
                except Exception as e:
                    messages.error(request, f'Ошибка при запуске генерации: {str(e)}')
            else:
                messages.error(request, 'Заполните все поля корректно!')
        
        return render(request, 'admin/core/qrcode/generate.html', {
            'title': 'Генерация QR-кодов',
        })


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


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """Админка для акций/баннеров."""
    list_display = [
        'image_preview', 'title', 'date_display', 'order', 'is_active', 'status_badge', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'date']
    search_fields = ['title']
    list_editable = ['order', 'is_active']
    ordering = ['order', '-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'image', 'date', 'order', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def image_preview(self, obj):
        """Превью изображения акции."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Rasm'
    
    def date_display(self, obj):
        """Отображает дату в формате DD.MM.YYYY."""
        if obj.date:
            return obj.date.strftime('%d.%m.%Y')
        return '-'
    date_display.short_description = 'Sana'
    date_display.admin_order_field = 'date'
    
    def status_badge(self, obj):
        """Отображает статус активности."""
        if obj.is_active:
            return format_html(
                '<span style="background: #10B981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">Faol</span>'
            )
        return format_html(
            '<span style="background: #EF4444; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">Nofaol</span>'
        )
    status_badge.short_description = 'Holat'


@admin.register(QRCodeGeneration)
class QRCodeGenerationAdmin(admin.ModelAdmin):
    """Админка для истории генерации QR-кодов."""
    list_display = [
        'generation_display', 'code_type_badge', 'quantity_display',
        'points_display', 'status_badge', 'created_by_display',
        'created_at', 'completed_at_display', 'download_button'
    ]
    list_filter = ['status', 'code_type', 'created_at']
    search_fields = ['id']
    readonly_fields = [
        'code_type', 'quantity', 'points', 'status', 'zip_file',
        'qr_codes', 'error_message', 'created_by', 'created_at', 'completed_at'
    ]
    ordering = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def generation_display(self, obj):
        """Отображает информацию о генерации."""
        return format_html(
            '<div style="line-height: 1.6;">'
            '<strong style="font-size: 16px;">#{}</strong><br>'
            '<span style="color: #718096; font-size: 12px;">{} шт.</span>',
            obj.id,
            obj.quantity
        )
    generation_display.short_description = 'Генерация'
    generation_display.admin_order_field = 'id'
    
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
    
    def quantity_display(self, obj):
        """Отображает количество."""
        return format_html(
            '<span style="font-weight: 600;">{}</span>',
            obj.quantity
        )
    quantity_display.short_description = 'Количество'
    quantity_display.admin_order_field = 'quantity'
    
    def points_display(self, obj):
        """Отображает баллы."""
        return format_html(
            '<span style="color: #667eea; font-weight: 700;">{} баллов</span>',
            obj.points
        )
    points_display.short_description = 'Баллы'
    points_display.admin_order_field = 'points'
    
    def status_badge(self, obj):
        """Отображает статус генерации."""
        colors = {
            'pending': ('#fff3cd', '#856404', '⏳'),
            'processing': ('#dbeafe', '#1e40af', '🔄'),
            'completed': ('#d4edda', '#155724', '✅'),
            'failed': ('#f8d7da', '#721c24', '❌'),
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
    
    def created_by_display(self, obj):
        """Отображает создателя."""
        if obj.created_by:
            return obj.created_by.username or str(obj.created_by)
        return '-'
    created_by_display.short_description = 'Создал'
    
    def completed_at_display(self, obj):
        """Отображает время завершения."""
        if obj.completed_at:
            return obj.completed_at.strftime('%d.%m.%Y %H:%M')
        return '-'
    completed_at_display.short_description = 'Завершено'
    completed_at_display.admin_order_field = 'completed_at'
    
    def download_button(self, obj):
        """Кнопка для скачивания ZIP файла."""
        if obj.status == 'completed' and obj.zip_file:
            return format_html(
                '<a href="{}" style="background: #417690; color: white; padding: 6px 12px; '
                'border-radius: 4px; text-decoration: none; display: inline-block;">📥 Скачать</a>',
                obj.zip_file.url
            )
        elif obj.status == 'failed':
            return format_html(
                '<span style="color: #dc3545; font-size: 11px;">{}</span>',
                obj.error_message[:50] + '...' if obj.error_message and len(obj.error_message) > 50 else obj.error_message or 'Ошибка'
            )
        return '-'
    download_button.short_description = 'Действие'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('code_type', 'quantity', 'points', 'status')
        }),
        ('Результаты', {
            'fields': ('zip_file', 'qr_codes', 'error_message')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'completed_at')
        }),
    )
    
    def has_add_permission(self, request):
        """Отключаем добавление через админку."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление."""
        return True


# Кастомная админка для дашборда
@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    """Админка для политики конфиденциальности."""
    list_display = ['is_active', 'updated_at', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    fieldsets = (
        ('Контент', {
            'fields': ('content_uz_latin', 'content_uz_cyrillic', 'content_ru', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Разрешаем создание только для superuser."""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Разрешаем удаление только для superuser."""
        return request.user.is_superuser


# Кастомная админка для дашборда
admin.site.site_header = 'Mona Admin Panel'
admin.site.site_title = 'Mona Admin'
admin.site.index_title = 'Панель управления'

