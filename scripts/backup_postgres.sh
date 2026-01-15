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

# Определяем директорию скрипта и корень проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Загрузка переменных окружения из .env файла
ENV_FILE="${ENV_FILE:-$PROJECT_ROOT/.env}"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    log "Загружен .env файл: $ENV_FILE"
else
    warning ".env файл не найден: $ENV_FILE (используются значения по умолчанию)"
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
        # Если используется Docker, но скрипт запускается на хосте, используем localhost
        if [ "$DB_HOST" = "db" ]; then
            DB_HOST="localhost"
            log "Исправлен DB_HOST на localhost для подключения с хоста"
        fi
    else
        USE_DOCKER="no"
        log "Docker контейнер не найден, используем прямое подключение к PostgreSQL"
        # Если DB_HOST = "db" (имя Docker контейнера), меняем на localhost
        if [ "$DB_HOST" = "db" ]; then
            DB_HOST="localhost"
            log "Исправлен DB_HOST на localhost (имя контейнера 'db' не работает на хосте)"
        fi
    fi
fi

# Функция проверки подключения к базе данных
check_db_connection() {
    log "Проверка подключения к базе данных..."
    if [ "$USE_DOCKER" = "yes" ]; then
        if docker exec "$DOCKER_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
            log "Подключение к базе данных успешно"
            return 0
        else
            error "Не удалось подключиться к базе данных через Docker"
            return 1
        fi
    else
        export PGPASSWORD="$DB_PASSWORD"
        if PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
            log "Подключение к базе данных успешно"
            unset PGPASSWORD
            return 0
        else
            error "Не удалось подключиться к базе данных: $DB_HOST:$DB_PORT"
            unset PGPASSWORD
            return 1
        fi
    fi
}

# Функция получения размера базы данных
get_db_size() {
    if [ "$USE_DOCKER" = "yes" ]; then
        export PGPASSWORD="$DB_PASSWORD"
        SIZE=$(docker exec "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | xargs)
        unset PGPASSWORD
    else
        export PGPASSWORD="$DB_PASSWORD"
        SIZE=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | xargs)
        unset PGPASSWORD
    fi
    echo "$SIZE"
}

# Проверяем подключение перед бэкапом
if ! check_db_connection; then
    error "Не удалось подключиться к базе данных. Проверьте настройки подключения."
    exit 1
fi

# Получаем размер базы данных
DB_SIZE=$(get_db_size)
if [ -n "$DB_SIZE" ]; then
    log "Размер базы данных: $DB_SIZE"
else
    warning "Не удалось определить размер базы данных"
fi

# Имя файла бэкапа
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql.gz"

log "Начало бэкапа базы данных: $DB_NAME"

# Выполняем бэкап
BACKUP_START_TIME=$(date +%s)
if [ "$USE_DOCKER" = "yes" ]; then
    # Бэкап через Docker
    log "Выполняю бэкап через Docker контейнер: $DOCKER_CONTAINER"
    
    if docker exec "$DOCKER_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --verbose 2>&1 | gzip > "$BACKUP_FILE"; then
        BACKUP_EXIT_CODE=${PIPESTATUS[0]}
        if [ $BACKUP_EXIT_CODE -eq 0 ]; then
            log "Бэкап успешно создан: $BACKUP_FILE"
        else
            error "Ошибка при создании бэкапа через Docker (код выхода: $BACKUP_EXIT_CODE)"
            exit 1
        fi
    else
        error "Ошибка при создании бэкапа через Docker"
        exit 1
    fi
else
    # Бэкап напрямую к PostgreSQL
    log "Выполняю бэкап напрямую к PostgreSQL: $DB_HOST:$DB_PORT"
    
    export PGPASSWORD="$DB_PASSWORD"
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --verbose 2>&1 | gzip > "$BACKUP_FILE"; then
        BACKUP_EXIT_CODE=${PIPESTATUS[0]}
        if [ $BACKUP_EXIT_CODE -eq 0 ]; then
            log "Бэкап успешно создан: $BACKUP_FILE"
        else
            error "Ошибка при создании бэкапа (код выхода: $BACKUP_EXIT_CODE)"
            unset PGPASSWORD
            exit 1
        fi
    else
        error "Ошибка при создании бэкапа"
        unset PGPASSWORD
        exit 1
    fi
    unset PGPASSWORD
fi
BACKUP_END_TIME=$(date +%s)
BACKUP_DURATION=$((BACKUP_END_TIME - BACKUP_START_TIME))
log "Время выполнения бэкапа: ${BACKUP_DURATION} секунд"

# Проверяем размер файла
if [ -f "$BACKUP_FILE" ]; then
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Размер бэкапа: $FILE_SIZE"
    
    # Получаем размер в байтах (совместимость с разными системами)
    if command -v stat > /dev/null 2>&1; then
        # Linux
        FILE_SIZE_BYTES=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || echo "0")
        # macOS fallback
        if [ "$FILE_SIZE_BYTES" = "0" ] || [ -z "$FILE_SIZE_BYTES" ]; then
            FILE_SIZE_BYTES=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || echo "0")
        fi
    else
        # Fallback на wc -c
        FILE_SIZE_BYTES=$(wc -c < "$BACKUP_FILE" 2>/dev/null || echo "0")
    fi
    
    # Проверяем, не слишком ли маленький бэкап (меньше 10KB подозрительно)
    if [ -n "$FILE_SIZE_BYTES" ] && [ "$FILE_SIZE_BYTES" != "0" ] && [ "$FILE_SIZE_BYTES" -lt 10240 ] 2>/dev/null; then
        warning "Размер бэкапа подозрительно мал ($FILE_SIZE)!"
        warning "Возможные причины:"
        warning "  1. База данных пустая или почти пустая"
        warning "  2. Проблема с подключением к базе данных"
        warning "  3. Неправильные параметры подключения"
        warning ""
        warning "Проверьте содержимое бэкапа:"
        warning "  gunzip -c $BACKUP_FILE | head -50"
        warning ""
        warning "Проверьте подключение к базе данных:"
        if [ "$USE_DOCKER" = "yes" ]; then
            warning "  docker exec $DOCKER_CONTAINER psql -U $DB_USER -d $DB_NAME -c 'SELECT COUNT(*) FROM information_schema.tables;'"
        else
            warning "  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c 'SELECT COUNT(*) FROM information_schema.tables;'"
        fi
    fi
    
    # Проверяем, что бэкап не пустой и содержит данные
    FIRST_LINES=$(gunzip -c "$BACKUP_FILE" 2>/dev/null | head -20 | grep -v "^--" | grep -v "^$" | head -5)
    if [ -z "$FIRST_LINES" ]; then
        warning "Бэкап может быть пустым или поврежденным!"
        warning "Проверьте содержимое: gunzip -c $BACKUP_FILE | head -100"
    else
        log "Проверка содержимого бэкапа: OK (найдены SQL команды)"
    fi
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

