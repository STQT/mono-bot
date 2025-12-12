#!/bin/bash
# Скрипт для автоматической настройки ngrok для Web App

set -e

echo "🔧 Настройка ngrok для Telegram Web App"

# Проверяем наличие ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен!"
    echo "Установите ngrok:"
    echo "  macOS: brew install ngrok"
    echo "  Или скачайте с https://ngrok.com/download"
    exit 1
fi

# Проверяем, запущен ли Django сервер
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "⚠️  Django сервер не запущен на порту 8000"
    echo "Запустите: docker-compose up web"
    exit 1
fi

echo "✅ Django сервер доступен"

# Запускаем ngrok в фоне с обходом предупреждения
echo "🚀 Запуск ngrok с обходом предупреждения..."
# Проверяем наличие конфигурационного файла ngrok
NGROK_CONFIG="$HOME/.ngrok2/ngrok.yml"
if [ -f "$NGROK_CONFIG" ]; then
    # Используем конфигурационный файл если он существует
    ngrok start webapp > /tmp/ngrok.log 2>&1 &
    NGROK_PID=$!
else
    # Запускаем с опцией обхода предупреждения через командную строку
    ngrok http 8000 --request-header-add "ngrok-skip-browser-warning: true" > /tmp/ngrok.log 2>&1 &
    NGROK_PID=$!
fi

# Ждем запуска ngrok
sleep 3

# Получаем URL из ngrok API
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Не удалось получить URL от ngrok"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo "✅ ngrok запущен: $NGROK_URL"

# Обновляем .env файл
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  Файл .env не найден, создаю из .env.example"
    cp .env.example .env
fi

# Обновляем или добавляем WEB_APP_URL
if grep -q "^WEB_APP_URL=" "$ENV_FILE"; then
    sed -i.bak "s|^WEB_APP_URL=.*|WEB_APP_URL=$NGROK_URL|" "$ENV_FILE"
else
    echo "WEB_APP_URL=$NGROK_URL" >> "$ENV_FILE"
fi

echo "✅ Обновлен .env файл: WEB_APP_URL=$NGROK_URL"
echo ""
echo "📝 Следующие шаги:"
echo "1. Перезапустите бота: docker-compose restart bot"
echo "2. Откройте бота в Telegram и проверьте кнопку '📱 Мои подарки'"
echo ""
echo "⚠️  ngrok запущен в фоне (PID: $NGROK_PID)"
echo "   Для остановки: kill $NGROK_PID"
echo ""
echo "💡 URL может измениться при перезапуске ngrok"
echo "   Запустите этот скрипт снова для обновления URL"

