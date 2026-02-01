from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os

# Load environment variables
#BOT_TOKEN = os.getenv("8528903183:AAE64cLbQBzBFO5PPNaO0ebgY_kudmJN-c0")
BOT_TOKEN = os.getenv("BOT_TOKEN")
#GROUP_CHAT_ID = int(os.getenv("-1003528787199"))
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


flask_app = Flask(__name__)

# Create Telegram application
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

# Example: /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your wedding photos here!")

app_bot.add_handler(CommandHandler("start", start))

# Handle photos & videos
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message.photo:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                       text=f"{user.first_name} sent a photo!")
    elif update.message.video:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                       text=f"{user.first_name} sent a video!")

app_bot.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

# Telegram webhook endpoint
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), app_bot.bot)
    app_bot.update_queue.put(update)
    return "ok"

# Health check (optional)
@flask_app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    flask_app.run(port=5000)