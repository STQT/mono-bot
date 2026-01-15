# Автоматический бэкап PostgreSQL

## Быстрый старт

### 1. Сделайте скрипт исполняемым:
```bash
chmod +x scripts/backup_postgres.sh
```

### 2. Создайте директорию для бэкапов:
```bash
sudo mkdir -p /var/backups/postgres
sudo chown $USER:$USER /var/backups/postgres
```

### 3. Протестируйте скрипт:
```bash
./scripts/backup_postgres.sh
```

### 4. Настройте crontab для запуска каждый день в 00:00:

Откройте crontab:
```bash
crontab -e
```

Добавьте строку (замените `/path/to/mono-bot` на реальный путь):
```cron
0 0 * * * cd /path/to/mono-bot && /path/to/mono-bot/scripts/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
```

**Пример для проекта в `/home/user/mono-bot`:**
```cron
0 0 * * * cd /home/user/mono-bot && /home/user/mono-bot/scripts/backup_postgres.sh >> /var/backups/postgres/cron.log 2>&1
```

### 5. Проверьте, что crontab записан:
```bash
crontab -l
```

## Настройки

Скрипт автоматически читает настройки из `.env` файла. Основные переменные:

- `DB_NAME` - имя базы данных (по умолчанию: `mona_db`)
- `DB_USER` - пользователь (по умолчанию: `mona_user`)
- `DB_PASSWORD` - пароль (по умолчанию: `mona_password`)
- `DB_HOST` - хост (по умолчанию: `localhost` или `db` для Docker)
- `DB_PORT` - порт (по умолчанию: `5432`)

Дополнительные переменные:

- `BACKUP_DIR` - директория для бэкапов (по умолчанию: `/var/backups/postgres`)
- `RETENTION_DAYS` - количество дней хранения бэкапов (по умолчанию: `30`)
- `USE_DOCKER` - использовать Docker (`yes`, `no`, `auto`) (по умолчанию: `auto`)
- `DOCKER_CONTAINER` - имя Docker контейнера (по умолчанию: `db`)

## Где хранятся бэкапы

По умолчанию: `/var/backups/postgres/`

Формат имени файла: `{DB_NAME}_backup_{YYYYMMDD}_HHMMSS.sql.gz`

Пример: `mona_db_backup_20240115_000000.sql.gz`

## Логи

- Лог скрипта: `/var/backups/postgres/backup.log`
- Лог crontab: `/var/backups/postgres/cron.log`

## Восстановление из бэкапа

### Если используется Docker:
```bash
gunzip < /var/backups/postgres/mona_db_backup_20240115_000000.sql.gz | docker exec -i db psql -U mona_user -d mona_db
```

### Если PostgreSQL локально:
```bash
export PGPASSWORD=mona_password
gunzip < /var/backups/postgres/mona_db_backup_20240115_000000.sql.gz | psql -h localhost -p 5432 -U mona_user -d mona_db
unset PGPASSWORD
```

## Проверка работы

1. Проверить список бэкапов:
   ```bash
   ls -lh /var/backups/postgres/*.sql.gz
   ```

2. Посмотреть последние логи:
   ```bash
   tail -f /var/backups/postgres/backup.log
   ```

3. Проверить crontab:
   ```bash
   crontab -l
   ```

## Другие расписания

- Каждый день в 2:00 ночи: `0 2 * * *`
- Каждые 12 часов: `0 */12 * * *`
- Каждую неделю в воскресенье: `0 0 * * 0`
- Каждый месяц 1-го числа: `0 0 1 * *`

Подробнее см. `CRONTAB_SETUP.md`

