#!/bin/bash
# Скрипт для бэкапа базы данных PostgreSQL
# Поддерживает как Docker контейнер, так и обычный PostgreSQL

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

# Загрузка переменных окружения из .env файла
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Настройки базы данных (можно переопределить через переменные окружения)
DB_NAME="${DB_NAME:-mona_db}"
DB_USER="${DB_USER:-mona_user}"
DB_PASSWORD="${DB_PASSWORD:-mona_password}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Настройки Docker (если используется Docker)
DOCKER_CONTAINER="${DOCKER_CONTAINER:-db}"
USE_DOCKER="${USE_DOCKER:-auto}"  # auto, yes, no

# Директория для бэкапов
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"
# Количество дней хранения бэкапов
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Создаем директорию для бэкапов если её нет
mkdir -p "$BACKUP_DIR"

# Файл лога
LOG_FILE="${LOG_FILE:-$BACKUP_DIR/backup.log}"

# Определяем, используется ли Docker
if [ "$USE_DOCKER" = "auto" ]; then
    if command -v docker &> /dev/null && docker ps --format '{{.Names}}' | grep -q "^${DOCKER_CONTAINER}$"; then
        USE_DOCKER="yes"
        log "Обнаружен Docker контейнер: $DOCKER_CONTAINER"
    else
        USE_DOCKER="no"
        log "Docker контейнер не найден, используем прямое подключение к PostgreSQL"
    fi
fi

# Имя файла бэкапа
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql.gz"

log "Начало бэкапа базы данных: $DB_NAME"

# Выполняем бэкап
if [ "$USE_DOCKER" = "yes" ]; then
    # Бэкап через Docker
    log "Выполняю бэкап через Docker контейнер: $DOCKER_CONTAINER"
    
    if docker exec "$DOCKER_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"; then
        log "Бэкап успешно создан: $BACKUP_FILE"
    else
        error "Ошибка при создании бэкапа через Docker"
        exit 1
    fi
else
    # Бэкап напрямую к PostgreSQL
    log "Выполняю бэкап напрямую к PostgreSQL: $DB_HOST:$DB_PORT"
    
    export PGPASSWORD="$DB_PASSWORD"
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"; then
        log "Бэкап успешно создан: $BACKUP_FILE"
    else
        error "Ошибка при создании бэкапа"
        exit 1
    fi
    unset PGPASSWORD
fi

# Проверяем размер файла
if [ -f "$BACKUP_FILE" ]; then
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Размер бэкапа: $FILE_SIZE"
else
    error "Файл бэкапа не найден: $BACKUP_FILE"
    exit 1
fi

# Удаляем старые бэкапы
log "Удаление бэкапов старше $RETENTION_DAYS дней..."
DELETED_COUNT=$(find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ "$DELETED_COUNT" -gt 0 ]; then
    log "Удалено старых бэкапов: $DELETED_COUNT"
else
    log "Старые бэкапы не найдены"
fi

# Показываем статистику
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql.gz" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "Всего бэкапов: $TOTAL_BACKUPS"
log "Общий размер: $TOTAL_SIZE"

log "Бэкап завершен успешно!"

