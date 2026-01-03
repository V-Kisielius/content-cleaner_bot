import asyncio
import logging
from collections import defaultdict
from telegram import Update, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Storage for media groups
media_groups = defaultdict(list)
media_group_tasks = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id

    # Check if user is authorized
    if user_id != config.USER_ID:
        await update.message.reply_text(
            "❌ Access denied. You are not authorized to use this bot."
        )
        logger.warning(f"Unauthorized access attempt from user {user_id}")
        return

    welcome_message = (
        "👋 Welcome to Content Cleaner Bot!\n\n"
        "🤖 I help you clean media files from metadata and captions.\n\n"
        "📌 How to use:\n"
        "• Send me any media file (photo, video, document, audio, sticker)\n"
        "• I will remove sender info and captions\n"
        "• Send the cleaned file to your channel or direct messages\n\n"
        "💡 All media types and albums are supported\n\n"
        "Use /help for more information."
    )

    await update.message.reply_text(welcome_message)
    logger.info(f"User {user_id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id

    # Check if user is authorized
    if user_id != config.USER_ID:
        await update.message.reply_text(
            "❌ Access denied. You are not authorized to use this bot."
        )
        logger.warning(f"Unauthorized access attempt from user {user_id}")
        return

    help_message = (
        "ℹ️ Content Cleaner Bot Help\n\n"
        "📋 Commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n\n"
        "🎯 Supported media types:\n"
        "• 📸 Photos\n"
        "• 🎥 Videos\n"
        "• 🎵 Audio and voice messages\n"
        "• 📄 Documents\n"
        "• 🎬 GIF animations\n"
        "• 😀 Stickers\n"
        "• 🖼 Albums (media groups)\n\n"
        "⚙️ What the bot does:\n"
        "1. Receives media file from you\n"
        "2. Removes sender information\n"
        "3. Removes captions and metadata\n"
        "4. Sends the cleaned file\n\n"
        "✅ File quality is preserved!\n\n"
        "❓ Issues? Check your bot settings in .env file"
    )

    await update.message.reply_text(help_message)
    logger.info(f"User {user_id} requested help")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages without media"""
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id

    # Check if user is authorized
    if user_id != config.USER_ID:
        await update.message.reply_text(
            "❌ Access denied. You are not authorized to use this bot."
        )
        logger.warning(f"Unauthorized text message from user {user_id}")
        return

    # User is authorized but sent text instead of media
    await update.message.reply_text(
        "⚠️ Please send a media file for processing.\n\n"
        "I can only process media files:\n"
        "• Photos\n"
        "• Videos\n"
        "• Audio\n"
        "• Documents\n"
        "• Stickers\n"
        "• Animations (GIF)\n\n"
        "Use /help for more information."
    )
    logger.info(f"User {user_id} sent text message instead of media")


async def send_media_group_delayed(context: ContextTypes.DEFAULT_TYPE, media_group_id: str, user_id: int):
    """Send media group after a delay to collect all items"""
    await asyncio.sleep(1)  # Wait 1 second to collect all media in the group

    if media_group_id in media_groups:
        media_list = media_groups[media_group_id]

        if media_list:
            try:
                # Prepare media for sending (without captions)
                input_media = []
                for media_item in media_list:
                    media_type = media_item['type']
                    file_id = media_item['file_id']

                    if media_type == 'photo':
                        input_media.append(InputMediaPhoto(media=file_id))
                    elif media_type == 'video':
                        input_media.append(InputMediaVideo(media=file_id))
                    elif media_type == 'document':
                        input_media.append(InputMediaDocument(media=file_id))
                    elif media_type == 'audio':
                        input_media.append(InputMediaAudio(media=file_id))

                # Send media group to channel or user
                target_chat = config.CHANNEL_ID if config.CHANNEL_ID else user_id
                sent_messages = await context.bot.send_media_group(
                    chat_id=target_chat,
                    media=input_media
                )
                logger.info(f"Sent media group {media_group_id} with {len(input_media)} items to {'channel' if config.CHANNEL_ID else 'user'} {target_chat}")
            except Exception as e:
                logger.error(f"Error sending media group: {e}")

        # Clean up
        del media_groups[media_group_id]
        if media_group_id in media_group_tasks:
            del media_group_tasks[media_group_id]


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all media messages"""
    # Check if message and user exist
    if not update.message or not update.effective_user:
        logger.warning("Received update without message or user")
        return

    message = update.message
    user_id = update.effective_user.id

    # Check if user is authorized
    if user_id != config.USER_ID:
        await message.reply_text(
            "❌ Access denied. You are not authorized to use this bot."
        )
        logger.warning(f"Unauthorized media upload attempt from user {user_id}")
        return

    media_group_id = message.media_group_id

    # Determine media type and file_id
    file_id = None
    media_type = None

    try:
        if message.photo:
            file_id = message.photo[-1].file_id  # Get highest quality photo
            media_type = 'photo'
        elif message.video:
            file_id = message.video.file_id
            media_type = 'video'
        elif message.audio:
            file_id = message.audio.file_id
            media_type = 'audio'
        elif message.voice:
            file_id = message.voice.file_id
            media_type = 'voice'
        elif message.video_note:
            file_id = message.video_note.file_id
            media_type = 'video_note'
        elif message.document:
            file_id = message.document.file_id
            media_type = 'document'
        elif message.animation:
            file_id = message.animation.file_id
            media_type = 'animation'
        elif message.sticker:
            file_id = message.sticker.file_id
            media_type = 'sticker'
    except Exception as e:
        logger.error(f"Error extracting media info: {e}")
        return

    if not file_id:
        logger.warning("No media found in message")
        return

    logger.info(f"Processing {media_type} from user {user_id}")

    # Handle media groups (albums)
    if media_group_id:
        # Add to media group collection
        media_groups[media_group_id].append({
            'type': media_type,
            'file_id': file_id,
            'user_id': user_id
        })

        # Cancel existing task if any
        if media_group_id in media_group_tasks:
            media_group_tasks[media_group_id].cancel()

        # Schedule sending with delay
        task = asyncio.create_task(send_media_group_delayed(context, media_group_id, user_id))
        media_group_tasks[media_group_id] = task

    else:
        # Handle single media
        try:
            target_chat = config.CHANNEL_ID if config.CHANNEL_ID else user_id

            if media_type == 'photo':
                await context.bot.send_photo(chat_id=target_chat, photo=file_id)
            elif media_type == 'video':
                await context.bot.send_video(chat_id=target_chat, video=file_id)
            elif media_type == 'audio':
                await context.bot.send_audio(chat_id=target_chat, audio=file_id)
            elif media_type == 'voice':
                await context.bot.send_voice(chat_id=target_chat, voice=file_id)
            elif media_type == 'video_note':
                await context.bot.send_video_note(chat_id=target_chat, video_note=file_id)
            elif media_type == 'document':
                await context.bot.send_document(chat_id=target_chat, document=file_id)
            elif media_type == 'animation':
                await context.bot.send_animation(chat_id=target_chat, animation=file_id)
            elif media_type == 'sticker':
                await context.bot.send_sticker(chat_id=target_chat, sticker=file_id)

            logger.info(f"Sent {media_type} to {'channel' if config.CHANNEL_ID else 'user'} {target_chat}")
        except Exception as e:
            logger.error(f"Error sending {media_type}: {e}")


def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Add handler for all media types
    media_filter = (
        filters.PHOTO | filters.VIDEO | filters.AUDIO |
        filters.VOICE | filters.VIDEO_NOTE | filters.Document.ALL |
        filters.ANIMATION | filters.Sticker.ALL
    )
    application.add_handler(MessageHandler(media_filter, handle_media))

    # Add handler for text messages (non-media, non-command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Start the bot
    logger.info("Bot started. Send media to clean and save to channel/user!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
