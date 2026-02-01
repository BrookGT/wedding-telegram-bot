import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


# ------------------------------
# Environment variables
# ------------------------------
BOT_TOKEN = require_env("BOT_TOKEN")
GROUP_CHAT_ID = int(require_env("GROUP_CHAT_ID"))
WEBHOOK_URL = require_env("WEBHOOK_URL")  # e.g., https://<service>.onrender.com/<BOT_TOKEN>

# ------------------------------
# Flask app
# ------------------------------
flask_app = Flask(__name__)

# ------------------------------
# Telegram Handlers (no polling!)
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send your wedding photos or videos here!")


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg:
        return

    user = update.effective_user
    full_name = user.full_name if user and user.full_name else "Unknown"
    username = f"@{user.username}" if user and user.username else "(no username)"
    orig_caption = msg.caption or ""

    lines = [
        f"From: {full_name}",
        f"Username: {username}",
    ]
    if orig_caption:
        lines.append(f"Caption: {orig_caption}")
    full_caption = "\n".join(lines)

    if msg.photo:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=msg.photo[-1].file_id, caption=full_caption)
    elif msg.video:
        await context.bot.send_video(chat_id=GROUP_CHAT_ID, video=msg.video.file_id, caption=full_caption)
    elif msg.document:
        await context.bot.send_document(chat_id=GROUP_CHAT_ID, document=msg.document.file_id, caption=full_caption)
    else:
        # Ignore other message types silently
        return


# ------------------------------
# Telegram Application
# ------------------------------
# Disable the legacy Updater to avoid AttributeError
app_bot = Application.builder().token(BOT_TOKEN).updater(None).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_media))


# ------------------------------
# Webhook endpoint
# ------------------------------
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Receive updates from Telegram via webhook."""
    data = request.get_json(force=True)
    update = Update.de_json(data, app_bot.bot)
    # Process the update immediately in this thread (sync context)
    asyncio.run(app_bot.process_update(update))
    return "ok", 200


# ------------------------------
# Health check
# ------------------------------
@flask_app.route("/")
def index():
    return "Bot is running!"


# ------------------------------
# Main entry (Flask only)
# ------------------------------
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
