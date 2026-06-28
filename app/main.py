import os
from dotenv import load_dotenv

from telegram.ext import (Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters,)

from app.bot.handlers.start import start
from app.bot.handlers.calendar import select_calendar
from app.bot.middlewares.logger import log_update

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing in .env file")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(select_calendar, pattern="^calendar:"))

    app.add_handler(
        MessageHandler(filters.ALL, log_update)
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()