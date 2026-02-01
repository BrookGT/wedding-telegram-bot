import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ------------------------------
# Environment variables
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://<your-service>.onrender.com/<BOT_TOKEN>

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
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user.first_name} sent a photo!"
        )
    elif update.message.video:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user.first_name} sent a video!"
        )

# ------------------------------
# Telegram Application
# ------------------------------
# Do NOT call .run_polling() or anything similar
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
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

    # Put the update into the bot's queue asynchronously
    asyncio.get_event_loop().create_task(app_bot.update_queue.put(update))

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
