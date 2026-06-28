import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from app.db.session import SessionLocal
from app.services.users.service import UserService


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    telegram_user = update.effective_user
    chat = update.effective_chat

    with SessionLocal() as session:

        user = UserService.create_or_update_user(
            session,
            telegram_user_id=telegram_user.id,
            telegram_chat_id=chat.id,
            name=telegram_user.full_name,
            timezone="Europe/Kyiv",
            default_city="Kyiv",
            default_country="Ukraine"
        )

        session.commit()

    BASE_URL = os.getenv("BASE_URL")

    keyboard = [
        [
            InlineKeyboardButton(
                text="🔗 Підключити Google Calendar",
                url=f"{BASE_URL}/auth/google/start?telegram_user_id={telegram_user.id}",
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=(
            "Привіт 👋\n\n"
            "Я допоможу створювати події у вашому Google Calendar.\n\n"
            "Після підключення Google-акаунта ви зможете обрати календар, "
            "у який бот буде створювати всі події."
        ),
        reply_markup=reply_markup,
    )