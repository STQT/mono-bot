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
from .models import TelegramUser, Gift, GiftRedemption
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
    gifts = Gift.objects.filter(is_active=True).order_by('points_cost')
    serializer = GiftSerializer(gifts, many=True, context={'request': request})
    return Response(serializer.data)


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

