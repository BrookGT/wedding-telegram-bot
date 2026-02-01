from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

flask_app = Flask(__name__)

# Create the Telegram app without build()
app_bot = Application.builder().token(BOT_TOKEN).build()  # still okay, don't call .build() for polling

# Command /start
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

# Webhook endpoint
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), app_bot.bot)
    await app_bot.update_queue.put(update)
    return "ok"

# Health check
@flask_app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    flask_app.run(port=5000)
