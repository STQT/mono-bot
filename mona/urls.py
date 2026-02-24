"""
URL configuration for mona project.
"""
from django.contrib import admin
from django.contrib.auth import logout
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta, date
from collections import defaultdict
from core.models import TelegramUser, QRCode, Gift, GiftRedemption
from core.regions import get_region_name


def _parse_date(s):
    """Парсит строку YYYY-MM-DD в date или None."""
    if not s:
        return None
    try:
        return date.fromisoformat(s.strip())
    except (ValueError, TypeError):
        return None


def dashboard_view(request):
    """Дашборд — единый daterange-фильтр для всех блоков."""
    date_from = _parse_date(request.GET.get('date_from'))
    date_to   = _parse_date(request.GET.get('date_to'))

    # Подпись периода
    if date_from is None and date_to is None:
        period_label = 'За весь период'
    elif date_from is not None and date_to is not None:
        period_label = f'с {date_from.strftime("%d.%m.%Y")} по {date_to.strftime("%d.%m.%Y")}'
    elif date_from is not None:
        period_label = f'с {date_from.strftime("%d.%m.%Y")}'
    else:
        period_label = f'по {date_to.strftime("%d.%m.%Y")}'

    # ── QR-коды периода ──────────────────────────────────────────────
    qr_period = QRCode.objects.filter(is_scanned=True)
    if date_from:
        qr_period = qr_period.filter(scanned_at__date__gte=date_from)
    if date_to:
        qr_period = qr_period.filter(scanned_at__date__lte=date_to)

    # ── Пользователи (зарегистрированные в периоде) ──────────────────
    user_qs = TelegramUser.objects.all()
    if date_from:
        user_qs = user_qs.filter(created_at__date__gte=date_from)
    if date_to:
        user_qs = user_qs.filter(created_at__date__lte=date_to)
    total_users        = user_qs.count()
    total_electricians = user_qs.filter(user_type='electrician').count()
    total_sellers      = user_qs.filter(user_type='seller').count()

    # ── QR-статистика ────────────────────────────────────────────────
    total_qrcodes    = QRCode.objects.count()            # всего сгенерировано (всегда)
    scanned_qrcodes  = qr_period.count()                 # отсканировано в периоде
    unscanned_qrcodes = QRCode.objects.filter(is_scanned=False).count()  # не использовано (всегда)

    # ── Баллы (начислено через QR в периоде) ─────────────────────────
    total_points_electricians = (
        qr_period.filter(scanned_by__user_type='electrician')
        .aggregate(total=Sum('points'))['total'] or 0
    )
    total_points_sellers = (
        qr_period.filter(scanned_by__user_type='seller')
        .aggregate(total=Sum('points'))['total'] or 0
    )

    # ── Подарки ──────────────────────────────────────────────────────
    total_gifts   = Gift.objects.count()
    active_gifts  = Gift.objects.filter(is_active=True).count()
    gift_qs = GiftRedemption.objects.all()
    if date_from:
        gift_qs = gift_qs.filter(requested_at__date__gte=date_from)
    if date_to:
        gift_qs = gift_qs.filter(requested_at__date__lte=date_to)
    pending_redemptions = gift_qs.filter(status='pending').count()

    # ── ТОП лидеры (по баллам QR в периоде) ─────────────────────────
    def get_top_leaders(user_type):
        qs = (
            qr_period
            .filter(scanned_by__user_type=user_type, scanned_by__isnull=False)
            .values('scanned_by__first_name', 'scanned_by__username')
            .annotate(points=Sum('points'))
            .order_by('-points')[:10]
        )
        return [
            {'first_name': r['scanned_by__first_name'],
             'username':   r['scanned_by__username'],
             'points':     r['points']}
            for r in qs
        ]

    top_electricians = get_top_leaders('electrician')
    top_sellers      = get_top_leaders('seller')

    # ── Вилояты ──────────────────────────────────────────────────────
    region_stats_electrician = defaultdict(lambda: {'points': 0, 'user_ids': set()})
    region_stats_seller      = defaultdict(lambda: {'points': 0, 'user_ids': set()})
    for qr in qr_period.select_related('scanned_by'):
        if qr.scanned_by and qr.scanned_by.region:
            uid = qr.scanned_by_id
            if qr.scanned_by.user_type == 'electrician':
                region_stats_electrician[qr.scanned_by.region]['points'] += qr.points
                region_stats_electrician[qr.scanned_by.region]['user_ids'].add(uid)
            elif qr.scanned_by.user_type == 'seller':
                region_stats_seller[qr.scanned_by.region]['points'] += qr.points
                region_stats_seller[qr.scanned_by.region]['user_ids'].add(uid)

    def sort_regions(stats):
        return sorted(
            [(get_region_name(rc, 'ru') or rc, len(d['user_ids']), d['points'])
             for rc, d in stats.items()],
            key=lambda x: x[2], reverse=True
        )

    regions_electrician = sort_regions(region_stats_electrician)
    regions_seller      = sort_regions(region_stats_seller)

    context = {
        **admin.site.each_context(request),
        'title': 'Дашборд',
        'period_label':             period_label,
        'date_from':                date_from.isoformat() if date_from else '',
        'date_to':                  date_to.isoformat()   if date_to   else '',
        'total_users':              total_users,
        'total_electricians':       total_electricians,
        'total_sellers':            total_sellers,
        'total_qrcodes':            total_qrcodes,
        'scanned_qrcodes':          scanned_qrcodes,
        'unscanned_qrcodes':        unscanned_qrcodes,
        'total_points_electricians': total_points_electricians,
        'total_points_sellers':     total_points_sellers,
        'total_gifts':              total_gifts,
        'active_gifts':             active_gifts,
        'pending_redemptions':      pending_redemptions,
        'top_electricians':         top_electricians,
        'top_sellers':              top_sellers,
        'regions_electrician':      regions_electrician,
        'regions_seller':           regions_seller,
    }

    return TemplateResponse(request, 'admin/dashboard.html', context)


def admin_logout_view(request):
    """Кастомный обработчик logout для админки, поддерживающий GET-запросы."""
    logout(request)
    return redirect(settings.LOGIN_URL)


urlpatterns = [
    path('admin/dashboard/', admin.site.admin_view(dashboard_view), name='dashboard'),
    path('admin/logout/', admin_logout_view, name='admin_logout'),
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

