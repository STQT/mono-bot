"""
Переводы для Telegram бота на двух языках:
- Узбекский (латиница) - uz_latin
- Русский - ru
"""

TRANSLATIONS = {
    'uz_latin': {
        'WELCOME': "👋 Xush kelibsiz!\n\nIshni boshlash uchun ro'yxatdan o'tishingiz kerak.\nIltimos, quyidagi tugma orqali telefon raqamingizni yuboring.",
        'ASK_NAME': "👤 Iltimos, ismingizni kiriting:",
        'NAME_SAVED': "✅ Ismingiz saqlandi!",
        'NAME_TOO_SHORT': "❌ Ismingiz juda qisqa. Iltimos, kamida 2 ta belgi kiriting.",
        'SEND_PHONE': "Telefon raqamini yuborish uchun tugmani bosing:",
        'PHONE_SAVED': "✅ Telefon raqamingiz saqlandi!\n\nEndi quyidagi tugma orqali joylashuvingizni yuboring.",
        'SEND_LOCATION': "Joylashuvni yuborish uchun tugmani bosing:",
        'LOCATION_SAVED': "✅ Joylashuvingiz saqlandi!",
        'REGISTRATION_COMPLETE': "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!",
        'USE_BUTTON_PHONE': "Iltimos, telefon raqamini yuborish uchun tugmani ishlating.",
        'USE_BUTTON_LOCATION': "Iltimos, joylashuvni yuborish uchun tugmani ishlating.",
        'SELECT_USER_TYPE': "Siz qaysi soha vakilisiz:\nAgar siz elektrika sohasida faoliyat yuritsangiz — «Elektrik» ni tanlang.\nAgar savdo yoki do‘konlar sohasida ishlasangiz — «Tadbirkor» ni tanlang.",
        'USER_TYPE_ELECTRICIAN': "⚡ Usta-Elektrik",
        'USER_TYPE_SELLER': "🛒 Tadbirkor",
        'USER_TYPE_SAVED': "✅ Kasbingiz saqlandi!",
        'PRIVACY_POLICY_TEXT': "📄 Iltimos, aksiya shartlari hamda shaxsiy ma’lumotlaringizni qayta ishlash qoidalari bilan tanishing va roziligingizni tasdiqlang.",
        'ACCEPT_PRIVACY': "✅ Shartlar bilan tanishdim va roziman",
        'DECLINE_PRIVACY': "❌ Rad etish",
        'ACCEPT_PRIVACY_QUESTION': "",
        'PRIVACY_ACCEPTED': "✅ Maxfiylik siyosatiga rozilik berildi!",
        'PRIVACY_DECLINED': "❌ Maxfiylik siyosatiga rozilik berilmadi",
        'PRIVACY_REQUIRED': "❌ Ro‘yxatdan o‘tish uchun maxfiylik siyosatiga rozilik berish talab etiladi.",
        'SEND_PHONE_BUTTON': "📱 Telefon raqamini yuborish",
        'REGISTRATION_COMPLETE_MESSAGE': "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi! Endi botdan foydalanishingiz mumkin.",
        'SEND_PROMO_CODE': "💡 Iltimos, o'z promo-kodingizni kiriting.",
        'PROMO_CODE_SAVED': "✅ Promo-kod saqlandi!",
        
        # QR-код сообщения
        'QR_ACTIVATED': "✅ QR-kod muvaffaqiyatli faollashtirildi!\n\n💰 Sizga {points} ball qo'shildi.\n📊 Joriy balansingiz: {total_points} ball.",
        'QR_MAX_ATTEMPTS': "❌ Siz bugun {max_attempts} marta noto'g'ri QR-kod kiritdingiz.\n\n⏰ Keyingi urinishlar ertaga (00:00) qayta ochiladi.\n\nIltimos, keyinroq urinib ko'ring yoki administrator bilan bog'laning.",
        'QR_NOT_FOUND': "❌ QR-kod topilmadi. Kod to'g'riligini tekshiring.",
        'QR_ALREADY_SCANNED': "❌ Bu QR-kod allaqachon boshqa foydalanuvchi tomonidan ishlatilgan.",
        'QR_WRONG_TYPE': "❌ Bu QR-kod sizning turingizga mos kelmaydi. Siz faqat o'z turingizga mos QR-kodlarni kiritishingiz mumkin.",
        'QR_ERROR': "❌ QR-kodni qayta ishlashda xatolik yuz berdi. Keyinroq urinib ko'ring.",
        
        # Главное меню
        'MAIN_MENU': "👋 Asosiy menyu\n\n💰 Balansingiz: {points} ball\n\nHarakatni tanlang:",
        'MY_GIFTS': "📱 Mening sovg'alarim",
        'OPEN_WEB_APP': "📱 Web ilovani ochish uchun quyidagi tugmani bosing:",
        'GIFTS': "🎁 Sovg'alar",
        'MY_BALANCE': "📊 Mening balansim",
        'TOP_LEADERS': "🏆 TOP yetakchilar",
        'LANGUAGE': "🌐 Til",
        
        # Баланс
        'BALANCE_INFO': "💰 Sizning balansingiz: {points} ball",
        
        # Подарки
        'NO_GIFTS': "😔 Hozircha sovg'alar mavjud emas.",
        'GIFTS_LIST': "🎁 Mavjud sovg'alar:\n\n",
        'GIFT_INFO': "{name}\n💎 Narxi: {points_cost} ball\n📝 {description}\n\n",
        'NOT_ENOUGH_POINTS': "❌ Sizda yetarli ball yo'q. Sizga {needed} ball kerak, lekin sizda {have} ball bor.",
        'GIFT_REQUEST_SENT': "✅ Sovg'a olish so'rovingiz '{gift_name}' qabul qilindi!\n\nAdministrator so'rovingizni tez orada ko'rib chiqadi.\n💰 Joriy balansingiz: {remaining_points} ball",
        'GIFT_STATUS_APPROVED': "✅ Tabriklaymiz! Sizning '{gift_name}' sovg'angiz tasdiqlandi!\n\nMahsulot tayyorlash bosqichida.",
        'GIFT_STATUS_SENT': "📦 Sizning '{gift_name}' sovg'angiz yetkazib berish xizmatiga topshirildi!\n\nTez orada sizga yetkaziladi.",
        'GIFT_STATUS_REJECTED': "❌ Afsuski, sizning '{gift_name}' sovg'angiz so'rovi bekor qilindi.\n\nSabab: {admin_notes}\n\nAdministrator bilan bog'laning.",
        'GIFT_STATUS_COMPLETED': "🎉 Tabriklaymiz! Sizning '{gift_name}' sovg'angiz yetkazildi!\n\nMahsulotni qabul qilganingizni tasdiqlang.",
        'INSUFFICIENT_POINTS': "❌ Bu sovg'a uchun yetarli ball yo'q!",
        'GIFT_NOT_FOUND': "❌ Sovg'a topilmadi!",
        'GIFT_REQUEST_ERROR': "❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.",
        
        # ТОП лидеры
        'TOP_LEADERS_TITLE': "🏆 TOP 10 yetakchilar:\n\n",
        'LEADER_ENTRY': "{position}. {name} - {points} ball\n",
        'NO_LEADERS': "😔 Hozircha yetakchilar yo'q.",
        'USER': "Foydalanuvchi",
        
        # Смена языка
        'SELECT_LANGUAGE': "🌐 Tilni tanlang:",
        'LANGUAGE_CHANGED': "✅ Til o'zgartirildi!",
        'UZBEK_LATIN': "🇺🇿 O'zbek (Lotin)",
        'RUSSIAN': "🇷🇺 Русский",
        
        # Ошибки
        'ERROR_OCCURRED': "❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.",
        'UNKNOWN_COMMAND': "Men bu buyruqni tushunmayapman. Menyu tugmalaridan foydalaning.",
        
        # Web App переводы
        'WEBAPP_MY_GIFTS': "Mening sovg'alarim",
        'WEBAPP_YOUR_POINTS': "Sizning ballingiz",
        'WEBAPP_TOTAL_POINTS': "Jami ballar",
        'WEBAPP_AVAILABLE_GIFTS': "🎁 Mavjud sovg'alar",
        'WEBAPP_MY_ORDERS': "📦 Mening buyurtmalarim",
        'WEBAPP_LOADING': "Yuklanmoqda...",
        'WEBAPP_LOADING_GIFTS': "Sovg'alar yuklanmoqda...",
        'WEBAPP_LOADING_ORDERS': "Buyurtmalar yuklanmoqda...",
        'WEBAPP_NO_GIFTS': "Mavjud sovg'alar yo'q",
        'WEBAPP_NO_ORDERS': "Sizda hozircha buyurtmalar yo'q",
        'WEBAPP_POINTS': "ball",
        'WEBAPP_CONFIRM_RECEIPT': "Qabul qilishni tasdiqlash",
        'WEBAPP_DID_YOU_RECEIVE': "Siz buyurtmani oldingizmi?",
        'WEBAPP_COMMENT_PLACEHOLDER': "Agar olmagan bo'lsangiz, sababni va qo'ng'iroq qilish so'rovingizni ko'rsating...",
        'WEBAPP_YES_RECEIVED': "Ha, oldim",
        'WEBAPP_NO_NOT_RECEIVED': "Yo'q, olmadim",
        'WEBAPP_CANCEL': "Bekor qilish",
        'WEBAPP_CONFIRM_REQUEST': "Siz bu sovg'ani so'rashni xohlaysizmi?",
        'WEBAPP_REQUEST_SENT': "Sovg'a olish so'rovi yuborildi!",
        'WEBAPP_ERROR': "Xatolik: {error}",
        'WEBAPP_ERROR_LOADING_USER': "Foydalanuvchi ma'lumotlarini yuklab bo'lmadi",
        'WEBAPP_ERROR_LOADING_GIFTS': "Sovg'alarni yuklashda xatolik",
        'WEBAPP_ERROR_LOADING_ORDERS': "Buyurtmalarni yuklashda xatolik",
        'WEBAPP_ERROR_REQUESTING_GIFT': "Sovg'a so'rashda xatolik",
        'WEBAPP_ERROR_CONFIRMING': "Tasdiqlashda xatolik",
        'WEBAPP_THANKS_CONFIRMATION': "Tasdiqlash uchun rahmat!",
        'WEBAPP_COMMENT_SENT': "Sizning izohingiz yuborildi. Siz bilan bog'lanamiz.",
        'WEBAPP_COMMENT_REQUIRED': "Iltimos, buyurtmani olmagan sababingizni ko'rsating",
        'WEBAPP_STATUS_PENDING': "Kutish jarayonida",
        'WEBAPP_STATUS_APPROVED': "Mahsulot tayyorlash bosqichida",
        'WEBAPP_STATUS_SENT': "Mahsulot yetkazib berish xizmatiga topshirildi",
        'WEBAPP_STATUS_REJECTED': "So'rov bekor qilindi (administrator bilan bog'laning)",
        'WEBAPP_STATUS_COMPLETED': "Mahsulotni qabul qilganingizni tasdiqlang",
        'WEBAPP_DELIVERY_PENDING': "Yuborish kutilmoqda",
        'WEBAPP_DELIVERY_SENT': "Yuborildi",
        'WEBAPP_DELIVERY_DELIVERED': "Yetkazildi",
        'WEBAPP_DELIVERY_STATUS': "Yetkazib berish holati:",
        'WEBAPP_REQUESTED': "So'ralgan:",
        'WEBAPP_YOUR_COMMENT': "Sizning izohingiz:",
        'WEBAPP_CONFIRM_RECEIPT_BUTTON': "Qabul qilishni tasdiqlash",
        'WEBAPP_BACK': "Orqaga",
        'WEBAPP_PARTNER_TEXT': "Mono Electric bilan hamkorlik qilib va sovg'alarga erishing",
        'WEBAPP_CONTACT_ADMIN': "Admin bilan bog'lanish",
        'WEBAPP_INFO_TEXT': "Ballar QR-kodni skanerdan oʻtkazganingizdan soʻng darhol hisobingizga tushadi. Agar ballar tushmagan boʻlsa, iltimos, administratorga murojaat qiling.",
        'WEBAPP_REGISTER': "Ro'yxatdan o'tkazish",
        'WEBAPP_VIEW_GIFTS': "Sovg'alarni ko'rish",
        'WEBAPP_PRIVACY_POLICY': "Maxfiylik siyosati",
        'WEBAPP_QR_ERROR': "Noto'g'ri QR kod kiritildi",
        'WEBAPP_QR_PLACEHOLDER': "QR kodni kiriting",
        'WEBAPP_GIFTS_TITLE': "Sovg'alar",
        'WEBAPP_GIFT_NAME': "Sovg'a nomi",
        'WEBAPP_GET_GIFT': "Sovg'ani olish",
        'WEBAPP_NOT_ENOUGH_POINTS': "Ballar yetarli emas",
        'WEBAPP_WAITING_PROCESS': "Kutish jarayonida",
        'WEBAPP_SUCCESS_TITLE': "Muvaffaqiyatli bajarildi!",
        'WEBAPP_SUCCESS_MESSAGE': "Sizning sovg'angiz tayyorlanmoqda, yaqin orada bizning xodimlarimiz siz bilan bog'lanishadi.",
        'WEBAPP_TO_HOME': "Bosh sahifaga",
        'WEBAPP_PROFILE': "Profil",
        'WEBAPP_INTERFACE_LANGUAGE': "Interfeys tili",
        'WEBAPP_GIFTS': "Mening sovg'alarim",
        'WEBAPP_QR_HISTORY': "QR kodlar tarixi",
        'WEBAPP_UZBEK': "O'zbekcha",
        'WEBAPP_RUSSIAN': "Ruscha",
        'WEBAPP_UPDATED': "Yangilangan",
        'WEBAPP_CLOSE': "Yopish",
        'WEBAPP_BALL': "Ball",
        'WEBAPP_LOADING_QR_HISTORY': "QR kodlar tarixi yuklanmoqda...",
        'WEBAPP_NO_QR_HISTORY': "QR kodlar tarixi yo'q",
        'WEBAPP_QR_MAX_ATTEMPTS': "❌ Сиз бугун {max_attempts} марта нотўғри QR-код киритдингиз. Кейинги уринишлар эртага (00:00) қайта очилади.",
        'WEBAPP_QR_WRONG_TYPE': "❌ Bu QR-kod sizning turingizga mos kelmaydi. Siz faqat o'z turingizga mos QR-kodlarni kiritishingiz mumkin.",
        'WEBAPP_PRIVACY_PDF_DESCRIPTION': "Maxfiylik siyosati PDF formatida mavjud. Hujjatni ochish uchun quyidagi tugmani bosing.",
        'WEBAPP_OPEN_PDF': "PDF-ni ochish",
    },
    
    'ru': {
        # Основные сообщения
        'WELCOME': "👋 Добро пожаловать!\n\nДля начала работы необходимо пройти регистрацию.\nПожалуйста, отправьте ваш номер телефона, используя кнопку ниже.",
        'ASK_NAME': "👤 Пожалуйста, введите ваше имя:",
        'NAME_SAVED': "✅ Имя сохранено!",
        'NAME_TOO_SHORT': "❌ Имя слишком короткое. Пожалуйста, введите минимум 2 символа.",
        'SEND_PHONE': "Нажмите на кнопку, чтобы отправить номер телефона:",
        'PHONE_SAVED': "✅ Номер телефона сохранен!\n\nТеперь отправьте вашу локацию, используя кнопку ниже.",
        'SEND_LOCATION': "Нажмите на кнопку, чтобы отправить локацию:",
        'LOCATION_SAVED': "✅ Локация сохранена!",
        'REGISTRATION_COMPLETE': "✅ Регистрация завершена!",
        'USE_BUTTON_PHONE': "Пожалуйста, используйте кнопку для отправки номера телефона.",
        'USE_BUTTON_LOCATION': "Пожалуйста, используйте кнопку для отправки геолокации.",
        'SELECT_USER_TYPE': "К какой категории профессии вы относитесь?\nЕсли вы работаете в сфере электрики — выберите «Электрик»\nЕсли вы относитесь к сфере торговли или магазинов — выберите «Предприниматель»..",
        'USER_TYPE_ELECTRICIAN': "1️⃣ Электрик",
        'USER_TYPE_SELLER': "2️⃣ Предприниматель",
        'USER_TYPE_SAVED': "✅ Тип сохранен!",
        'PRIVACY_POLICY_TEXT': "📄 Пожалуйста, ознакомьтесь с условиями участия в программе и правилами обработки ваших персональных данных, затем подтвердите свое согласие.",
        'ACCEPT_PRIVACY': "✅  Ознакомился с условиями и даю своё согласие",
        'DECLINE_PRIVACY': "❌ Отклонить",
        'ACCEPT_PRIVACY_QUESTION': "",
        'PRIVACY_ACCEPTED': "✅ Согласие на политику конфиденциальности получено!",
        'PRIVACY_DECLINED': "❌ Согласие на политику конфиденциальности не получено",
        'PRIVACY_REQUIRED': "❌ Для регистрации необходимо согласие с политикой конфиденциальности.",
        'SEND_PHONE_BUTTON': "📱 Отправить номер телефона",
        'REGISTRATION_COMPLETE_MESSAGE': "✅ Регистрация успешно завершена! Теперь вы можете пользоваться ботом.",
        'SEND_PROMO_CODE': "💡 Пожалуйста, введите ваш промокод.",
        'PROMO_CODE_SAVED': "✅ Промокод сохранен!",
        
        # QR-код сообщения
        'QR_ACTIVATED': "✅ QR-код успешно активирован!\n\n💰 Вам начислено {points} баллов.\n📊 Ваш текущий баланс: {total_points} баллов.",
        'QR_MAX_ATTEMPTS': "❌ Вы сегодня {max_attempts} раз ввели неверный QR-код.\n\n⏰ Следующие попытки откроются завтра (00:00).\n\nПожалуйста, попробуйте позже или свяжитесь с администратором.",
        'QR_NOT_FOUND': "❌ QR-код не найден. Проверьте правильность кода.",
        'QR_ALREADY_SCANNED': "❌ Этот QR-код уже был использован другим пользователем.",
        'QR_WRONG_TYPE': "❌ Этот QR-код не соответствует вашему типу. Вы можете вводить только QR-коды, соответствующие вашему типу.",
        'QR_ERROR': "❌ Произошла ошибка при обработке QR-кода. Попробуйте позже.",
        
        # Главное меню
        'MAIN_MENU': "👋 Главное меню\n\n💰 Ваш баланс: {points} баллов\n\nВыберите действие:",
        'MY_GIFTS': "📱 Мои подарки",
        'OPEN_WEB_APP': "📱 Нажмите кнопку ниже, чтобы открыть веб-приложение:",
        'GIFTS': "🎁 Подарки",
        'MY_BALANCE': "📊 Мой баланс",
        'TOP_LEADERS': "🏆 ТОП лидеры",
        'LANGUAGE': "🌐 Язык",
        
        # Баланс
        'BALANCE_INFO': "💰 Ваш текущий баланс: {points} баллов",
        
        # Подарки
        'NO_GIFTS': "😔 К сожалению, сейчас нет доступных подарков.",
        'GIFTS_LIST': "🎁 Доступные подарки:\n\n",
        'GIFT_INFO': "{name}\n💎 Стоимость: {points_cost} баллов\n📝 {description}\n\n",
        'NOT_ENOUGH_POINTS': "❌ Недостаточно баллов. Вам нужно {needed} баллов, но у вас {have} баллов.",
        'GIFT_REQUEST_SENT': "✅ Ваш запрос на получение подарка '{gift_name}' принят!\n\nАдминистратор обработает ваш запрос в ближайшее время.\n💰 Ваш текущий баланс: {remaining_points} баллов",
        'GIFT_STATUS_APPROVED': "✅ Поздравляем! Ваш запрос на подарок '{gift_name}' одобрен!\n\nПродукт находится в стадии подготовки.",
        'GIFT_STATUS_SENT': "📦 Ваш подарок '{gift_name}' передан в службу доставки!\n\nСкоро он будет доставлен вам.",
        'GIFT_STATUS_REJECTED': "❌ К сожалению, ваш запрос на подарок '{gift_name}' отменен.\n\n{admin_notes}\n\nСвяжитесь с администратором.",
        'GIFT_STATUS_COMPLETED': "🎉 Поздравляем! Ваш подарок '{gift_name}' доставлен!\n\nПодтверждение получения продукта.",
        'INSUFFICIENT_POINTS': "❌ Недостаточно баллов для этого подарка!",
        'GIFT_NOT_FOUND': "❌ Подарок не найден!",
        'GIFT_REQUEST_ERROR': "❌ Произошла ошибка. Попробуйте позже.",
        
        # ТОП лидеры
        'TOP_LEADERS_TITLE': "🏆 ТОП-10 лидеров:\n\n",
        'LEADER_ENTRY': "{position}. {name} - {points} баллов\n",
        'NO_LEADERS': "😔 Пока нет лидеров.",
        'USER': "Пользователь",
        
        # Смена языка
        'SELECT_LANGUAGE': "🌐 Выберите язык:",
        'LANGUAGE_CHANGED': "✅ Язык изменен!",
        'UZBEK_LATIN': "🇺🇿 O'zbek (Lotin)",
        'RUSSIAN': "🇷🇺 Русский",
        
        # Ошибки
        'ERROR_OCCURRED': "❌ Произошла ошибка. Попробуйте позже.",
        'UNKNOWN_COMMAND': "Я не понимаю эту команду. Используйте кнопки меню.",
        
        # Web App переводы
        'WEBAPP_MY_GIFTS': "Мои подарки",
        'WEBAPP_YOUR_POINTS': "Ваши баллы",
        'WEBAPP_TOTAL_POINTS': "Всего баллов",
        'WEBAPP_AVAILABLE_GIFTS': "🎁 Доступные подарки",
        'WEBAPP_MY_ORDERS': "📦 Мои заказы",
        'WEBAPP_LOADING': "Загрузка...",
        'WEBAPP_LOADING_GIFTS': "Загрузка подарков...",
        'WEBAPP_LOADING_ORDERS': "Загрузка заказов...",
        'WEBAPP_NO_GIFTS': "Нет доступных подарков",
        'WEBAPP_NO_ORDERS': "У вас пока нет заказов",
        'WEBAPP_POINTS': "баллов",
        'WEBAPP_CONFIRM_RECEIPT': "Подтверждение получения",
        'WEBAPP_DID_YOU_RECEIVE': "Вы получили заказ?",
        'WEBAPP_COMMENT_PLACEHOLDER': "Если не получили, укажите причину и просьбу позвонить...",
        'WEBAPP_YES_RECEIVED': "Да, получил",
        'WEBAPP_NO_NOT_RECEIVED': "Нет, не получил",
        'WEBAPP_CANCEL': "Отмена",
        'WEBAPP_CONFIRM_REQUEST': "Вы уверены, что хотите запросить этот подарок?",
        'WEBAPP_REQUEST_SENT': "Запрос на получение подарка отправлен!",
        'WEBAPP_ERROR': "Ошибка: {error}",
        'WEBAPP_ERROR_LOADING_USER': "Не удалось получить данные пользователя",
        'WEBAPP_ERROR_LOADING_GIFTS': "Ошибка загрузки подарков",
        'WEBAPP_ERROR_LOADING_ORDERS': "Ошибка загрузки заказов",
        'WEBAPP_ERROR_REQUESTING_GIFT': "Ошибка при запросе подарка",
        'WEBAPP_ERROR_CONFIRMING': "Ошибка при подтверждении",
        'WEBAPP_THANKS_CONFIRMATION': "Спасибо за подтверждение!",
        'WEBAPP_COMMENT_SENT': "Ваш комментарий отправлен. С вами свяжутся.",
        'WEBAPP_COMMENT_REQUIRED': "Пожалуйста, укажите причину, почему вы не получили заказ",
        'WEBAPP_STATUS_PENDING': "Запрос принят к обработке",
        'WEBAPP_STATUS_APPROVED': "Продукт находится в стадии подготовки",
        'WEBAPP_STATUS_SENT': "Продукт передан в службу доставки",
        'WEBAPP_STATUS_REJECTED': "Запрос отменен (свяжитесь с администратором)",
        'WEBAPP_STATUS_COMPLETED': "Подтверждение получения продукта",
        'WEBAPP_DELIVERY_PENDING': "Ожидает отправки",
        'WEBAPP_DELIVERY_SENT': "Отправлено",
        'WEBAPP_DELIVERY_DELIVERED': "Доставлено",
        'WEBAPP_DELIVERY_STATUS': "Статус доставки:",
        'WEBAPP_REQUESTED': "Запрошено:",
        'WEBAPP_YOUR_COMMENT': "Ваш комментарий:",
        'WEBAPP_CONFIRM_RECEIPT_BUTTON': "Подтвердить получение",
        'WEBAPP_BACK': "Назад",
        'WEBAPP_PARTNER_TEXT': "Сотрудничайте с Mono Electric и получайте подарки",
        'WEBAPP_CONTACT_ADMIN': "Связаться с администратором",
        'WEBAPP_INFO_TEXT': "Баллы зачисляются на ваш счет сразу после сканирования QR-кода.\n\n\n\nЕсли баллы не зачислились, пожалуйста, обратитесь к администратору.",
        'WEBAPP_REGISTER': "Зарегистрировать",
        'WEBAPP_VIEW_GIFTS': "Посмотреть подарки",
        'WEBAPP_PRIVACY_POLICY': "Политика конфиденциальности",
        'WEBAPP_QR_ERROR': "Введен неверный QR код",
        'WEBAPP_QR_PLACEHOLDER': "Введите QR код",
        'WEBAPP_GIFTS_TITLE': "Подарки",
        'WEBAPP_GIFT_NAME': "Название подарка",
        'WEBAPP_GET_GIFT': "Получить подарок",
        'WEBAPP_NOT_ENOUGH_POINTS': "Недостаточно баллов",
        'WEBAPP_WAITING_PROCESS': "В процессе ожидания",
        'WEBAPP_SUCCESS_TITLE': "Успешно выполнено!",
        'WEBAPP_SUCCESS_MESSAGE': "Ваш подарок готовится, наши сотрудники свяжутся с вами в ближайшее время.",
        'WEBAPP_TO_HOME': "На главную",
        'WEBAPP_PROFILE': "Профиль",
        'WEBAPP_INTERFACE_LANGUAGE': "Язык интерфейса",
        'WEBAPP_GIFTS': "Мои подарки",
        'WEBAPP_QR_HISTORY': "История QR-кодов",
        'WEBAPP_UZBEK': "Узбекский",
        'WEBAPP_RUSSIAN': "Русский",
        'WEBAPP_UPDATED': "Обновлено",
        'WEBAPP_CLOSE': "Закрыть",
        'WEBAPP_BALL': "Балл",
        'WEBAPP_LOADING_QR_HISTORY': "Загрузка истории QR-кодов...",
        'WEBAPP_NO_QR_HISTORY': "История QR-кодов отсутствует",
        'WEBAPP_QR_MAX_ATTEMPTS': "❌ Вы сегодня {max_attempts} раз ввели неверный QR-код. Следующие попытки откроются завтра (00:00).",
        'WEBAPP_QR_WRONG_TYPE': "❌ Этот QR-код не соответствует вашему типу. Вы можете вводить только QR-коды, соответствующие вашему типу.",
        'WEBAPP_PRIVACY_PDF_DESCRIPTION': "Политика конфиденциальности доступна в формате PDF. Нажмите кнопку ниже, чтобы открыть документ в браузере.",
        'WEBAPP_OPEN_PDF': "Открыть PDF",
    },
}


def get_text(user, key, **kwargs):
    """
    Получает переведенный текст для пользователя.
    
    Args:
        user: Экземпляр TelegramUser
        key: Ключ перевода
        **kwargs: Параметры для форматирования строки
    
    Returns:
        str: Переведенный текст
    """
    language = getattr(user, 'language', 'uz_latin')
    translations = TRANSLATIONS.get(language, TRANSLATIONS['uz_latin'])
    text = translations.get(key, key)
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    
    return text


# Обратная совместимость - экспорт для старого кода
def _get_default_translations():
    """Возвращает переводы по умолчанию (uz_latin) для обратной совместимости."""
    return TRANSLATIONS['uz_latin']


# Экспорт констант для обратной совместимости
WELCOME = _get_default_translations()['WELCOME']
SEND_PHONE = _get_default_translations()['SEND_PHONE']
PHONE_SAVED = _get_default_translations()['PHONE_SAVED']
SEND_LOCATION = _get_default_translations()['SEND_LOCATION']
REGISTRATION_COMPLETE = _get_default_translations()['REGISTRATION_COMPLETE']
USE_BUTTON_PHONE = _get_default_translations()['USE_BUTTON_PHONE']
USE_BUTTON_LOCATION = _get_default_translations()['USE_BUTTON_LOCATION']
QR_ACTIVATED = _get_default_translations()['QR_ACTIVATED']
QR_MAX_ATTEMPTS = _get_default_translations()['QR_MAX_ATTEMPTS']
QR_NOT_FOUND = _get_default_translations()['QR_NOT_FOUND']
QR_ALREADY_SCANNED = _get_default_translations()['QR_ALREADY_SCANNED']
QR_ERROR = _get_default_translations()['QR_ERROR']
MAIN_MENU = _get_default_translations()['MAIN_MENU']
MY_GIFTS = _get_default_translations()['MY_GIFTS']
GIFTS = _get_default_translations()['GIFTS']
MY_BALANCE = _get_default_translations()['MY_BALANCE']
TOP_LEADERS = _get_default_translations()['TOP_LEADERS']
BALANCE_INFO = _get_default_translations()['BALANCE_INFO']
NO_GIFTS = _get_default_translations()['NO_GIFTS']
GIFTS_LIST = _get_default_translations()['GIFTS_LIST']
NO_LEADERS = _get_default_translations()['NO_LEADERS']
ERROR_OCCURRED = _get_default_translations()['ERROR_OCCURRED']
