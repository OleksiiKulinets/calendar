from telegram import Bot, InlineKeyboardMarkup
import os


class TelegramService:

    _bot = Bot(
        token=os.getenv("BOT_TOKEN"),
    )

    @classmethod
    async def send_message(
        cls,
        *,
        chat_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ):
        await cls._bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )