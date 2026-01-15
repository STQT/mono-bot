# Автоматический бэкап PostgreSQL

## Быстрый старт

### 1. Сделайте скрипты исполняемыми:
```bash
chmod +x scripts/backup_postgres.sh
chmod +x scripts/check_db.sh
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

4. **Проверить состояние базы данных** (если размер бэкапов подозрительно мал):
   ```bash
   chmod +x scripts/check_db.sh
   ./scripts/check_db.sh
   ```

## Диагностика проблем

### Проблема: Размер бэкапа слишком маленький (< 10KB)

Если размер бэкапа подозрительно мал, это может означать:

1. **База данных пустая или почти пустая** - проверьте:
   ```bash
   ./scripts/check_db.sh
   ```

2. **Проблема с подключением** - скрипт автоматически исправляет `DB_HOST=db` на `localhost` при работе на хосте

3. **Неправильные параметры подключения** - проверьте `.env` файл:
   ```bash
   cat .env | grep DB_
   ```

4. **Проверьте содержимое бэкапа**:
   ```bash
   gunzip -c /var/backups/postgres/mona_db_backup_*.sql.gz | head -50
   ```

5. **Проверьте подключение к базе данных вручную**:
   
   Если используется Docker:
   ```bash
   docker exec db psql -U mona_user -d mona_db -c "SELECT COUNT(*) FROM information_schema.tables;"
   ```
   
   Если PostgreSQL локально:
   ```bash
   psql -h localhost -p 5432 -U mona_user -d mona_db -c "SELECT COUNT(*) FROM information_schema.tables;"
   ```

## Другие расписания

- Каждый день в 2:00 ночи: `0 2 * * *`
- Каждые 12 часов: `0 */12 * * *`
- Каждую неделю в воскресенье: `0 0 * * 0`
- Каждый месяц 1-го числа: `0 0 1 * *`

Подробнее см. `CRONTAB_SETUP.md`

