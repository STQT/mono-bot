"""
Telegram bot implementation using aiogram.
"""
import asyncio
import logging
import os
import django
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
from django.conf import settings
from django.db import transaction
from core.models import TelegramUser, QRCode, QRCodeScanAttempt, Gift, GiftRedemption
from core.utils import generate_qr_code_image

# Настройка Django для использования в боте
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mona.settings')
django.setup()

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot_token = settings.TELEGRAM_BOT_TOKEN
if not bot_token:
    logger.warning("TELEGRAM_BOT_TOKEN не установлен в настройках!")
    bot = None
    dp = None
else:
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())


class RegistrationStates(StatesGroup):
    """Состояния для регистрации пользователя."""
    waiting_for_phone = State()
    waiting_for_location = State()


class GiftRedemptionStates(StatesGroup):
    """Состояния для получения подарка."""
    selecting_gift = State()


def start_bot():
    """Запускает бота в отдельном потоке."""
    if not bot or not dp:
        logger.error("Бот не может быть запущен: TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    async def run():
        try:
            logger.info("Запуск Telegram бота...")
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())


@sync_to_async
def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Получает или создает пользователя Telegram."""
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
    )
    return user


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Если передан QR-код в аргументе
    if args:
        qr_code_str = args[0]
        await handle_qr_code_scan(message, user, qr_code_str, state)
        return
    
    # Проверяем, зарегистрирован ли пользователь
    if not user.phone_number or not user.latitude:
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Для начала работы необходимо пройти регистрацию.\n"
            "Пожалуйста, отправьте ваш номер телефона, используя кнопку ниже."
        )
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
            ],
            resize_keyboard=True
        )
        await message.answer("Нажмите на кнопку, чтобы отправить номер телефона:", reply_markup=keyboard)
        await state.set_state(RegistrationStates.waiting_for_phone)
    else:
        await show_main_menu(message, user)


@dp.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработчик получения номера телефона."""
    if message.contact:
        phone_number = message.contact.phone_number
        
        @sync_to_async
        def update_phone():
            user = TelegramUser.objects.get(telegram_id=message.from_user.id)
            user.phone_number = phone_number
            user.save(update_fields=['phone_number'])
            return user
        
        await update_phone()
        
        await message.answer(
            "✅ Номер телефона сохранен!\n\n"
            "Теперь отправьте вашу локацию, используя кнопку ниже."
        )
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="📍 Отправить локацию", request_location=True)]
            ],
            resize_keyboard=True
        )
        await message.answer("Нажмите на кнопку, чтобы отправить локацию:", reply_markup=keyboard)
        await state.set_state(RegistrationStates.waiting_for_location)
    else:
        await message.answer("Пожалуйста, используйте кнопку для отправки номера телефона.")


@dp.message(RegistrationStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Обработчик получения локации."""
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        
        @sync_to_async
        def update_location():
            user = TelegramUser.objects.get(telegram_id=message.from_user.id)
            user.latitude = latitude
            user.longitude = longitude
            user.save(update_fields=['latitude', 'longitude'])
            return user
        
        await update_location()
        
        await message.answer("✅ Регистрация завершена!")
        await state.clear()
        await show_main_menu(message, user)
    else:
        await message.answer("Пожалуйста, используйте кнопку для отправки локации.")


async def handle_qr_code_scan(message: Message, user, qr_code_str: str, state: FSMContext):
    """Обрабатывает сканирование QR-кода."""
    try:
        @sync_to_async
        def process_qr_scan():
            from django.utils import timezone
            
            # Проверяем количество попыток
            attempts_count = QRCodeScanAttempt.objects.filter(
                user=user,
                qr_code__code=qr_code_str
            ).count()
            
            if attempts_count >= settings.QR_CODE_MAX_ATTEMPTS:
                return {'error': 'max_attempts'}
            
            # Ищем QR-код
            try:
                qr_code = QRCode.objects.get(code=qr_code_str)
            except QRCode.DoesNotExist:
                return {'error': 'not_found'}
            
            # Проверяем, не был ли уже отсканирован
            if qr_code.is_scanned:
                # Создаем запись о неудачной попытке
                QRCodeScanAttempt.objects.create(
                    user=user,
                    qr_code=qr_code,
                    is_successful=False
                )
                return {'error': 'already_scanned'}
            
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
            
            return {
                'success': True,
                'points': qr_code.points,
                'total_points': user.points
            }
        
        result = await process_qr_scan()
        
        if result.get('error') == 'max_attempts':
            await message.answer(
                f"❌ Превышено максимальное количество попыток ({settings.QR_CODE_MAX_ATTEMPTS}).\n"
                "Этот QR-код больше нельзя использовать."
            )
        elif result.get('error') == 'not_found':
            await message.answer("❌ QR-код не найден. Проверьте правильность кода.")
        elif result.get('error') == 'already_scanned':
            await message.answer("❌ Этот QR-код уже был использован другим пользователем.")
        elif result.get('success'):
            await message.answer(
                f"✅ QR-код успешно активирован!\n\n"
                f"💰 Вам начислено {result['points']} баллов.\n"
                f"📊 Ваш текущий баланс: {result['total_points']} баллов."
            )
            await show_main_menu(message, user)
        
    except Exception as e:
        logger.error(f"Error processing QR code scan: {e}")
        await message.answer("❌ Произошла ошибка при обработке QR-кода. Попробуйте позже.")


async def show_main_menu(message: Message, user: TelegramUser):
    """Показывает главное меню бота."""
    @sync_to_async
    def get_user_points():
        user_obj = TelegramUser.objects.get(telegram_id=message.from_user.id)
        return user_obj.points
    
    points = await get_user_points()
    
    # Создаем кнопку для Web App
    # Используем полный URL с протоколом
    from django.conf import settings
    web_app_url = f"https://{settings.ALLOWED_HOSTS[0]}/api/webapp/" if settings.ALLOWED_HOSTS and not settings.DEBUG else f"http://localhost:8000/api/webapp/"
    web_app_button = types.WebAppInfo(url=web_app_url)
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📱 Мои подарки", web_app=web_app_button)],
            [types.KeyboardButton(text="🎁 Подарки")],
            [types.KeyboardButton(text="📊 Мой баланс"), types.KeyboardButton(text="🏆 ТОП лидеры")],
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"👋 Главное меню\n\n"
        f"💰 Ваш баланс: {points} баллов\n\n"
        f"Выберите действие:",
        reply_markup=keyboard
    )


@dp.message(lambda message: message.text == "📊 Мой баланс")
async def show_balance(message: Message):
    """Показывает баланс пользователя."""
    @sync_to_async
    def get_user_points():
        user = TelegramUser.objects.get(telegram_id=message.from_user.id)
        return user.points
    
    points = await get_user_points()
    await message.answer(f"💰 Ваш текущий баланс: {points} баллов")


@dp.message(lambda message: message.text == "🎁 Подарки")
async def show_gifts(message: Message, state: FSMContext):
    """Показывает список доступных подарков."""
    @sync_to_async
    def get_gifts_and_user():
        user = TelegramUser.objects.get(telegram_id=message.from_user.id)
        gifts = list(Gift.objects.filter(is_active=True).order_by('points_cost'))
        return user, gifts
    
    user, gifts = await get_gifts_and_user()
    
    if not gifts:
        await message.answer("😔 К сожалению, сейчас нет доступных подарков.")
        return
    
    text = "🎁 Доступные подарки:\n\n"
    buttons = []
    
    for gift in gifts:
        can_afford = "✅" if user.points >= gift.points_cost else "❌"
        text += f"{can_afford} {gift.name} - {gift.points_cost} баллов\n"
        buttons.append([types.InlineKeyboardButton(
            text=f"{gift.name} ({gift.points_cost} баллов)",
            callback_data=f"gift_{gift.id}"
        )])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(GiftRedemptionStates.selecting_gift)


@dp.callback_query(lambda c: c.data.startswith("gift_"))
async def process_gift_selection(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор подарка."""
    gift_id = int(callback.data.split("_")[1])
    
    @sync_to_async
    def process_gift():
        try:
            gift = Gift.objects.get(id=gift_id, is_active=True)
            user = TelegramUser.objects.get(telegram_id=callback.from_user.id)
            
            if user.points < gift.points_cost:
                return {'error': 'insufficient_points'}
            
            # Создаем запрос на получение подарка
            GiftRedemption.objects.create(
                user=user,
                gift=gift,
                status='pending'
            )
            
            # Списываем баллы
            user.points -= gift.points_cost
            user.save(update_fields=['points'])
            
            return {
                'success': True,
                'gift_name': gift.name,
                'remaining_points': user.points
            }
        except Gift.DoesNotExist:
            return {'error': 'not_found'}
    
    try:
        result = await process_gift()
        
        if result.get('error') == 'insufficient_points':
            await callback.answer("❌ Недостаточно баллов для этого подарка!", show_alert=True)
        elif result.get('error') == 'not_found':
            await callback.answer("❌ Подарок не найден!", show_alert=True)
        elif result.get('success'):
            await callback.answer("✅ Запрос на получение подарка отправлен!", show_alert=True)
            await callback.message.answer(
                f"✅ Ваш запрос на получение подарка '{result['gift_name']}' принят!\n\n"
                f"Администратор обработает ваш запрос в ближайшее время.\n"
                f"💰 Ваш текущий баланс: {result['remaining_points']} баллов"
            )
            await state.clear()
    except Exception as e:
        logger.error(f"Error processing gift selection: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)


@dp.message(lambda message: message.text == "🏆 ТОП лидеры")
async def show_leaders(message: Message):
    """Показывает ТОП лидеров."""
    @sync_to_async
    def get_leaders():
        return list(TelegramUser.objects.order_by('-points')[:10])
    
    leaders = await get_leaders()
    
    text = "🏆 ТОП-10 лидеров:\n\n"
    position = 1
    
    for leader in leaders:
        emoji = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
        text += f"{emoji} {leader.first_name or 'Пользователь'} - {leader.points} баллов\n"
        position += 1
    
    await message.answer(text)


@dp.message()
async def handle_unknown_message(message: Message):
    """Обработчик неизвестных сообщений."""
    await message.answer("Я не понимаю эту команду. Используйте кнопки меню.")

