#!/bin/bash
# Скрипт для проверки состояния базы данных PostgreSQL
# Помогает диагностировать проблемы с бэкапами

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Определяем директорию скрипта и корень проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Загрузка переменных окружения из .env файла
ENV_FILE="${ENV_FILE:-$PROJECT_ROOT/.env}"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo -e "${GREEN}✓${NC} Загружен .env файл: $ENV_FILE"
else
    echo -e "${YELLOW}⚠${NC} .env файл не найден: $ENV_FILE (используются значения по умолчанию)"
fi

# Настройки базы данных
DB_NAME="${DB_NAME:-mona_db}"
DB_USER="${DB_USER:-mona_user}"
DB_PASSWORD="${DB_PASSWORD:-mona_password}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Определяем директорию скрипта и корень проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Настройки Docker
DOCKER_CONTAINER="${DOCKER_CONTAINER:-}"
USE_DOCKER="${USE_DOCKER:-auto}"
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-}"

echo -e "${BLUE}=== Проверка состояния базы данных PostgreSQL ===${NC}\n"

# Функция определения Docker Compose проекта и контейнера
detect_docker_compose() {
    # Используем явно docker-compose.prod.yml
    local compose_file="docker-compose.prod.yml"
    local compose_path="$PROJECT_ROOT/$compose_file"
    
    if [ -f "$compose_path" ]; then
        DOCKER_COMPOSE_FILE="$compose_path"
        echo -e "${GREEN}✓${NC} Найден Docker Compose файл: $compose_file"
        
        if command -v docker-compose > /dev/null 2>&1; then
            local container_name=$(cd "$PROJECT_ROOT" && docker-compose -f "$compose_file" ps -q db 2>/dev/null | head -1)
            if [ -n "$container_name" ]; then
                DOCKER_CONTAINER=$(docker ps --format '{{.Names}}' --filter "id=$container_name" 2>/dev/null | head -1)
            fi
        elif command -v docker > /dev/null 2>&1 && docker compose version > /dev/null 2>&1; then
            local container_name=$(cd "$PROJECT_ROOT" && docker compose -f "$compose_file" ps -q db 2>/dev/null | head -1)
            if [ -n "$container_name" ]; then
                DOCKER_CONTAINER=$(docker ps --format '{{.Names}}' --filter "id=$container_name" 2>/dev/null | head -1)
            fi
        fi
        
        if [ -n "$DOCKER_CONTAINER" ]; then
            echo -e "${GREEN}✓${NC} Найден контейнер БД через Docker Compose: $DOCKER_CONTAINER"
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
    
    local env_vars=$(docker inspect "$DOCKER_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null)
    
    if [ -z "$env_vars" ]; then
        return 1
    fi
    
    local postgres_db=$(echo "$env_vars" | grep "^POSTGRES_DB=" | cut -d'=' -f2 | head -1)
    local postgres_user=$(echo "$env_vars" | grep "^POSTGRES_USER=" | cut -d'=' -f2 | head -1)
    local postgres_password=$(echo "$env_vars" | grep "^POSTGRES_PASSWORD=" | cut -d'=' -f2 | head -1)
    
    if [ -n "$postgres_db" ]; then
        DB_NAME="$postgres_db"
        echo -e "${GREEN}✓${NC} Получено DB_NAME из контейнера: $DB_NAME"
    fi
    if [ -n "$postgres_user" ]; then
        DB_USER="$postgres_user"
        echo -e "${GREEN}✓${NC} Получено DB_USER из контейнера: $DB_USER"
    fi
    if [ -n "$postgres_password" ]; then
        DB_PASSWORD="$postgres_password"
        echo -e "${GREEN}✓${NC} Получено DB_PASSWORD из контейнера (скрыто)"
    fi
    
    return 0
}

# Функция выполнения команды в Docker контейнере
docker_exec() {
    local cmd="$1"
    if [ -n "$DOCKER_COMPOSE_FILE" ]; then
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

# Определяем, используется ли Docker
if [ "$USE_DOCKER" = "auto" ]; then
    if detect_docker_compose; then
        USE_DOCKER="yes"
        get_db_config_from_container || echo -e "${YELLOW}⚠${NC} Не удалось получить настройки БД из контейнера"
    elif command -v docker > /dev/null 2>&1; then
        found_container=$(docker ps --format '{{.Names}}' | grep -E "^(.*_)?db(_.*)?$" | head -1)
        if [ -n "$found_container" ]; then
            DOCKER_CONTAINER="$found_container"
            USE_DOCKER="yes"
            echo -e "${GREEN}✓${NC} Найден Docker контейнер БД: $DOCKER_CONTAINER"
            get_db_config_from_container || echo -e "${YELLOW}⚠${NC} Не удалось получить настройки БД из контейнера"
        else
            USE_DOCKER="no"
            echo -e "${YELLOW}⚠${NC} Docker контейнер БД не найден, используем прямое подключение"
            if [ "$DB_HOST" = "db" ]; then
                DB_HOST="localhost"
                echo -e "${YELLOW}⚠${NC} Исправлен DB_HOST на localhost"
            fi
        fi
    else
        USE_DOCKER="no"
        echo -e "${YELLOW}⚠${NC} Docker не установлен, используем прямое подключение"
        if [ "$DB_HOST" = "db" ]; then
            DB_HOST="localhost"
            echo -e "${YELLOW}⚠${NC} Исправлен DB_HOST на localhost"
        fi
    fi
elif [ "$USE_DOCKER" = "yes" ]; then
    if [ -z "$DOCKER_CONTAINER" ]; then
        DOCKER_CONTAINER="db"
    fi
    if ! docker ps --format '{{.Names}}' | grep -q "^${DOCKER_CONTAINER}$"; then
        echo -e "${RED}✗${NC} Указанный Docker контейнер не найден: $DOCKER_CONTAINER"
        exit 1
    fi
    get_db_config_from_container || echo -e "${YELLOW}⚠${NC} Не удалось получить настройки БД из контейнера"
fi

echo ""
echo -e "${BLUE}Параметры подключения:${NC}"
echo "  DB_NAME: $DB_NAME"
echo "  DB_USER: $DB_USER"
echo "  DB_HOST: $DB_HOST"
echo "  DB_PORT: $DB_PORT"
echo "  USE_DOCKER: $USE_DOCKER"
if [ "$USE_DOCKER" = "yes" ]; then
    echo "  DOCKER_CONTAINER: $DOCKER_CONTAINER"
fi
echo ""

# Функция выполнения SQL запроса
run_sql() {
    local query="$1"
    if [ "$USE_DOCKER" = "yes" ]; then
        docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\" -t -c \"$query\"" 2>/dev/null | xargs
    else
        export PGPASSWORD="$DB_PASSWORD"
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "$query" 2>/dev/null | xargs
        unset PGPASSWORD
    fi
}

# Проверка подключения
echo -e "${BLUE}1. Проверка подключения к базе данных...${NC}"
if [ "$USE_DOCKER" = "yes" ]; then
    if docker_exec "pg_isready -U \"$DB_USER\" -d \"$DB_NAME\"" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Подключение успешно"
    else
        echo -e "${RED}✗${NC} Не удалось подключиться к базе данных"
        exit 1
    fi
else
    export PGPASSWORD="$DB_PASSWORD"
    if PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Подключение успешно"
    else
        echo -e "${RED}✗${NC} Не удалось подключиться к базе данных: $DB_HOST:$DB_PORT"
        unset PGPASSWORD
        exit 1
    fi
    unset PGPASSWORD
fi

# Размер базы данных
echo ""
echo -e "${BLUE}2. Размер базы данных:${NC}"
DB_SIZE=$(run_sql "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));")
if [ -n "$DB_SIZE" ]; then
    echo -e "${GREEN}✓${NC} Размер: $DB_SIZE"
else
    echo -e "${RED}✗${NC} Не удалось определить размер"
fi

# Количество таблиц
echo ""
echo -e "${BLUE}3. Количество таблиц:${NC}"
TABLE_COUNT=$(run_sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
if [ -n "$TABLE_COUNT" ]; then
    echo -e "${GREEN}✓${NC} Таблиц в схеме public: $TABLE_COUNT"
else
    echo -e "${RED}✗${NC} Не удалось подсчитать таблицы"
fi

# Список таблиц и их размеры
if [ -n "$TABLE_COUNT" ] && [ "$TABLE_COUNT" -gt 0 ]; then
    echo ""
    echo -e "${BLUE}4. Таблицы и их размеры:${NC}"
    if [ "$USE_DOCKER" = "yes" ]; then
        docker_exec "PGPASSWORD=\"$DB_PASSWORD\" psql -U \"$DB_USER\" -d \"$DB_NAME\" -c \"
            SELECT 
                schemaname || '.' || tablename AS table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 20;
        \"" 2>/dev/null || echo -e "${YELLOW}⚠${NC} Не удалось получить список таблиц"
    else
        export PGPASSWORD="$DB_PASSWORD"
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
            SELECT 
                schemaname || '.' || tablename AS table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 20;
        " 2>/dev/null || echo -e "${YELLOW}⚠${NC} Не удалось получить список таблиц"
        unset PGPASSWORD
    fi
fi

# Количество записей в основных таблицах
echo ""
echo -e "${BLUE}5. Количество записей в основных таблицах:${NC}"
TABLES=("core_telegramuser" "core_qrcode" "core_gift" "core_giftredemption" "core_qrcodescanattempt")
for table in "${TABLES[@]}"; do
    COUNT=$(run_sql "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "N/A")
    if [ "$COUNT" != "N/A" ] && [ -n "$COUNT" ]; then
        echo "  $table: $COUNT записей"
    fi
done

# Тестовый бэкап
echo ""
echo -e "${BLUE}6. Тестовый бэкап (первые 50 строк):${NC}"
TEMP_BACKUP="/tmp/test_backup_$$.sql"
if [ "$USE_DOCKER" = "yes" ]; then
    if docker_exec "pg_dump -U \"$DB_USER\" -d \"$DB_NAME\"" 2>/dev/null | head -50 > "$TEMP_BACKUP"; then
        BACKUP_SIZE=$(stat -f%z "$TEMP_BACKUP" 2>/dev/null || stat -c%s "$TEMP_BACKUP" 2>/dev/null || echo "0")
        if [ "$BACKUP_SIZE" -gt 1000 ]; then
            echo -e "${GREEN}✓${NC} Тестовый бэкап создан успешно (размер: ${BACKUP_SIZE} байт)"
            echo -e "${BLUE}Первые строки бэкапа:${NC}"
            head -20 "$TEMP_BACKUP"
        else
            echo -e "${RED}✗${NC} Тестовый бэкап слишком маленький (${BACKUP_SIZE} байт)!"
            echo -e "${YELLOW}⚠${NC} Возможно, база данных пустая или есть проблема с подключением"
        fi
    else
        echo -e "${RED}✗${NC} Ошибка при создании тестового бэкапа"
    fi
    unset PGPASSWORD
    rm -f "$TEMP_BACKUP"
else
    export PGPASSWORD="$DB_PASSWORD"
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" 2>/dev/null | head -50 > "$TEMP_BACKUP"; then
        BACKUP_SIZE=$(stat -f%z "$TEMP_BACKUP" 2>/dev/null || stat -c%s "$TEMP_BACKUP" 2>/dev/null || echo "0")
        if [ "$BACKUP_SIZE" -gt 1000 ]; then
            echo -e "${GREEN}✓${NC} Тестовый бэкап создан успешно (размер: ${BACKUP_SIZE} байт)"
            echo -e "${BLUE}Первые строки бэкапа:${NC}"
            head -20 "$TEMP_BACKUP"
        else
            echo -e "${RED}✗${NC} Тестовый бэкап слишком маленький (${BACKUP_SIZE} байт)!"
            echo -e "${YELLOW}⚠${NC} Возможно, база данных пустая или есть проблема с подключением"
        fi
    else
        echo -e "${RED}✗${NC} Ошибка при создании тестового бэкапа"
    fi
    unset PGPASSWORD
    rm -f "$TEMP_BACKUP"
fi

echo ""
echo -e "${BLUE}=== Проверка завершена ===${NC}"

