# Используем официальный образ Python 3.12
# Use official Python 3.12 runtime as base image
FROM python:3.12-slim

# Метаданные образа
# Set metadata
LABEL maintainer="etoya"
LABEL description="Telegram Content Cleaner Bot - removes metadata and captions from media"

# Устанавливаем рабочую директорию внутри контейнера
# Set working directory inside container
WORKDIR /app

# Переменные окружения
# Environment variables

# Предотвращает создание .pyc файлов (оптимизация)
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1

# Отключает буферизацию stdout/stderr (важно для логов в реальном времени)
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Копируем файл зависимостей
# Copy requirements file
COPY requirements.txt .

# Устанавливаем Python зависимости
# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
# Copy application code
COPY bot.py .
COPY config.py .

# Создаём непривилегированного пользователя для безопасности
# Create non-root user for security
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Переключаемся на непривилегированного пользователя
# Switch to non-root user
USER botuser

# Команда запуска бота
# Command to run the bot
CMD ["python", "bot.py"]
