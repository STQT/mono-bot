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
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    
    class Meta:
        model = Gift
        fields = [
            'id', 'name', 'description', 'image',
            'points_cost', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_language(self):
        """Определяет язык пользователя."""
        language = self.context.get('language')
        
        if not language:
            request = self.context.get('request')
            if request:
                telegram_id = request.GET.get('telegram_id') or request.data.get('telegram_id')
                if telegram_id:
                    try:
                        from .models import TelegramUser
                        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
                        language = user.language or 'uz_latin'
                    except (TelegramUser.DoesNotExist, ValueError, TypeError):
                        language = 'uz_latin'
                else:
                    language = 'uz_latin'
            else:
                language = 'uz_latin'
        
        return language
    
    def get_name(self, obj):
        """Возвращает название подарка на языке пользователя."""
        language = self.get_language()
        return obj.get_name(language)
    
    def get_image(self, obj):
        """Возвращает полный URL изображения."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_description(self, obj):
        """Возвращает описание на языке пользователя."""
        language = self.get_language()
        
        # Возвращаем описание на нужном языке
        if language == 'ru' and obj.description_ru:
            return obj.description_ru
        elif language == 'uz_latin' and obj.description_uz_latin:
            return obj.description_uz_latin
        # Fallback: возвращаем доступное описание или пустую строку
        return obj.description_uz_latin or obj.description_ru or ''


class GiftRedemptionSerializer(serializers.ModelSerializer):
    """Сериализатор для получения подарка."""
    user = TelegramUserSerializer(read_only=True)
    gift = serializers.SerializerMethodField()
    
    class Meta:
        model = GiftRedemption
        fields = [
            'id', 'user', 'gift', 'status',
            'requested_at', 'processed_at', 'admin_notes',
            'user_confirmed', 'user_comment', 'confirmed_at'
        ]
        read_only_fields = ['id', 'requested_at', 'processed_at', 'confirmed_at']
    
    def get_gift(self, obj):
        """Возвращает подарок с учетом языка пользователя."""
        # Получаем язык пользователя для передачи в GiftSerializer
        user_language = obj.user.language if obj.user and obj.user.language else 'uz_latin'
        context = self.context.copy()
        context['language'] = user_language
        return GiftSerializer(obj.gift, context=context).data

