"""
API views for core app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import TelegramUser, QRCode, Gift, GiftRedemption
from .serializers import (
    TelegramUserSerializer, QRCodeSerializer,
    GiftSerializer, GiftRedemptionSerializer
)


class TelegramUserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для пользователей Telegram."""
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    
    @action(detail=False, methods=['get'])
    def leaders(self, request):
        """Возвращает ТОП лидеров по баллам."""
        leaders = self.queryset.order_by('-points')[:10]
        serializer = self.get_serializer(leaders, many=True)
        return Response(serializer.data)


class QRCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для QR-кодов."""
    queryset = QRCode.objects.all()
    serializer_class = QRCodeSerializer
    lookup_field = 'code'


class GiftViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для подарков."""
    queryset = Gift.objects.filter(is_active=True)
    serializer_class = GiftSerializer

