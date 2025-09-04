FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя для запуска приложения
RUN useradd --create-home --shell /bin/bash appuser

# Изменение владельца директории
RUN chown -R appuser:appuser /app
USER appuser

# Запуск приложения (команда задается в docker-compose.yml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]