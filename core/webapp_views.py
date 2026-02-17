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
from django.db import models
from functools import wraps
from .models import TelegramUser, Gift, GiftRedemption, QRCode, Promotion, PrivacyPolicy, AdminContactSettings
from .serializers import GiftSerializer, GiftRedemptionSerializer
from django.utils import timezone


def no_cache_response(func):
    """Декоратор для добавления заголовков отключения кеша к ответам API."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, Response):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['X-Accel-Expires'] = '0'
            # Удаляем заголовки кеширования, если они есть
            if 'ETag' in response:
                del response['ETag']
            if 'Last-Modified' in response:
                del response['Last-Modified']
        return response
    return wrapper


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
    
    # Версия для cache busting (изменяйте при обновлении CSS/JS)
    import time
    app_version = str(int(time.time()))  # Используем timestamp для гарантии обновления
    
    # Не используем Django i18n для кастомных языков, используем наш template tag
    # Просто передаем язык в контекст для использования в шаблоне
    context = {
        'user_language': user_language,
        'TELEGRAM_BOT_USERNAME': settings.TELEGRAM_BOT_USERNAME or '',
        'TELEGRAM_BOT_ADMIN_USERNAME': settings.TELEGRAM_BOT_ADMIN_USERNAME or '',
        'app_version': app_version,
    }
    
    response = render(request, 'webapp/index.html', context)
    
    # Добавляем заголовки для отключения кеширования
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['X-Accel-Expires'] = '0'  # Для nginx
    # Удаляем заголовки кеширования, если они есть
    if 'ETag' in response:
        del response['ETag']
    if 'Last-Modified' in response:
        del response['Last-Modified']
    
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
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
            'points': user.calculate_points(),
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
@no_cache_response
def get_translations(request):
    """Получает переводы для Web App на указанном языке."""
    from bot.translations import TRANSLATIONS
    
    language = request.GET.get('lang', 'uz_latin')
    
    # Получаем переводы для указанного языка
    translations = TRANSLATIONS.get(language, TRANSLATIONS.get('uz_latin', {}))
    
    return Response(translations)


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
def get_gifts(request):
    """Получает список активных подарков с фильтрацией по типу пользователя."""
    try:
        telegram_id = request.GET.get('telegram_id')
        
        # Базовый запрос для активных подарков
        gifts_query = Gift.objects.filter(is_active=True)
        
        # Если передан telegram_id, фильтруем по типу пользователя
        if telegram_id:
            try:
                user = TelegramUser.objects.get(telegram_id=int(telegram_id))
                # Показываем подарки для типа пользователя или без типа (для всех)
                if user.user_type:
                    gifts_query = gifts_query.filter(
                        models.Q(user_type=user.user_type) | models.Q(user_type__isnull=True)
                    )
                else:
                    # Если у пользователя нет типа, показываем только подарки без типа
                    gifts_query = gifts_query.filter(user_type__isnull=True)
            except TelegramUser.DoesNotExist:
                # Если пользователь не найден, показываем только подарки без типа
                gifts_query = gifts_query.filter(user_type__isnull=True)
        else:
            # Если telegram_id не передан, показываем только подарки без типа
            gifts_query = gifts_query.filter(user_type__isnull=True)
        
        gifts = gifts_query.order_by('order', 'points_cost')
        serializer = GiftSerializer(gifts, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
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
@no_cache_response
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
        
        # Проверяем, доступен ли подарок для типа пользователя
        if gift.user_type and gift.user_type != user.user_type:
            from bot.translations import get_text
            error_message = get_text(user, 'GIFT_NOT_AVAILABLE_FOR_USER_TYPE')
            return Response(
                {'error': error_message},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверяем баланс (вычисляемый, без кеша для точности)
        current_points = user.calculate_points(force=True)
        if current_points < gift.points_cost:
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
        
        # Инвалидируем кеш и пересчитываем баллы
        user.invalidate_points_cache()
        user.calculate_points(force=True)
        
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
@no_cache_response
def cancel_order(request):
    """Отмена заказа пользователем (в течение 1 часа после создания)."""
    redemption_id = request.data.get('redemption_id')
    telegram_id = request.data.get('telegram_id')
    
    if not redemption_id or not telegram_id:
        return Response(
            {'error': 'redemption_id and telegram_id are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
        redemption = GiftRedemption.objects.get(id=redemption_id, user=user)
        
        # Проверяем статус - можно отменить только pending
        if redemption.status != 'pending':
            return Response(
                {'error': 'Можно отменить только заказы в статусе ожидания'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем 1-часовое окно
        time_diff = timezone.now() - redemption.requested_at
        if time_diff.total_seconds() > 3600:  # 1 час = 3600 секунд
            from bot.translations import get_text
            return Response(
                {'error': get_text(user, 'WEBAPP_CANCEL_ORDER_EXPIRED')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Отменяем заказ
        redemption.status = 'cancelled_by_user'
        redemption.save(update_fields=['status'])
        
        # Инвалидируем кеш и пересчитываем баллы (баллы возвращаются автоматически)
        user.invalidate_points_cache()
        user.calculate_points(force=True)
        
        serializer = GiftRedemptionSerializer(redemption, context={'request': request})
        return Response({
            'success': True,
            'redemption': serializer.data,
            'new_points': user.calculate_points()
        })
        
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except GiftRedemption.DoesNotExist:
        return Response(
            {'error': 'Redemption not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@no_cache_response
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
        update_fields = ['user_confirmed', 'user_comment']

        if confirmed:
            # Пользователь подтвердил получение подарка
            redemption.confirmed_at = timezone.now()
            redemption.status = 'completed'
            update_fields.extend(['confirmed_at', 'status'])
        else:
            # Пользователь указал, что подарок не получил
            redemption.confirmed_at = timezone.now()
            redemption.status = 'not_received'
            update_fields.extend(['confirmed_at', 'status'])

        redemption.save(update_fields=update_fields)
        
        serializer = GiftRedemptionSerializer(redemption, context={'request': request})
        return Response(serializer.data)
        
    except GiftRedemption.DoesNotExist:
        return Response(
            {'error': 'Redemption not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
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
@no_cache_response
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


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
def get_promotion_detail(request, promotion_id):
    """Получает детальную информацию об акции."""
    try:
        promotion = Promotion.objects.get(id=promotion_id, is_active=True)
        
        promotion_data = {
            'id': promotion.id,
            'title': promotion.title,
            'image': request.build_absolute_uri(promotion.image.url) if promotion.image else None,
            'date': promotion.date.strftime('%d.%m.%Y') if promotion.date else None,
        }
        
        return Response(promotion_data)
    except Promotion.DoesNotExist:
        return Response(
            {'error': 'Promotion not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
def get_privacy_policy(request):
    """Получает политику конфиденциальности на указанном языке."""
    language = request.GET.get('lang', 'uz_latin')
    
    try:
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        
        if not policy:
            return Response(
                {'error': 'Privacy policy not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Выбираем PDF в зависимости от языка
        if language == 'uz_latin':
            pdf_file = policy.pdf_uz_latin
        elif language == 'ru':
            pdf_file = policy.pdf_ru
        else:
            pdf_file = policy.pdf_uz_latin
        
        # Формируем URL для PDF файла, если он существует
        pdf_url = None
        if pdf_file:
            pdf_url = request.build_absolute_uri(pdf_file.url)
        
        return Response({
            'pdf_url': pdf_url,
            'updated_at': policy.updated_at.strftime('%d.%m.%Y %H:%M') if policy.updated_at else None
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
@no_cache_response
def get_admin_contact(request):
    """Получает настройки контакта администратора."""
    try:
        contact_settings = AdminContactSettings.get_active_contact()
        
        if not contact_settings:
            return Response({
                'contact_type': None,
                'contact_value': None,
                'contact_url': None
            })
        
        return Response({
            'contact_type': contact_settings.contact_type,
            'contact_value': contact_settings.contact_value,
            'contact_url': contact_settings.get_contact_url()
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@no_cache_response
def update_user_language(request):
    """Обновляет язык пользователя."""
    telegram_id = request.data.get('telegram_id')
    language = request.data.get('language')
    
    if not telegram_id or not language:
        return Response(
            {'error': 'telegram_id and language are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if language not in ['uz_latin', 'ru']:
        return Response(
            {'error': 'Invalid language'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
        user.language = language
        user.save(update_fields=['language'])
        
        return Response({
            'success': True,
            'language': user.language
        })
    except TelegramUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@no_cache_response
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
    
    from django.db import transaction
    from bot.translations import get_text
    
    try:
        # Используем транзакцию для атомарности операций
        with transaction.atomic():
            # ВАЖНО: Проверяем количество неудачных попыток за сегодня ПЕРВЫМ ДЕЛОМ
            # Это предотвращает создание новых попыток, если лимит уже превышен
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_attempts = QRCodeScanAttempt.objects.filter(
                user=user,
                attempted_at__gte=today_start,
                is_successful=False
            ).count()
            
            max_attempts = getattr(settings, 'QR_CODE_MAX_ATTEMPTS', 5)
            if today_attempts >= max_attempts:
                error_message = get_text(user, 'QR_MAX_ATTEMPTS', max_attempts=max_attempts)
                return Response(
                    {'error': error_message, 'error_code': 'max_attempts'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Нормализуем ввод: приводим к верхнему регистру для поиска
            qr_code_str_normalized = qr_code_str.upper().strip()
            
            # Ищем QR-код по коду или hash_code (case-insensitive)
            qr_code = None
            try:
                # Сначала ищем по полному коду (E-ABC123 или D-ABC123) - нечувствительно к регистру
                qr_code = QRCode.objects.get(code__iexact=qr_code_str_normalized)
            except QRCode.DoesNotExist:
                # Если не нашли, пробуем найти по hash_code (без префикса) - нечувствительно к регистру
                try:
                    qr_code = QRCode.objects.get(hash_code__iexact=qr_code_str_normalized)
                except QRCode.DoesNotExist:
                    # QR-код не найден, возвращаем ошибку без создания попытки
                    error_message = get_text(user, 'QR_NOT_FOUND')
                    return Response(
                        {'error': error_message, 'error_code': 'not_found'},
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
                error_message = get_text(user, 'QR_ALREADY_SCANNED')
                return Response(
                    {'error': error_message, 'error_code': 'already_scanned'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Валидация типа кода - проверяем соответствие типу пользователя
            if user.user_type and user.user_type != qr_code.code_type:
                # Создаем запись о неудачной попытке (несоответствие типа)
                QRCodeScanAttempt.objects.create(
                    user=user,
                    qr_code=qr_code,
                    is_successful=False
                )
                error_message = get_text(user, 'QR_WRONG_TYPE')
                return Response(
                    {'error': error_message, 'error_code': 'wrong_type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Определяем тип пользователя на основе типа QR-кода (если еще не установлен)
            if not user.user_type:
                user.user_type = qr_code.code_type
                user.save(update_fields=['user_type'])
            
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
            
            # Инвалидируем кеш и пересчитываем баллы
            user.invalidate_points_cache()
            total_points = user.calculate_points(force=True)
            
            success_message = get_text(user, 'QR_ACTIVATED',
                points=qr_code.points,
                total_points=total_points
            )
            
            return Response({
                'success': True,
                'message': success_message,
                'points': qr_code.points,
                'total_points': total_points
            })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing QR code scan in webapp: {e}")
        
        error_message = get_text(user, 'QR_ERROR')
        return Response(
            {'error': error_message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

