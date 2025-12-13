"""
Переводы для Telegram бота на трех языках:
- Узбекский (латиница) - uz_latin
- Узбекский (кириллица) - uz_cyrillic  
- Русский - ru
"""

TRANSLATIONS = {
    'uz_latin': {
        # Основные сообщения
        'WELCOME': "👋 Xush kelibsiz!\n\nIshni boshlash uchun ro'yxatdan o'tishingiz kerak.\nIltimos, quyidagi tugma orqali telefon raqamingizni yuboring.",
        'SEND_PHONE': "Telefon raqamini yuborish uchun tugmani bosing:",
        'PHONE_SAVED': "✅ Telefon raqami saqlandi!\n\nEndi quyidagi tugma orqali joylashuvingizni yuboring.",
        'SEND_LOCATION': "Joylashuvni yuborish uchun tugmani bosing:",
        'REGISTRATION_COMPLETE': "✅ Ro'yxatdan o'tish yakunlandi!",
        'USE_BUTTON_PHONE': "Iltimos, telefon raqamini yuborish uchun tugmani ishlating.",
        'USE_BUTTON_LOCATION': "Iltimos, joylashuvni yuborish uchun tugmani ishlating.",
        'SELECT_USER_TYPE': "Sizning turingizni tanlang:",
        'USER_TYPE_ELECTRICIAN': "⚡ Elektrik",
        'USER_TYPE_SELLER': "🛒 Sotuvchi",
        'USER_TYPE_SAVED': "✅ Tur saqlandi!",
        'PRIVACY_POLICY_TEXT': "Maxfiylik siyosati: Biz sizning shaxsiy ma'lumotlaringizni himoya qilamiz.",
        'ACCEPT_PRIVACY': "✅ Roziman",
        'DECLINE_PRIVACY': "❌ Rad etish",
        'ACCEPT_PRIVACY_QUESTION': "Maxfiylik siyosatiga rozimisiz?",
        'PRIVACY_ACCEPTED': "✅ Maxfiylik siyosatiga rozilik berildi!",
        'PRIVACY_DECLINED': "❌ Maxfiylik siyosatiga rozilik berilmadi",
        'PRIVACY_REQUIRED': "❌ Ro'yxatdan o'tish uchun maxfiylik siyosatiga rozilik berishingiz kerak.",
        'SEND_PHONE_BUTTON': "📱 Telefon raqamini yuborish",
        'REGISTRATION_COMPLETE_MESSAGE': "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi! Endi botdan foydalanishingiz mumkin.",
        
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
        'UZBEK_CYRILLIC': "🇺🇿 Ўзбек (Кирилл)",
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
        'WEBAPP_STATUS_PENDING': "Kutilmoqda",
        'WEBAPP_STATUS_APPROVED': "Tasdiqlandi",
        'WEBAPP_STATUS_REJECTED': "Rad etildi",
        'WEBAPP_STATUS_COMPLETED': "Yakunlandi",
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
        'WEBAPP_GIFTS': "Sovg'alar",
        'WEBAPP_QR_HISTORY': "QR kodlar tarixi",
        'WEBAPP_UZBEK': "O'zbekcha",
        'WEBAPP_UZBEK_CYRILLIC': "Ўзбекча",
        'WEBAPP_RUSSIAN': "Ruscha",
        'WEBAPP_UPDATED': "Yangilangan",
        'WEBAPP_CLOSE': "Yopish",
        'WEBAPP_BALL': "Ball",
        'WEBAPP_LOADING_QR_HISTORY': "QR kodlar tarixi yuklanmoqda...",
        'WEBAPP_NO_QR_HISTORY': "QR kodlar tarixi yo'q",
        'WEBAPP_QR_MAX_ATTEMPTS': "❌ Сиз бугун {max_attempts} марта нотўғри QR-код киритдингиз. Кейинги уринишлар эртага (00:00) қайта очилади.",
        'WEBAPP_QR_WRONG_TYPE': "❌ Bu QR-kod sizning turingizga mos kelmaydi. Siz faqat o'z turingizga mos QR-kodlarni kiritishingiz mumkin.",
    },
    
    'uz_cyrillic': {
        # Основные сообщения
        'WELCOME': "👋 Хуш келибсиз!\n\nИшни бошлаш учун рўйхатдан ўтишингиз керак.\nИлтимос, қуйидаги tugma орқали телефон рақамингизни юборинг.",
        'SEND_PHONE': "Телефон рақамини юбориш учун tugmani босинг:",
        'PHONE_SAVED': "✅ Телефон рақами сақланди!\n\nЭнди қуйидаги tugma орқали жойлашувингизни юборинг.",
        'SEND_LOCATION': "Жойлашувни юбориш учун tugmani босинг:",
        'REGISTRATION_COMPLETE': "✅ Рўйхатдан ўтиш якунланди!",
        'USE_BUTTON_PHONE': "Илтимос, телефон рақамини юбориш учун tugmani ишлатинг.",
        'USE_BUTTON_LOCATION': "Илтимос, жойлашувни юбориш учун tugmani ишлатинг.",
        'SELECT_USER_TYPE': "Сизнинг турингизни танланг:",
        'USER_TYPE_ELECTRICIAN': "⚡ Электрик",
        'USER_TYPE_SELLER': "🛒 Сотувчи",
        'USER_TYPE_SAVED': "✅ Тур сақланди!",
        'PRIVACY_POLICY_TEXT': "Махфийлик сиёсати: Биз сизнинг шахсий маълумотларингизни ҳимоя қиламиз.",
        'ACCEPT_PRIVACY': "✅ Розиман",
        'DECLINE_PRIVACY': "❌ Рад этиш",
        'ACCEPT_PRIVACY_QUESTION': "Махфийлик сиёсатига розимисиз?",
        'PRIVACY_ACCEPTED': "✅ Махфийлик сиёсатига розилик берилди!",
        'PRIVACY_DECLINED': "❌ Махфийлик сиёсатига розилик берилмади",
        'PRIVACY_REQUIRED': "❌ Рўйхатдан ўтиш учун махфийлик сиёсатига розилик беришингиз керак.",
        'SEND_PHONE_BUTTON': "📱 Телефон рақамини юбориш",
        'REGISTRATION_COMPLETE_MESSAGE': "✅ Рўйхатдан ўтиш муваффақиятли якунланди! Энди ботдан фойдаланишингиз мумкин.",
        
        # QR-код сообщения
        'QR_ACTIVATED': "✅ QR-код муваффақиятли фаоллаштирилди!\n\n💰 Сизга {points} балл қўшилди.\n📊 Жорий балансингиз: {total_points} балл.",
        'QR_MAX_ATTEMPTS': "❌ Сиз бугун {max_attempts} марта нотўғри QR-код киритдингиз.\n\n⏰ Кейинги уринишлар эртага (00:00) қайта очилади.\n\nИлтимос, кейинроқ уриниб кўринг ёки администратор билан боғланинг.",
        'QR_NOT_FOUND': "❌ QR-код топилмади. Код тўғрилигини текширинг.",
        'QR_ALREADY_SCANNED': "❌ Бу QR-код аллақачон бошқа фойдаланувчи томонидан ишлатилган.",
        'QR_WRONG_TYPE': "❌ Бу QR-код сизнинг турингизга мос келмайди. Сиз фақат ўз турингизга мос QR-кодларни киритишингиз мумкин.",
        'QR_ERROR': "❌ QR-кодни қайта ишлашда хатолик юз берди. Кейинроқ уриниб кўринг.",
        
        # Главное меню
        'MAIN_MENU': "👋 Асосий меню\n\n💰 Балансингиз: {points} балл\n\nҲаракатни танланг:",
        'MY_GIFTS': "📱 Менинг совғаларим",
        'OPEN_WEB_APP': "📱 Web иловани очиш учун қуйидаги tugmani босинг:",
        'GIFTS': "🎁 Совғалар",
        'MY_BALANCE': "📊 Менинг балансим",
        'TOP_LEADERS': "🏆 TOP етакчилар",
        'LANGUAGE': "🌐 Тил",
        
        # Баланс
        'BALANCE_INFO': "💰 Сизнинг балансингиз: {points} балл",
        
        # Подарки
        'NO_GIFTS': "😔 Ҳозирча совғалар мавжуд эмас.",
        'GIFTS_LIST': "🎁 Мавжуд совғалар:\n\n",
        'GIFT_INFO': "{name}\n💎 Narxi: {points_cost} балл\n📝 {description}\n\n",
        'NOT_ENOUGH_POINTS': "❌ Сизда етарли балл йўқ. Сизга {needed} балл керак, лекин сизда {have} балл бор.",
        'GIFT_REQUEST_SENT': "✅ Совға олиш сўровиниз '{gift_name}' қабул қилинди!\n\nАдминистратор сўровинизни тез орада кўриб чиқади.\n💰 Жорий балансингиз: {remaining_points} балл",
        'INSUFFICIENT_POINTS': "❌ Бу совға учун етарли балл йўқ!",
        'GIFT_NOT_FOUND': "❌ Совға топилмади!",
        'GIFT_REQUEST_ERROR': "❌ Хатолик юз берди. Кейинроқ уриниб кўринг.",
        
        # ТОП лидеры
        'TOP_LEADERS_TITLE': "🏆 TOP 10 етакчилар:\n\n",
        'LEADER_ENTRY': "{position}. {name} - {points} балл\n",
        'NO_LEADERS': "😔 Ҳозирча етакчилар йўқ.",
        'USER': "Фойдаланувчи",
        
        # Смена языка
        'SELECT_LANGUAGE': "🌐 Тилни танланг:",
        'LANGUAGE_CHANGED': "✅ Тил ўзгартирилди!",
        'UZBEK_LATIN': "🇺🇿 Ўзбек (Лотин)",
        'UZBEK_CYRILLIC': "🇺🇿 Ўзбек (Кирилл)",
        'RUSSIAN': "🇷🇺 Русский",
        
        # Ошибки
        'ERROR_OCCURRED': "❌ Хатолик юз берди. Илтимос, кейинроқ уриниб кўринг.",
        'UNKNOWN_COMMAND': "Мен бу буюруқни тушунмайапман. Меню tugmalaridan фойдаланинг.",
        
        # Web App переводы
        'WEBAPP_MY_GIFTS': "Менинг совғаларим",
        'WEBAPP_YOUR_POINTS': "Сизнинг баллингиз",
        'WEBAPP_TOTAL_POINTS': "Жами балллар",
        'WEBAPP_AVAILABLE_GIFTS': "🎁 Мавжуд совғалар",
        'WEBAPP_MY_ORDERS': "📦 Менинг буюртмаларим",
        'WEBAPP_LOADING': "Юкланмоқда...",
        'WEBAPP_LOADING_GIFTS': "Совғалар юкланмоқда...",
        'WEBAPP_LOADING_ORDERS': "Буюртмалар юкланмоқда...",
        'WEBAPP_NO_GIFTS': "Мавжуд совғалар йўқ",
        'WEBAPP_NO_ORDERS': "Сизда ҳозирча буюртмалар йўқ",
        'WEBAPP_POINTS': "балл",
        'WEBAPP_CONFIRM_RECEIPT': "Қабул қилишни тасдиқлаш",
        'WEBAPP_DID_YOU_RECEIVE': "Сиз буюртмани олдингизми?",
        'WEBAPP_COMMENT_PLACEHOLDER': "Агар олмаган бўлсангиз, сабабни ва қўнғироқ қилиш сўровинизни кўрсатинг...",
        'WEBAPP_YES_RECEIVED': "Ҳа, олдим",
        'WEBAPP_NO_NOT_RECEIVED': "Йўқ, олмадим",
        'WEBAPP_CANCEL': "Бекор қилиш",
        'WEBAPP_CONFIRM_REQUEST': "Сиз бу совғани сўрашни хоҳлайсизми?",
        'WEBAPP_REQUEST_SENT': "Совға олиш сўрови юборилди!",
        'WEBAPP_ERROR': "Хатолик: {error}",
        'WEBAPP_ERROR_LOADING_USER': "Фойдаланувчи маълумотларини юклаб бўлмади",
        'WEBAPP_ERROR_LOADING_GIFTS': "Совғаларни юклашда хатолик",
        'WEBAPP_ERROR_LOADING_ORDERS': "Буюртмаларни юклашда хатолик",
        'WEBAPP_ERROR_REQUESTING_GIFT': "Совға сўрашда хатолик",
        'WEBAPP_ERROR_CONFIRMING': "Тасдиқлашда хатолик",
        'WEBAPP_THANKS_CONFIRMATION': "Тасдиқлаш учун рахмат!",
        'WEBAPP_COMMENT_SENT': "Сизнинг изоҳингиз юборилди. Сиз билан боғланамиз.",
        'WEBAPP_COMMENT_REQUIRED': "Илтимос, буюртмани олмаган сабабингизни кўрсатинг",
        'WEBAPP_STATUS_PENDING': "Кутилмоқда",
        'WEBAPP_STATUS_APPROVED': "Тасдиқланди",
        'WEBAPP_STATUS_REJECTED': "Рад этилди",
        'WEBAPP_STATUS_COMPLETED': "Якунланди",
        'WEBAPP_DELIVERY_PENDING': "Юбориш кутилмоқда",
        'WEBAPP_DELIVERY_SENT': "Юборилди",
        'WEBAPP_DELIVERY_DELIVERED': "Етказилди",
        'WEBAPP_DELIVERY_STATUS': "Етказиб бериш ҳолати:",
        'WEBAPP_REQUESTED': "Сўралган:",
        'WEBAPP_YOUR_COMMENT': "Сизнинг изоҳингиз:",
        'WEBAPP_CONFIRM_RECEIPT_BUTTON': "Қабул қилишни тасдиқлаш",
        'WEBAPP_BACK': "Орқага",
        'WEBAPP_PARTNER_TEXT': "Mono Electric bilan hamkorlik qilib va sovg'alarga erishing",
        'WEBAPP_CONTACT_ADMIN': "Admin bilan bog'lanish",
        'WEBAPP_INFO_TEXT': "Балллар QR-кодни сканердан ўтказганингиздан сўнг дарҳол ҳисобингизга тушади.\n\n\n\nАгар балллар тушмаган бўлса, илтимос, администраторга мурожаат қилинг.",
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
        'WEBAPP_GIFTS': "Sovg'alar",
        'WEBAPP_QR_HISTORY': "QR kodlar tarixi",
        'WEBAPP_UZBEK': "O'zbekcha",
        'WEBAPP_UZBEK_CYRILLIC': "Ўзбекча",
        'WEBAPP_RUSSIAN': "Ruscha",
        'WEBAPP_UPDATED': "Yangilangan",
        'WEBAPP_CLOSE': "Yopish",
        'WEBAPP_BALL': "Ball",
        'WEBAPP_LOADING_QR_HISTORY': "QR kodlar tarixi yuklanmoqda...",
        'WEBAPP_NO_QR_HISTORY': "QR kodlar tarixi yo'q",
        'WEBAPP_QR_MAX_ATTEMPTS': "❌ Вы сегодня {max_attempts} раз ввели неверный QR-код. Следующие попытки откроются завтра (00:00).",
        'WEBAPP_QR_WRONG_TYPE': "❌ Бу QR-код сизнинг турингизга мос келмайди. Сиз фақат ўз турингизга мос QR-кодларни киритишингиз мумкин.",
    },
    
    'ru': {
        # Основные сообщения
        'WELCOME': "👋 Добро пожаловать!\n\nДля начала работы необходимо пройти регистрацию.\nПожалуйста, отправьте ваш номер телефона, используя кнопку ниже.",
        'SEND_PHONE': "Нажмите на кнопку, чтобы отправить номер телефона:",
        'PHONE_SAVED': "✅ Номер телефона сохранен!\n\nТеперь отправьте вашу локацию, используя кнопку ниже.",
        'SEND_LOCATION': "Нажмите на кнопку, чтобы отправить локацию:",
        'REGISTRATION_COMPLETE': "✅ Регистрация завершена!",
        'USE_BUTTON_PHONE': "Пожалуйста, используйте кнопку для отправки номера телефона.",
        'USE_BUTTON_LOCATION': "Пожалуйста, используйте кнопку для отправки локации.",
        'SELECT_USER_TYPE': "Выберите ваш тип:",
        'USER_TYPE_ELECTRICIAN': "⚡ Электрик",
        'USER_TYPE_SELLER': "🛒 Продавец",
        'USER_TYPE_SAVED': "✅ Тип сохранен!",
        'PRIVACY_POLICY_TEXT': "Политика конфиденциальности: Мы защищаем ваши личные данные.",
        'ACCEPT_PRIVACY': "✅ Согласен",
        'DECLINE_PRIVACY': "❌ Отклонить",
        'ACCEPT_PRIVACY_QUESTION': "Согласны ли вы с политикой конфиденциальности?",
        'PRIVACY_ACCEPTED': "✅ Согласие на политику конфиденциальности получено!",
        'PRIVACY_DECLINED': "❌ Согласие на политику конфиденциальности не получено",
        'PRIVACY_REQUIRED': "❌ Для регистрации необходимо согласие с политикой конфиденциальности.",
        'SEND_PHONE_BUTTON': "📱 Отправить номер телефона",
        'REGISTRATION_COMPLETE_MESSAGE': "✅ Регистрация успешно завершена! Теперь вы можете пользоваться ботом.",
        
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
        'UZBEK_CYRILLIC': "🇺🇿 Ўзбек (Кирилл)",
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
        'WEBAPP_STATUS_PENDING': "Ожидает",
        'WEBAPP_STATUS_APPROVED': "Одобрено",
        'WEBAPP_STATUS_REJECTED': "Отклонено",
        'WEBAPP_STATUS_COMPLETED': "Выполнено",
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
        'WEBAPP_GIFTS': "Подарки",
        'WEBAPP_QR_HISTORY': "История QR-кодов",
        'WEBAPP_UZBEK': "Узбекский",
        'WEBAPP_UZBEK_CYRILLIC': "Ўзбекча",
        'WEBAPP_RUSSIAN': "Русский",
        'WEBAPP_UPDATED': "Обновлено",
        'WEBAPP_CLOSE': "Закрыть",
        'WEBAPP_BALL': "Балл",
        'WEBAPP_LOADING_QR_HISTORY': "Загрузка истории QR-кодов...",
        'WEBAPP_NO_QR_HISTORY': "История QR-кодов отсутствует",
        'WEBAPP_QR_MAX_ATTEMPTS': "❌ Вы сегодня {max_attempts} раз ввели неверный QR-код. Следующие попытки откроются завтра (00:00).",
        'WEBAPP_QR_WRONG_TYPE': "❌ Этот QR-код не соответствует вашему типу. Вы можете вводить только QR-коды, соответствующие вашему типу.",
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
