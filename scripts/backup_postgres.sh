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
DOCKER_CONTAINER="${DOCKER_CONTAINER:-}"
USE_DOCKER="${USE_DOCKER:-auto}"  # auto, yes, no
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-}"

# Директория для бэкапов
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"
# Количество дней хранения бэкапов
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Создаем директорию для бэкапов если её нет
mkdir -p "$BACKUP_DIR"

# Файл лога
LOG_FILE="${LOG_FILE:-$BACKUP_DIR/backup.log}"

# Функция определения Docker Compose проекта и контейнера
detect_docker_compose() {
    # Используем явно docker-compose.prod.yml
    local compose_file="docker-compose.prod.yml"
    local compose_path="$PROJECT_ROOT/$compose_file"
    
    if [ -f "$compose_path" ]; then
        DOCKER_COMPOSE_FILE="$compose_path"
        log "Найден Docker Compose файл: $compose_file"
        
        # Пытаемся найти контейнер БД через docker-compose
        if command -v docker-compose > /dev/null 2>&1; then
            # Используем docker-compose (старая версия)
            local container_name=$(cd "$PROJECT_ROOT" && docker-compose -f "$compose_file" ps -q db 2>/dev/null | head -1)
            if [ -n "$container_name" ]; then
                DOCKER_CONTAINER=$(docker ps --format '{{.Names}}' --filter "id=$container_name" 2>/dev/null | head -1)
            fi
        elif command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
            # Используем docker compose (новая версия)
            local container_name=$(cd "$PROJECT_ROOT" && docker compose -f "$compose_file" ps -q db 2>/dev/null | head -1)
            if [ -n "$container_name" ]; then
                DOCKER_CONTAINER=$(docker ps --format '{{.Names}}' --filter "id=$container_name" 2>/dev/null | head -1)
            fi
        fi
        
        if [ -n "$DOCKER_CONTAINER" ]; then
            log "Найден контейнер БД через Docker Compose: $DOCKER_CONTAINER"
            return 0
        fi
    fi
    
    return 1
}

# Функция получения настроек БД из Docker контейнера
get_db_config_from_container() {
    if [ -z "$DOCKER_CONTAINER" ]; then
        return 1
    fi
    
    # Получаем переменные окружения из контейнера
    local env_vars=$(docker inspect "$DOCKER_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null)
    
    if [ -z "$env_vars" ]; then
        return 1
    fi
    
    # Извлекаем настройки БД из переменных окружения контейнера
    local postgres_db=$(echo "$env_vars" | grep "^POSTGRES_DB=" | cut -d'=' -f2 | head -1)
    local postgres_user=$(echo "$env_vars" | grep "^POSTGRES_USER=" | cut -d'=' -f2 | head -1)
    local postgres_password=$(echo "$env_vars" | grep "^POSTGRES_PASSWORD=" | cut -d'=' -f2 | head -1)
    
    if [ -n "$postgres_db" ]; then
        DB_NAME="$postgres_db"
        log "Получено DB_NAME из контейнера: $DB_NAME"
    fi
    if [ -n "$postgres_user" ]; then
        DB_USER="$postgres_user"
        log "Получено DB_USER из контейнера: $DB_USER"
    fi
    if [ -n "$postgres_password" ]; then
        DB_PASSWORD="$postgres_password"
        log "Получено DB_PASSWORD из контейнера (скрыто)"
    fi
    
    return 0
}

# Определяем, используется ли Docker
if [ "$USE_DOCKER" = "auto" ]; then
    # Сначала пытаемся найти через Docker Compose
    if detect_docker_compose; then
        USE_DOCKER="yes"
        # Получаем настройки БД из контейнера
        get_db_config_from_container || warning "Не удалось получить настройки БД из контейнера, используем значения по умолчанию"
    elif command -v docker > /dev/null 2>&1; then
        # Пытаемся найти контейнер по имени "db"
        found_container=$(docker ps --format '{{.Names}}' | grep -E "^(.*_)?db(_.*)?$" | head -1)
        if [ -n "$found_container" ]; then
            DOCKER_CONTAINER="$found_container"
            USE_DOCKER="yes"
            log "Найден Docker контейнер БД: $DOCKER_CONTAINER"
            get_db_config_from_container || warning "Не удалось получить настройки БД из контейнера"
        else
            USE_DOCKER="no"
            log "Docker контейнер БД не найден, используем прямое подключение к PostgreSQL"
            # Если DB_HOST = "db" (имя Docker контейнера), меняем на localhost
            if [ "$DB_HOST" = "db" ]; then
                DB_HOST="localhost"
                log "Исправлен DB_HOST на localhost (имя контейнера 'db' не работает на хосте)"
            fi
        fi
    else
        USE_DOCKER="no"
        log "Docker не установлен, используем прямое подключение к PostgreSQL"
        if [ "$DB_HOST" = "db" ]; then
            DB_HOST="localhost"
            log "Исправлен DB_HOST на localhost"
        fi
    fi
elif [ "$USE_DOCKER" = "yes" ]; then
    # Принудительное использование Docker
    if [ -z "$DOCKER_CONTAINER" ]; then
        DOCKER_CONTAINER="db"
    fi
    if ! docker ps --format '{{.Names}}' | grep -q "^${DOCKER_CONTAINER}$"; then
        error "Указанный Docker контейнер не найден: $DOCKER_CONTAINER"
        exit 1
    fi
    get_db_config_from_container || warning "Не удалось получить настройки БД из контейнера"
fi

# Функция выполнения команды в Docker контейнере
docker_exec() {
    local cmd="$1"
    if [ -n "$DOCKER_COMPOSE_FILE" ]; then
        # Используем docker-compose если доступно
        local compose_file=$(basename "$DOCKER_COMPOSE_FILE")
        if command -v docker-compose > /dev/null 2>&1; then
            (cd "$PROJECT_ROOT" && docker-compose -f "$compose_file" exec -T db sh -c "$cmd")
        elif command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
            (cd "$PROJECT_ROOT" && docker compose -f "$compose_file" exec -T db sh -c "$cmd")
        else
            docker exec "$DOCKER_CONTAINER" sh -c "$cmd"
        fi
    else
        docker exec "$DOCKER_CONTAINER" sh -c "$cmd"
    fi
}

# Функция проверки подключения к базе данных
check_db_connection() {
    log "Проверка подключения к базе данных..."
    if [ "$USE_DOCKER" = "yes" ]; then
        if docker_exec "pg_isready -U \"$DB_USER\" -d \"$DB_NAME\"" > /dev/null 2>&1; then
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
        SIZE=$(docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\" -t -c \"SELECT pg_size_pretty(pg_database_size('$DB_NAME'));\"" 2>/dev/null | xargs)
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
    if [ -n "$DOCKER_COMPOSE_FILE" ]; then
        log "Выполняю бэкап через Docker Compose: $(basename "$DOCKER_COMPOSE_FILE")"
    else
        log "Выполняю бэкап через Docker контейнер: $DOCKER_CONTAINER"
    fi
    
    if docker_exec "pg_dump -U \"$DB_USER\" -d \"$DB_NAME\" --verbose" 2>&1 | gzip > "$BACKUP_FILE"; then
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


