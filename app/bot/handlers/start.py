from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from app.db.session import SessionLocal
from app.services.user.service import UserService


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    telegram_user = update.effective_user
    chat = update.effective_chat

    with SessionLocal() as session:

        UserService.create_or_update_user(
            session,
            telegram_user_id=telegram_user.id,
            telegram_chat_id=chat.id,
            name=telegram_user.full_name,
        )

        session.commit()

    keyboard = [
        [
            InlineKeyboardButton(
                text="🔗 Підключити Google Calendar",
                url="https://stem-occultist-directly.ngrok-free.dev/auth/google/start",
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=(
            "Привіт 👋\n\n"
            "Я допоможу створювати події у вашому Google Calendar.\n\n"
            "Для початку необхідно підключити Google Calendar."
        ),
        reply_markup=reply_markup,
    )