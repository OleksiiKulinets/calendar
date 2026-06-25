import os
from dotenv import load_dotenv

from telegram.ext import (Application, CommandHandler, MessageHandler, filters,)

from app.bot.handlers.start import start
from app.bot.middlewares.logger import log_update

load_dotenv()

TOKEN = os.getenv("TOKEN")


def main():
    if not TOKEN:
        raise ValueError("TOKEN is missing in .env file")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.ALL, log_update)
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()