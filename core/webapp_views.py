"""
Views for Telegram Web App.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.conf import settings
from django.utils import translation
from .models import TelegramUser, Gift, GiftRedemption, QRCode, Promotion
from .serializers import GiftSerializer, GiftRedemptionSerializer
from django.utils import timezone


def webapp_view(request):
    """Главная страница веб-приложения."""
    # Определяем язык пользователя из initData или параметра
    user_language = 'uz_latin'  # По умолчанию
    
    # Пытаемся получить язык из Telegram initData (передается через JavaScript)
    # Telegram Web App передает initData через window.Telegram.WebApp.initData
    # Мы будем получать язык через JavaScript и передавать в контекст
    
    # Если передан telegram_id в GET параметрах, получаем язык из БД
    telegram_id = request.GET.get('telegram_id')
    if telegram_id:
        try:
            user = TelegramUser.objects.get(telegram_id=int(telegram_id))
            user_language = user.language
        except (TelegramUser.DoesNotExist, ValueError):
            pass
    
    # Не используем Django i18n для кастомных языков, используем наш template tag
    # Просто передаем язык в контекст для использования в шаблоне
    context = {
        'user_language': user_language,
        'TELEGRAM_BOT_USERNAME': settings.TELEGRAM_BOT_USERNAME or '',
    }
    
    return render(request, 'webapp/index.html', context)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_data(request):
    """Получает данные пользователя по telegram_id из initData."""
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        return Response(
            {'error': 'telegram_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
        serializer = {
            'id': user.id,
            'telegram_id': user.telegram_id,
            'first_name': user.first_name,
            'username': user.username,
            'points': user.points,
            'user_type': user.user_type,
            'language': user.language,
        }
        return Response(serializer)
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_translations(request):
    """Получает переводы для Web App на указанном языке."""
    from bot.translations import TRANSLATIONS
    
    language = request.GET.get('lang', 'uz_latin')
    
    # Получаем переводы для указанного языка
    translations = TRANSLATIONS.get(language, TRANSLATIONS.get('uz_latin', {}))
    
    return Response(translations)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_gifts(request):
    """Получает список активных подарков."""
    try:
        gifts = Gift.objects.filter(is_active=True).order_by('points_cost')
        serializer = GiftSerializer(gifts, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_redemptions(request):
    """Получает список запросов на подарки пользователя."""
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        return Response(
            {'error': 'telegram_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
        redemptions = GiftRedemption.objects.filter(user=user).order_by('-requested_at')
        serializer = GiftRedemptionSerializer(redemptions, many=True, context={'request': request})
        return Response(serializer.data)
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def request_gift(request):
    """Создает запрос на получение подарка."""
    telegram_id = request.data.get('telegram_id')
    gift_id = request.data.get('gift_id')
    
    if not telegram_id or not gift_id:
        return Response(
            {'error': 'telegram_id and gift_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
        gift = Gift.objects.get(id=gift_id, is_active=True)
        
        if user.points < gift.points_cost:
            # Получаем перевод ошибки
            from bot.translations import get_text
            error_message = get_text(user, 'INSUFFICIENT_POINTS')
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем запрос
        redemption = GiftRedemption.objects.create(
            user=user,
            gift=gift,
            status='pending'
        )
        
        # Списываем баллы
        user.points -= gift.points_cost
        user.save(update_fields=['points'])
        
        serializer = GiftRedemptionSerializer(redemption, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Gift.DoesNotExist:
        return Response(
            {'error': 'Gift not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_delivery(request):
    """Подтверждает получение заказа или оставляет комментарий."""
    redemption_id = request.data.get('redemption_id')
    confirmed = request.data.get('confirmed', False)
    comment = request.data.get('comment', '')
    
    if not redemption_id:
        return Response(
            {'error': 'redemption_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        redemption = GiftRedemption.objects.get(id=redemption_id)
        
        redemption.user_confirmed = confirmed
        redemption.user_comment = comment
        if confirmed:
            redemption.confirmed_at = timezone.now()
        redemption.save(update_fields=['user_confirmed', 'user_comment', 'confirmed_at'])
        
        serializer = GiftRedemptionSerializer(redemption, context={'request': request})
        return Response(serializer.data)
        
    except GiftRedemption.DoesNotExist:
        return Response(
            {'error': 'Redemption not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_qr_history(request):
    """Получает историю отсканированных QR-кодов пользователя."""
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        return Response(
            {'error': 'telegram_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
        # Получаем все отсканированные QR-коды пользователя
        qr_codes = QRCode.objects.filter(
            scanned_by=user,
            is_scanned=True
        ).order_by('-scanned_at')
        
        history = []
        for qr in qr_codes:
            history.append({
                'id': qr.id,
                'code': qr.code,
                'points': qr.points,
                'scanned_at': qr.scanned_at.strftime('%d.%m.%Y') if qr.scanned_at else None,
                'code_type': qr.get_code_type_display(),
            })
        
        return Response(history)
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_promotions(request):
    """Получает список активных акций для слайдера."""
    try:
        promotions = Promotion.objects.filter(is_active=True).order_by('order', '-created_at')
        
        promotions_data = []
        for promotion in promotions:
            promotions_data.append({
                'id': promotion.id,
                'title': promotion.title,
                'image': request.build_absolute_uri(promotion.image.url) if promotion.image else None,
                'date': promotion.date.strftime('%d.%m.%Y') if promotion.date else None,
            })
        
        return Response(promotions_data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_qr_code(request):
    """Регистрирует QR-код для пользователя."""
    from django.utils import timezone
    from django.conf import settings
    from core.models import QRCode, QRCodeScanAttempt
    
    telegram_id = request.data.get('telegram_id')
    qr_code_str = request.data.get('qr_code')
    
    if not telegram_id or not qr_code_str:
        return Response(
            {'error': 'telegram_id and qr_code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Проверяем количество неудачных попыток за сегодня
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_attempts = QRCodeScanAttempt.objects.filter(
            user=user,
            attempted_at__gte=today_start,
            is_successful=False
        ).count()
        
        max_attempts = getattr(settings, 'QR_CODE_MAX_ATTEMPTS', 3)
        if today_attempts >= max_attempts:
            from bot.translations import get_text
            error_message = get_text(user, 'QR_MAX_ATTEMPTS', max_attempts=max_attempts)
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ищем QR-код по коду или hash_code
        try:
            # Сначала ищем по полному коду (E-ABC123 или D-ABC123)
            qr_code = QRCode.objects.get(code=qr_code_str)
        except QRCode.DoesNotExist:
            # Если не нашли, пробуем найти по hash_code (без префикса)
            try:
                qr_code = QRCode.objects.get(hash_code=qr_code_str)
            except QRCode.DoesNotExist:
                from bot.translations import get_text
                error_message = get_text(user, 'QR_NOT_FOUND')
                return Response(
                    {'error': error_message},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Проверяем, не был ли уже отсканирован
        if qr_code.is_scanned:
            # Создаем запись о неудачной попытке
            QRCodeScanAttempt.objects.create(
                user=user,
                qr_code=qr_code,
                is_successful=False
            )
            from bot.translations import get_text
            error_message = get_text(user, 'QR_ALREADY_SCANNED')
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Определяем тип пользователя на основе типа QR-кода (если еще не установлен)
        if not user.user_type:
            user.user_type = qr_code.code_type
            user.save(update_fields=['user_type'])
        
        # Начисляем баллы
        user.points += qr_code.points
        user.save(update_fields=['points'])
        
        # Отмечаем QR-код как отсканированный
        qr_code.is_scanned = True
        qr_code.scanned_at = timezone.now()
        qr_code.scanned_by = user
        qr_code.save(update_fields=['is_scanned', 'scanned_at', 'scanned_by'])
        
        # Создаем запись об успешной попытке
        QRCodeScanAttempt.objects.create(
            user=user,
            qr_code=qr_code,
            is_successful=True
        )
        
        from bot.translations import get_text
        success_message = get_text(user, 'QR_ACTIVATED',
            points=qr_code.points,
            total_points=user.points
        )
        
        return Response({
            'success': True,
            'message': success_message,
            'points': qr_code.points,
            'total_points': user.points
        })
        
    except Exception as e:
        from bot.translations import get_text
        error_message = get_text(user, 'QR_ERROR')
        return Response(
            {'error': error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

