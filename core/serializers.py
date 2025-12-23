"""
Serializers for core app.
"""
from rest_framework import serializers
from .models import TelegramUser, QRCode, Gift, GiftRedemption


class TelegramUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя Telegram."""
    
    class Meta:
        model = TelegramUser
        fields = [
            'id', 'telegram_id', 'username', 'first_name',
            'last_name', 'phone_number', 'user_type', 'points',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QRCodeSerializer(serializers.ModelSerializer):
    """Сериализатор для QR-кода."""
    scanned_by = TelegramUserSerializer(read_only=True)
    
    class Meta:
        model = QRCode
        fields = [
            'id', 'code', 'code_type', 'points',
            'generated_at', 'scanned_at', 'scanned_by', 'is_scanned'
        ]
        read_only_fields = ['id', 'generated_at', 'scanned_at', 'is_scanned']


class GiftSerializer(serializers.ModelSerializer):
    """Сериализатор для подарка."""
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Gift
        fields = [
            'id', 'name', 'description', 'image',
            'points_cost', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_image(self, obj):
        """Возвращает полный URL изображения."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class GiftRedemptionSerializer(serializers.ModelSerializer):
    """Сериализатор для получения подарка."""
    user = TelegramUserSerializer(read_only=True)
    gift = GiftSerializer(read_only=True)
    
    class Meta:
        model = GiftRedemption
        fields = [
            'id', 'user', 'gift', 'status',
            'requested_at', 'processed_at', 'admin_notes',
            'user_confirmed', 'user_comment', 'confirmed_at'
        ]
        read_only_fields = ['id', 'requested_at', 'processed_at', 'confirmed_at']

