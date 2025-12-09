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
from .translations import get_text, TRANSLATIONS

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
    waiting_for_language = State()
    waiting_for_user_type = State()
    waiting_for_privacy = State()
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


def get_web_app_url():
    """Получает URL для Web App на основе настроек."""
    # Приоритет 1: Явно указанный WEB_APP_URL (для тестирования через ngrok)
    if settings.WEB_APP_URL and settings.WEB_APP_URL.startswith('https://'):
        return f"{settings.WEB_APP_URL.rstrip('/')}/api/webapp/"
    # Приоритет 2: WEBHOOK_URL (production)
    elif settings.WEBHOOK_URL and settings.WEBHOOK_URL.startswith('https://'):
        return f"{settings.WEBHOOK_URL.rstrip('/')}/api/webapp/"
    # Приоритет 3: ALLOWED_HOSTS в production
    elif not settings.DEBUG and settings.ALLOWED_HOSTS:
        domain = settings.ALLOWED_HOSTS[0]
        if domain and domain != 'localhost':
            return f"https://{domain}/api/webapp/"
    return None


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


@sync_to_async
def is_registration_complete(user):
    """Проверяет, завершена ли регистрация пользователя."""
    return (
        user.language and
        user.user_type and
        user.privacy_accepted and
        user.phone_number and
        user.latitude is not None and
        user.longitude is not None
    )


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""
    # Парсим аргументы команды /start
    # Формат может быть: /start qr_ABC123 или /start E-ABC123
    args_text = message.text.split()[1:] if len(message.text.split()) > 1 else []
    qr_code_str = None
    
    # Проверяем формат ?start=qr_{qr_code} или ?start={qr_code}
    if args_text:
        arg = args_text[0]
        if arg.startswith('qr_'):
            qr_code_str = arg[3:]  # Убираем префикс 'qr_' - это hash_code
        else:
            # Если формат без префикса, пробуем использовать как есть (может быть полный код или hash_code)
            qr_code_str = arg
    
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Если передан QR-код в аргументе
    if qr_code_str:
        await handle_qr_code_scan(message, user, qr_code_str, state)
        return
    
    # Проверяем, завершена ли регистрация
    registration_complete = await is_registration_complete(user)
    
    if registration_complete:
        # Пользователь уже зарегистрирован - показываем меню
        await show_main_menu(message, user)
        await state.clear()
        return
    
    # Начинаем процесс регистрации с первого шага
    await state.clear()
    
    # Шаг 1: Выбор языка
    if not user.language:
        await ask_language(message, user, state)
        return
    
    # Шаг 2: Выбор типа пользователя
    if not user.user_type:
        await ask_user_type(message, user, state)
        return
    
    # Шаг 3: Согласие на политику конфиденциальности
    if not user.privacy_accepted:
        await ask_privacy_acceptance(message, user, state)
        return
    
    # Шаг 4: Телефонный номер
    if not user.phone_number:
        await ask_phone(message, user, state)
        return
    
    # Шаг 5: Локация
    if user.latitude is None or user.longitude is None:
        await ask_location(message, user, state)
        return


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
        
        user = await update_phone()
        await message.answer(get_text(user, 'PHONE_SAVED'))
        
        # Переходим к следующему шагу - локация
        await ask_location(message, user, state)
    else:
        @sync_to_async
        def get_user():
            return TelegramUser.objects.get(telegram_id=message.from_user.id)
        user = await get_user()
        await message.answer(get_text(user, 'USE_BUTTON_PHONE'))


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
        
        user = await update_location()
        
        await message.answer(get_text(user, 'REGISTRATION_COMPLETE'))
        await state.clear()
        
        # Убираем клавиатуру
        remove_keyboard = types.ReplyKeyboardRemove()
        await message.answer(get_text(user, 'REGISTRATION_COMPLETE_MESSAGE'), reply_markup=remove_keyboard)
        
        # Показываем главное меню
        await show_main_menu(message, user)
    else:
        @sync_to_async
        def get_user_for_location():
            return TelegramUser.objects.get(telegram_id=message.from_user.id)
        user = await get_user_for_location()
        await message.answer(get_text(user, 'USE_BUTTON_LOCATION'))


async def ask_language(message: Message, user, state: FSMContext):
    """Спрашивает у пользователя язык интерфейса."""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="🇺🇿 O'zbek (Lotin)",
            callback_data='lang_uz_latin'
        )],
        [types.InlineKeyboardButton(
            text="🇺🇿 Ўзбек (Кирилл)",
            callback_data='lang_uz_cyrillic'
        )],
        [types.InlineKeyboardButton(
            text="🇷🇺 Русский",
            callback_data='lang_ru'
        )],
    ])
    await message.answer("🌐 Tilni tanlang / Выберите язык / Выберите язык:", reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_language)


async def ask_user_type(message: Message, user, state: FSMContext):
    """Спрашивает у пользователя его тип (электрик или продавец)."""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=get_text(user, 'USER_TYPE_ELECTRICIAN'),
            callback_data='user_type_electrician'
        )],
        [types.InlineKeyboardButton(
            text=get_text(user, 'USER_TYPE_SELLER'),
            callback_data='user_type_seller'
        )],
    ])
    await message.answer(get_text(user, 'SELECT_USER_TYPE'), reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_user_type)


async def ask_privacy_acceptance(message: Message, user, state: FSMContext):
    """Спрашивает согласие на политику конфиденциальности."""
    from core.models import PrivacyPolicy
    
    @sync_to_async
    def get_privacy_text():
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if policy:
            if user.language == 'uz_latin':
                return policy.content_uz_latin or ""
            elif user.language == 'uz_cyrillic':
                return policy.content_uz_cyrillic or policy.content_uz_latin or ""
            elif user.language == 'ru':
                return policy.content_ru or policy.content_uz_latin or ""
        return get_text(user, 'PRIVACY_POLICY_TEXT')
    
    privacy_text = await get_privacy_text()
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=get_text(user, 'ACCEPT_PRIVACY'),
            callback_data='accept_privacy'
        )],
        [types.InlineKeyboardButton(
            text=get_text(user, 'DECLINE_PRIVACY'),
            callback_data='decline_privacy'
        )],
    ])
    await message.answer(privacy_text + "\n\n" + get_text(user, 'ACCEPT_PRIVACY_QUESTION'), reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_privacy)


async def ask_phone(message: Message, user, state: FSMContext):
    """Спрашивает номер телефона."""
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=get_text(user, 'SEND_PHONE_BUTTON'), request_contact=True)]
        ],
        resize_keyboard=True
    )
    await message.answer(get_text(user, 'SEND_PHONE'), reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_phone)


async def ask_location(message: Message, user, state: FSMContext):
    """Спрашивает локацию."""
    send_location_text = get_text(user, 'SEND_LOCATION')
    button_text = send_location_text.split(':')[0] if ':' in send_location_text else send_location_text.split('\n')[0]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📍 " + button_text, request_location=True)]
        ],
        resize_keyboard=True
    )
    await message.answer(get_text(user, 'SEND_LOCATION'), reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_location)


@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор языка."""
    language = callback.data.split('_')[1]  # uz_latin, uz_cyrillic или ru
    
    @sync_to_async
    def update_language():
        user = TelegramUser.objects.get(telegram_id=callback.from_user.id)
        user.language = language
        user.save(update_fields=['language'])
        return user
    
    user = await update_language()
    
    await callback.answer(get_text(user, 'LANGUAGE_CHANGED'))
    await callback.message.delete()
    
    # Переходим к следующему шагу - выбор типа пользователя
    await ask_user_type(callback.message, user, state)


@dp.callback_query(lambda c: c.data.startswith('user_type_'))
async def process_user_type_selection(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор типа пользователя."""
    user_type = callback.data.split('_')[2]  # electrician или seller
    
    @sync_to_async
    def update_user_type():
        user = TelegramUser.objects.get(telegram_id=callback.from_user.id)
        user.user_type = user_type
        user.save(update_fields=['user_type'])
        return user
    
    user = await update_user_type()
    
    await callback.answer(get_text(user, 'USER_TYPE_SAVED'))
    await callback.message.delete()
    
    # Переходим к следующему шагу - согласие на политику конфиденциальности
    await ask_privacy_acceptance(callback.message, user, state)


@dp.callback_query(lambda c: c.data in ['accept_privacy', 'decline_privacy'])
async def process_privacy_acceptance(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает согласие на политику конфиденциальности."""
    if callback.data == 'decline_privacy':
        @sync_to_async
        def get_user():
            return TelegramUser.objects.get(telegram_id=callback.from_user.id)
        user = await get_user()
        await callback.answer(get_text(user, 'PRIVACY_DECLINED'))
        await callback.message.answer(get_text(user, 'PRIVACY_REQUIRED'))
        return
    
    @sync_to_async
    def update_privacy():
        user = TelegramUser.objects.get(telegram_id=callback.from_user.id)
        user.privacy_accepted = True
        user.save(update_fields=['privacy_accepted'])
        return user
    
    user = await update_privacy()
    
    await callback.answer(get_text(user, 'PRIVACY_ACCEPTED'))
    await callback.message.delete()
    
    # Переходим к следующему шагу - телефонный номер
    await ask_phone(callback.message, user, state)


async def handle_qr_code_scan(message: Message, user, qr_code_str: str, state: FSMContext):
    """Обрабатывает сканирование QR-кода."""
    try:
        @sync_to_async
        def process_qr_scan():
            from django.utils import timezone
            from datetime import datetime, time as dt_time
            
            # ВАЖНО: Проверяем количество неудачных попыток за сегодня ПЕРВЫМ ДЕЛОМ
            # Это предотвращает создание новых попыток, если лимит уже превышен
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_attempts = QRCodeScanAttempt.objects.filter(
                user=user,
                attempted_at__gte=today_start,
                is_successful=False
            ).count()
            
            if today_attempts >= settings.QR_CODE_MAX_ATTEMPTS:
                # Лимит превышен - сразу возвращаем ошибку без создания новой попытки
                return {'error': 'max_attempts'}
            
            # Ищем QR-код по коду или hash_code
            try:
                # Сначала ищем по полному коду (E-ABC123 или D-ABC123)
                qr_code = QRCode.objects.get(code=qr_code_str)
            except QRCode.DoesNotExist:
                # Если не нашли, пробуем найти по hash_code (без префикса)
                try:
                    qr_code = QRCode.objects.get(hash_code=qr_code_str)
                except QRCode.DoesNotExist:
                    # Создаем запись о неудачной попытке только если лимит еще не превышен
                    # Но сначала проверяем, не превысили ли мы лимит после предыдущей проверки
                    today_attempts_after = QRCodeScanAttempt.objects.filter(
                        user=user,
                        attempted_at__gte=today_start,
                        is_successful=False
                    ).count()
                    if today_attempts_after < settings.QR_CODE_MAX_ATTEMPTS:
                        # Создаем временный QR-код для записи попытки (если нужно)
                        # Но так как QR-код не найден, просто возвращаем ошибку
                        return {'error': 'not_found'}
                    else:
                        return {'error': 'max_attempts'}
            
            # Проверяем, не был ли уже отсканирован
            if qr_code.is_scanned:
                # Проверяем лимит еще раз перед созданием попытки
                today_attempts_before_scan = QRCodeScanAttempt.objects.filter(
                    user=user,
                    attempted_at__gte=today_start,
                    is_successful=False
                ).count()
                
                if today_attempts_before_scan >= settings.QR_CODE_MAX_ATTEMPTS:
                    return {'error': 'max_attempts'}
                
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
            await message.answer(get_text(user, 'QR_MAX_ATTEMPTS', max_attempts=settings.QR_CODE_MAX_ATTEMPTS))
        elif result.get('error') == 'not_found':
            await message.answer(get_text(user, 'QR_NOT_FOUND'))
        elif result.get('error') == 'already_scanned':
            await message.answer(get_text(user, 'QR_ALREADY_SCANNED'))
        elif result.get('success'):
            await message.answer(get_text(user, 'QR_ACTIVATED',
                points=result['points'],
                total_points=result['total_points']
            ))
            # Если пользователь еще не зарегистрирован, продолжаем регистрацию
            if not user.phone_number or not user.latitude:
                keyboard = types.ReplyKeyboardMarkup(
                    keyboard=[
                        [types.KeyboardButton(text=get_text(user, 'SEND_PHONE').split(':')[0] + "...", request_contact=True)]
                    ],
                    resize_keyboard=True
                )
                await message.answer(get_text(user, 'SEND_PHONE'), reply_markup=keyboard)
                await state.set_state(RegistrationStates.waiting_for_phone)
            else:
                await show_main_menu(message, user)
        
    except Exception as e:
        logger.error(f"Error processing QR code scan: {e}")
        await message.answer(get_text(user, 'QR_ERROR'))


async def show_main_menu(message: Message, user: TelegramUser):
    """Показывает главное меню бота."""
    @sync_to_async
    def get_user_points():
        user_obj = TelegramUser.objects.get(telegram_id=message.from_user.id)
        return user_obj.points
    
    points = await get_user_points()
    
    # Создаем reply keyboard кнопки
    keyboard_buttons = []
    
    # Определяем URL для Web App
    web_app_url = get_web_app_url()
    
    # Добавляем остальные кнопки (без Web App кнопки в reply keyboard)
    keyboard_buttons.extend([
        [types.KeyboardButton(text=get_text(user, 'GIFTS'))],
        [types.KeyboardButton(text=get_text(user, 'MY_BALANCE')), types.KeyboardButton(text=get_text(user, 'TOP_LEADERS'))],
        [types.KeyboardButton(text=get_text(user, 'LANGUAGE'))],
    ])
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )
    
    # Создаем inline кнопку для Web App
    inline_keyboard = None
    if web_app_url:
        try:
            web_app_button = types.InlineKeyboardButton(
                text=get_text(user, 'MY_GIFTS'),
                web_app=types.WebAppInfo(url=web_app_url)
            )
            inline_keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[[web_app_button]]
            )
        except Exception as e:
            logger.warning(f"Не удалось создать Web App inline кнопку: {e}")
    
    await message.answer(
        get_text(user, 'MAIN_MENU', points=points),
        reply_markup=keyboard
    )
    
    # Отправляем отдельное сообщение с inline кнопкой для Web App
    if inline_keyboard:
        await message.answer(
            get_text(user, 'OPEN_WEB_APP'),
            reply_markup=inline_keyboard
        )


@dp.message()
async def handle_message(message: Message, state: FSMContext = None):
    """Универсальный обработчик сообщений."""
    @sync_to_async
    def get_user():
        return TelegramUser.objects.get(telegram_id=message.from_user.id)
    
    user = await get_user()
    
    # Если пользователь в состоянии регистрации, не обрабатываем как QR-код
    if state:
        current_state = await state.get_state()
        if current_state in [RegistrationStates.waiting_for_phone, RegistrationStates.waiting_for_location, RegistrationStates.waiting_for_user_type]:
            # Пропускаем обработку, пусть обрабатывают соответствующие handlers
            return
    
    # Получаем все возможные варианты текстов кнопок
    all_balance_texts = [
        TRANSLATIONS['uz_latin']['MY_BALANCE'],
        TRANSLATIONS['uz_cyrillic']['MY_BALANCE'],
        TRANSLATIONS['ru']['MY_BALANCE'],
    ]
    
    all_gifts_texts = [
        TRANSLATIONS['uz_latin']['GIFTS'],
        TRANSLATIONS['uz_cyrillic']['GIFTS'],
        TRANSLATIONS['ru']['GIFTS'],
    ]
    
    all_leaders_texts = [
        TRANSLATIONS['uz_latin']['TOP_LEADERS'],
        TRANSLATIONS['uz_cyrillic']['TOP_LEADERS'],
        TRANSLATIONS['ru']['TOP_LEADERS'],
    ]
    
    all_language_texts = [
        TRANSLATIONS['uz_latin']['LANGUAGE'],
        TRANSLATIONS['uz_cyrillic']['LANGUAGE'],
        TRANSLATIONS['ru']['LANGUAGE'],
    ]
    
    # Обрабатываем в зависимости от текста
    if message.text in all_balance_texts:
        await show_balance(message, user)
    elif message.text in all_gifts_texts:
        await show_gifts(message, state)
    elif message.text in all_leaders_texts:
        await show_leaders(message)
    elif message.text in all_language_texts:
        await show_language_selection(message)
    else:
        # Если это не команда меню, пытаемся обработать как QR-код
        # Пользователь может ввести QR-код вручную
        # Не обрабатываем контакты и локации как QR-коды
        if message.text and len(message.text.strip()) > 0 and not message.contact and not message.location:
            # Убираем пробелы и пробуем обработать как QR-код
            qr_code_str = message.text.strip()
            await handle_qr_code_scan(message, user, qr_code_str, state)
        else:
            await handle_unknown_message(message)


async def show_balance(message: Message, user: TelegramUser):
    """Показывает баланс пользователя."""
    await message.answer(get_text(user, 'BALANCE_INFO', points=user.points))




async def show_gifts(message: Message, state: FSMContext):
    """Показывает список доступных подарков."""
    @sync_to_async
    def get_gifts_and_user():
        user = TelegramUser.objects.get(telegram_id=message.from_user.id)
        gifts = list(Gift.objects.filter(is_active=True).order_by('points_cost'))
        return user, gifts
    
    user, gifts = await get_gifts_and_user()
    
    if not gifts:
        await message.answer(get_text(user, 'NO_GIFTS'))
        return
    
    text = get_text(user, 'GIFTS_LIST')
    buttons = []
    
    for gift in gifts:
        can_afford = "✅" if user.points >= gift.points_cost else "❌"
        # Получаем слово "ball" на нужном языке
        balance_text = get_text(user, 'BALANCE_INFO', points=1)
        if 'ball' in balance_text.lower():
            ball_word = 'ball'
        elif 'балл' in balance_text.lower():
            ball_word = 'балл'
        else:
            ball_word = 'ball'
        text += f"{can_afford} {gift.name} - {gift.points_cost} {ball_word}\n"
        buttons.append([types.InlineKeyboardButton(
            text=f"{gift.name} ({gift.points_cost} {ball_word})",
            callback_data=f"gift_{gift.id}"
        )])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard)
    if state:
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
        
        @sync_to_async
        def get_user_for_callback():
            return TelegramUser.objects.get(telegram_id=callback.from_user.id)
        
        user = await get_user_for_callback()
        
        if result.get('error') == 'insufficient_points':
            await callback.answer(get_text(user, 'INSUFFICIENT_POINTS'), show_alert=True)
        elif result.get('error') == 'not_found':
            await callback.answer(get_text(user, 'GIFT_NOT_FOUND'), show_alert=True)
        elif result.get('success'):
            await callback.answer(get_text(user, 'GIFT_REQUEST_SENT', gift_name=result['gift_name'], remaining_points=result['remaining_points']).split('!')[0] + "!", show_alert=True)
            await callback.message.answer(get_text(user, 'GIFT_REQUEST_SENT',
                gift_name=result['gift_name'],
                remaining_points=result['remaining_points']
            ))
            if state:
                await state.clear()
    except Exception as e:
        logger.error(f"Error processing gift selection: {e}")
        @sync_to_async
        def get_user_for_error():
            return TelegramUser.objects.get(telegram_id=callback.from_user.id)
        user = await get_user_for_error()
        await callback.answer(get_text(user, 'GIFT_REQUEST_ERROR'), show_alert=True)


async def show_leaders(message: Message):
    """Показывает ТОП лидеров."""
    @sync_to_async
    def get_leaders_and_user():
        user = TelegramUser.objects.get(telegram_id=message.from_user.id)
        leaders = list(TelegramUser.objects.order_by('-points')[:10])
        return user, leaders
    
    user, leaders = await get_leaders_and_user()
    
    if not leaders:
        await message.answer(get_text(user, 'NO_LEADERS'))
        return
    
    text = get_text(user, 'TOP_LEADERS_TITLE')
    position = 1
    
    for leader in leaders:
        emoji = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else f"{position}."
        name = leader.first_name or get_text(user, 'USER')
        text += get_text(user, 'LEADER_ENTRY', position=emoji, name=name, points=leader.points)
        position += 1
    
    await message.answer(text)


async def show_language_selection(message: Message):
    """Показывает выбор языка."""
    @sync_to_async
    def get_user():
        return TelegramUser.objects.get(telegram_id=message.from_user.id)
    
    user = await get_user()
    
    # Используем фиксированные тексты для кнопок выбора языка
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=TRANSLATIONS['uz_latin']['UZBEK_LATIN'],
            callback_data='lang_uz_latin'
        )],
        [types.InlineKeyboardButton(
            text=TRANSLATIONS['uz_latin']['UZBEK_CYRILLIC'],
            callback_data='lang_uz_cyrillic'
        )],
        [types.InlineKeyboardButton(
            text=TRANSLATIONS['uz_latin']['RUSSIAN'],
            callback_data='lang_ru'
        )],
    ])
    
    await message.answer(get_text(user, 'SELECT_LANGUAGE'), reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def change_language(callback: CallbackQuery):
    """Обрабатывает смену языка."""
    language_code = callback.data.split('_', 1)[1]  # uz_latin, uz_cyrillic, ru
    
    @sync_to_async
    def update_language():
        user = TelegramUser.objects.get(telegram_id=callback.from_user.id)
        user.language = language_code
        user.save(update_fields=['language'])
        return user
    
    user = await update_language()
    
    # Показываем уведомление о смене языка
    await callback.answer(get_text(user, 'LANGUAGE_CHANGED'), show_alert=True)
    
    # Удаляем сообщение с выбором языка
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение: {e}")
    
    # Отправляем новое сообщение с обновленной клавиатурой через бота напрямую
    # Это гарантирует обновление ReplyKeyboard с новыми текстами кнопок
    @sync_to_async
    def get_user_points():
        user_obj = TelegramUser.objects.get(telegram_id=callback.from_user.id)
        return user_obj.points
    
    points = await get_user_points()
    
    # Создаем reply keyboard кнопки
    keyboard_buttons = []
    
    # Определяем URL для Web App
    web_app_url = get_web_app_url()
    
    # Добавляем остальные кнопки (без Web App кнопки в reply keyboard)
    keyboard_buttons.extend([
        [types.KeyboardButton(text=get_text(user, 'GIFTS'))],
        [types.KeyboardButton(text=get_text(user, 'MY_BALANCE')), types.KeyboardButton(text=get_text(user, 'TOP_LEADERS'))],
        [types.KeyboardButton(text=get_text(user, 'LANGUAGE'))],
    ])
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )
    
    # Создаем inline кнопку для Web App
    inline_keyboard = None
    if web_app_url:
        try:
            web_app_button = types.InlineKeyboardButton(
                text=get_text(user, 'MY_GIFTS'),
                web_app=types.WebAppInfo(url=web_app_url)
            )
            inline_keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[[web_app_button]]
            )
        except Exception as e:
            logger.warning(f"Не удалось создать Web App inline кнопку: {e}")
    
    # Отправляем сообщение через бота напрямую, чтобы обновить клавиатуру
    await bot.send_message(
        chat_id=callback.from_user.id,
        text=get_text(user, 'MAIN_MENU', points=points),
        reply_markup=keyboard
    )
    
    # Отправляем отдельное сообщение с inline кнопкой для Web App
    if inline_keyboard:
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=get_text(user, 'OPEN_WEB_APP'),
            reply_markup=inline_keyboard
        )


async def handle_unknown_message(message: Message):
    """Обработчик неизвестных сообщений."""
    @sync_to_async
    def get_user():
        return TelegramUser.objects.get(telegram_id=message.from_user.id)
    
    user = await get_user()
    await message.answer(get_text(user, 'UNKNOWN_COMMAND'))

