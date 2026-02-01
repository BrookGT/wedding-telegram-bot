import os
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
# Load environment variables
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
# Example: WEBHOOK_URL = "https://your-render-url.com/" + BOT_TOKEN
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ------------------------------
# Flask app
# ------------------------------
flask_app = Flask(__name__)

# ------------------------------
# Telegram Application (no polling!)
# ------------------------------
# This will be used for webhook updates
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

# ------------------------------
# Command Handlers
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Send your wedding photos or videos here, and I'll forward them to the group."
    )


app_bot.add_handler(CommandHandler("start", start))

# ------------------------------
# Media Handler (photos/videos)
# ------------------------------
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


app_bot.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

# ------------------------------
# Webhook endpoint for Telegram
# ------------------------------
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Receives updates from Telegram via POST"""
    from telegram import Bot
    from telegram.ext import updatequeue

    # Convert JSON into a Telegram Update object
    update = Update.de_json(request.get_json(force=True), app_bot.bot)

    # Put the update into the bot's update queue
    # Must run synchronously because Flask route is sync
    import asyncio
    asyncio.get_event_loop().create_task(app_bot.update_queue.put(update))

    return "ok", 200

# ------------------------------
# Health Check endpoint
# ------------------------------
@flask_app.route("/")
def index():
    return "Bot is running!"

# ------------------------------
# Main entry (Flask only, no polling!)
# ------------------------------
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
