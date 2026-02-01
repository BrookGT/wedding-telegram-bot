import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Load environment variables
#BOT_TOKEN = os.getenv("8528903183:AAE64cLbQBzBFO5PPNaO0ebgY_kudmJN-c0")
BOT_TOKEN = os.getenv("BOT_TOKEN")
#GROUP_CHAT_ID = int(os.getenv("-1003528787199"))
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


# Initialize Telegram bot application
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

# ---- Bot logic ----
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    username = f"@{user.username}" if user.username else "No username"

    caption = (
        f"📸 Wedding Upload\n"
        f"👤 Name: {user.full_name}\n"
        f"🔗 Username: {username}"
    )

    if msg.photo:
        await context.bot.send_photo(GROUP_CHAT_ID, msg.photo[-1].file_id, caption=caption)
    elif msg.video:
        await context.bot.send_video(GROUP_CHAT_ID, msg.video.file_id, caption=caption)
    elif msg.document:
        await context.bot.send_document(GROUP_CHAT_ID, msg.document.file_id, caption=caption)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💍 Welcome! Send your wedding photos or videos here 📸"
    )

# Add handlers
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(MessageHandler(filters.ALL, handle_media))

# ---- Flask server for webhook ----
flask_app = Flask(__name__)

@flask_app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), app_bot.bot)
    app_bot.update_queue.put(update)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    webhook_url = os.environ.get("WEBHOOK_URL")
    # Start webhook mode
    app_bot.run_webhook(listen="0.0.0.0", port=port, webhook_url=webhook_url)
