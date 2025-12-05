"""
URL configuration for core app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelegramUserViewSet, QRCodeViewSet, GiftViewSet
from .webapp_views import (
    webapp_view, get_user_data, get_gifts,
    get_user_redemptions, request_gift, confirm_delivery
)

router = DefaultRouter()
router.register(r'users', TelegramUserViewSet, basename='user')
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')
router.register(r'gifts', GiftViewSet, basename='gift')

urlpatterns = [
    path('', include(router.urls)),
    # Web App endpoints
    path('webapp/', webapp_view, name='webapp'),
    path('webapp/user/', get_user_data, name='webapp_user'),
    path('webapp/gifts/', get_gifts, name='webapp_gifts'),
    path('webapp/redemptions/', get_user_redemptions, name='webapp_redemptions'),
    path('webapp/request-gift/', request_gift, name='webapp_request_gift'),
    path('webapp/confirm-delivery/', confirm_delivery, name='webapp_confirm_delivery'),
]

