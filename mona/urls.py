"""
URL configuration for mona project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.template.response import TemplateResponse
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from collections import defaultdict
from core.models import TelegramUser, QRCode, Gift, GiftRedemption
from core.regions import get_region_name, get_district_name


def dashboard_view(request):
    """Дашборд с ТОП лидерами по продажам."""
    # ТОП лидеры по баллам (электрики)
    top_electricians = TelegramUser.objects.filter(
        user_type='electrician'
    ).order_by('-points')[:10]
    
    # ТОП лидеры по баллам (продавцы)
    top_sellers = TelegramUser.objects.filter(
        user_type='seller'
    ).order_by('-points')[:10]
    
    # Общая статистика
    total_users = TelegramUser.objects.count()
    total_electricians = TelegramUser.objects.filter(user_type='electrician').count()
    total_sellers = TelegramUser.objects.filter(user_type='seller').count()
    
    # Статистика по QR-кодам
    total_qrcodes = QRCode.objects.count()
    scanned_qrcodes = QRCode.objects.filter(is_scanned=True).count()
    unscanned_qrcodes = total_qrcodes - scanned_qrcodes
    
    # Статистика по баллам
    total_points_electricians = TelegramUser.objects.filter(
        user_type='electrician'
    ).aggregate(total=Sum('points'))['total'] or 0
    
    total_points_sellers = TelegramUser.objects.filter(
        user_type='seller'
    ).aggregate(total=Sum('points'))['total'] or 0
    
    # Статистика по подаркам
    total_gifts = Gift.objects.count()
    active_gifts = Gift.objects.filter(is_active=True).count()
    pending_redemptions = GiftRedemption.objects.filter(status='pending').count()
    
    # Статистика по вилоятам и районам за месяц и год
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # QR-коды за текущий месяц
    qrcodes_month = QRCode.objects.filter(
        is_scanned=True,
        scanned_at__gte=current_month_start
    ).select_related('scanned_by')
    
    # QR-коды за текущий год
    qrcodes_year = QRCode.objects.filter(
        is_scanned=True,
        scanned_at__gte=current_year_start
    ).select_related('scanned_by')
    
    # Статистика по вилоятам за месяц
    region_stats_month = defaultdict(int)
    for qr in qrcodes_month:
        if qr.scanned_by and qr.scanned_by.region:
            region_stats_month[qr.scanned_by.region] += qr.points
    
    # Статистика по вилоятам за год
    region_stats_year = defaultdict(int)
    for qr in qrcodes_year:
        if qr.scanned_by and qr.scanned_by.region:
            region_stats_year[qr.scanned_by.region] += qr.points
    
    # Статистика по районам за месяц
    district_stats_month = defaultdict(int)
    for qr in qrcodes_month:
        if qr.scanned_by and qr.scanned_by.region and qr.scanned_by.district:
            key = (qr.scanned_by.region, qr.scanned_by.district)
            district_stats_month[key] += qr.points
    
    # Статистика по районам за год
    district_stats_year = defaultdict(int)
    for qr in qrcodes_year:
        if qr.scanned_by and qr.scanned_by.region and qr.scanned_by.district:
            key = (qr.scanned_by.region, qr.scanned_by.district)
            district_stats_year[key] += qr.points
    
    # Формируем списки для отображения
    regions_month = sorted(
        [(get_region_name(region_code, 'ru') or region_code, points) 
         for region_code, points in region_stats_month.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    regions_year = sorted(
        [(get_region_name(region_code, 'ru') or region_code, points) 
         for region_code, points in region_stats_year.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    districts_month = sorted(
        [(get_region_name(region_code, 'ru') or region_code, 
          get_district_name(district_code, region_code, 'ru') or district_code, 
          points) 
         for (region_code, district_code), points in district_stats_month.items()],
        key=lambda x: x[2],
        reverse=True
    )
    
    districts_year = sorted(
        [(get_region_name(region_code, 'ru') or region_code, 
          get_district_name(district_code, region_code, 'ru') or district_code, 
          points) 
         for (region_code, district_code), points in district_stats_year.items()],
        key=lambda x: x[2],
        reverse=True
    )
    
    context = {
        **admin.site.each_context(request),
        'title': 'Дашборд',
        'top_electricians': top_electricians,
        'top_sellers': top_sellers,
        'total_users': total_users,
        'total_electricians': total_electricians,
        'total_sellers': total_sellers,
        'total_qrcodes': total_qrcodes,
        'scanned_qrcodes': scanned_qrcodes,
        'unscanned_qrcodes': unscanned_qrcodes,
        'total_points_electricians': total_points_electricians,
        'total_points_sellers': total_points_sellers,
        'total_gifts': total_gifts,
        'active_gifts': active_gifts,
        'pending_redemptions': pending_redemptions,
        'regions_month': regions_month,
        'regions_year': regions_year,
        'districts_month': districts_month,
        'districts_year': districts_year,
        'current_month': current_month_start.strftime('%B %Y'),
        'current_year': current_year_start.year,
    }
    
    return TemplateResponse(request, 'admin/dashboard.html', context)


def send_region_message_view(request):
    """Представление для отправки сообщений пользователям области."""
    from django.shortcuts import render, redirect
    from django import forms
    from core.regions import get_all_regions
    from core.models import TelegramUser
    from django.contrib import messages
    from django.conf import settings
    import asyncio
    from aiogram import Bot
    from core.messaging import send_message_to_user
    from core.regions import get_region_by_coordinates
    
    # Проверяем пермишн
    if not request.user.has_perm('core.send_region_messages'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    
    class RegionMessageForm(forms.Form):
        region = forms.ChoiceField(
            choices=[('', 'Выберите область')] + get_all_regions('ru'),
            label='Область',
            required=True
        )
        message = forms.CharField(
            widget=forms.Textarea(attrs={'rows': 10}),
            label='Текст сообщения',
            required=True
        )
        parse_mode = forms.ChoiceField(
            choices=[('', 'Без форматирования'), ('HTML', 'HTML'), ('Markdown', 'Markdown')],
            required=False,
            label='Режим парсинга'
        )
        user_type_filter = forms.ChoiceField(
            choices=[
                ('', 'Все типы'),
                ('electrician', 'Электрики'),
                ('seller', 'Продавцы'),
            ],
            required=False,
            label='Тип пользователя'
        )
        only_active = forms.BooleanField(
            initial=True,
            required=False,
            label='Только активные пользователи'
        )
    
    if request.method == 'POST':
        form = RegionMessageForm(request.POST)
        if form.is_valid():
            region_code = form.cleaned_data['region']
            message_text = form.cleaned_data['message']
            parse_mode = form.cleaned_data['parse_mode'] or None
            user_type_filter = form.cleaned_data['user_type_filter'] or None
            only_active = form.cleaned_data['only_active']
            
            # Получаем всех пользователей выбранной области
            users_in_region = []
            all_users = TelegramUser.objects.exclude(
                latitude__isnull=True
            ).exclude(
                longitude__isnull=True
            )
            
            if only_active:
                all_users = all_users.filter(is_active=True)
            
            if user_type_filter:
                all_users = all_users.filter(user_type=user_type_filter)
            
            for user in all_users:
                user_region = get_region_by_coordinates(user.latitude, user.longitude)
                if user_region == region_code:
                    users_in_region.append(user)
            
            if not users_in_region:
                messages.warning(
                    request,
                    'В выбранной области не найдено пользователей с указанными критериями.'
                )
                return redirect('send_region_message')
            
            # Отправляем сообщения
            async def send_messages():
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                try:
                    sent = 0
                    failed = 0
                    for user in users_in_region:
                        success, error = await send_message_to_user(
                            bot=bot,
                            user=user,
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
            
            region_name = dict(get_all_regions('ru')).get(region_code, region_code)
            messages.success(
                request,
                f'Отправлено сообщений пользователям области "{region_name}": {sent}, Ошибок: {failed}'
            )
            return redirect('send_region_message')
    else:
        form = RegionMessageForm()
    
    context = {
        **admin.site.each_context(request),
        'form': form,
        'title': 'Отправить сообщение пользователям области',
        'opts': TelegramUser._meta,
    }
    
    return render(request, 'admin/core/telegramuser/send_region_message.html', context)


urlpatterns = [
    path('admin/dashboard/', admin.site.admin_view(dashboard_view), name='dashboard'),
    path('admin/send-region-message/', admin.site.admin_view(send_region_message_view), name='send_region_message'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# WhiteNoise обрабатывает статические файлы автоматически через middleware
# Но в режиме DEBUG также добавляем явную обработку для надежности
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Добавляем обработку статических файлов через Django (для разработки)
    urlpatterns += staticfiles_urlpatterns()
    # Для media файлов используем стандартный способ
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

