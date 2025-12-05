# Production Deployment Guide

## Подготовка к production деплою

### 1. Настройка переменных окружения

Создайте файл `.env` с production настройками:

```bash
# Django Settings
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=mona_db
DB_USER=mona_user
DB_PASSWORD=strong-production-password
DB_HOST=db
DB_PORT=5432

# MongoDB
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_DB=mona_mongodb

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Webhook URL (обязательно HTTPS!)
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8443

# Media Files
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles
```

### 2. SSL сертификаты

Для работы webhook необходим HTTPS. Поместите SSL сертификаты в `nginx/ssl/`:
- `cert.pem` - сертификат
- `key.pem` - приватный ключ

Можно использовать Let's Encrypt:
```bash
mkdir -p nginx/ssl
# Получите сертификаты через certbot
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 3. Сборка и запуск

```bash
# Используйте production docker-compose
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Применение миграций

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 5. Создание суперпользователя

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 6. Установка webhook

После запуска всех сервисов установите webhook:

```bash
docker-compose -f docker-compose.prod.yml exec bot-webhook python manage.py set_webhook
```

Или вручную:
```bash
docker-compose -f docker-compose.prod.yml exec bot-webhook python manage.py set_webhook --url https://yourdomain.com/webhook/YOUR_BOT_TOKEN
```

### 7. Проверка статуса

Проверьте статус webhook:
```bash
docker-compose -f docker-compose.prod.yml exec bot-webhook python manage.py set_webhook
```

Проверьте логи:
```bash
docker-compose -f docker-compose.prod.yml logs bot-webhook
docker-compose -f docker-compose.prod.yml logs nginx
```

## Управление webhook

### Установка webhook
```bash
docker-compose -f docker-compose.prod.yml exec bot-webhook python manage.py set_webhook
```

### Удаление webhook
```bash
docker-compose -f docker-compose.prod.yml exec bot-webhook python manage.py set_webhook --delete
```

### Проверка информации о webhook
```bash
docker-compose -f docker-compose.prod.yml exec bot-webhook python manage.py set_webhook
```

## Структура production окружения

```
┌─────────────┐
│   Nginx     │ (443/80) - SSL termination, reverse proxy
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Django    │ │ Bot Webhook│ │  (Static)  │
│   (Gunicorn)│ │  (aiohttp) │ │   Files    │
└──────┬──────┘ └─────┬──────┘ └────────────┘
       │              │
       └──────┬───────┘
              │
       ┌──────▼──────┐
       │ PostgreSQL  │
       │  MongoDB    │
       │   Redis     │
       └─────────────┘
```

## Мониторинг

### Health checks

- Django: `https://yourdomain.com/admin/`
- Webhook: `https://yourdomain.com/health`
- Bot: проверка через `set_webhook` команду

### Логи

```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f bot-webhook
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
```

## Обновление

```bash
# Остановить сервисы
docker-compose -f docker-compose.prod.yml down

# Обновить код
git pull

# Пересобрать и запустить
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Применить миграции
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Перезапустить webhook
docker-compose -f docker-compose.prod.yml restart bot-webhook
```

## Безопасность

1. **SECRET_KEY**: Используйте сильный секретный ключ
2. **Пароли БД**: Используйте сложные пароли
3. **HTTPS**: Обязательно используйте HTTPS для webhook
4. **Firewall**: Ограничьте доступ к портам 8443 и 8000 только через nginx
5. **Backup**: Регулярно делайте бэкапы базы данных

## Troubleshooting

### Webhook не работает

1. Проверьте, что HTTPS настроен правильно
2. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs bot-webhook`
3. Проверьте доступность: `curl https://yourdomain.com/health`
4. Проверьте webhook info: `python manage.py set_webhook`

### SSL ошибки

1. Убедитесь, что сертификаты в `nginx/ssl/` правильные
2. Проверьте права доступа к файлам
3. Проверьте конфигурацию nginx

### Бот не отвечает

1. Проверьте логи бота
2. Проверьте подключение к базе данных
3. Проверьте, что webhook установлен правильно
4. Проверьте, что бот запущен: `docker-compose -f docker-compose.prod.yml ps`

