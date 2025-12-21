"""
Утилиты для определения областей и районов Узбекистана по координатам.
"""
import math

# Области Узбекистана с центральными координатами и радиусами покрытия
UZBEKISTAN_REGIONS = {
    'tashkent_city': {
        'name_uz': 'Toshkent shahri',
        'name_ru': 'Город Ташкент',
        'center_lat': 41.2995,
        'center_lon': 69.2401,
        'radius_km': 30  # Примерный радиус города
    },
    'tashkent_region': {
        'name_uz': 'Toshkent viloyati',
        'name_ru': 'Ташкентская область',
        'center_lat': 41.2044,
        'center_lon': 69.2167,
        'radius_km': 80
    },
    'andijan': {
        'name_uz': 'Andijon viloyati',
        'name_ru': 'Андижанская область',
        'center_lat': 40.7833,
        'center_lon': 72.3333,
        'radius_km': 50
    },
    'bukhara': {
        'name_uz': 'Buxoro viloyati',
        'name_ru': 'Бухарская область',
        'center_lat': 39.7756,
        'center_lon': 64.4286,
        'radius_km': 100
    },
    'jizzakh': {
        'name_uz': 'Jizzax viloyati',
        'name_ru': 'Джизакская область',
        'center_lat': 40.1158,
        'center_lon': 67.8422,
        'radius_km': 80
    },
    'kashkadarya': {
        'name_uz': 'Qashqadaryo viloyati',
        'name_ru': 'Кашкадарьинская область',
        'center_lat': 38.8606,
        'center_lon': 65.7892,
        'radius_km': 100
    },
    'navoi': {
        'name_uz': 'Navoiy viloyati',
        'name_ru': 'Навоийская область',
        'center_lat': 40.0844,
        'center_lon': 65.3792,
        'radius_km': 120
    },
    'namangan': {
        'name_uz': 'Namangan viloyati',
        'name_ru': 'Наманганская область',
        'center_lat': 40.9983,
        'center_lon': 71.6726,
        'radius_km': 60
    },
    'samarkand': {
        'name_uz': 'Samarqand viloyati',
        'name_ru': 'Самаркандская область',
        'center_lat': 39.6542,
        'center_lon': 66.9597,
        'radius_km': 80
    },
    'surkhandarya': {
        'name_uz': 'Surxondaryo viloyati',
        'name_ru': 'Сурхандарьинская область',
        'center_lat': 37.2242,
        'center_lon': 67.2783,
        'radius_km': 100
    },
    'syrdarya': {
        'name_uz': 'Sirdaryo viloyati',
        'name_ru': 'Сырдарьинская область',
        'center_lat': 40.7500,
        'center_lon': 68.5000,
        'radius_km': 80
    },
    'fergana': {
        'name_uz': 'Farg\'ona viloyati',
        'name_ru': 'Ферганская область',
        'center_lat': 40.3842,
        'center_lon': 71.7842,
        'radius_km': 60
    },
    'khorezm': {
        'name_uz': 'Xorazm viloyati',
        'name_ru': 'Хорезмская область',
        'center_lat': 41.5500,
        'center_lon': 60.6333,
        'radius_km': 80
    },
    'karakalpakstan': {
        'name_uz': 'Qoraqalpog\'iston Respublikasi',
        'name_ru': 'Республика Каракалпакстан',
        'center_lat': 42.4531,
        'center_lon': 59.1403,
        'radius_km': 200
    },
}

# Границы Узбекистана для проверки
UZBEKISTAN_BOUNDS = {
    'min_lat': 37.1442,
    'max_lat': 45.5906,
    'min_lon': 56.0000,
    'max_lon': 73.1397,
}


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Вычисляет расстояние между двумя точками на Земле по формуле гаверсинуса.
    Возвращает расстояние в километрах.
    """
    R = 6371  # Радиус Земли в километрах
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_region_by_coordinates(latitude, longitude):
    """
    Определяет область Узбекистана по координатам.
    
    Args:
        latitude: Широта
        longitude: Долгота
    
    Returns:
        str: Код области или None, если координаты вне Узбекистана
    """
    if latitude is None or longitude is None:
        return None
    
    # Проверяем, находятся ли координаты в пределах Узбекистана
    if not (UZBEKISTAN_BOUNDS['min_lat'] <= latitude <= UZBEKISTAN_BOUNDS['max_lat'] and
            UZBEKISTAN_BOUNDS['min_lon'] <= longitude <= UZBEKISTAN_BOUNDS['max_lon']):
        return None
    
    # Находим ближайшую область
    min_distance = float('inf')
    closest_region = None
    
    for region_code, region_data in UZBEKISTAN_REGIONS.items():
        distance = haversine_distance(
            latitude, longitude,
            region_data['center_lat'], region_data['center_lon']
        )
        
        # Если расстояние меньше радиуса области, это наша область
        if distance <= region_data['radius_km']:
            if distance < min_distance:
                min_distance = distance
                closest_region = region_code
    
    return closest_region


def get_region_name(region_code, language='ru'):
    """
    Получает название области на указанном языке.
    
    Args:
        region_code: Код области
        language: Язык ('ru' или 'uz')
    
    Returns:
        str: Название области или None
    """
    if region_code not in UZBEKISTAN_REGIONS:
        return None
    
    if language == 'uz':
        return UZBEKISTAN_REGIONS[region_code]['name_uz']
    else:
        return UZBEKISTAN_REGIONS[region_code]['name_ru']


def get_all_regions(language='ru'):
    """
    Возвращает список всех областей с их кодами и названиями.
    
    Args:
        language: Язык ('ru' или 'uz')
    
    Returns:
        list: Список кортежей (код, название)
    """
    return [
        (code, get_region_name(code, language))
        for code in UZBEKISTAN_REGIONS.keys()
    ]


# Районы Узбекистана с координатами (основные районы для каждой области)
UZBEKISTAN_DISTRICTS = {
    # Ташкент город - основные районы
    'tashkent_city': {
        'yunusobod': {'name_uz': 'Yunusobod', 'name_ru': 'Юнусабад', 'lat': 41.3500, 'lon': 69.2833, 'radius': 5},
        'mirabad': {'name_uz': 'Mirobod', 'name_ru': 'Мирабад', 'lat': 41.3000, 'lon': 69.2500, 'radius': 5},
        'olmazor': {'name_uz': 'Olmazor', 'name_ru': 'Олмазор', 'lat': 41.2800, 'lon': 69.2167, 'radius': 5},
        'sergeli': {'name_uz': 'Sirg\'ali', 'name_ru': 'Сергели', 'lat': 41.2333, 'lon': 69.2000, 'radius': 5},
        'uchtepa': {'name_uz': 'Uchtepa', 'name_ru': 'Учтепа', 'lat': 41.3167, 'lon': 69.2667, 'radius': 5},
        'yakkasaroy': {'name_uz': 'Yakkasaroy', 'name_ru': 'Яккасарай', 'lat': 41.2833, 'lon': 69.2333, 'radius': 5},
        'chilonzor': {'name_uz': 'Chilonzor', 'name_ru': 'Чилонзар', 'lat': 41.2667, 'lon': 69.1833, 'radius': 5},
        'shaykhontohur': {'name_uz': 'Shayxontohur', 'name_ru': 'Шайхантахур', 'lat': 41.3167, 'lon': 69.2500, 'radius': 5},
    },
    # Ташкентская область - основные районы
    'tashkent_region': {
        'angren': {'name_uz': 'Angren', 'name_ru': 'Ангрен', 'lat': 41.0167, 'lon': 70.1333, 'radius': 10},
        'bekabad': {'name_uz': 'Bekobod', 'name_ru': 'Бекабад', 'lat': 40.2167, 'lon': 69.2167, 'radius': 10},
        'chirchik': {'name_uz': 'Chirchiq', 'name_ru': 'Чирчик', 'lat': 41.4667, 'lon': 69.5833, 'radius': 10},
        'gulistan': {'name_uz': 'Guliston', 'name_ru': 'Гулистан', 'lat': 40.5000, 'lon': 68.7833, 'radius': 10},
        'yangiyul': {'name_uz': 'Yangiyo\'l', 'name_ru': 'Янгиюль', 'lat': 41.1167, 'lon': 69.0500, 'radius': 10},
    },
    # Андижанская область
    'andijan': {
        'andijan_city': {'name_uz': 'Andijon shahri', 'name_ru': 'Андижан', 'lat': 40.7833, 'lon': 72.3333, 'radius': 8},
        'asaka': {'name_uz': 'Asaka', 'name_ru': 'Асака', 'lat': 40.6500, 'lon': 72.2333, 'radius': 8},
        'khanabad': {'name_uz': 'Xonobod', 'name_ru': 'Ханабад', 'lat': 40.8000, 'lon': 72.9000, 'radius': 8},
        'pakhtaabad': {'name_uz': 'Paxtaobod', 'name_ru': 'Пахтаабад', 'lat': 40.9333, 'lon': 72.5000, 'radius': 8},
    },
    # Бухарская область
    'bukhara': {
        'bukhara_city': {'name_uz': 'Buxoro shahri', 'name_ru': 'Бухара', 'lat': 39.7756, 'lon': 64.4286, 'radius': 10},
        'kagan': {'name_uz': 'Kogon', 'name_ru': 'Каган', 'lat': 39.7167, 'lon': 64.5500, 'radius': 10},
        'gijduvan': {'name_uz': 'G\'ijduvon', 'name_ru': 'Гиждуван', 'lat': 40.1000, 'lon': 64.6833, 'radius': 10},
    },
    # Джизакская область
    'jizzakh': {
        'jizzakh_city': {'name_uz': 'Jizzax shahri', 'name_ru': 'Джизак', 'lat': 40.1158, 'lon': 67.8422, 'radius': 8},
        'gagarin': {'name_uz': 'Gagarin', 'name_ru': 'Гагарин', 'lat': 40.2500, 'lon': 67.9500, 'radius': 8},
    },
    # Кашкадарьинская область
    'kashkadarya': {
        'karshi': {'name_uz': 'Qarshi', 'name_ru': 'Карши', 'lat': 38.8606, 'lon': 65.7892, 'radius': 10},
        'shakhrisabz': {'name_uz': 'Shahrisabz', 'name_ru': 'Шахрисабз', 'lat': 39.0500, 'lon': 66.8333, 'radius': 10},
        'kitab': {'name_uz': 'Kitob', 'name_ru': 'Китаб', 'lat': 39.1167, 'lon': 66.8833, 'radius': 10},
    },
    # Навоийская область
    'navoi': {
        'navoi_city': {'name_uz': 'Navoiy shahri', 'name_ru': 'Навои', 'lat': 40.0844, 'lon': 65.3792, 'radius': 10},
        'zarafshan': {'name_uz': 'Zarafshon', 'name_ru': 'Зарафшан', 'lat': 41.5667, 'lon': 64.2000, 'radius': 10},
    },
    # Наманганская область
    'namangan': {
        'namangan_city': {'name_uz': 'Namangan shahri', 'name_ru': 'Наманган', 'lat': 40.9983, 'lon': 71.6726, 'radius': 8},
        'chust': {'name_uz': 'Chust', 'name_ru': 'Чуст', 'lat': 41.0167, 'lon': 71.2333, 'radius': 8},
        'pap': {'name_uz': 'Pop', 'name_ru': 'Поп', 'lat': 40.8667, 'lon': 71.1000, 'radius': 8},
    },
    # Самаркандская область
    'samarkand': {
        'samarkand_city': {'name_uz': 'Samarqand shahri', 'name_ru': 'Самарканд', 'lat': 39.6542, 'lon': 66.9597, 'radius': 10},
        'kattakurgan': {'name_uz': 'Kattaqo\'rg\'on', 'name_ru': 'Каттакурган', 'lat': 39.9000, 'lon': 66.2500, 'radius': 10},
        'urgut': {'name_uz': 'Urgut', 'name_ru': 'Ургут', 'lat': 39.4000, 'lon': 67.2500, 'radius': 10},
    },
    # Сурхандарьинская область
    'surkhandarya': {
        'termez': {'name_uz': 'Termiz', 'name_ru': 'Термез', 'lat': 37.2242, 'lon': 67.2783, 'radius': 10},
        'denau': {'name_uz': 'Denov', 'name_ru': 'Денау', 'lat': 38.2667, 'lon': 67.9000, 'radius': 10},
    },
    # Сырдарьинская область
    'syrdarya': {
        'gulistan': {'name_uz': 'Guliston', 'name_ru': 'Гулистан', 'lat': 40.5000, 'lon': 68.7833, 'radius': 8},
        'sirdaryo': {'name_uz': 'Sirdaryo', 'name_ru': 'Сырдарья', 'lat': 40.8500, 'lon': 68.6667, 'radius': 8},
    },
    # Ферганская область
    'fergana': {
        'fergana_city': {'name_uz': 'Farg\'ona shahri', 'name_ru': 'Фергана', 'lat': 40.3842, 'lon': 71.7842, 'radius': 8},
        'kokand': {'name_uz': 'Qo\'qon', 'name_ru': 'Коканд', 'lat': 40.5286, 'lon': 70.9425, 'radius': 8},
        'margilan': {'name_uz': 'Marg\'ilon', 'name_ru': 'Маргилан', 'lat': 40.4711, 'lon': 71.7247, 'radius': 8},
        'rishtan': {'name_uz': 'Rishton', 'name_ru': 'Риштан', 'lat': 40.3500, 'lon': 71.2833, 'radius': 8},
    },
    # Хорезмская область
    'khorezm': {
        'urgench': {'name_uz': 'Urganch', 'name_ru': 'Ургенч', 'lat': 41.5500, 'lon': 60.6333, 'radius': 10},
        'khiva': {'name_uz': 'Xiva', 'name_ru': 'Хива', 'lat': 41.3833, 'lon': 60.3667, 'radius': 10},
    },
    # Каракалпакстан
    'karakalpakstan': {
        'nukus': {'name_uz': 'Nukus', 'name_ru': 'Нукус', 'lat': 42.4531, 'lon': 59.1403, 'radius': 15},
        'muynak': {'name_uz': 'Mo\'ynoq', 'name_ru': 'Муйнак', 'lat': 43.7667, 'lon': 59.0167, 'radius': 15},
    },
}


def get_district_by_coordinates(latitude, longitude, region_code=None):
    """
    Определяет район Узбекистана по координатам.
    
    Args:
        latitude: Широта
        longitude: Долгота
        region_code: Код области (опционально, для ускорения поиска)
    
    Returns:
        tuple: (код района, название района) или (None, None)
    """
    if latitude is None or longitude is None:
        return None, None
    
    # Если указана область, ищем только в её районах
    if region_code and region_code in UZBEKISTAN_DISTRICTS:
        districts_to_check = UZBEKISTAN_DISTRICTS[region_code]
    else:
        # Ищем во всех районах
        districts_to_check = {}
        for region_districts in UZBEKISTAN_DISTRICTS.values():
            districts_to_check.update(region_districts)
    
    # Находим ближайший район
    min_distance = float('inf')
    closest_district_code = None
    closest_district_name = None
    
    for district_code, district_data in districts_to_check.items():
        distance = haversine_distance(
            latitude, longitude,
            district_data['lat'], district_data['lon']
        )
        
        # Если расстояние меньше радиуса района
        if distance <= district_data['radius']:
            if distance < min_distance:
                min_distance = distance
                closest_district_code = district_code
                closest_district_name = district_data['name_ru']
    
    return closest_district_code, closest_district_name


def get_district_name(district_code, region_code, language='ru'):
    """
    Получает название района на указанном языке.
    
    Args:
        district_code: Код района
        region_code: Код области
        language: Язык ('ru' или 'uz')
    
    Returns:
        str: Название района или None
    """
    if region_code not in UZBEKISTAN_DISTRICTS:
        return None
    
    if district_code not in UZBEKISTAN_DISTRICTS[region_code]:
        return None
    
    district_data = UZBEKISTAN_DISTRICTS[region_code][district_code]
    
    if language == 'uz':
        return district_data['name_uz']
    else:
        return district_data['name_ru']

