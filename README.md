# Telegram Content Cleaner Bot

Removes metadata and captions from forwarded media files, then sends clean content to your private channel or direct messages.

## Features

- Supports all media types: photos, videos, audio, voice, documents, GIFs, stickers
- Removes sender info and captions
- Preserves media groups (albums)
- Uses file_id forwarding (no quality loss)
- User authorization with access control
- Error messages for invalid requests
- Interactive commands (/start, /help)

## Quick Start (Docker)

```bash
# 1. Create .env file
cp .env.example .env
nano .env  # Add your BOT_TOKEN, USER_ID, CHANNEL_ID

# 2. Run
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

## Manual Setup

```bash
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add your credentials
python bot.py
```

## Configuration

Create `.env` file with:

```env
BOT_TOKEN=your_bot_token        # From @BotFather
USER_ID=your_user_id            # From @userinfobot
CHANNEL_ID=your_channel_id      # From @userinfobot (optional)
```

**Note:** If using a channel, add bot as admin with post permissions.

## Bot Commands

- `/start` - Welcome message and quick start guide
- `/help` - Detailed help information about supported media types and features

Simply send any media file to the bot to clean it!

## Docker Commands

```bash
docker-compose up -d        # Start
docker-compose down         # Stop
docker-compose restart      # Restart
docker-compose logs -f      # View logs
docker-compose ps           # Status
```

## Troubleshooting

**Bot doesn't start:**
- Check `.env` file exists and contains valid values
- View logs: `docker-compose logs -f`

**Bot doesn't send to channel:**
- Add bot as channel admin
- Verify `CHANNEL_ID` starts with `-100`

**Permission denied:**
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

## Requirements

- Python 3.7+ (3.12 recommended) OR Docker
- python-telegram-bot 20.0+
- python-dotenv

## License

Free to use and modify.
