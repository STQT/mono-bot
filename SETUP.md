# Инструкция по настройке проекта

## Шаги для запуска проекта

### 1. Создание файла окружения
Скопируйте `.env.example` в `.env` и заполните необходимые значения:
```bash
cp .env.example .env
```

Обязательно укажите:
- `SECRET_KEY` - сгенерируйте новый секретный ключ Django:
  ```bash
  python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
  Или используйте онлайн генератор Django secret key
- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота (получите у @BotFather в Telegram)

### 2. Запуск через Docker Compose
```bash
docker-compose up -d
```

### 3. Применение миграций
```bash
docker-compose exec web python manage.py migrate
```

### 4. Создание суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Сбор статических файлов (опционально)
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 6. Проверка работы бота
Бот должен запуститься автоматически в контейнере `bot`. Проверьте логи:
```bash
docker-compose logs bot
```

## Важные замечания

### Если бот не запускается:
1. Проверьте, что `TELEGRAM_BOT_TOKEN` установлен в `.env`
2. Проверьте логи: `docker-compose logs bot`
3. Убедитесь, что база данных запущена: `docker-compose ps`

### Если нужно запустить бот вручную:
```bash
docker-compose exec web python manage.py run_bot
```

### Доступ к админ-панели:
Откройте в браузере: `http://localhost:8000/admin/`

### Генерация QR-кодов:
1. Войдите в админ-панель
2. Перейдите в раздел "QR-коды" или используйте ссылку "Генерация QR-кодов" в меню
3. Выберите тип (Электрик/Продавец) и количество
4. После генерации скачайте ZIP архив

## Структура базы данных

После применения миграций будут созданы следующие таблицы:
- `core_telegramuser` - пользователи Telegram
- `core_qrcode` - QR-коды
- `core_qrcodescanattempt` - попытки сканирования
- `core_gift` - подарки
- `core_giftredemption` - запросы на получение подарков

## Troubleshooting

### Проблема: "TELEGRAM_BOT_TOKEN не установлен"
**Решение**: Добавьте токен в файл `.env`:
```
TELEGRAM_BOT_TOKEN=your_token_here
```

### Проблема: База данных не подключается
**Решение**: Проверьте, что контейнер `db` запущен:
```bash
docker-compose ps
docker-compose logs db
```

### Проблема: Миграции не применяются
**Решение**: Убедитесь, что база данных запущена и доступна, затем:
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

