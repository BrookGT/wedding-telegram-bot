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
    user = update.effective_user
    if update.message.photo:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"{user.first_name} sent a photo!")
    elif update.message.video:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"{user.first_name} sent a video!")


# ------------------------------
# Telegram Application
# ------------------------------
# Disable the legacy Updater to avoid AttributeError
app_bot = Application.builder().token(BOT_TOKEN).updater(None).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))


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
