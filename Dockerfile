FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (включая зависимости для Playwright/Chromium)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры Playwright
# Зависимости уже установлены выше, поэтому install-deps не нужен
RUN python -m playwright install chromium

# Копируем проект
COPY . .

# Создаем директории для media и static
RUN mkdir -p /app/media /app/staticfiles

# Собираем статические файлы
RUN python manage.py collectstatic --noinput || true

# Открываем порт
EXPOSE 8000

# Команда для запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

