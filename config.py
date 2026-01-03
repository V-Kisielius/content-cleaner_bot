# Telegram Bot Configuration
# Читает конфигурацию из переменных окружения (файл .env)
# Reads configuration from environment variables (.env file)

import os
from dotenv import load_dotenv

# Загрузить переменные окружения из .env файла
# Load environment variables from .env file
load_dotenv()

# Получить токен бота от @BotFather в Telegram
# Get your bot token from @BotFather in Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set. Please create .env file with BOT_TOKEN")

# Ваш Telegram User ID (получите от @userinfobot)
# Только этот пользователь сможет использовать бота
# Your Telegram User ID (get it from @userinfobot)
# Only this user can use the bot
USER_ID_STR = os.getenv("USER_ID")
if not USER_ID_STR:
    raise ValueError("USER_ID environment variable is not set. Please create .env file with USER_ID")

try:
    USER_ID = int(USER_ID_STR)
except ValueError:
    raise ValueError(f"USER_ID must be a valid integer, got: {USER_ID_STR}")

# ID канала для сохранения очищенных медиа (опционально, если не задан - отправляет пользователю)
# Чтобы получить ID канала: перешлите сообщение из канала боту @userinfobot
# Пример: -1001234567890
# Channel ID for storing cleaned media (optional, if not set - sends to user)
# To get channel ID: forward any message from the channel to @userinfobot
# Example: -1001234567890
CHANNEL_ID_STR = os.getenv("CHANNEL_ID", "")
CHANNEL_ID = None

if CHANNEL_ID_STR:
    try:
        CHANNEL_ID = int(CHANNEL_ID_STR)
    except ValueError:
        raise ValueError(f"CHANNEL_ID must be a valid integer or empty, got: {CHANNEL_ID_STR}")
