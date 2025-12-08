"""
URL configuration for mona project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.template.response import TemplateResponse
from django.db.models import Sum
from core.models import TelegramUser, QRCode, Gift, GiftRedemption


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
    }
    
    return TemplateResponse(request, 'admin/dashboard.html', context)


urlpatterns = [
    path('admin/dashboard/', admin.site.admin_view(dashboard_view), name='dashboard'),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

# WhiteNoise обрабатывает статические файлы автоматически через middleware
# Для media файлов используем стандартный способ (в production лучше через nginx)
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

