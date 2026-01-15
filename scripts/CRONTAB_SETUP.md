# Настройка автоматического бэкапа PostgreSQL через Crontab

## Установка скрипта бэкапа

1. **Сделайте скрипт исполняемым:**
   ```bash
   chmod +x scripts/backup_postgres.sh
   ```

2. **Создайте директорию для бэкапов (если её нет):**
   ```bash
   sudo mkdir -p /var/backups/postgres
   sudo chown $USER:$USER /var/backups/postgres
   ```

   Или используйте другую директорию, указав её в переменной окружения:
   ```bash
   export BACKUP_DIR=/home/$USER/backups/postgres
   mkdir -p $BACKUP_DIR
   ```

## Настройка Crontab

### Вариант 1: Для пользователя (рекомендуется)

1. **Откройте crontab для редактирования:**
   ```bash
   crontab -e
   ```

2. **Добавьте следующую строку для запуска бэкапа каждый день в 00:00 (полночь):**
   ```cron
   0 0 * * * /path/to/mono-bot/scripts/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
   ```

   Замените `/path/to/mono-bot` на реальный путь к вашему проекту.

   **Пример с полным путем:**
   ```cron
   0 0 * * * cd /home/user/mono-bot && /home/user/mono-bot/scripts/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
   ```

### Вариант 2: Для root (если нужны системные права)

1. **Откройте crontab root:**
   ```bash
   sudo crontab -e
   ```

2. **Добавьте строку:**
   ```cron
   0 0 * * * cd /path/to/mono-bot && /path/to/mono-bot/scripts/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
   ```

## Настройка переменных окружения

Скрипт автоматически загружает переменные из `.env` файла. Если нужно переопределить настройки, можно:

1. **Создать отдельный файл с переменными:**
   ```bash
   export ENV_FILE=/path/to/.env.production
   export BACKUP_DIR=/var/backups/postgres
   export RETENTION_DAYS=30
   export USE_DOCKER=yes  # или no, или auto
   export DOCKER_CONTAINER=db
   ```

2. **Использовать в crontab:**
   ```cron
   0 0 * * * source /path/to/backup_env.sh && /path/to/mono-bot/scripts/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
   ```

## Примеры расписания Crontab

- **Каждый день в полночь:** `0 0 * * *`
- **Каждый день в 2:00 ночи:** `0 2 * * *`
- **Каждые 12 часов:** `0 */12 * * *`
- **Каждую неделю в воскресенье в 00:00:** `0 0 * * 0`
- **Каждый месяц 1-го числа в 00:00:** `0 0 1 * *`

## Проверка работы

1. **Проверьте, что crontab записан:**
   ```bash
   crontab -l
   ```

2. **Протестируйте скрипт вручную:**
   ```bash
   ./scripts/backup_postgres.sh
   ```

3. **Проверьте логи:**
   ```bash
   tail -f /var/backups/postgres/backup.log
   tail -f /var/backups/postgres/cron.log
   ```

## Восстановление из бэкапа

### Если используется Docker:
```bash
gunzip < /var/backups/postgres/mona_db_backup_20240101_000000.sql.gz | docker exec -i db psql -U mona_user -d mona_db
```

### Если PostgreSQL установлен локально:
```bash
export PGPASSWORD=mona_password
gunzip < /var/backups/postgres/mona_db_backup_20240101_000000.sql.gz | psql -h localhost -p 5432 -U mona_user -d mona_db
unset PGPASSWORD
```

## Настройка для Docker Compose

Если вы используете Docker Compose, убедитесь, что:

1. **Контейнер с базой данных запущен:**
   ```bash
   docker-compose ps db
   ```

2. **Имя контейнера соответствует настройкам:**
   ```bash
   docker ps --format '{{.Names}}'
   ```

3. **В .env файле указаны правильные параметры:**
   ```env
   DB_NAME=mona_db
   DB_USER=mona_user
   DB_PASSWORD=your_password
   DB_HOST=db
   DB_PORT=5432
   ```

## Мониторинг и уведомления

Для отправки уведомлений об ошибках можно добавить в скрипт отправку email или сообщения в Telegram. Пример:

```bash
# В конце скрипта backup_postgres.sh можно добавить:
if [ $? -ne 0 ]; then
    # Отправить уведомление об ошибке
    echo "Ошибка бэкапа!" | mail -s "Backup Failed" admin@example.com
fi
```

## Ротация логов

Для предотвращения переполнения диска логами, можно настроить logrotate:

Создайте файл `/etc/logrotate.d/postgres-backup`:
```
/var/backups/postgres/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

