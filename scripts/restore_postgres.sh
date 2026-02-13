#!/bin/bash
# Скрипт для восстановления базы данных PostgreSQL из бэкапа
# Поддерживает как Docker контейнер, так и обычный PostgreSQL

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Определяем директорию скрипта и корень проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Директория для бэкапов (определяем до загрузки .env, чтобы можно было переопределить)
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"

# Файл лога (определяем до использования функций логирования)
LOG_FILE="${LOG_FILE:-$BACKUP_DIR/restore.log}"

# Функция для логирования
log() {
    if [ -n "$LOG_FILE" ]; then
        echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
    else
        echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    fi
}

error() {
    if [ -n "$LOG_FILE" ]; then
        echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    fi
}

warning() {
    if [ -n "$LOG_FILE" ]; then
        echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
    else
        echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
    fi
}

# Показываем справку
show_help() {
    echo "Использование: $0 [OPTIONS] <BACKUP_FILE>"
    echo ""
    echo "Восстанавливает базу данных PostgreSQL из бэкапа."
    echo ""
    echo "Аргументы:"
    echo "  BACKUP_FILE          Путь к файлу бэкапа (.sql.gz или .sql)"
    echo ""
    echo "Опции:"
    echo "  -h, --help           Показать эту справку"
    echo "  -y, --yes            Пропустить подтверждение"
    echo "  --drop-db            Удалить базу данных перед восстановлением"
    echo "  --create-db          Создать базу данных если её нет"
    echo ""
    echo "Переменные окружения:"
    echo "  BACKUP_DIR           Директория с бэкапами (по умолчанию: /var/backups/postgres)"
    echo "  USE_DOCKER           Использовать Docker (yes, no, auto) (по умолчанию: auto)"
    echo "  DOCKER_CONTAINER     Имя Docker контейнера (по умолчанию: db)"
    echo ""
    echo "Примеры:"
    echo "  $0 /var/backups/postgres/mona_db_backup_20240115_000000.sql.gz"
    echo "  $0 mona_db_backup_20240115_000000.sql.gz"
    echo "  $0 --drop-db --yes mona_db_backup_20240115_000000.sql.gz"
    exit 0
}

# Парсинг аргументов
SKIP_CONFIRM=false
DROP_DB=false
CREATE_DB=false
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -y|--yes)
            SKIP_CONFIRM=true
            shift
            ;;
        --drop-db)
            DROP_DB=true
            shift
            ;;
        --create-db)
            CREATE_DB=true
            shift
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$1"
            else
                error "Неизвестный аргумент: $1"
                echo "Используйте $0 --help для справки"
                exit 1
            fi
            shift
            ;;
    esac
done

# Проверяем, что указан файл бэкапа
if [ -z "$BACKUP_FILE" ]; then
    error "Не указан файл бэкапа!"
    echo "Используйте $0 --help для справки"
    exit 1
fi

# Если файл указан без пути, ищем в BACKUP_DIR
if [ ! -f "$BACKUP_FILE" ] && [ -d "$BACKUP_DIR" ]; then
    if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
        log "Найден файл бэкапа: $BACKUP_FILE"
    fi
fi

# Проверяем существование файла
if [ ! -f "$BACKUP_FILE" ]; then
    error "Файл бэкапа не найден: $BACKUP_FILE"
    exit 1
fi

# Загрузка переменных окружения из .env файла
ENV_FILE="${ENV_FILE:-$PROJECT_ROOT/.env}"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    # Обновляем BACKUP_DIR если он был переопределен в .env
    BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgres}"
    LOG_FILE="${LOG_FILE:-$BACKUP_DIR/restore.log}"
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
        if docker_exec "pg_isready -U \"$DB_USER\"" > /dev/null 2>&1; then
            log "Подключение к серверу PostgreSQL успешно"
            return 0
        else
            error "Не удалось подключиться к серверу PostgreSQL через Docker"
            return 1
        fi
    else
        export PGPASSWORD="$DB_PASSWORD"
        if PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
            log "Подключение к серверу PostgreSQL успешно"
            unset PGPASSWORD
            return 0
        else
            error "Не удалось подключиться к серверу PostgreSQL: $DB_HOST:$DB_PORT"
            unset PGPASSWORD
            return 1
        fi
    fi
}

# Функция проверки существования базы данных
check_db_exists() {
    if [ "$USE_DOCKER" = "yes" ]; then
        EXISTS=$(docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -lqt" 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME" && echo "yes" || echo "no")
    else
        export PGPASSWORD="$DB_PASSWORD"
        EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "$DB_NAME" && echo "yes" || echo "no")
        unset PGPASSWORD
    fi
    [ "$EXISTS" = "yes" ]
}

# Функция создания базы данных
create_database() {
    log "Создание базы данных: $DB_NAME"
    if [ "$USE_DOCKER" = "yes" ]; then
        if docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -c \"CREATE DATABASE $DB_NAME;\"" 2>/dev/null; then
            log "База данных создана успешно"
            return 0
        else
            error "Не удалось создать базу данных"
            return 1
        fi
    else
        export PGPASSWORD="$DB_PASSWORD"
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null; then
            log "База данных создана успешно"
            unset PGPASSWORD
            return 0
        else
            error "Не удалось создать базу данных"
            unset PGPASSWORD
            return 1
        fi
    fi
}

# Функция удаления базы данных
drop_database() {
    log "Удаление базы данных: $DB_NAME"
    if [ "$USE_DOCKER" = "yes" ]; then
        # Отключаем все соединения перед удалением
        docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();\"" 2>/dev/null || true
        if docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -c \"DROP DATABASE IF EXISTS $DB_NAME;\"" 2>/dev/null; then
            log "База данных удалена успешно"
            return 0
        else
            error "Не удалось удалить базу данных"
            return 1
        fi
    else
        export PGPASSWORD="$DB_PASSWORD"
        # Отключаем все соединения перед удалением
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" 2>/dev/null || true
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null; then
            log "База данных удалена успешно"
            unset PGPASSWORD
            return 0
        else
            error "Не удалось удалить базу данных"
            unset PGPASSWORD
            return 1
        fi
    fi
}

# Проверяем подключение к серверу PostgreSQL
if ! check_db_connection; then
    error "Не удалось подключиться к серверу PostgreSQL. Проверьте настройки подключения."
    exit 1
fi

# Проверяем существование базы данных
if check_db_exists; then
    log "База данных существует: $DB_NAME"
    if [ "$DROP_DB" = "true" ]; then
        if ! drop_database; then
            error "Не удалось удалить базу данных"
            exit 1
        fi
        if ! create_database; then
            error "Не удалось создать базу данных"
            exit 1
        fi
    fi
else
    log "База данных не существует: $DB_NAME"
    if [ "$CREATE_DB" = "true" ]; then
        if ! create_database; then
            error "Не удалось создать базу данных"
            exit 1
        fi
    else
        error "База данных не существует. Используйте --create-db для создания."
        exit 1
    fi
fi

# Показываем информацию о восстановлении
FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "Файл бэкапа: $BACKUP_FILE"
log "Размер файла: $FILE_SIZE"
log "База данных: $DB_NAME"
log "Пользователь: $DB_USER"

# Подтверждение перед восстановлением
if [ "$SKIP_CONFIRM" = "false" ]; then
    warning "ВНИМАНИЕ: Это действие перезапишет данные в базе данных $DB_NAME!"
    echo -n "Продолжить? (yes/no): "
    read -r CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        log "Восстановление отменено пользователем"
        exit 0
    fi
fi

# Определяем, сжат ли файл
if [[ "$BACKUP_FILE" == *.gz ]]; then
    IS_COMPRESSED=true
    log "Файл бэкапа сжат (gzip)"
else
    IS_COMPRESSED=false
    log "Файл бэкапа не сжат"
fi

# Функция проверки наличия gunzip
check_gunzip() {
    if command -v gunzip > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Выполняем восстановление
log "Начало восстановления базы данных: $DB_NAME"
RESTORE_START_TIME=$(date +%s)

if [ "$USE_DOCKER" = "yes" ]; then
    # Восстановление через Docker
    if [ -n "$DOCKER_COMPOSE_FILE" ]; then
        log "Выполняю восстановление через Docker Compose: $(basename "$DOCKER_COMPOSE_FILE")"
    else
        log "Выполняю восстановление через Docker контейнер: $DOCKER_CONTAINER"
    fi
    
    if [ "$IS_COMPRESSED" = "true" ]; then
        # Для сжатых файлов в Docker: копируем файл в контейнер и распаковываем там
        # где gunzip точно доступен (в postgres:15-alpine)
        log "Копирую файл бэкапа в контейнер для распаковки..."
        
        # Получаем ID контейнера
        if [ -n "$DOCKER_COMPOSE_FILE" ]; then
            local compose_file=$(basename "$DOCKER_COMPOSE_FILE")
            CONTAINER_ID=$(cd "$PROJECT_ROOT" && docker-compose -f "$compose_file" ps -q db 2>/dev/null | head -1)
            if [ -z "$CONTAINER_ID" ] && command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
                CONTAINER_ID=$(cd "$PROJECT_ROOT" && docker compose -f "$compose_file" ps -q db 2>/dev/null | head -1)
            fi
        else
            CONTAINER_ID=$(docker ps --format '{{.ID}}' --filter "name=$DOCKER_CONTAINER" | head -1)
        fi
        
        if [ -z "$CONTAINER_ID" ]; then
            error "Не удалось найти ID контейнера БД"
            exit 1
        fi
        
        # Копируем файл в контейнер
        TEMP_BACKUP_PATH="/tmp/restore_backup.sql.gz"
        log "Копирую $BACKUP_FILE в контейнер..."
        if docker cp "$BACKUP_FILE" "$CONTAINER_ID:$TEMP_BACKUP_PATH"; then
            log "Файл скопирован в контейнер"
            
            # Распаковываем и восстанавливаем внутри контейнера
            if docker_exec "gunzip -c $TEMP_BACKUP_PATH | PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\""; then
                log "Восстановление успешно завершено"
                # Удаляем временный файл из контейнера
                docker_exec "rm -f $TEMP_BACKUP_PATH" 2>/dev/null || true
            else
                error "Ошибка при восстановлении базы данных через Docker"
                # Удаляем временный файл из контейнера
                docker_exec "rm -f $TEMP_BACKUP_PATH" 2>/dev/null || true
                exit 1
            fi
        else
            error "Не удалось скопировать файл в контейнер"
            exit 1
        fi
    else
        # Для несжатых файлов используем прямой ввод
        if docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\"" < "$BACKUP_FILE"; then
            log "Восстановление успешно завершено"
        else
            error "Ошибка при восстановлении базы данных через Docker"
            exit 1
        fi
    fi
else
    # Восстановление напрямую к PostgreSQL
    log "Выполняю восстановление напрямую к PostgreSQL: $DB_HOST:$DB_PORT"
    
    export PGPASSWORD="$DB_PASSWORD"
    if [ "$IS_COMPRESSED" = "true" ]; then
        # Проверяем наличие gunzip на хосте
        if check_gunzip; then
            log "Используется gunzip на хосте"
            if gunzip -c "$BACKUP_FILE" | PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
                log "Восстановление успешно завершено"
            else
                error "Ошибка при восстановлении базы данных"
                unset PGPASSWORD
                exit 1
            fi
        else
            # Пытаемся использовать Python для распаковки (обычно доступен)
            if command -v python > /dev/null 2>&1 || command -v python3 > /dev/null 2>&1; then
                log "gunzip не найден, используем Python для распаковки"
                PYTHON_CMD=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)
                if $PYTHON_CMD -c "import gzip; import sys; sys.stdout.buffer.write(gzip.open('$BACKUP_FILE', 'rb').read())" | PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; then
                    log "Восстановление успешно завершено"
                else
                    error "Ошибка при восстановлении базы данных"
                    unset PGPASSWORD
                    exit 1
                fi
            else
                error "gunzip не найден и Python недоступен. Установите gunzip или используйте Docker."
                error "Для Windows: используйте Docker или установите Git Bash / WSL"
                unset PGPASSWORD
                exit 1
            fi
        fi
    else
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"; then
            log "Восстановление успешно завершено"
        else
            error "Ошибка при восстановлении базы данных"
            unset PGPASSWORD
            exit 1
        fi
    fi
    unset PGPASSWORD
fi

RESTORE_END_TIME=$(date +%s)
RESTORE_DURATION=$((RESTORE_END_TIME - RESTORE_START_TIME))
log "Время выполнения восстановления: ${RESTORE_DURATION} секунд"

# Проверяем восстановленную базу данных
log "Проверка восстановленной базы данных..."
if [ "$USE_DOCKER" = "yes" ]; then
    TABLE_COUNT=$(docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\" -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';\"" 2>/dev/null | xargs)
    DB_SIZE=$(docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\" -t -c \"SELECT pg_size_pretty(pg_database_size('$DB_NAME'));\"" 2>/dev/null | xargs)
else
    export PGPASSWORD="$DB_PASSWORD"
    TABLE_COUNT=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)
    DB_SIZE=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | xargs)
    unset PGPASSWORD
fi

if [ -n "$TABLE_COUNT" ]; then
    log "Количество таблиц в базе данных: $TABLE_COUNT"
fi
if [ -n "$DB_SIZE" ]; then
    log "Размер базы данных: $DB_SIZE"
fi

log "Восстановление завершено успешно!"
