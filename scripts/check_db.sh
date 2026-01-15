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

# Загрузка переменных окружения из .env файла
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Настройки базы данных
DB_NAME="${DB_NAME:-mona_db}"
DB_USER="${DB_USER:-mona_user}"
DB_PASSWORD="${DB_PASSWORD:-mona_password}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Настройки Docker
DOCKER_CONTAINER="${DOCKER_CONTAINER:-db}"
USE_DOCKER="${USE_DOCKER:-auto}"

echo -e "${BLUE}=== Проверка состояния базы данных PostgreSQL ===${NC}\n"

# Определяем, используется ли Docker
if [ "$USE_DOCKER" = "auto" ]; then
    if command -v docker &> /dev/null && docker ps --format '{{.Names}}' | grep -q "^${DOCKER_CONTAINER}$"; then
        USE_DOCKER="yes"
        echo -e "${GREEN}✓${NC} Обнаружен Docker контейнер: $DOCKER_CONTAINER"
        if [ "$DB_HOST" = "db" ]; then
            DB_HOST="localhost"
        fi
    else
        USE_DOCKER="no"
        echo -e "${YELLOW}⚠${NC} Docker контейнер не найден, используем прямое подключение"
        if [ "$DB_HOST" = "db" ]; then
            DB_HOST="localhost"
            echo -e "${YELLOW}⚠${NC} Исправлен DB_HOST на localhost"
        fi
    fi
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
        export PGPASSWORD="$DB_PASSWORD"
        docker exec "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "$query" 2>/dev/null | xargs
        unset PGPASSWORD
    else
        export PGPASSWORD="$DB_PASSWORD"
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "$query" 2>/dev/null | xargs
        unset PGPASSWORD
    fi
}

# Проверка подключения
echo -e "${BLUE}1. Проверка подключения к базе данных...${NC}"
if [ "$USE_DOCKER" = "yes" ]; then
    if docker exec "$DOCKER_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; then
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
        export PGPASSWORD="$DB_PASSWORD"
        docker exec "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
            SELECT 
                schemaname || '.' || tablename AS table_name,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 20;
        " 2>/dev/null || echo -e "${YELLOW}⚠${NC} Не удалось получить список таблиц"
        unset PGPASSWORD
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
    export PGPASSWORD="$DB_PASSWORD"
    if docker exec "$DOCKER_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" 2>/dev/null | head -50 > "$TEMP_BACKUP"; then
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

