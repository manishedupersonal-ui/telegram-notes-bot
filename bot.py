import os
import logging
from dotenv import load_dotenv
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from db import add_note, get_notes

# ------------------ ENV + TOKEN ------------------

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment")

# ------------------ LOGGING ------------------

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ------------------ HANDLERS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome.\n"
        "Commands:\n"
        "/note <text> - save a note\n"
        "/notes - list your notes"
    )

async def note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not context.args:
        await update.message.reply_text("Usage: /note <text>")
        return

    text = " ".join(context.args).strip()

    if len(text) > 200:
        await update.message.reply_text(
            "Note too long. Keep it under 200 characters."
        )
        return

    try:
        add_note(user_id, text)
    except Exception as e:
        logger.exception(e)
        await update.message.reply_text("Failed to save note.")
        return

    await update.message.reply_text("Note saved.")

async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    try:
        notes = get_notes(user_id)
    except Exception as e:
        logger.exception(e)
        await update.message.reply_text("Failed to fetch notes.")
        return

    if not notes:
        await update.message.reply_text("No notes found.")
        return

    message = "\n".join(f"- {n[0]}" for n in notes)
    await update.message.reply_text(message)

# ------------------ HEALTH SERVER ------------------

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# ------------------ APP ------------------

def main():
    # start health server FIRST
    Thread(target=run_health_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("note", note))
    app.add_handler(CommandHandler("notes", notes))

    logger.info("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
